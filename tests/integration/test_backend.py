# ============================================================
# STEP 1: IMPORTS
# ============================================================

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.backend_src.main import app

from src.agents_src.schemas.incident_classification_schemas import (
    IncidentClassification
)

from src.agents_src.schemas.knowledge_schemas import (
    KnowledgeResult
)

from src.agents_src.schemas.investigation_schemas import (
    InvestigationResult
)

from src.agents_src.schemas.resolution_schemas import (
    ResolutionResult
)


# ============================================================
# STEP 2: CREATE FASTAPI TEST CLIENT
# ============================================================

client = TestClient(app)


# ============================================================
# STEP 3: TEST STATUS ENDPOINT
# ============================================================

def test_status_endpoint():

    response = client.get("/status")

    assert response.status_code == 200

    assert response.json() == {
        #"status": "running"
        "status": "healthy"
    }


# ============================================================
# STEP 4: TEST INCIDENT RESOLUTION ENDPOINT
# ============================================================

@patch("src.backend_src.main.run_incident_workflow")
def test_resolve_incident_endpoint(mock_workflow):

    # --------------------------------------------------------
    # MOCK WORKFLOW RESULT
    # --------------------------------------------------------

    mock_workflow.return_value = {
        "route": "CRITICAL_INCIDENT",

        "classification": IncidentClassification(
            service="Payments API",
            category="API Failure",
            severity="P1",
            intent="Report issue"
        ),

        "knowledge": KnowledgeResult(
            answer="Check database connection pool utilization.",
            source_files=[
                "payment_api_500_runbook.md"
            ],
            grounded=True
        ),

        "investigation": InvestigationResult(
            service="payments-api",
            health={
                "status": "degraded",
                "cpu_percent": 72,
                "memory_percent": 68,
                "db_pool_utilization_percent": 98,
                "active_db_connections": 49,
                "max_db_connections": 50
            },
            logs=[
                "ERROR DatabaseConnectionPoolTimeout"
            ],
            asset={
                "service": "payments-api"
            },
            findings=[
                "Database connection pool utilization is 98%."
            ]
        ),

        "resolution": ResolutionResult(
            root_cause="Database connection pool exhaustion.",
            recommended_actions=[
                "Restart service after engineer approval."
            ],
            requires_human_approval=True,
            escalation_required=True,
            escalation_team="Payments Team"
        ),

        "requires_human_approval": True
    }

    # --------------------------------------------------------
    # SEND REQUEST TO FASTAPI
    # --------------------------------------------------------

    response = client.post(
        "/incidents/resolve",
        json={
            "incident": (
                "Payments API is returning HTTP 500 and "
                "customers cannot complete checkout."
            )
        }
    )

    # --------------------------------------------------------
    # VERIFY HTTP RESPONSE
    # --------------------------------------------------------

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "CRITICAL_INCIDENT"

    assert data["classification"]["severity"] == "P1"

    assert data["knowledge"]["grounded"] is True

    assert (
        data["investigation"]["health"]
        ["db_pool_utilization_percent"]
        == 98
    )

    assert (
        data["resolution"]["root_cause"]
        == "Database connection pool exhaustion."
    )

    assert data["requires_human_approval"] is True

    mock_workflow.assert_called_once()


# ============================================================
# STEP 5: TEST REJECTED ACTION ENDPOINT
# ============================================================

@patch("src.backend_src.main.execute_restart_service")
def test_rejected_action_endpoint(mock_restart):

    response = client.post(
        "/actions/execute",
        json={
            "service_name": "payments-api",
            "action": "restart",
            "approved": False
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "REJECTED"

    assert data["execution_status"] == "NOT_EXECUTED"

    # Rejected action must never reach IT Operations MCP.
    mock_restart.assert_not_called()


# ============================================================
# STEP 6: TEST APPROVED ACTION ENDPOINT
# ============================================================

@patch("src.backend_src.main.execute_restart_service")
def test_approved_action_endpoint(mock_restart):

    # --------------------------------------------------------
    # MOCK SUCCESSFUL MCP ACTION RESULT
    # --------------------------------------------------------

    mock_restart.return_value = {
        "success": True,
        "service": "payments-api",
        "action": "restart",
        "message": (
            "payments-api restarted and "
            "health verified successfully."
        )
    }

    # --------------------------------------------------------
    # SEND APPROVED ACTION
    # --------------------------------------------------------

    response = client.post(
        "/actions/execute",
        json={
            "service_name": "payments-api",
            "action": "restart",
            "approved": True
        }
    )

    # --------------------------------------------------------
    # VERIFY RESPONSE
    # --------------------------------------------------------

    assert response.status_code == 200

    data = response.json()

    assert data["approval_status"] == "APPROVED"

    assert data["execution_status"] == "COMPLETED"

    assert (
        data["message"]
        == "payments-api restarted and health verified successfully."
    )

    # FastAPI must call the action layer exactly once.
    mock_restart.assert_called_once_with("payments-api")