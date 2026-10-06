# ============================================================
# STEP 1: IMPORTS
# ============================================================

from unittest.mock import patch

from src.agents_src.crews.incident_resolution_workflow import (
    run_incident_workflow
)

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
# STEP 2: TEST CRITICAL INCIDENT WORKFLOW
# ============================================================

@patch(
    "src.agents_src.crews.incident_resolution_workflow."
    "run_resolution_stage"
)
@patch(
    "src.agents_src.crews.incident_resolution_workflow."
    "run_investigation_stage"
)
@patch(
    "src.agents_src.crews.incident_resolution_workflow."
    "search_incident_knowledge_stage"
)
@patch(
    "src.agents_src.crews.incident_resolution_workflow."
    "classify_incident"
)
def test_critical_incident_workflow(
    mock_classify,
    mock_knowledge,
    mock_investigation,
    mock_resolution
):

    # ========================================================
    # STEP 3: MOCK CLASSIFICATION RESULT
    # ========================================================

    mock_classify.return_value = IncidentClassification(
        service="Payments API",
        category="API Failure",
        severity="P1",
        intent="Report issue"
    )


    # ========================================================
    # STEP 4: MOCK KNOWLEDGE RESULT
    # ========================================================

    mock_knowledge.return_value = KnowledgeResult(
        answer="Check database connection pool utilization.",
        source_files=[
            "payment_api_500_runbook.md",
            "INC-2026-001_payment_db_pool.md"
        ],
        grounded=True
    )


    # ========================================================
    # STEP 5: MOCK INVESTIGATION RESULT
    # ========================================================

    mock_investigation.return_value = InvestigationResult(
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
            "Database connection pool utilization is 98%.",
            "DatabaseConnectionPoolTimeout found in logs."
        ]
    )


    # ========================================================
    # STEP 6: MOCK RESOLUTION RESULT
    # ========================================================

    mock_resolution.return_value = ResolutionResult(
        root_cause="Database connection pool exhaustion.",
        recommended_actions=[
            "Review database connection pool capacity.",
            "Restart service after engineer approval."
        ],
        requires_human_approval=True,
        escalation_required=True,
        escalation_team="Payments Team"
    )


    # ========================================================
    # STEP 7: RUN WORKFLOW
    # ========================================================

    result = run_incident_workflow(
        "Payments API is returning HTTP 500 and "
        "customers cannot complete checkout."
    )


    # ========================================================
    # STEP 8: VERIFY ROUTE
    # ========================================================

    assert result["route"] == "CRITICAL_INCIDENT"


    # ========================================================
    # STEP 9: VERIFY ALL REQUIRED STAGES RAN
    # ========================================================

    mock_knowledge.assert_called_once()
    mock_investigation.assert_called_once()
    mock_resolution.assert_called_once()


    # ========================================================
    # STEP 10: VERIFY RESULTS
    # ========================================================

    assert result["knowledge"].grounded is True

    assert (
        result["investigation"]
        .health["db_pool_utilization_percent"]
        == 98
    )

    assert (
        result["resolution"].root_cause
        == "Database connection pool exhaustion."
    )


    # ========================================================
    # STEP 11: VERIFY HUMAN APPROVAL
    # ========================================================

    assert result["requires_human_approval"] is True