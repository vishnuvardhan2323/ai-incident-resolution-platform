# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json

from crewai import Crew

from src.agents_src.agents.investigation_agent import investigation_agent
from src.agents_src.tasks.investigation_task import investigation_task
from src.agents_src.schemas.investigation_schemas import InvestigationResult


# ============================================================
# STEP 2: CREATE INVESTIGATION CREW
# ============================================================

investigation_crew = Crew(
    agents=[investigation_agent],
    tasks=[investigation_task],
    verbose=True
)


# ============================================================
# STEP 3: FUNCTION TO RUN INVESTIGATION AGENT
# ============================================================

def run_investigation_stage(
    service_name: str,
    knowledge_result: str
) -> InvestigationResult:

    result = investigation_crew.kickoff(
        inputs={
            "service_name": service_name,
            "knowledge_result": knowledge_result
        }
    )

    # Convert JSON string → Python dictionary
    parsed_output = json.loads(result.raw)

    # Validate using Pydantic
    validated_output = InvestigationResult(
        **parsed_output
    )

    return validated_output


# ============================================================
# STEP 4: TEST
# ============================================================

if __name__ == "__main__":

    # Exact service normally comes from Classification Agent
    service_name = "payments-api"

    # Temporary output from Knowledge Agent
    knowledge_result = """
    Runbook recommends:
    - Check database connectivity.
    - Check database connection pool utilization.
    - Inspect application logs.

    Previous RCA:
    Database connection pool exhaustion can cause
    HTTP 500 checkout failures.
    """

    result = run_investigation_stage(
        service_name,
        knowledge_result
    )

    print("\n--- INVESTIGATION RESULT ---")
    print(
        result.model_dump_json(indent=2)
    )