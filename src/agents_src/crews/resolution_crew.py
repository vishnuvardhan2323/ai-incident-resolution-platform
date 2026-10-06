# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json

from crewai import Crew

from src.agents_src.agents.resolution_agent import resolution_agent
from src.agents_src.tasks.resolution_task import resolution_task
from src.agents_src.schemas.resolution_schemas import ResolutionResult


# ============================================================
# STEP 2: CREATE RESOLUTION CREW
# ============================================================

resolution_crew = Crew(
    agents=[resolution_agent],
    tasks=[resolution_task],
    verbose=True
)


# ============================================================
# STEP 3: RUN RESOLUTION STAGE
# ============================================================

def run_resolution_stage(investigation_result: str) -> ResolutionResult:

    result = resolution_crew.kickoff(
        inputs={
            "investigation_result": investigation_result
        }
    )

    # Convert JSON string → Python dictionary
    parsed_output = json.loads(result.raw)

    # Validate using Pydantic
    validated_output = ResolutionResult(**parsed_output)

    return validated_output


# ============================================================
# STEP 4: TEST
# ============================================================

if __name__ == "__main__":

    # Temporary output from Investigation Agent
    investigation_result = """
    Service: payments-api
    Status: degraded
    DB pool utilization: 98%
    Active DB connections: 49/50

    Logs:
    - DatabaseConnectionPoolTimeout
    - HTTP 500 POST /payments

    Asset:
    - Owner team: Payments Team
    - Environment: production
    - Host: payment-prod-01

    Findings:
    - Database connection pool utilization is critically high.
    - Database connection pool timeout errors are present.
    - Pool exhaustion is consistent with the HTTP 500 failures.
    - Production restart or configuration changes require engineer approval.
    """

    result = run_resolution_stage(investigation_result)

    print("\n--- RESOLUTION RESULT ---")
    print(result.model_dump_json(indent=2))