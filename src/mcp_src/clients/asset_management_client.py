import asyncio
import sys
import os

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from src.common.logging_config import get_logger
from src.rag_src.config.rag_settings import BASE_DIR


logger = get_logger("asset_management_client")


async def main():

    # =====================================================
    # STEP 1: Define Asset Management MCP server
    # =====================================================

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp_src.servers.asset_management.server"
        ],
        cwd=str(BASE_DIR),
        env = os.environ.copy()
    )

    # =====================================================
    # STEP 2: Start stdio transport
    # =====================================================

    async with stdio_client(server_params) as (read, write):

        # =================================================
        # STEP 3: Create MCP client session
        # =================================================

        async with ClientSession(read, write) as session:

            # MCP handshake
            await session.initialize()

            print("\nAsset Management MCP connected.")

            # =============================================
            # STEP 4: List available tools
            # =============================================

            tools_result = await session.list_tools()

            print("\n--- AVAILABLE TOOLS ---")

            for tool in tools_result.tools:
                print(tool.name)

            # =============================================
            # STEP 5: Get service asset
            # =============================================

            result = await session.call_tool(
                "get_service_asset",
                {
                    "service_name": "payments-api"
                }
            )

            print("\n--- SERVICE ASSET ---")

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)


if __name__ == "__main__":
    asyncio.run(main())