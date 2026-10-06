# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json

from src.agents_src.tools.mcp_tool_wrapper import call_mcp_tool


# ============================================================
# STEP 2: TEST KNOWLEDGE RAG MCP SERVER
# ============================================================

def test_knowledge_rag_mcp():

    result = call_mcp_tool(
        "src.mcp_src.servers.knowledge_rag.server",
        "search_knowledge",
        {
            "query": (
                "Payments API is returning HTTP 500 "
                "due to database connection pool timeout."
            )
        }
    )

    assert result.content

    data = json.loads(result.content[0].text)

    assert "answer" in data
    assert "source_files" in data
    assert "grounded" in data


# ============================================================
# STEP 3: TEST IT OPERATIONS MCP SERVER
# ============================================================

def test_it_operations_mcp():

    result = call_mcp_tool(
        "src.mcp_src.servers.it_operations.server",
        "get_service_health",
        {
            "service_name": "payments-api"
        }
    )

    assert result.content

    data = json.loads(result.content[0].text)

    assert data["service"] == "payments-api"
    assert "status" in data
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "db_pool_utilization_percent" in data


# ============================================================
# STEP 4: TEST ASSET MANAGEMENT MCP SERVER
# ============================================================

def test_asset_management_mcp():

    result = call_mcp_tool(
        "src.mcp_src.servers.asset_management.server",
        "get_service_asset",
        {
            "service_name": "payments-api"
        }
    )

    assert result.content

    data = json.loads(result.content[0].text)

    assert data


# ============================================================
# STEP 5: TEST TICKET MANAGEMENT MCP SERVER
# ============================================================
'''
def test_ticket_management_mcp():

    result = call_mcp_tool(
        "src.mcp_src.servers.ticket_management.server",
        "create_incident_ticket",
        {
            "service_name": "payments-api",
            "summary": "Integration test incident"
        }
    )

    assert result.content

    data = json.loads(result.content[0].text)

    assert data

'''

# ============================================================
# STEP 5: TEST TICKET MANAGEMENT MCP SERVER
# ============================================================

def test_ticket_management_mcp():

    result = call_mcp_tool(
        "src.mcp_src.servers.ticket_management.server",
        "create_ticket",
        {
            "service": "payments-api",
            "summary": "Integration test incident",
            "severity": "P1"
        }
    )

    assert result.content

    data = json.loads(result.content[0].text)

    assert data["created"] is True
    assert "ticket" in data

    assert data["ticket"]["service"] == "payments-api"
    assert data["ticket"]["severity"] == "P1"
    assert data["ticket"]["status"] == "Open"