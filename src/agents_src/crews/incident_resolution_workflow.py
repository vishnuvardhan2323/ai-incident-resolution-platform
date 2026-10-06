# ============================================================
# STEP 1: IMPORTS
# ============================================================

from src.agents_src.crews.incident_classification_crew import (
    classify_incident
)

from src.agents_src.crews.knowledge_crew import (
    search_incident_knowledge_stage
)

from src.agents_src.crews.investigation_crew import (
    run_investigation_stage
)

from src.agents_src.crews.resolution_crew import (
    run_resolution_stage
)


# ============================================================
# STEP 2: DETERMINE WORKFLOW ROUTE
# ============================================================

def determine_route(classification_result):

    intent = classification_result.intent.lower()
    severity = classification_result.severity.upper()

    # --------------------------------------------------------
    # ROUTE 1: SIMPLE HELP / INFORMATION REQUEST
    # --------------------------------------------------------

    knowledge_intents = [
        "help",
        "how_to",
        "how to",
        "information",
        "question",
        "guidance"
    ]

    if any(value in intent for value in knowledge_intents):
        return "KNOWLEDGE_ONLY"

    # --------------------------------------------------------
    # ROUTE 2: CRITICAL PRODUCTION INCIDENT
    # --------------------------------------------------------

    if severity == "P1":
        return "CRITICAL_INCIDENT"

    # --------------------------------------------------------
    # ROUTE 3: NORMAL PRODUCTION INCIDENT
    # --------------------------------------------------------

    return "PRODUCTION_INCIDENT"


# ============================================================
# STEP 3: COMPLETE INCIDENT WORKFLOW
# ============================================================

def run_incident_workflow(incident: str):

    # --------------------------------------------------------
    # STEP 3.1: CLASSIFICATION AGENT
    # --------------------------------------------------------

    classification_result = classify_incident(incident)

    print("\n--- CLASSIFICATION RESULT ---")
    print(
        classification_result.model_dump_json(indent=2)
    )


    # --------------------------------------------------------
    # STEP 3.2: DETERMINE ROUTE
    # --------------------------------------------------------

    route = determine_route(
        classification_result
    )

    print("\n--- WORKFLOW ROUTE ---")
    print(route)


    # --------------------------------------------------------
    # STEP 3.3: KNOWLEDGE AGENT
    #
    # All routes need company knowledge first.
    # --------------------------------------------------------

    classification_input = (
        classification_result.model_dump_json()
    )

    knowledge_result = search_incident_knowledge_stage(
        classification_input
    )

    print("\n--- KNOWLEDGE RESULT ---")
    print(
        knowledge_result.model_dump_json(indent=2)
    )


    # ========================================================
    # ROUTE 1: KNOWLEDGE ONLY
    # ========================================================

    if route == "KNOWLEDGE_ONLY":

        print("\nKnowledge-only request completed.")

        return {
            "route": route,
            "classification": classification_result,
            "knowledge": knowledge_result,
            "investigation": None,
            "resolution": None,
            "requires_human_approval": False
        }


    # ========================================================
    # ROUTE 2 + 3:
    # PRODUCTION / CRITICAL INCIDENT
    # ========================================================

    # --------------------------------------------------------
    # STEP 3.4: INVESTIGATION AGENT
    #
    # Pass BOTH:
    # 1. Exact service identified by Classification Agent
    # 2. Knowledge Agent result
    #
    # Investigation must not infer the service again.
    # --------------------------------------------------------

    knowledge_input = (
        knowledge_result.model_dump_json()
    )

    investigation_result = run_investigation_stage(
        classification_result.service,
        knowledge_input
    )

    print("\n--- INVESTIGATION RESULT ---")
    print(
        investigation_result.model_dump_json(indent=2)
    )


    # --------------------------------------------------------
    # STEP 3.5: RESOLUTION AGENT
    # --------------------------------------------------------

    investigation_input = (
        investigation_result.model_dump_json()
    )

    resolution_result = run_resolution_stage(
        investigation_input
    )

    print("\n--- RESOLUTION RESULT ---")
    print(
        resolution_result.model_dump_json(indent=2)
    )


    # --------------------------------------------------------
    # STEP 3.6: HUMAN APPROVAL REQUIREMENT
    # --------------------------------------------------------

    requires_human_approval = (
        route == "CRITICAL_INCIDENT"
        and resolution_result.requires_human_approval
    )


    # --------------------------------------------------------
    # STEP 3.7: RETURN COMPLETE RESULT
    # --------------------------------------------------------

    return {
        "route": route,
        "classification": classification_result,
        "knowledge": knowledge_result,
        "investigation": investigation_result,
        "resolution": resolution_result,
        "requires_human_approval": requires_human_approval
    }


# ============================================================
# STEP 4: TEST WORKFLOW
# ============================================================

if __name__ == "__main__":

    incident = (
        "Payments API is returning HTTP 500 and "
        "customers cannot complete checkout."
    )

    workflow_result = run_incident_workflow(
        incident
    )

    print("\n========================================")
    print("INCIDENT WORKFLOW COMPLETED")
    print("========================================")

    print(
        "Route:",
        workflow_result["route"]
    )

    print(
        "Human Approval Required:",
        workflow_result["requires_human_approval"]
    )