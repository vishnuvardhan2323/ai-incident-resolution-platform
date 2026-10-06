# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Agent

from src.agents_src.llms.groq_llm import groq_llm
from src.agents_src.tools.knowledge_tool import search_incident_knowledge


# ============================================================
# STEP 2: CREATE KNOWLEDGE AGENT
# ============================================================

knowledge_agent = Agent(
    role="Incident Knowledge Agent",

    goal=(
        "Find relevant company runbooks, SOPs, and previous incident "
        "information for the classified IT incident."
    ),

    backstory=(
        "You are an IT operations knowledge specialist. "
        "You use the company knowledge base to find documented "
        "troubleshooting procedures and previous incident information."
    ),

    llm=groq_llm,

    tools=[
        search_incident_knowledge
    ],

    verbose=True,
    allow_delegation=False
)