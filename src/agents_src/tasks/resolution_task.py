# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Task

from src.agents_src.agents.resolution_agent import resolution_agent


# ============================================================
# STEP 2: CREATE RESOLUTION TASK
# ============================================================

resolution_task = Task(
    description=(
        "Analyze the following investigation result:\n\n"

        "{investigation_result}\n\n"

        "Determine:\n"
        "1. The most likely root cause.\n"
        "2. Recommended remediation actions.\n"
        "3. Whether human approval is required.\n"
        "4. Whether escalation is required.\n"
        "5. The appropriate escalation team.\n\n"

        "Do not automatically perform risky production actions such as "
        "restarting services or changing database configuration.\n\n"

        "Return ONLY valid JSON in exactly this format:\n"
        "{\n"
        '  "root_cause": "string",\n'
        '  "recommended_actions": [],\n'
        '  "requires_human_approval": true,\n'
        '  "escalation_required": true,\n'
        '  "escalation_team": "string"\n'
        "}"
    ),

    expected_output=(
        "Valid JSON containing root cause, recommended actions, "
        "human approval requirement, escalation decision, "
        "and escalation team."
    ),

    agent=resolution_agent
)