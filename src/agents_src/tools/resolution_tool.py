# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai.tools import tool

from src.agents_src.tools.mcp_tool_wrapper import call_mcp_tool


# ============================================================
# STEP 2: GET TICKET TOOL
# ============================================================

@tool("get_ticket")
def get_ticket(ticket_id: str) -> str:
    """
    Get details of an existing incident ticket.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.ticket_management.server",
        "get_ticket",
        {"ticket_id": ticket_id}
    )

    if result.content:
        return result.content[0].text

    return "No ticket information returned."


# ============================================================
# STEP 3: CREATE TICKET TOOL
# ============================================================

@tool("create_ticket")
def create_ticket(service: str, summary: str, severity: str) -> str:
    """
    Create a new incident ticket.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.ticket_management.server",
        "create_ticket",
        {
            "service": service,
            "summary": summary,
            "severity": severity
        }
    )

    if result.content:
        return result.content[0].text

    return "Ticket creation failed."


# ============================================================
# STEP 4: UPDATE TICKET TOOL
# ============================================================

@tool("update_ticket")
def update_ticket(ticket_id: str, status: str) -> str:
    """
    Update the status of an existing incident ticket.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.ticket_management.server",
        "update_ticket",
        {
            "ticket_id": ticket_id,
            "status": status
        }
    )

    if result.content:
        return result.content[0].text

    return "Ticket update failed."