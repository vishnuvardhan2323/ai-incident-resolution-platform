# ============================================================
# STEP 1: IMPORTS
# ============================================================

from crewai.tools import tool

from src.agents_src.tools.mcp_tool_wrapper import call_mcp_tool


# ============================================================
# STEP 2: SERVICE HEALTH TOOL
# ============================================================

@tool("get_service_health")
def get_service_health(service_name: str) -> str:
    """
    Get the current health and metrics of a production service.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.it_operations.server",
        "get_service_health",
        {"service_name": service_name}
    )

    if result.content:
        return result.content[0].text

    return "No service health information returned."


# ============================================================
# STEP 3: SERVICE LOGS TOOL
# ============================================================

@tool("get_service_logs")
def get_service_logs(service_name: str) -> str:
    """
    Get recent production logs for a service.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.it_operations.server",
        "get_service_logs",
        {"service_name": service_name}
    )

    if result.content:
        return result.content[0].text

    return "No service logs returned."


# ============================================================
# STEP 4: SERVICE ASSET TOOL
# ============================================================

@tool("get_service_asset")
def get_service_asset(service_name: str) -> str:
    """
    Get service ownership, environment, host and dependencies.
    """

    result = call_mcp_tool(
        "src.mcp_src.servers.asset_management.server",
        "get_service_asset",
        {"service_name": service_name}
    )

    if result.content:
        return result.content[0].text

    return "No asset information returned."