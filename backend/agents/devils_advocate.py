"""Devil's Advocate Agent: challenges assumptions and finds weaknesses in agent analyses."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import logging

logger = logging.getLogger(__name__)


def run_devils_advocate_agent(all_agent_results: dict, guardrails_data: dict = None) -> dict:
    """Challenge the findings of all 4 risk agents."""

    market = all_agent_results.get("market", {})
    sentiment = all_agent_results.get("sentiment", {})
    financial = all_agent_results.get("financial", {})
    regulatory = all_agent_results.get("regulatory", {})

    guardrails_context = ""
    if guardrails_data and guardrails_data.get("agents"):
        flagged = []
        for agent_key, g in guardrails_data["agents"].items():
            for issue in g.get("issues", []):
                flagged.append(f"- [{agent_key}] {issue.get('description', '')} (severity: {issue.get('severity', 'unknown')})")
        if flagged:
            guardrails_context = f"\n\nGUARDRAILS FLAGS:\n" + "\n".join(flagged)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a Devil's Advocate financial risk analyst. Your job is to rigorously "
            "challenge assumptions, find weaknesses in reasoning, identify conflicts between "
            "agents, and stress-test conclusions. Be constructive but thorough. "
            "Return ONLY valid JSON with no additional text."
        )),
        ("human", (
            "Four risk agents analyzed a company. Challenge their findings:\n\n"
            "MARKET RISK AGENT (Score: {market_score}/100):\n{market_analysis}\n\n"
            "SENTIMENT AGENT (Score: {sentiment_score}/100):\n{sentiment_analysis}\n\n"
            "FINANCIAL REPORT AGENT (Score: {financial_score}/100):\n{financial_analysis}\n\n"
            "REGULATORY AGENT (Score: {regulatory_score}/100):\n{regulatory_analysis}\n"
            "{guardrails_context}\n\n"
            "Return JSON: {{"
            "\"challenges\": [{{\"target_agent\": \"market|sentiment|financial|regulatory\", "
            "\"challenge\": \"description of weakness or assumption\", "
            "\"severity\": \"minor|major|critical\"}}], "
            "\"contradictions\": [{{\"agents\": [\"agent1\", \"agent2\"], "
            "\"description\": \"what contradicts\"}}], "
            "\"analysis\": \"overall devil's advocate summary paragraph\""
            "}}"
        )),
    ])

    default_result = {
        "agent": "Devil's Advocate",
        "challenges": [
            {"target_agent": "market", "challenge": "Historical volatility may not predict future risk in current market conditions.", "severity": "major"},
            {"target_agent": "sentiment", "challenge": "News sentiment sampling may miss recent developments or sentiment shifts.", "severity": "minor"},
            {"target_agent": "financial", "challenge": "Financial ratios alone don't capture off-balance-sheet risks or contingent liabilities.", "severity": "major"},
        ],
        "contradictions": [],
        "analysis": "The analysis provides a reasonable baseline but relies heavily on historical data and may not capture emerging risks or rapid market changes.",
    }

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        chain = prompt | llm
        response = chain.invoke({
            "market_score": market.get("score", 50),
            "market_analysis": market.get("analysis", "No analysis available")[:800],
            "sentiment_score": sentiment.get("score", 50),
            "sentiment_analysis": sentiment.get("analysis", "No analysis available")[:800],
            "financial_score": financial.get("score", 50),
            "financial_analysis": financial.get("analysis", "No analysis available")[:800],
            "regulatory_score": regulatory.get("score", 50),
            "regulatory_analysis": regulatory.get("analysis", "No analysis available")[:800],
            "guardrails_context": guardrails_context,
        })

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)

        return {
            "agent": "Devil's Advocate",
            "challenges": parsed.get("challenges", default_result["challenges"]),
            "contradictions": parsed.get("contradictions", []),
            "analysis": parsed.get("analysis", default_result["analysis"]),
        }

    except Exception as e:
        logger.warning(f"[Devil's Advocate] Agent failed: {e}")
        return default_result
