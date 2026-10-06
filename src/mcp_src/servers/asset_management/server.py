from mcp.server.fastmcp import FastMCP

from src.common.logging_config import get_logger


logger = get_logger("asset_management")

mcp = FastMCP("Asset Management Server")


# =========================================================
# SIMULATED ASSET / CMDB DATA
# =========================================================

ASSETS = {

    "payments-api": {
        "service": "payments-api",
        "owner_team": "Payments Team",
        "environment": "production",
        "host": "payment-prod-01",
        "dependencies": [
            "payments-db",
            "redis-cache"
        ]
    },

    "checkout-api": {
        "service": "checkout-api",
        "owner_team": "Checkout Team",
        "environment": "production",
        "host": "checkout-prod-01",
        "dependencies": [
            "payments-api",
            "inventory-api"
        ]
    }
}


# =========================================================
# TOOL: GET SERVICE ASSET
# =========================================================

@mcp.tool()
def get_service_asset(service_name: str) -> dict:
    """
    Get asset, ownership and dependency information
    for a service.
    """

    logger.info(
        "Asset information requested for service=%s",
        service_name
    )

    asset = ASSETS.get(service_name)

    if asset is None:

        logger.warning(
            "Asset not found for service=%s",
            service_name
        )

        return {
            "service": service_name,
            "found": False,
            "message": "Asset not found"
        }

    logger.info(
        "Asset found for service=%s",
        service_name
    )

    return {
        "found": True,
        "asset": asset
    }


# =========================================================
# START MCP SERVER - STDIO
# =========================================================

if __name__ == "__main__":
    mcp.run()


# =========================================================
# HTTP VERSION
# Keep this commented while testing stdio MCP.
# =========================================================

"""
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        json_response=True
    )
"""