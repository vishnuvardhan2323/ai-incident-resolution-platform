import asyncio
import sys
import os

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from src.common.logging_config import get_logger
from src.rag_src.config.rag_settings import BASE_DIR


logger = get_logger("it_operations_client")


async def main():

    # =====================================================
    # STEP 1: Define IT Operations MCP server subprocess
    # =====================================================

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp_src.servers.it_operations.server"
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

            print("\nIT Operations MCP connection established.")

            # =============================================
            # STEP 4: Discover available tools
            # =============================================

            tools_result = await session.list_tools()

            print("\n--- AVAILABLE MCP TOOLS ---")

            for tool in tools_result.tools:
                print(tool.name)

            # =============================================
            # STEP 5: Call service health tool
            # =============================================

            health_result = await session.call_tool(
                "get_service_health",
                {
                    "service_name": "payments-api"
                }
            )

            print("\n--- SERVICE HEALTH ---")

            for content in health_result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)

            # =============================================
            # STEP 6: Call service logs tool
            # =============================================

            logs_result = await session.call_tool(
                "get_service_logs",
                {
                    "service_name": "payments-api"
                }
            )

            print("\n--- SERVICE LOGS ---")

            for content in logs_result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)


if __name__ == "__main__":
    asyncio.run(main())