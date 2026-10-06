# ============================================================
# STEP 1: IMPORTS
# ============================================================

from fastapi.testclient import TestClient

from src.backend_src.main import app


# ============================================================
# STEP 2: CREATE FASTAPI TEST CLIENT
# ============================================================

client = TestClient(app)


# ============================================================
# STEP 3: TEST REJECTED RESTART
# ============================================================

def test_rejected_restart():

    request_data = {
        "service_name": "payments-api",
        "action": "restart",
        "approved": False
    }

    response = client.post(
        "/actions/execute",
        json=request_data
    )

    assert response.status_code == 200

    result = response.json()

    assert result["service_name"] == "payments-api"
    assert result["action"] == "restart"
    assert result["approval_status"] == "REJECTED"
    assert result["execution_status"] == "NOT_EXECUTED"
    assert result["message"] == "Action rejected by engineer."


# ============================================================
# STEP 4: TEST APPROVED RESTART
# ============================================================

def test_approved_restart():

    request_data = {
        "service_name": "payments-api",
        "action": "restart",
        "approved": True
    }

    response = client.post(
        "/actions/execute",
        json=request_data
    )

    assert response.status_code == 200

    result = response.json()

    assert result["service_name"] == "payments-api"
    assert result["action"] == "restart"
    assert result["approval_status"] == "APPROVED"
    assert result["execution_status"] == "COMPLETED"


# ============================================================
# STEP 5: TEST UNSUPPORTED ACTION
# ============================================================

def test_unsupported_action():

    request_data = {
        "service_name": "payments-api",
        "action": "delete",
        "approved": True
    }

    response = client.post(
        "/actions/execute",
        json=request_data
    )

    assert response.status_code == 200

    result = response.json()

    assert result["service_name"] == "payments-api"
    assert result["action"] == "delete"
    assert result["approval_status"] == "APPROVED"
    assert result["execution_status"] == "NOT_EXECUTED"
    assert result["message"] == "Unsupported action."