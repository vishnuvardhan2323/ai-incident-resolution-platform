# ============================================================
# STEP 1: IMPORTS
# ============================================================

import json

from src.agents_src.tools.mcp_tool_wrapper import (
    call_mcp_tool
)


# ============================================================
# STEP 2: RESTART SERVICE THROUGH MCP
# ============================================================

def execute_restart_service(service_name: str) -> dict:

    result = call_mcp_tool(
        "src.mcp_src.servers.it_operations.server",
        "restart_service",
        {
            "service_name": service_name
        }
    )

    if result.content:
        return json.loads(
            result.content[0].text
        )

    return {
        "success": False,
        "service": service_name,
        "action": "restart",
        "message": "No response returned from IT Operations MCP."
    }