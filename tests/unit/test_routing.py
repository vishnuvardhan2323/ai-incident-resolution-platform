# ============================================================
# STEP 1: IMPORTS
# ============================================================

from src.agents_src.crews.incident_resolution_workflow import (
    determine_route
)

from src.agents_src.schemas.incident_classification_schemas import (
    IncidentClassification
)


# ============================================================
# STEP 2: TEST CRITICAL INCIDENT ROUTING
# ============================================================

def test_critical_incident_route():

    classification = IncidentClassification(
        service="Payments API",
        category="API Failure",
        severity="P1",
        intent="Report issue"
    )

    route = determine_route(classification)

    assert route == "CRITICAL_INCIDENT"


# ============================================================
# STEP 3: TEST NORMAL PRODUCTION INCIDENT ROUTING
# ============================================================

def test_production_incident_route():

    classification = IncidentClassification(
        service="Payments API",
        category="Performance Issue",
        severity="P3",
        intent="Report issue"
    )

    route = determine_route(classification)

    assert route == "PRODUCTION_INCIDENT"


# ============================================================
# STEP 4: TEST KNOWLEDGE-ONLY ROUTING
# ============================================================

def test_knowledge_only_route():

    classification = IncidentClassification(
        service="Payments API",
        category="Information Request",
        severity="P3",
        intent="Help"
    )

    route = determine_route(classification)

    assert route == "KNOWLEDGE_ONLY"