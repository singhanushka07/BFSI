from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mcp_server.dispatcher import call_mcp_tool
import os


def run_sentiment_agent(company: str, ticker: str) -> dict:
    """Sentiment Agent: fetches news via MCP, analyzes reputational and market sentiment risk."""
    mcp_calls = []

    # MCP tool call: get news sentiment data
    news_call = call_mcp_tool("get_news_sentiment", {"company": company, "count": 12})
    mcp_calls.append({k: v for k, v in news_call.items() if k != "result"})
    news = news_call["result"] or []

    if not news:
        news = []

    scores = [n["score"] for n in news] if news else [0.0]
    avg_score = sum(scores) / len(scores)
    positive_count = sum(1 for n in news if n["sentiment"] == "positive")
    negative_count = sum(1 for n in news if n["sentiment"] == "negative")
    neutral_count = sum(1 for n in news if n["sentiment"] == "neutral")

    sentiment_risk_score = round((1 - (avg_score + 1) / 2) * 100, 1)
    sentiment_risk_score = max(0, min(100, sentiment_risk_score))

    news_summary = "\n".join([
        f"- [{n['sentiment'].upper()}] {n['headline']} ({n['source']})"
        for n in news[:6]
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a financial sentiment analyst specializing in reputational risk for BFSI institutions. Be concise and professional."),
        ("human", """Perform sentiment risk analysis for {company} based on recent news.

News Headlines fetched via MCP get_news_sentiment tool (last 72 hours):
{news_summary}

Sentiment Breakdown: {positive} positive, {negative} negative, {neutral} neutral
Average Sentiment Score: {avg_score:.3f} (-1 very negative, +1 very positive)

Provide a 3-sentence assessment of: overall sentiment trend, reputational risk exposure, and impact on investor confidence. Be direct and analytical.""")
    ])

    analysis_text = (
        f"{company} shows an average sentiment score of {avg_score:.3f} across {len(news)} recent news items. "
        f"With {negative_count} negative vs {positive_count} positive stories, the sentiment outlook is "
        f"{'concerning' if avg_score < 0 else 'favorable'}. "
        f"Sentiment risk score: {sentiment_risk_score}/100. [MCP tool used: get_news_sentiment]"
    )

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
        chain = prompt | llm
        response = chain.invoke({
            "company": company, "news_summary": news_summary,
            "positive": positive_count, "negative": negative_count,
            "neutral": neutral_count, "avg_score": avg_score,
        })
        analysis_text = response.content
    except Exception:
        pass

    return {
        "agent": "Sentiment Analysis",
        "score": sentiment_risk_score,
        "risk_level": _risk_level(sentiment_risk_score),
        "analysis": analysis_text,
        "mcp_calls": mcp_calls,
        "metrics": {
            "average_sentiment": round(avg_score, 3),
            "positive_articles": positive_count,
            "negative_articles": negative_count,
            "neutral_articles": neutral_count,
            "total_articles_analyzed": len(news),
        },
        "news_feed": news[:8],
    }


def _risk_level(score: float) -> str:
    if score < 25: return "LOW"
    if score < 50: return "MEDIUM"
    if score < 75: return "HIGH"
    return "CRITICAL"
