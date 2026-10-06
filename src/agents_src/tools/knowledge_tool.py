'''
Before code, one important point: our generic mcp_tool_wrapper.py is the MCP client infrastructure,
but CrewAI still needs a callable tool representing “search knowledge.”

'''
# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json
from crewai.tools import tool

from src.agents_src.tools.mcp_tool_wrapper import call_mcp_tool


# ============================================================
# STEP 2: CREATE KNOWLEDGE SEARCH TOOL FOR THE AGENT
# ============================================================

@tool("search_incident_knowledge")
def search_incident_knowledge(query: str) -> str:
    """
    Search company runbooks, SOPs and previous incident RCAs
    through the Knowledge RAG MCP server.
    """

    # STEP 2.1: CALL KNOWLEDGE RAG MCP
    result = call_mcp_tool(
        "src.mcp_src.servers.knowledge_rag.server",
        "search_knowledge",
        {"query": query}
    )

    # STEP 2.2: EXTRACT TEXT FROM MCP RESULT
    if result.content:
        return result.content[0].text

    # STEP 2.3: FALLBACK
    return json.dumps({
        "answer": "No knowledge result returned.",
        "source_files": [],
        "grounded": False
    })