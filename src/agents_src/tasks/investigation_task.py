# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Task

from src.agents_src.agents.investigation_agent import investigation_agent


# ============================================================
# STEP 2: CREATE INVESTIGATION TASK
# ============================================================

investigation_task = Task(
    description=(
        "Investigate the following production service:\n\n"

        "Service: {service_name}\n\n"

        "Use the following company knowledge result:\n\n"

        "{knowledge_result}\n\n"

        "IMPORTANT SERVICE RULE:\n"
        "- Use exactly the service name provided above: "
        "{service_name}\n"
        "- Do NOT infer, rename, normalize, or guess another "
        "service name.\n"
        "- Do NOT retry tools using alternative service names.\n"
        "- If the service is not found, report that fact in "
        "the findings.\n\n"

        "Use the available tools to:\n"
        "1. Check current service health and metrics.\n"
        "2. Inspect recent service logs.\n"
        "3. Retrieve service asset information.\n"
        "4. Identify important findings from the evidence.\n\n"

        "Return ONLY valid JSON in exactly this format:\n"
        "{\n"
        '  "service": "string",\n'
        '  "health": {},\n'
        '  "logs": [],\n'
        '  "asset": {},\n'
        '  "findings": []\n'
        "}"
    ),

    expected_output=(
        "Valid JSON containing service, health, logs, "
        "asset information, and investigation findings."
    ),

    agent=investigation_agent
)