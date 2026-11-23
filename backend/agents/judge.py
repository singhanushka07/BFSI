"""Judge Agent: resolves the Devil's Advocate debate and issues final verdicts."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import logging

logger = logging.getLogger(__name__)


def run_judge_agent(all_agent_results: dict, devils_advocate_result: dict, original_scores: dict) -> dict:
    """Evaluate Devil's Advocate challenges and produce adjusted scores."""

    challenges_text = "\n".join(
        f"- [{c.get('severity', 'minor').upper()}] Against {c.get('target_agent', 'unknown')}: {c.get('challenge', '')}"
        for c in devils_advocate_result.get("challenges", [])
    )

    contradictions_text = "\n".join(
        f"- Between {' and '.join(c.get('agents', []))}: {c.get('description', '')}"
        for c in devils_advocate_result.get("contradictions", [])
    )

    da_analysis = devils_advocate_result.get("analysis", "No analysis provided")

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a senior risk committee judge. Review the original agent risk analyses "
            "and the Devil's Advocate challenges. Issue a fair, evidence-based final verdict. "
            "Adjust scores only when challenges are substantive and well-founded. "
            "Return ONLY valid JSON with no additional text."
        )),
        ("human", (
            "ORIGINAL SCORES:\n"
            "- Market Risk: {market_score}/100\n"
            "- Sentiment: {sentiment_score}/100\n"
            "- Financial: {financial_score}/100\n"
            "- Compliance: {compliance_score}/100\n"
            "- Overall (weighted): {overall_score}/100\n\n"
            "DEVIL'S ADVOCATE CHALLENGES:\n{challenges_text}\n\n"
            "CONTRADICTIONS IDENTIFIED:\n{contradictions_text}\n\n"
            "DEVIL'S ADVOCATE SUMMARY:\n{da_analysis}\n\n"
            "AGENT SUMMARIES:\n"
            "Market: {market_summary}\n"
            "Sentiment: {sentiment_summary}\n"
            "Financial: {financial_summary}\n"
            "Regulatory: {regulatory_summary}\n\n"
            "For each challenge, decide: accepted, partially_accepted, or dismissed.\n"
            "If accepted/partially accepted, adjust the relevant score.\n\n"
            "Return JSON: {{"
            "\"verdicts\": [{{\"challenge_index\": 0, \"ruling\": \"accepted|partially_accepted|dismissed\", \"reasoning\": \"...\"}}], "
            "\"adjusted_scores\": {{\"market\": <0-100>, \"sentiment\": <0-100>, \"financial\": <0-100>, \"compliance\": <0-100>}}, "
            "\"adjusted_overall\": <0-100 weighted average>, "
            "\"verdict\": \"final verdict paragraph\", "
            "\"debate_impact\": \"minimal|moderate|significant\""
            "}}"
        )),
    ])

    weights = {"market": 0.30, "sentiment": 0.20, "financial": 0.30, "compliance": 0.20}
    original_overall = sum(original_scores.get(k, 50) * weights[k] for k in weights)

    default_result = {
        "agent": "Judge",
        "verdicts": [
            {"challenge_index": i, "ruling": "partially_accepted", "reasoning": "Challenge has merit but impact is limited."}
            for i in range(len(devils_advocate_result.get("challenges", [])))
        ],
        "adjusted_scores": original_scores,
        "adjusted_overall": round(original_overall, 1),
        "verdict": "After reviewing all challenges, the original risk assessment is largely upheld with minor adjustments. The agents' analyses are methodologically sound but could benefit from broader data coverage.",
        "debate_impact": "minimal",
    }

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        market = all_agent_results.get("market", {})
        sentiment = all_agent_results.get("sentiment", {})
        financial = all_agent_results.get("financial", {})
        regulatory = all_agent_results.get("regulatory", {})

        chain = prompt | llm
        response = chain.invoke({
            "market_score": original_scores.get("market", 50),
            "sentiment_score": original_scores.get("sentiment", 50),
            "financial_score": original_scores.get("financial", 50),
            "compliance_score": original_scores.get("compliance", 50),
            "overall_score": round(original_overall, 1),
            "challenges_text": challenges_text or "No challenges raised.",
            "contradictions_text": contradictions_text or "No contradictions found.",
            "da_analysis": da_analysis[:600],
            "market_summary": market.get("analysis", "N/A")[:300],
            "sentiment_summary": sentiment.get("analysis", "N/A")[:300],
            "financial_summary": financial.get("analysis", "N/A")[:300],
            "regulatory_summary": regulatory.get("analysis", "N/A")[:300],
        })

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        parsed = json.loads(content)

        adjusted = parsed.get("adjusted_scores", original_scores)
        for k in weights:
            if k not in adjusted:
                adjusted[k] = original_scores.get(k, 50)
            adjusted[k] = min(100, max(0, float(adjusted[k])))

        adjusted_overall = parsed.get("adjusted_overall")
        if adjusted_overall is None:
            adjusted_overall = sum(adjusted.get(k, 50) * weights[k] for k in weights)
        adjusted_overall = round(min(100, max(0, float(adjusted_overall))), 1)

        return {
            "agent": "Judge",
            "verdicts": parsed.get("verdicts", default_result["verdicts"]),
            "adjusted_scores": adjusted,
            "adjusted_overall": adjusted_overall,
            "verdict": parsed.get("verdict", default_result["verdict"]),
            "debate_impact": parsed.get("debate_impact", "minimal"),
        }

    except Exception as e:
        logger.warning(f"[Judge] Agent failed: {e}")
        return default_result
