import asyncio
import sys
import os

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from src.common.logging_config import get_logger
from src.rag_src.config.rag_settings import BASE_DIR


logger = get_logger("ticket_management_client")


async def main():

    # =====================================================
    # STEP 1: Define Ticket Management MCP server
    # =====================================================

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp_src.servers.ticket_management.server"
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

            print("\nTicket Management MCP connected.")

            # =============================================
            # 1. LIST TOOLS
            # =============================================

            tools_result = await session.list_tools()

            print("\n--- AVAILABLE TOOLS ---")

            for tool in tools_result.tools:
                print(tool.name)

            # =============================================
            # 2. GET EXISTING TICKET
            # =============================================

            result = await session.call_tool(
                "get_ticket",
                {
                    "ticket_id": "INC-1001"
                }
            )

            print("\n--- GET TICKET ---")

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)

            # =============================================
            # 3. CREATE NEW TICKET
            # =============================================

            result = await session.call_tool(
                "create_ticket",
                {
                    "service": "payments-api",
                    "summary": "Database connection pool timeout",
                    "severity": "P1"
                }
            )

            print("\n--- CREATE TICKET ---")

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)

            # =============================================
            # 4. UPDATE CREATED TICKET
            # =============================================

            result = await session.call_tool(
                "update_ticket",
                {
                    "ticket_id": "INC-1003",
                    "status": "Investigating"
                }
            )

            print("\n--- UPDATE TICKET ---")

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                    logger.info(content.text)


if __name__ == "__main__":
    asyncio.run(main())