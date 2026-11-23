"""LangGraph orchestrator: routes and coordinates all risk agents including debate."""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List
from agents.market_risk import run_market_risk_agent
from agents.sentiment import run_sentiment_agent
from agents.financial_report import run_financial_report_agent
from agents.regulatory import run_regulatory_agent
from agents.guardrails import validate_all_agents
from agents.devils_advocate import run_devils_advocate_agent
from agents.judge import run_judge_agent


class RiskState(TypedDict):
    company: str
    ticker: str
    sector: str
    collection_name: Optional[str]
    market_result: Optional[dict]
    sentiment_result: Optional[dict]
    financial_result: Optional[dict]
    regulatory_result: Optional[dict]
    mcp_calls: List[dict]
    final_report: Optional[dict]
    debate_result: Optional[dict]
    judge_result: Optional[dict]
    error: Optional[str]


def market_risk_node(state: RiskState) -> RiskState:
    try:
        result = run_market_risk_agent(state["company"], state["ticker"])
        agent_mcp_calls = result.pop("mcp_calls", [])
        return {**state, "market_result": result, "mcp_calls": state["mcp_calls"] + agent_mcp_calls}
    except Exception as e:
        return {**state, "error": f"Market risk agent failed: {str(e)}"}


def sentiment_node(state: RiskState) -> RiskState:
    try:
        result = run_sentiment_agent(state["company"], state["ticker"])
        agent_mcp_calls = result.pop("mcp_calls", [])
        return {**state, "sentiment_result": result, "mcp_calls": state["mcp_calls"] + agent_mcp_calls}
    except Exception as e:
        return {**state, "error": f"Sentiment agent failed: {str(e)}"}


def financial_report_node(state: RiskState) -> RiskState:
    try:
        result = run_financial_report_agent(
            state["company"], state["ticker"], state.get("collection_name")
        )
        agent_mcp_calls = result.pop("mcp_calls", [])
        return {**state, "financial_result": result, "mcp_calls": state["mcp_calls"] + agent_mcp_calls}
    except Exception as e:
        return {**state, "error": f"Financial report agent failed: {str(e)}"}


def regulatory_node(state: RiskState) -> RiskState:
    try:
        result = run_regulatory_agent(state["company"], state["ticker"], state.get("sector", "Financial Services"))
        agent_mcp_calls = result.pop("mcp_calls", [])
        return {**state, "regulatory_result": result, "mcp_calls": state["mcp_calls"] + agent_mcp_calls}
    except Exception as e:
        return {**state, "error": f"Regulatory agent failed: {str(e)}"}


def aggregator_node(state: RiskState) -> RiskState:
    """Aggregates all agent results into a final risk report."""
    market = state.get("market_result") or {}
    sentiment = state.get("sentiment_result") or {}
    financial = state.get("financial_result") or {}
    regulatory = state.get("regulatory_result") or {}

    scores = {
        "market": market.get("score", 50),
        "sentiment": sentiment.get("score", 50),
        "financial": financial.get("score", 50),
        "compliance": regulatory.get("score", 50),
    }

    # Weighted average: market 30%, sentiment 20%, financial 30%, compliance 20%
    weights = {"market": 0.30, "sentiment": 0.20, "financial": 0.30, "compliance": 0.20}
    overall = sum(scores[k] * weights[k] for k in scores)
    overall = round(overall, 1)

    def risk_label(s):
        if s < 25: return "LOW"
        if s < 50: return "MEDIUM"
        if s < 75: return "HIGH"
        return "CRITICAL"

    mcp_calls = state.get("mcp_calls", [])
    mcp_tool_names = [c["tool"] for c in mcp_calls]

    final_report = {
        "company": state["company"],
        "ticker": state["ticker"],
        "overall_risk_score": overall,
        "risk_level": risk_label(overall),
        "scores": scores,
        "agents": {
            "market": market,
            "sentiment": sentiment,
            "financial": financial,
            "regulatory": regulatory,
        },
        "mcp_calls": mcp_calls,
        "mcp_tools_invoked": mcp_tool_names,
        "rag_enabled": financial.get("rag_enabled", False),
        "rag_collection": financial.get("rag_collection", ""),
        "rag_chunks_retrieved": financial.get("rag_chunks_retrieved", 0),
        "rag_sources": financial.get("sources_used", []),
        "tech_stack_active": {
            "LangGraph": True,
            "LangChain": True,
            "GPT-4o-mini": True,
            "FastAPI": True,
            "ChromaDB_RAG": financial.get("rag_enabled", False),
            "MCP": len(mcp_calls) > 0,
            "SQLAlchemy": True,
            "JWT_Auth": True,
        },
        "summary": (
            f"{state['company']} has an overall risk score of {overall}/100 ({risk_label(overall)} risk). "
            f"Key drivers: market exposure ({scores['market']:.1f}), "
            f"sentiment ({scores['sentiment']:.1f}), "
            f"financial health ({scores['financial']:.1f}), "
            f"regulatory compliance ({scores['compliance']:.1f}). "
            f"Analysis used {len(mcp_calls)} MCP tool calls and "
            f"{'retrieved ' + str(financial.get('rag_chunks_retrieved', 0)) + ' RAG document chunks' if financial.get('rag_enabled') else 'no RAG context'}."
        ),
    }

    # Run guardrails validation
    try:
        guardrails_result = validate_all_agents(final_report)
        final_report["guardrails"] = guardrails_result
        final_report["trust_score"] = guardrails_result.get("trust_score", 0)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Guardrails validation failed: {e}")

    return {**state, "final_report": final_report}


