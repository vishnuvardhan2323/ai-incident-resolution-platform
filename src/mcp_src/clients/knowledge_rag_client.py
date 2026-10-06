import asyncio
import sys
import os

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from src.common.logging_config import get_logger
from src.rag_src.config.rag_settings import BASE_DIR


logger = get_logger("knowledge_rag_client")


async def main():

    # =====================================================
    # STEP 1: Define MCP server subprocess
    # =====================================================

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "src.mcp_src.servers.knowledge_rag.server"
        ],
        cwd=str(BASE_DIR),
        env = os.environ.copy()
    )

    # =====================================================
    # STEP 2: Start server transport
    # =====================================================

    async with stdio_client(server_params) as (read, write):

        # =================================================
        # STEP 3: Create MCP client session
        # =================================================

        async with ClientSession(read, write) as session:

            # MCP handshake / initialization
            await session.initialize()

            print("\nMCP connection established.")

            # =============================================
            # STEP 4: Discover MCP tools
            # =============================================

            tools_result = await session.list_tools()

            print("\n--- AVAILABLE MCP TOOLS ---")

            for tool in tools_result.tools:
                print(tool.name)

            # =============================================
            # STEP 5: Call Knowledge RAG tool
            # =============================================

            result = await session.call_tool(
                "search_knowledge",
                {
                    "query": (
                        "Payments API is returning HTTP 500 with "
                        "DatabaseConnectionPoolTimeout. "
                        "What should I investigate?"
                    )
                }
            )

            # =============================================
            # STEP 6: Display + log MCP response
            # =============================================

            print("\n--- MCP TOOL RESPONSE ---")

            for content in result.content:

                if hasattr(content, "text"):

                    # Display result while testing
                    print(content.text)

                    # Also save result to log file
                    logger.info(content.text)


if __name__ == "__main__":
    asyncio.run(main())