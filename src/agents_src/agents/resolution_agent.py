# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Agent

from src.agents_src.llms.groq_llm import groq_llm
from src.agents_src.tools.resolution_tool import (
    get_ticket,
    create_ticket,
    update_ticket
)


# ============================================================
# STEP 2: CREATE RESOLUTION AGENT
# ============================================================

resolution_agent = Agent(
    role="Incident Resolution Agent",

    goal=(
        "Analyze the investigation result, determine the likely root cause, "
        "recommend safe remediation actions, and determine whether human "
        "approval or escalation is required."
    ),

    backstory=(
        "You are an experienced production incident resolution engineer. "
        "You use investigation evidence to recommend safe resolutions. "
        "You do not automatically perform risky production changes. "
        "You use the ticket management tools when ticket operations are needed."
    ),

    llm=groq_llm,

    tools=[
        get_ticket,
        create_ticket,
        update_ticket
    ],

    verbose=True,
    allow_delegation=False
)