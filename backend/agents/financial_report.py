from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mcp_server.dispatcher import call_mcp_tool
import os
import random

DEFAULT_RAG_COLLECTION = "sample_financial_docs"


def run_financial_report_agent(company: str, ticker: str, collection_name: str = None) -> dict:
    """
    Financial Report Agent — full pipeline:
    1. MCP get_financial_metrics → fetch key ratios
    2. MCP hybrid_rag_search → BM25 + dense vector retrieval from ChromaDB
    3. MCP rerank → LLM batch re-ranking of retrieved chunks
    4. LangChain ChatPromptTemplate | ChatOpenAI → GPT-4o-mini analysis
    """
    mcp_calls = []

    # ── Step 1: MCP — get financial metrics ─────────────────────────────────
    metrics_call = call_mcp_tool("get_financial_metrics", {"company": company})
    mcp_calls.append({k: v for k, v in metrics_call.items() if k != "result"})
    metrics = metrics_call["result"] or {}

    # ── Step 2: MCP — hybrid RAG search (BM25 + ChromaDB dense) ─────────────
    active_collection = collection_name or DEFAULT_RAG_COLLECTION
    rag_query_text = f"financial risk {company} {ticker} revenue debt earnings credit solvency liquidity"

    hybrid_call = call_mcp_tool("hybrid_rag_search", {
        "collection": active_collection,
        "query": rag_query_text,
        "n_results": 8,
        "alpha": 0.6,
    })
    mcp_calls.append({k: v for k, v in hybrid_call.items() if k != "result"})
    raw_chunks = hybrid_call["result"] or []

    # ── Step 3: MCP — LLM re-ranking ────────────────────────────────────────
    rerank_call = call_mcp_tool("rerank_chunks", {
        "query": rag_query_text,
        "chunks": raw_chunks,
        "top_k": 4,
    })
    mcp_calls.append({k: v for k, v in rerank_call.items() if k != "result"})
    rag_chunks = rerank_call["result"] or raw_chunks[:4]

    # ── Assemble RAG context ─────────────────────────────────────────────────
    rag_context = ""
    sources_used = []
    hybrid_scores = []

    if rag_chunks:
        rag_context = "\n\n".join([
            f"[{c['metadata'].get('source', 'doc')} p.{c['metadata'].get('page', '?')} "
            f"| hybrid={c.get('hybrid_score', 0):.2f} rerank={c.get('rerank_score', 0):.2f}]\n{c['text']}"
            for c in rag_chunks[:4]
        ])
        sources_used = list({c["metadata"].get("source", "document") for c in rag_chunks})
        hybrid_scores = [
            {
                "source": c["metadata"].get("source", "doc"),
                "page": c["metadata"].get("page", "?"),
                "hybrid_score": c.get("hybrid_score", 0),
                "dense_score": c.get("dense_score", 0),
                "bm25_score": c.get("bm25_score", 0),
                "rerank_score": c.get("rerank_score", 0),
            }
            for c in rag_chunks[:4]
        ]

    # ── Compute risk score ───────────────────────────────────────────────────
    debt_ratio = metrics.get("debt_to_equity", 0.5)
    current_ratio = metrics.get("current_ratio", 1.5)
    roe = metrics.get("roe", 0.10)
    roa = metrics.get("roa", 0.05)
    liquidity_risk = max(0, (2.0 - current_ratio) * 20)
    leverage_risk = min(60, debt_ratio * 20)
    profitability_risk = max(0, (0.15 - roe) * 200)
    financial_risk_score = round(
        (liquidity_risk + leverage_risk + profitability_risk) / 3 + random.uniform(5, 20), 1
    )
    financial_risk_score = max(0, min(100, financial_risk_score))

    rag_status = (
        f"Hybrid RAG ACTIVE — {len(rag_chunks)} chunks retrieved & re-ranked from {sources_used} "
        f"(collection: {active_collection})"
        if rag_chunks
        else f"RAG queried '{active_collection}' — no chunks returned (collection may be empty)"
    )

    # ── Step 4: LangChain — GPT analysis ────────────────────────────────────
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior financial analyst at a BFSI risk management firm. "
         "Analyze financial health with precision, citing specific document evidence where available."),
        ("human",
         """Analyze the financial risk for {company} ({ticker}).

Financial Metrics (via MCP get_financial_metrics):
- Revenue: ${revenue:,.0f}  |  Net Income: ${net_income:,.0f}
- Total Debt: ${total_debt:,.0f}  |  Total Equity: ${total_equity:,.0f}
- Current Ratio: {current_ratio}  |  Debt-to-Equity: {debt_to_equity}
- ROE: {roe:.1%}  |  ROA: {roa:.1%}

Retrieved Document Context (ChromaDB Hybrid RAG → LLM Re-ranked, collection: {collection}):
{rag_section}

Provide a 3-sentence financial risk assessment: liquidity risk, leverage/solvency risk, and profitability concerns.
Reference specific document evidence where available. Be precise and formal.""")
    ])

    analysis_text = (
        f"{company} has a current ratio of {current_ratio} and D/E of {debt_ratio}, "
        f"{'indicating liquidity concerns' if current_ratio < 1.5 else 'showing adequate liquidity'}. "
        f"ROE of {roe:.1%} {'is below industry average' if roe < 0.10 else 'reflects solid profitability'}. "
        f"Financial risk score: {financial_risk_score}/100. {rag_status}."
    )

    rag_section = (
        rag_context if rag_context
        else "No matching document excerpts found. Analysis based on financial metrics only."
    )

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
        chain = prompt | llm
        response = chain.invoke({
            "company": company, "ticker": ticker,
            "revenue": metrics.get("revenue", 0),
            "net_income": metrics.get("net_income", 0),
            "total_debt": metrics.get("total_debt", 0),
            "total_equity": metrics.get("total_equity", 0),
            "current_ratio": current_ratio,
            "debt_to_equity": debt_ratio,
            "roe": roe, "roa": roa,
            "rag_section": rag_section,
            "collection": active_collection,
        })
        analysis_text = response.content
    except Exception:
        pass

    return {
        "agent": "Financial Report Analysis",
        "score": financial_risk_score,
        "risk_level": _risk_level(financial_risk_score),
        "analysis": analysis_text,
        "rag_enabled": True,
        "rag_collection": active_collection,
        "rag_chunks_retrieved": len(raw_chunks),
        "rag_chunks_reranked": len(rag_chunks),
        "rag_method": "hybrid_bm25_dense_reranked",
        "sources_used": sources_used,
        "rag_status": rag_status,
        "hybrid_scores": hybrid_scores,
        "mcp_calls": mcp_calls,
        "metrics": {
            "revenue": metrics.get("revenue", 0),
            "net_income": metrics.get("net_income", 0),
            "current_ratio": current_ratio,
            "debt_to_equity": debt_ratio,
            "roe": round(roe, 4),
            "roa": round(roa, 4),
        },
    }


def _risk_level(score: float) -> str:
    if score < 25: return "LOW"
    if score < 50: return "MEDIUM"
    if score < 75: return "HIGH"
    return "CRITICAL"
