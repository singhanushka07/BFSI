from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mcp_server.dispatcher import call_mcp_tool
import os
import math


def run_market_risk_agent(company: str, ticker: str) -> dict:
    """Market Risk Agent: fetches data via MCP tools, analyzes volatility, VaR, and market exposure."""
    mcp_calls = []

    # MCP tool call: get stock price data
    stock_call = call_mcp_tool("get_stock_data", {"ticker": ticker, "days": 30})
    mcp_calls.append({k: v for k, v in stock_call.items() if k != "result"})
    stock_data = stock_call["result"] or []

    # MCP tool call: get financial ratios
    metrics_call = call_mcp_tool("get_financial_metrics", {"company": company})
    mcp_calls.append({k: v for k, v in metrics_call.items() if k != "result"})
    metrics = metrics_call["result"] or {}

    closes = [d["close"] for d in stock_data] if stock_data else [100.0] * 30
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
    volatility = round(math.sqrt(sum(r ** 2 for r in returns) / len(returns)) * math.sqrt(252), 4)
    mean_return = sum(returns) / len(returns)
    std_return = math.sqrt(sum((r - mean_return) ** 2 for r in returns) / len(returns))
    var_95 = round(abs(mean_return - 1.645 * std_return) * 100, 3)
    risk_score = min(100, round((volatility * 100 * 0.5) + (var_95 * 3) + (metrics.get("beta", 1.0) * 10), 1))

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert quantitative financial risk analyst at a top-tier BFSI firm. Be precise and professional."),
        ("human", """Analyze the market risk for {company} ({ticker}).

Financial Metrics (retrieved via MCP get_stock_data + get_financial_metrics tools):
- 30-day Volatility: {volatility}
- Value at Risk (95%): {var_95}%
- Beta: {beta}
- P/E Ratio: {pe_ratio}
- Debt-to-Equity: {debt_to_equity}
- Current Ratio: {current_ratio}

Provide a 3-sentence professional risk assessment covering: volatility risk, systematic risk (beta), and overall market exposure risk. End with a risk score between 0-100.""")
    ])

    analysis_text = (
        f"{company} exhibits {volatility:.1%} annualized volatility with a 95% VaR of {var_95}%. "
        f"The stock's beta of {metrics.get('beta', 1.0)} indicates "
        f"{'above-average' if metrics.get('beta', 1.0) > 1 else 'below-average'} systematic risk exposure. "
        f"Market risk score: {risk_score}/100. [MCP tools used: get_stock_data, get_financial_metrics]"
    )

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
        chain = prompt | llm
        response = chain.invoke({
            "company": company, "ticker": ticker,
            "volatility": f"{volatility:.4f}", "var_95": var_95,
            "beta": metrics.get("beta", 1.0), "pe_ratio": metrics.get("pe_ratio", 20),
            "debt_to_equity": metrics.get("debt_to_equity", 0.5),
            "current_ratio": metrics.get("current_ratio", 1.5),
        })
        analysis_text = response.content
    except Exception:
        pass

    return {
        "agent": "Market Risk",
        "score": risk_score,
        "risk_level": _risk_level(risk_score),
        "analysis": analysis_text,
        "mcp_calls": mcp_calls,
        "metrics": {
            "volatility_annualized": volatility,
            "var_95_pct": var_95,
            "beta": metrics.get("beta", 1.0),
            "pe_ratio": metrics.get("pe_ratio", 20),
            "debt_to_equity": metrics.get("debt_to_equity", 0.5),
        },
        "price_history": stock_data[-14:] if stock_data else [],
    }


def _risk_level(score: float) -> str:
    if score < 25: return "LOW"
    if score < 50: return "MEDIUM"
    if score < 75: return "HIGH"
    return "CRITICAL"
