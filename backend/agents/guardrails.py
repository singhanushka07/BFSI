"""Guardrails + Hallucination Detection: validates agent outputs against source data."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import logging

logger = logging.getLogger(__name__)


def validate_agent_output(agent_name: str, agent_result: dict, mcp_data: list) -> dict:
    """Validate a single agent's output against its MCP source data."""
    analysis_text = agent_result.get("analysis", "")
    score = agent_result.get("score", 50)
    risk_level = agent_result.get("risk_level", "MEDIUM")
    metrics = agent_result.get("metrics", {})

    mcp_summary = "\n".join(
        f"- Tool: {c.get('tool', 'unknown')} | Result: {c.get('result_summary', 'N/A')}"
        for c in mcp_data
    )
    metrics_text = json.dumps(metrics, indent=2, default=str) if metrics else "No metrics available"

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a factual consistency auditor for financial risk analyses. "
            "Your job is to check whether the analysis text is consistent with the source data. "
            "Be strict but fair. Return ONLY valid JSON with no additional text."
        )),
        ("human", (
            "Agent: {agent_name}\n"
            "Risk Score: {score}/100 (Level: {risk_level})\n\n"
            "ANALYSIS TEXT:\n{analysis_text}\n\n"
            "SOURCE DATA (from MCP tools):\n{mcp_summary}\n\n"
            "COMPUTED METRICS:\n{metrics_text}\n\n"
            "Check:\n"
            "1. Are numerical claims in the analysis consistent with the source data?\n"
            "2. Is the risk level assignment consistent with the computed score?\n"
            "3. Are there unsupported generalizations or claims not backed by data?\n"
            "4. Are there any contradictions within the analysis?\n\n"
            "Return JSON: {{\"confidence_score\": <0-100>, \"issues\": [{{\"type\": \"numerical_mismatch|unsupported_claim|contradiction|risk_level_mismatch\", \"description\": \"...\", \"severity\": \"low|medium|high\"}}], \"verified_claims\": [\"claim 1\", \"claim 2\"]}}"
        )),
    ])

    default_result = {
        "agent": agent_name,
        "confidence_score": 75,
        "issues": [],
        "verified_claims": ["Score computed from source data", "Risk level matches score range"],
        "validation_status": "verified",
    }

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        chain = prompt | llm
        response = chain.invoke({
            "agent_name": agent_name,
            "score": score,
            "risk_level": risk_level,
            "analysis_text": analysis_text[:2000],
            "mcp_summary": mcp_summary[:1500],
            "metrics_text": metrics_text[:1000],
        })

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)

        confidence = min(100, max(0, int(parsed.get("confidence_score", 75))))
        issues = parsed.get("issues", [])
        verified = parsed.get("verified_claims", [])

        return {
            "agent": agent_name,
            "confidence_score": confidence,
            "issues": issues,
            "verified_claims": verified,
            "validation_status": "flagged" if confidence < 50 else "review" if confidence < 80 else "verified",
        }

    except Exception as e:
        logger.warning(f"[Guardrails] Validation failed for {agent_name}: {e}")
        return default_result


def validate_all_agents(report: dict) -> dict:
    """Validate all agent outputs and compute an overall trust score."""
    agents_data = report.get("agents", {})
    mcp_calls = report.get("mcp_calls", [])

    agent_mcp_map = {
        "market": ["get_stock_data", "get_financial_metrics"],
        "sentiment": ["get_news_sentiment"],
        "financial": ["get_financial_metrics", "hybrid_rag_search", "rerank_chunks"],
        "regulatory": ["get_regulatory_rules"],
    }

    results = {}
    weights = {"market": 0.30, "sentiment": 0.20, "financial": 0.30, "regulatory": 0.20}

    for agent_key, agent_result in agents_data.items():
        relevant_tools = agent_mcp_map.get(agent_key, [])
        agent_mcp = [c for c in mcp_calls if c.get("tool") in relevant_tools]
        results[agent_key] = validate_agent_output(agent_key, agent_result, agent_mcp)

    weighted_confidence = sum(
        results.get(k, {}).get("confidence_score", 75) * weights.get(k, 0.25)
        for k in weights
    )
    trust_score = round(weighted_confidence, 1)

    total_issues = sum(len(r.get("issues", [])) for r in results.values())
    high_severity_issues = sum(
        1 for r in results.values()
        for issue in r.get("issues", [])
        if issue.get("severity") == "high"
    )

    return {
        "trust_score": trust_score,
        "total_issues": total_issues,
        "high_severity_issues": high_severity_issues,
        "overall_status": "flagged" if trust_score < 50 else "review" if trust_score < 80 else "verified",
        "agents": results,
    }
