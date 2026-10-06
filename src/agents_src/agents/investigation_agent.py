# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai import Agent

from src.agents_src.llms.groq_llm import groq_llm
from src.agents_src.tools.investigation_tool import (
    get_service_health,
    get_service_logs,
    get_service_asset
)


# ============================================================
# STEP 2: CREATE INVESTIGATION AGENT
# ============================================================

investigation_agent = Agent(
    role="Production Incident Investigation Agent",

    goal=(
        "Investigate the current production state of the affected "
        "service using service health, logs, and asset information."
    ),

    backstory=(
        "You are an experienced production support engineer. "
        "You investigate incidents using live operational evidence "
        "such as service metrics, application logs, infrastructure "
        "information, ownership, and dependencies."
    ),

    llm=groq_llm,

    tools=[
        get_service_health,
        get_service_logs,
        get_service_asset
    ],

    verbose=True,
    allow_delegation=False
)