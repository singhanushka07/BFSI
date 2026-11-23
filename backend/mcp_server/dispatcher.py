"""
Internal MCP dispatcher — agents call this instead of importing data functions directly.
Every data fetch goes through the MCP tool interface, making MCP provably active.
Now includes hybrid_rag_search (BM25 + dense) and rerank_chunks tools.
"""
from datetime import datetime
from data.mock_data import generate_stock_data, generate_financial_metrics, generate_news_feed, REGULATORY_RULES
from rag.pipeline import query_collection
from rag.hybrid_search import hybrid_rag_search, bm25_available
from rag.reranker import rerank_chunks


def call_mcp_tool(tool_name: str, parameters: dict) -> dict:
    """
    Central MCP tool dispatcher. Returns:
      { tool, params, result, result_summary, called_at, success }
    Agents accumulate these records and pass them up to orchestrator state.
    """
    called_at = datetime.utcnow().isoformat() + "Z"

    try:
        if tool_name == "get_stock_data":
            ticker = parameters.get("ticker", "TKR")
            days = parameters.get("days", 30)
            data = generate_stock_data(ticker, days)
            return _ok(tool_name, parameters, data,
                       f"{len(data)} price records for {ticker}", called_at)

        elif tool_name == "get_financial_metrics":
            company = parameters.get("company", "Company")
            data = generate_financial_metrics(company)
            summary = (
                f"D/E={data['debt_to_equity']}, "
                f"ROE={data['roe']:.2%}, "
                f"CurrentRatio={data['current_ratio']}"
            )
            return _ok(tool_name, parameters, data, summary, called_at)

        elif tool_name == "get_news_sentiment":
            company = parameters.get("company", "Company")
            count = parameters.get("count", 10)
            data = generate_news_feed(company, count)
            pos = sum(1 for n in data if n["sentiment"] == "positive")
            neg = sum(1 for n in data if n["sentiment"] == "negative")
            return _ok(tool_name, parameters, data,
                       f"{len(data)} articles: {pos} positive, {neg} negative", called_at)

        elif tool_name == "get_regulatory_rules":
            return _ok(tool_name, parameters, REGULATORY_RULES,
                       f"{len(REGULATORY_RULES)} regulatory frameworks loaded", called_at)

        elif tool_name == "rag_query":
            collection = parameters.get("collection", "sample_financial_docs")
            query = parameters.get("query", "")
            n_results = parameters.get("n_results", 5)
            data = query_collection(collection, query, n_results)
            sources = list({r["metadata"].get("source", "unknown") for r in data})
            return _ok(tool_name, parameters, data,
                       f"{len(data)} chunks from {sources}", called_at)

        elif tool_name == "hybrid_rag_search":
            collection = parameters.get("collection", "sample_financial_docs")
            query = parameters.get("query", "")
            n_results = parameters.get("n_results", 8)
            alpha = parameters.get("alpha", 0.6)
            data = hybrid_rag_search(collection, query, n_results, alpha)
            sources = list({r["metadata"].get("source", "unknown") for r in data})
            method = "BM25+dense" if bm25_available() else "dense-only"
            return _ok(tool_name, parameters, data,
                       f"{len(data)} chunks via {method} from {sources}", called_at)

        elif tool_name == "rerank_chunks":
            query = parameters.get("query", "")
            chunks = parameters.get("chunks", [])
            top_k = parameters.get("top_k", 4)
            data = rerank_chunks(query, chunks, top_k)
            scores = [round(c.get("rerank_score", 0), 3) for c in data]
            return _ok(tool_name, parameters, data,
                       f"Re-ranked {len(chunks)} → top {len(data)} chunks, scores={scores}", called_at)

        else:
            return {
                "tool": tool_name, "params": parameters,
                "result": None,
                "result_summary": f"Unknown tool: {tool_name}",
                "called_at": called_at, "success": False,
            }

    except Exception as e:
        return {
            "tool": tool_name, "params": parameters,
            "result": None,
            "result_summary": f"Error: {str(e)}",
            "called_at": called_at, "success": False,
        }


def _ok(tool_name, parameters, result, summary, called_at):
    return {
        "tool": tool_name,
        "params": {k: v for k, v in parameters.items() if k != "chunks"},
        "result": result,
        "result_summary": summary,
        "called_at": called_at,
        "success": True,
    }
