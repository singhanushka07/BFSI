"""
MCP (Model Context Protocol) HTTP server — exposes all financial risk tools via REST.
Agents use the internal dispatcher (mcp_server/dispatcher.py) for in-process calls.
This router provides the same tools over HTTP for external clients and UI inspection.

For the official stdio MCP SDK server, see mcp_server/mcp_sdk_server.py.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from data.mock_data import generate_stock_data, generate_financial_metrics, generate_news_feed, REGULATORY_RULES
from rag.pipeline import query_collection, list_collections
from rag.hybrid_search import hybrid_rag_search, bm25_available
from rag.reranker import rerank_chunks
from mcp_server.mcp_sdk_server import get_mcp_sdk_status
from typing import Optional

mcp_router = APIRouter(prefix="/mcp", tags=["MCP Tools"])


class MCPToolRequest(BaseModel):
    tool_name: str
    parameters: dict


class MCPToolResponse(BaseModel):
    tool_name: str
    result: dict
    success: bool
    error: Optional[str] = None


MCP_TOOLS_MANIFEST = [
    {
        "name": "get_stock_data",
        "description": "Retrieve historical stock price and volume data for a given ticker",
        "parameters": {"ticker": "string", "days": "integer (default 30)"},
        "category": "market",
    },
    {
        "name": "get_financial_metrics",
        "description": "Retrieve key financial ratios and metrics for a company",
        "parameters": {"company": "string"},
        "category": "financial",
    },
    {
        "name": "get_news_sentiment",
        "description": "Retrieve recent news headlines and sentiment scores for a company",
        "parameters": {"company": "string", "count": "integer (default 10)"},
        "category": "sentiment",
    },
    {
        "name": "get_regulatory_rules",
        "description": "Retrieve the list of BFSI regulatory rules to check against",
        "parameters": {},
        "category": "regulatory",
    },
    {
        "name": "rag_query",
        "description": "Dense vector search over ChromaDB financial documents",
        "parameters": {"collection": "string", "query": "string", "n_results": "integer (default 5)"},
        "category": "rag",
    },
    {
        "name": "hybrid_rag_search",
        "description": "Hybrid BM25 sparse + ChromaDB dense vector search — better for financial terminology",
        "parameters": {
            "collection": "string",
            "query": "string",
            "n_results": "integer (default 8)",
            "alpha": "float 0-1 (dense weight, default 0.6)",
        },
        "category": "rag",
    },
    {
        "name": "rerank_chunks",
        "description": "LLM batch re-ranker: scores retrieved chunks by relevance in a single GPT call",
        "parameters": {"query": "string", "chunks": "list[dict]", "top_k": "integer (default 4)"},
        "category": "rag",
    },
]


@mcp_router.get("/tools")
def list_mcp_tools():
    """List all available MCP tools."""
    return {
        "tools": MCP_TOOLS_MANIFEST,
        "count": len(MCP_TOOLS_MANIFEST),
        "bm25_active": bm25_available(),
        "sdk_server": get_mcp_sdk_status(),
    }


@mcp_router.post("/invoke", response_model=MCPToolResponse)
def invoke_mcp_tool(request: MCPToolRequest):
    """Invoke a specific MCP tool by name."""
    tool = request.tool_name
    params = request.parameters

    try:
        if tool == "get_stock_data":
            result = generate_stock_data(params.get("ticker", "TKR"), params.get("days", 30))
            return MCPToolResponse(tool_name=tool, result={"data": result}, success=True)

        elif tool == "get_financial_metrics":
            result = generate_financial_metrics(params.get("company", "Company"))
            return MCPToolResponse(tool_name=tool, result=result, success=True)

        elif tool == "get_news_sentiment":
            result = generate_news_feed(params.get("company", "Company"), params.get("count", 10))
            return MCPToolResponse(tool_name=tool, result={"news": result}, success=True)

        elif tool == "get_regulatory_rules":
            return MCPToolResponse(tool_name=tool, result={"rules": REGULATORY_RULES}, success=True)

        elif tool == "rag_query":
            result = query_collection(
                params.get("collection", ""),
                params.get("query", ""),
                params.get("n_results", 5),
            )
            return MCPToolResponse(tool_name=tool, result={"chunks": result}, success=True)

        elif tool == "hybrid_rag_search":
            result = hybrid_rag_search(
                params.get("collection", "sample_financial_docs"),
                params.get("query", ""),
                params.get("n_results", 8),
                params.get("alpha", 0.6),
            )
            return MCPToolResponse(
                tool_name=tool,
                result={"chunks": result, "bm25_active": bm25_available()},
                success=True,
            )

        elif tool == "rerank_chunks":
            result = rerank_chunks(
                params.get("query", ""),
                params.get("chunks", []),
                params.get("top_k", 4),
            )
            return MCPToolResponse(tool_name=tool, result={"chunks": result}, success=True)

        else:
            return MCPToolResponse(tool_name=tool, result={}, success=False, error=f"Unknown tool: {tool}")

    except Exception as e:
        return MCPToolResponse(tool_name=tool, result={}, success=False, error=str(e))
