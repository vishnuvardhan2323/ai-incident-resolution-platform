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


# ============================================================
# STEP 2: TEST KNOWLEDGE-ONLY WORKFLOW
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
def test_knowledge_only_workflow(
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
        category="Information Request",
        severity="P3",
        intent="Help"
    )


    # ========================================================
    # STEP 4: MOCK KNOWLEDGE RESULT
    # ========================================================

    mock_knowledge.return_value = KnowledgeResult(
        answer="Restart requires engineer approval.",
        source_files=["service_restart_sop.md"],
        grounded=True
    )


    # ========================================================
    # STEP 5: RUN WORKFLOW
    # ========================================================

    result = run_incident_workflow(
        "How do I safely restart the Payments API?"
    )


    # ========================================================
    # STEP 6: CHECK ROUTE
    # ========================================================

    assert result["route"] == "KNOWLEDGE_ONLY"


    # ========================================================
    # STEP 7: CHECK KNOWLEDGE RESULT
    # ========================================================

    assert result["knowledge"].grounded is True

    assert result["knowledge"].source_files == [
        "service_restart_sop.md"
    ]


    # ========================================================
    # STEP 8: VERIFY LATER AGENTS WERE SKIPPED
    # ========================================================

    mock_investigation.assert_not_called()
    mock_resolution.assert_not_called()


    # ========================================================
    # STEP 9: CHECK FINAL WORKFLOW RESULT
    # ========================================================

    assert result["investigation"] is None
    assert result["resolution"] is None
    assert result["requires_human_approval"] is False