def devils_advocate_node(state: RiskState) -> RiskState:
    try:
        all_results = {
            "market": state.get("market_result", {}),
            "sentiment": state.get("sentiment_result", {}),
            "financial": state.get("financial_result", {}),
            "regulatory": state.get("regulatory_result", {}),
        }
        guardrails = state.get("final_report", {}).get("guardrails")
        result = run_devils_advocate_agent(all_results, guardrails)
        return {**state, "debate_result": result}
    except Exception as e:
        return {**state, "error": f"Devil's Advocate agent failed: {str(e)}"}


def judge_node(state: RiskState) -> RiskState:
    try:
        all_results = {
            "market": state.get("market_result", {}),
            "sentiment": state.get("sentiment_result", {}),
            "financial": state.get("financial_result", {}),
            "regulatory": state.get("regulatory_result", {}),
        }
        scores = state.get("final_report", {}).get("scores", {})
        result = run_judge_agent(all_results, state.get("debate_result", {}), scores)

        final_report = state["final_report"]
        final_report["debate"] = {
            "devils_advocate": state.get("debate_result", {}),
            "judge": result,
        }
        if result.get("adjusted_overall"):
            final_report["adjusted_risk_score"] = result["adjusted_overall"]
            final_report["adjusted_scores"] = result.get("adjusted_scores", {})

        return {**state, "judge_result": result, "final_report": final_report}
    except Exception as e:
        return {**state, "error": f"Judge agent failed: {str(e)}"}


def build_risk_graph() -> StateGraph:
    workflow = StateGraph(RiskState)

    workflow.add_node("market_risk", market_risk_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("financial_report", financial_report_node)
    workflow.add_node("regulatory", regulatory_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("devils_advocate", devils_advocate_node)
    workflow.add_node("judge", judge_node)

    workflow.set_entry_point("market_risk")
    workflow.add_edge("market_risk", "sentiment")
    workflow.add_edge("sentiment", "financial_report")
    workflow.add_edge("financial_report", "regulatory")
    workflow.add_edge("regulatory", "aggregator")
    workflow.add_edge("aggregator", "devils_advocate")
    workflow.add_edge("devils_advocate", "judge")
    workflow.add_edge("judge", END)

    return workflow.compile()


_graph = None


def get_risk_graph():
    global _graph
    if _graph is None:
        _graph = build_risk_graph()
    return _graph


def run_full_analysis(company: str, ticker: str, sector: str = "Financial Services", collection_name: str = None) -> dict:
    graph = get_risk_graph()
    initial_state = RiskState(
        company=company,
        ticker=ticker,
        sector=sector,
        collection_name=collection_name,
        market_result=None,
        sentiment_result=None,
        financial_result=None,
        regulatory_result=None,
        mcp_calls=[],
        final_report=None,
        debate_result=None,
        judge_result=None,
        error=None,
    )
    result = graph.invoke(initial_state)
    return result.get("final_report", {})
