import json
import subprocess
import time

import requests


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"

BACKEND_CONTAINER = "ai-incident-backend"
FRONTEND_CONTAINER = "ai-incident-frontend"

SERVICE_NAME = "payments-api"

INCIDENT = (
    "The payments-api service is responding very slowly. "
    "CPU utilization has remained above 95% and users are "
    "reporting timeouts. Investigate the issue and recommend "
    "what should be done."
)


# ============================================================
# HELPER
# ============================================================

def run_docker_command(*args, timeout=900):

    result = subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout
    )

    assert result.returncode == 0, result.stderr

    return result.stdout.strip()

def wait_for_backend(timeout=120):
    """
    Wait until FastAPI becomes healthy.
    """

    deadline = time.time() + timeout

    while time.time() < deadline:

        try:
            response = requests.get(
                f"{BACKEND_URL}/status",
                timeout=5
            )

            if response.status_code == 200:
                return

        except requests.RequestException:
            pass

        time.sleep(2)

    raise AssertionError(
        "Backend did not become healthy after restart."
    )


# ============================================================
# TEST 1
# BACKEND CONTAINER + FASTAPI HEALTH
# ============================================================

def test_01_backend_health():

    output = run_docker_command(
        "inspect",
        "-f",
        "{{.State.Running}}",
        BACKEND_CONTAINER
    )

    assert output.lower() == "true"

    # Wait until FastAPI is actually ready
    wait_for_backend(timeout=120)

    response = requests.get(
        f"{BACKEND_URL}/status",
        timeout=10
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ============================================================
# TEST 2
# FRONTEND → BACKEND DOCKER NETWORKING
# ============================================================

def test_02_frontend_to_backend_network():

    # Make sure backend FastAPI is actually ready
    wait_for_backend(timeout=120)

    output = run_docker_command(
        "exec",
        FRONTEND_CONTAINER,
        "python",
        "-c",
        (
            "import requests; "
            "r=requests.get("
            "'http://backend:8000/status', timeout=10"
            "); "
            "print(r.status_code); "
            "print(r.json()['status'])"
        )
    )

    assert "200" in output
    assert "healthy" in output.lower()


# ============================================================
# TEST 3
# CHROMADB PERSISTENCE / COLLECTION
# ============================================================

def test_03_chroma_database():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-c",
        (
            "import chromadb; "
            "c=chromadb.PersistentClient("
            "path='/app/data/chroma_db'); "
            "x=c.get_collection('incident_knowledge'); "
            "print(x.name); "
            "print(x.count())"
        )
    )

    lines = output.splitlines()

    assert "incident_knowledge" in output

    chunk_count = int(lines[-1])

    assert chunk_count > 0


# ============================================================
# TEST 4
# KNOWLEDGE RAG MCP
# ============================================================

def test_04_knowledge_rag_mcp():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-m",
        "src.mcp_src.clients.knowledge_rag_client",
        timeout=900
    )

    assert "search_knowledge" in output

    # We expect a grounded answer from our project knowledge.
    assert "grounded" in output.lower()


# ============================================================
# TEST 5
# IT OPERATIONS MCP
# ============================================================

def test_05_it_operations_mcp():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-m",
        "src.mcp_src.clients.it_operations_client"
    )

    assert "get_service_health" in output
    assert "get_service_logs" in output
    assert "restart_service" in output

    assert SERVICE_NAME in output


# ============================================================
# TEST 6
# TICKET MANAGEMENT MCP
# ============================================================

def test_06_ticket_management_mcp():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-m",
        "src.mcp_src.clients.ticket_management_client"
    )

    assert "get_ticket" in output
    assert "create_ticket" in output
    assert "update_ticket" in output


# ============================================================
# TEST 7
# ASSET MANAGEMENT MCP
# ============================================================

def test_07_asset_management_mcp():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-m",
        "src.mcp_src.clients.asset_management_client"
    )

    assert "get_service_asset" in output
    assert SERVICE_NAME in output


# ============================================================
# TEST 8
# COMPLETE MULTI-AGENT WORKFLOW
# ============================================================

def test_08_complete_multi_agent_workflow():

    output = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-m",
        "src.agents_src.crews.incident_resolution_workflow",
        timeout=900
    )

    assert "INCIDENT WORKFLOW COMPLETED" in output
    assert "Route:" in output


# ============================================================
# TEST 9
# FASTAPI INCIDENT ENDPOINT
# ============================================================

def test_09_fastapi_incident_resolution():

    response = requests.post(
        f"{BACKEND_URL}/incidents/resolve",
        json={
            "incident": INCIDENT
        },
        timeout=900
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "route" in data
    assert "classification" in data
    assert "knowledge" in data

    # Operational incidents should continue to investigation.
    assert data.get("investigation") is not None

    assert data.get("resolution") is not None


# ============================================================
# TEST 10
# HUMAN APPROVAL — REJECT
# ============================================================

def test_10_human_approval_reject():

    response = requests.post(
        f"{BACKEND_URL}/actions/execute",
        json={
            "service_name": SERVICE_NAME,
            "action": "restart",
            "approved": False
        },
        timeout=30
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["approval_status"] == "REJECTED"
    assert data["execution_status"] == "NOT_EXECUTED"


# ============================================================
# TEST 11
# HUMAN APPROVAL — APPROVE
# ============================================================

def test_11_human_approval_approve():

    response = requests.post(
        f"{BACKEND_URL}/actions/execute",
        json={
            "service_name": SERVICE_NAME,
            "action": "restart",
            "approved": True
        },
        timeout=60
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["approval_status"] == "APPROVED"
    assert data["execution_status"] == "COMPLETED"


# ============================================================
# TEST 12
# PERSISTENCE AFTER BACKEND CONTAINER RESTART
# ============================================================

def test_12_backend_restart_persistence():

    # --------------------------------------------------------
    # 1. Read service_state.json BEFORE restart
    # --------------------------------------------------------

    before_raw = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-c",
        (
            "from pathlib import Path; "
            "print(Path('/app/data/service_state.json')"
            ".read_text())"
        )
    )

    before_state = json.loads(before_raw)

    assert SERVICE_NAME in before_state["services"]

    # --------------------------------------------------------
    # 2. Restart ONLY backend container
    # --------------------------------------------------------

    run_docker_command(
        "compose",
        "restart",
        "backend"
    )

    # --------------------------------------------------------
    # 3. Wait for FastAPI to become available again
    # --------------------------------------------------------

    wait_for_backend(timeout=120)

    # --------------------------------------------------------
    # 4. Read state AFTER restart
    # --------------------------------------------------------

    after_raw = run_docker_command(
        "exec",
        BACKEND_CONTAINER,
        "python",
        "-c",
        (
            "from pathlib import Path; "
            "print(Path('/app/data/service_state.json')"
            ".read_text())"
        )
    )

    after_state = json.loads(after_raw)

    # --------------------------------------------------------
    # 5. State must survive container restart
    # --------------------------------------------------------

    assert before_state == after_state

    # --------------------------------------------------------
    # 6. Verify backend is still healthy
    # --------------------------------------------------------

    response = requests.get(
        f"{BACKEND_URL}/status",
        timeout=10
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"