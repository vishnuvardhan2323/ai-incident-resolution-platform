import json

from crewai import Crew

from src.agents_src.agents.incident_classification_agent import (
    incident_classification_agent
)

from src.agents_src.tasks.incident_classification_task import (
    classification_task
)

from src.agents_src.schemas.incident_classification_schemas import (
    IncidentClassification
)


# Create Crew
classification_crew = Crew(
    agents=[
        incident_classification_agent
    ],

    tasks=[
        classification_task
    ],

    verbose=True
)


def classify_incident(
    incident: str
) -> IncidentClassification:

    # Start Crew execution
    result = classification_crew.kickoff(
        inputs={
            "incident": incident
        }
    )

    # LLM returns JSON as a string.
    # Convert JSON string -> Python dictionary.
    parsed_output = json.loads(result.raw)

    # Validate dictionary using our Pydantic schema.
    return IncidentClassification(**parsed_output)


# Local test
if __name__ == "__main__":

    incident = (
        "Payments API is returning HTTP 500 and "
        "customers cannot complete checkout."
    )

    result = classify_incident(incident)

    print("\n--- INCIDENT CLASSIFICATION ---")
    print(result)