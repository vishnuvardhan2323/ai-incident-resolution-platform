from src.mcp_src.servers.asset_management.server import mcp


# =========================================================
# START ASSET MANAGEMENT MCP - STREAMABLE HTTP
# =========================================================

if __name__ == "__main__":
    mcp.settings.stateless_http = True
    mcp.settings.json_response = True

    mcp.run(
        transport="streamable-http"
    )