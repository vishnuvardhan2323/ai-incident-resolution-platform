from mcp.server.fastmcp import FastMCP

from src.rag_src.retrieval.query_engine import rag_query


# =========================================================
# STEP 1: Create MCP server
# =========================================================

mcp = FastMCP("Knowledge RAG Server")


# =========================================================
# STEP 2: Expose existing RAG function as an MCP tool
# =========================================================

@mcp.tool()
def search_knowledge(query: str) -> dict:
    """
    Search the enterprise IT knowledge base.

    Retrieves information from runbooks,
    SOPs and historical incident RCA documents.
    """

    return rag_query(query)


# =========================================================
# STEP 3: Start MCP server
# =========================================================

if __name__ == "__main__":
    mcp.run()