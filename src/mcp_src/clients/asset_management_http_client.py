import asyncio

from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

from src.common.logging_config import get_logger


logger = get_logger("asset_management_http_client")


async def main():

    # =====================================================
    # STEP 1: Asset Management MCP HTTP endpoint
    # =====================================================

    mcp_url = "http://127.0.0.1:8000/mcp"

    # =====================================================
    # STEP 2: Connect using Streamable HTTP transport
    # =====================================================

    async with streamable_http_client(mcp_url) as (
        read_stream,
        write_stream,
        _
    ):

        # =================================================
        # STEP 3: Create MCP client session
        # =================================================

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            # MCP handshake
            await session.initialize()

            print("\nHTTP MCP connection established.")

            # =============================================
            # STEP 4: Discover tools
            # =============================================

            tools_result = await session.list_tools()

            print("\n--- AVAILABLE TOOLS ---")

            for tool in tools_result.tools:
                print(tool.name)

            # =============================================
            # STEP 5: Call Asset Management tool
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