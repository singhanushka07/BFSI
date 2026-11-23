"""
Official MCP SDK server using FastMCP.
Exposes all BFSI risk platform tools as a proper Model Context Protocol server
that can be connected to by any MCP client (Claude Desktop, Cursor, etc.).

Run standalone:
    cd backend && python -m mcp_server.mcp_sdk_server

Or register in claude_desktop_config.json:
    {
      "mcpServers": {
        "bfsi-risk": {
          "command": "python",
          "args": ["-m", "mcp_server.mcp_sdk_server"],
          "cwd": "/path/to/project/backend"
        }
      }
    }
"""
import sys
import os

# Add backend to path when run as module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from mcp.server.fastmcp import FastMCP
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False

from data.mock_data import generate_stock_data, generate_financial_metrics, generate_news_feed, REGULATORY_RULES
from rag.hybrid_search import hybrid_rag_search, bm25_available
from rag.pipeline import query_collection, list_collections


def _build_server():
    if not MCP_SDK_AVAILABLE:
        raise RuntimeError("mcp package not installed. Run: pip install mcp")

    mcp = FastMCP(
        name="BFSI Multi-Agent Financial Risk Assessment Platform",
        instructions=(
            "Tools for financial risk analysis in the BFSI sector. "
            "Use get_stock_data and get_financial_metrics for market risk analysis. "
            "Use get_news_sentiment for reputational risk. "
            "Use get_regulatory_rules for compliance checking. "
            "Use hybrid_rag_search to retrieve relevant financial document excerpts from ChromaDB."
        ),
    )

    @mcp.tool()
    def get_stock_data(ticker: str, days: int = 30) -> dict:
        """Retrieve historical OHLCV stock price data for a given ticker over N trading days."""
        data = generate_stock_data(ticker, days)
        return {
            "ticker": ticker,
            "days": days,
            "records": len(data),
            "data": data,
        }

    @mcp.tool()
    def get_financial_metrics(company: str) -> dict:
        """
        Retrieve key financial ratios and metrics for a company.
        Returns: debt_to_equity, current_ratio, ROE, ROA, beta, P/E ratio,
                 revenue, net_income, total_debt, total_equity.
        """
        return generate_financial_metrics(company)

    @mcp.tool()
    def get_news_sentiment(company: str, count: int = 10) -> dict:
        """
        Retrieve recent news headlines with sentiment scores for a company.
        Sentiment: positive / negative / neutral with score in [-1, +1].
        """
        news = generate_news_feed(company, count)
        avg = sum(n["score"] for n in news) / len(news) if news else 0.0
        return {
            "company": company,
            "articles": news,
            "average_sentiment": round(avg, 3),
            "positive": sum(1 for n in news if n["sentiment"] == "positive"),
            "negative": sum(1 for n in news if n["sentiment"] == "negative"),
            "neutral": sum(1 for n in news if n["sentiment"] == "neutral"),
        }

    @mcp.tool()
    def get_regulatory_rules() -> dict:
        """
        Retrieve the full BFSI regulatory rule set used for compliance checking.
        Covers: Basel III, AML/KYC, GDPR, SOX, MiFID II, Dodd-Frank, IFRS 9.
        """
        return {
            "rules": REGULATORY_RULES,
            "total": len(REGULATORY_RULES),
            "categories": list({r["category"] for r in REGULATORY_RULES}),
        }

    @mcp.tool()
    def hybrid_rag_search_tool(
        collection: str,
        query: str,
        n_results: int = 5,
        alpha: float = 0.6,
    ) -> dict:
        """
        Hybrid BM25 + ChromaDB dense vector search over financial documents.
        Returns ranked chunks with hybrid_score, dense_score, and bm25_score.
        alpha controls dense vs sparse weighting (0.6 = 60% dense, 40% BM25).
        """
        chunks = hybrid_rag_search(collection, query, n_results, alpha)
        return {
            "collection": collection,
            "query": query,
            "n_results": len(chunks),
            "bm25_active": bm25_available(),
            "chunks": chunks,
        }

    @mcp.tool()
    def list_rag_collections() -> dict:
        """List all available ChromaDB vector store collections."""
        cols = list_collections()
        return {"collections": cols, "count": len(cols)}

    return mcp


if MCP_SDK_AVAILABLE:
    _mcp_server = _build_server()


def get_mcp_sdk_status() -> dict:
    return {
        "sdk_available": MCP_SDK_AVAILABLE,
        "server_name": "BFSI Multi-Agent Financial Risk Assessment Platform",
        "tools": [
            "get_stock_data",
            "get_financial_metrics",
            "get_news_sentiment",
            "get_regulatory_rules",
            "hybrid_rag_search_tool",
            "list_rag_collections",
        ],
        "bm25_active": bm25_available(),
        "note": "Run as standalone: python -m mcp_server.mcp_sdk_server" if MCP_SDK_AVAILABLE
                else "Install mcp SDK: pip install mcp",
    }


if __name__ == "__main__":
    if not MCP_SDK_AVAILABLE:
        print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)
    print(f"Starting BFSI MCP SDK server (BM25={'active' if bm25_available() else 'fallback'})...")
    _mcp_server.run()
