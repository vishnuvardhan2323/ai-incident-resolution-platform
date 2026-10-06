# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json
import re

from crewai import Crew

from src.agents_src.agents.knowledge_agent import knowledge_agent
from src.agents_src.tasks.knowledge_task import knowledge_task
from src.agents_src.schemas.knowledge_schemas import KnowledgeResult


# ============================================================
# STEP 2: CREATE KNOWLEDGE CREW
# ============================================================

knowledge_crew = Crew(
    agents=[knowledge_agent],
    tasks=[knowledge_task],
    verbose=True
)


# ============================================================
# STEP 3: EXTRACT JSON FROM AGENT OUTPUT
# ============================================================

def extract_json(raw_output: str) -> dict:

    # --------------------------------------------------------
    # CASE 1:
    # Agent returned pure JSON
    # --------------------------------------------------------

    try:
        return json.loads(raw_output)

    except json.JSONDecodeError:
        pass


    # --------------------------------------------------------
    # CASE 2:
    # Agent returned JSON inside Markdown code block
    #
    # Example:
    # ```json
    # {
    #     "answer": "...",
    #     "source_files": [...],
    #     "grounded": true
    # }
    # ```
    # --------------------------------------------------------

    match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        raw_output,
        re.DOTALL
    )

    if match:
        return json.loads(
            match.group(1)
        )


    # --------------------------------------------------------
    # CASE 3:
    # No valid JSON found
    # --------------------------------------------------------

    raise ValueError(
        "Knowledge Agent did not return valid JSON."
    )


# ============================================================
# STEP 4: FUNCTION TO RUN KNOWLEDGE AGENT
# ============================================================

def search_incident_knowledge_stage(classified_incident: str):

    # --------------------------------------------------------
    # Run Knowledge Agent
    # --------------------------------------------------------

    result = knowledge_crew.kickoff(
        inputs={
            "classified_incident": classified_incident
        }
    )


    # --------------------------------------------------------
    # DEBUG:
    # See exactly what CrewAI returned BEFORE processing
    # --------------------------------------------------------

    print(
        "\n========== RAW KNOWLEDGE AGENT OUTPUT =========="
    )

    print(result.raw)

    print(
        "================================================\n"
    )


    # --------------------------------------------------------
    # Convert agent JSON string → Python dictionary
    # --------------------------------------------------------

    parsed_output = extract_json(
        result.raw
    )


    # --------------------------------------------------------
    # Validate dictionary using Pydantic schema
    # --------------------------------------------------------

    validated_output = KnowledgeResult(
        **parsed_output
    )


    # --------------------------------------------------------
    # Return structured KnowledgeResult
    # --------------------------------------------------------

    return validated_output


# ============================================================
# STEP 5: TEST
# ============================================================

if __name__ == "__main__":

    classified_incident = """
    Service: Payments API
    Category: Service Outage
    Severity: P1
    Intent: Customers cannot complete checkout because
    Payments API is returning HTTP 500.
    """


    result = search_incident_knowledge_stage(
        classified_incident
    )


    print(
        "\n========== KNOWLEDGE RESULT =========="
    )

    print(
        result.model_dump_json(
            indent=2
        )
    )

    print(
        "======================================\n"
    )