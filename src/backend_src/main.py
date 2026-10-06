# ============================================================
# STEP 1: IMPORTS
# ============================================================

from fastapi import FastAPI

from src.backend_src.schemas import (
    IncidentRequest,
    IncidentResponse,
    ApprovedActionRequest,
    ActionResponse
)

from src.agents_src.crews.incident_resolution_workflow import (
    run_incident_workflow
)


from src.agents_src.tools.action_tools import (
    execute_restart_service
)

# ============================================================
# STEP 2: CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI-Powered IT Service Desk API",
    version="1.0.0"
)


# ============================================================
# STEP 3: FASTAPI STATUS  CHECK ENDPOINT
# ============================================================

@app.get("/status")
def service_status():

    return {
        "status": "healthy"
    }


# ============================================================
# STEP 4: INCIDENT RESOLUTION ENDPOINT
# ============================================================

@app.post(
    "/incidents/resolve",
    response_model=IncidentResponse
)
def resolve_incident(request: IncidentRequest):

    # Run complete conditional agent workflow
    result = run_incident_workflow(
        request.incident
    )

    # Convert Pydantic objects returned by workflow
    # into dictionaries for API response
    return IncidentResponse(
        route=result["route"],

        classification=(
            result["classification"].model_dump()
        ),

        knowledge=(
            result["knowledge"].model_dump()
        ),

        investigation=(
            result["investigation"].model_dump()
            if result["investigation"]
            else None
        ),

        resolution=(
            result["resolution"].model_dump()
            if result["resolution"]
            else None
        ),

        requires_human_approval=(
            result["requires_human_approval"]
        )
    )

# ============================================================
# STEP 5: APPROVED ACTION ENDPOINT
# ============================================================

@app.post(
    "/actions/execute",
    response_model=ActionResponse
)
def execute_approved_action(
    request: ApprovedActionRequest
):

    # --------------------------------------------------------
    # HUMAN REJECTED THE ACTION ( Security / control check did Human approve? )
    # --------------------------------------------------------

    if not request.approved:

        return ActionResponse(
            service_name=request.service_name,
            action=request.action,
            approval_status="REJECTED",
            execution_status="NOT_EXECUTED",
            message="Action rejected by engineer."
        )


    # --------------------------------------------------------
    # ALLOW ONLY SUPPORTED ACTIONS ( saftey check)
    # --------------------------------------------------------

    if request.action.lower() != "restart":

        return ActionResponse(
            service_name=request.service_name,
            action=request.action,
            approval_status="APPROVED",
            execution_status="NOT_EXECUTED",
            message="Unsupported action."
        )


    # --------------------------------------------------------
    # EXECUTE APPROVED RESTART THROUGH MCP
    # --------------------------------------------------------

    result = execute_restart_service(
        request.service_name
    )


    # --------------------------------------------------------
    # RETURN EXECUTION RESULT
    # --------------------------------------------------------

    return ActionResponse(
        service_name=request.service_name,
        action=request.action,
        approval_status="APPROVED",
        execution_status=(
            "COMPLETED"
            if result.get("success")
            else "FAILED"
        ),
        message=result.get(
            "message",
            "Action execution completed."
        )
    )