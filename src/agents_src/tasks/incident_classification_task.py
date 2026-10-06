from crewai import Task

from src.agents_src.agents.incident_classification_agent import (
    incident_classification_agent
)


classification_task = Task(
    description=(
        "Analyze the following IT incident:\n\n"
        "{incident}\n\n"
        "Identify:\n"
        "1. affected service\n"
        "2. incident category\n"
        "3. severity (P1, P2, P3, or P4)\n"
        "4. user intent\n\n"
        "Return ONLY valid JSON in exactly this format:\n"
        '{\n'
        '  "service": "string",\n'
        '  "category": "string",\n'
        '  "severity": "P1",\n'
        '  "intent": "string"\n'
        '}'
    ),

    expected_output=(
        "Valid JSON containing service, category, severity, and intent."
    ),

    agent=incident_classification_agent
)