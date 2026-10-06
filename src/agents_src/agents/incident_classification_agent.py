from crewai import Agent

from src.agents_src.llms.groq_llm import groq_llm


incident_classification_agent = Agent(
    role="Incident Classification Agent",

    goal=(
        "Analyze incoming IT incidents and identify the affected "
        "service, incident category, severity, and user intent."
    ),

    backstory=(
        "You are an experienced IT service desk engineer responsible "
        "for the initial classification and prioritization of "
        "production incidents."
    ),

    llm=groq_llm,
    verbose=True,
    allow_delegation=False
)