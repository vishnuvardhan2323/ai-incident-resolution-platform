# ============================================================
# STEP 1: IMPORT REQUIRED LIBRARIES
# ============================================================

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession


# ============================================================
# STEP 2: FIND PROJECT ROOT DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]


# ============================================================
# STEP 3: ASYNC FUNCTION TO CALL ANY MCP TOOL
# ============================================================

async def _call_mcp_tool_async(
    server_module: str,
    tool_name: str,
    arguments: dict[str, Any]
):

    # --------------------------------------------------------
    # STEP 3.1: CONFIGURE HOW TO START THE MCP SERVER
    # --------------------------------------------------------

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
        cwd=str(BASE_DIR),

        # Explicitly pass the backend container's environment
        # variables to the MCP subprocess.
        env=os.environ.copy()
    )

    # --------------------------------------------------------
    # STEP 3.2: START / CONNECT TO MCP SERVER USING STDIO
    # --------------------------------------------------------

    async with stdio_client(server_params) as (read, write):

        # ----------------------------------------------------
        # STEP 3.3: CREATE MCP CLIENT SESSION
        # ----------------------------------------------------

        async with ClientSession(read, write) as session:

            # ------------------------------------------------
            # STEP 3.4: INITIALIZE MCP HANDSHAKE
            # ------------------------------------------------

            await session.initialize()

            # ------------------------------------------------
            # STEP 3.5: CALL REQUESTED MCP TOOL
            # ------------------------------------------------

            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            # ------------------------------------------------
            # STEP 3.6: RETURN MCP TOOL RESULT
            # ------------------------------------------------

            return result


# ============================================================
# STEP 4: SYNCHRONOUS WRAPPER FOR AGENTS
# ============================================================

def call_mcp_tool(
    server_module: str,
    tool_name: str,
    arguments: dict[str, Any]
):

    return asyncio.run(
        _call_mcp_tool_async(
            server_module,
            tool_name,
            arguments
        )
    )


# ============================================================
# STEP 5: TEST REUSABLE MCP CLIENT
# ============================================================

if __name__ == "__main__":

    result = call_mcp_tool(
        "src.mcp_src.servers.knowledge_rag.server",
        "search_knowledge",
        {
            "query":
            "Payments API HTTP 500 checkout failure"
        }
    )

    print(result)