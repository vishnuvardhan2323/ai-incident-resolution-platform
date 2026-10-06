# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Task

from src.agents_src.agents.knowledge_agent import knowledge_agent


# ============================================================
# STEP 2: CREATE KNOWLEDGE TASK
# ============================================================

knowledge_task = Task(
    description=(
        "Analyze the following classified incident:\n\n"
        "{classified_incident}\n\n"

        "Search the company knowledge base for relevant runbooks, "
        "SOPs, and previous incident RCAs.\n\n"

        "Use the search_incident_knowledge tool.\n\n"

        "Return ONLY valid JSON.\n"
        "Do not return Markdown outside the JSON.\n"
        "Do not add explanations before or after the JSON.\n\n"

        "Return exactly these fields:\n"
        "{\n"
        '  "answer": "grounded answer from the knowledge base",\n'
        '  "source_files": ["source1.md", "source2.md"],\n'
        '  "grounded": true\n'
        "}"
    ),

    expected_output=(
        "A valid JSON object containing exactly these fields: "
        "answer, source_files, and grounded. "
        "The output must be JSON only, with no Markdown "
        "or additional text outside the JSON."
    ),

    agent=knowledge_agent
)