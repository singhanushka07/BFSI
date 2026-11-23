import random
from datetime import datetime, timedelta


COMPANIES = [
    {"name": "TechCorp Global", "ticker": "TCG", "sector": "Technology"},
    {"name": "FinanceHub Ltd", "ticker": "FHL", "sector": "Financial Services"},
    {"name": "EnergyMax Inc", "ticker": "EMX", "sector": "Energy"},
    {"name": "PharmaCare Corp", "ticker": "PCC", "sector": "Healthcare"},
    {"name": "RetailGiant Co", "ticker": "RGC", "sector": "Retail"},
]

NEWS_TEMPLATES = {
    "positive": [
        "{company} reports record quarterly earnings, beating analyst estimates by 15%.",
        "{company} announces strategic partnership expanding market reach across Asia-Pacific.",
        "{company} receives regulatory approval for new product line, boosting investor confidence.",
        "{company} upgrades full-year guidance citing strong consumer demand.",
        "Analysts upgrade {company} to 'Buy' following strong balance sheet improvements.",
    ],
    "negative": [
        "{company} faces regulatory investigation over compliance practices.",
        "{company} reports disappointing Q3 results, missing revenue targets by 8%.",
        "{company} CEO resigns amid controversy, triggering market uncertainty.",
        "Credit rating agency downgrades {company} outlook to 'Negative'.",
        "{company} warns of supply chain disruptions affecting Q4 earnings.",
    ],
    "neutral": [
        "{company} announces board changes as part of annual governance review.",
        "{company} completes $500M acquisition of regional competitor.",
        "{company} schedules investor day for December to outline 5-year strategy.",
        "{company} files quarterly 10-Q with SEC, in line with expectations.",
        "{company} opens new headquarters in major financial district.",
    ],
}

REGULATORY_RULES = [
    {"rule": "Basel III Capital Requirements", "category": "Capital Adequacy", "severity": "HIGH"},
    {"rule": "GDPR Data Protection", "category": "Data Privacy", "severity": "HIGH"},
    {"rule": "AML/KYC Compliance", "category": "Financial Crime", "severity": "CRITICAL"},
    {"rule": "Dodd-Frank Act", "category": "Systemic Risk", "severity": "HIGH"},
    {"rule": "IFRS 9 Financial Instruments", "category": "Accounting Standards", "severity": "MEDIUM"},
    {"rule": "SOX Section 404", "category": "Internal Controls", "severity": "HIGH"},
    {"rule": "MiFID II Regulations", "category": "Market Conduct", "severity": "MEDIUM"},
    {"rule": "PCI DSS Compliance", "category": "Payment Security", "severity": "HIGH"},
]


def generate_stock_data(ticker: str, days: int = 30) -> list[dict]:
    base_price = random.uniform(50, 500)
    prices = []
    date = datetime.now() - timedelta(days=days)
    for _ in range(days):
        change = random.gauss(0, 0.02)
        base_price *= (1 + change)
        prices.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(base_price * random.uniform(0.98, 1.0), 2),
            "high": round(base_price * random.uniform(1.0, 1.03), 2),
            "low": round(base_price * random.uniform(0.97, 1.0), 2),
            "close": round(base_price, 2),
            "volume": random.randint(1_000_000, 10_000_000),
        })
        date += timedelta(days=1)
    return prices


def generate_risk_history(company: str, days: int = 30) -> list[dict]:
    history = []
    date = datetime.now() - timedelta(days=days)
    base_score = random.uniform(40, 75)
    for i in range(days):
        base_score += random.gauss(0, 2)
        base_score = max(0, min(100, base_score))
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "overall": round(base_score, 1),
            "market": round(base_score + random.gauss(0, 5), 1),
            "sentiment": round(base_score + random.gauss(0, 8), 1),
            "financial": round(base_score + random.gauss(0, 6), 1),
            "compliance": round(base_score + random.gauss(0, 4), 1),
        })
        date += timedelta(days=1)
    return history


def generate_news_feed(company: str, count: int = 10) -> list[dict]:
    news = []
    sentiments = ["positive", "negative", "neutral"]
    weights = [0.4, 0.35, 0.25]
    for i in range(count):
        sentiment = random.choices(sentiments, weights=weights)[0]
        template = random.choice(NEWS_TEMPLATES[sentiment])
        score = {"positive": random.uniform(0.5, 0.95), "negative": random.uniform(-0.95, -0.3), "neutral": random.uniform(-0.2, 0.2)}
        news.append({
            "headline": template.format(company=company),
            "source": random.choice(["Reuters", "Bloomberg", "WSJ", "Financial Times", "CNBC"]),
            "sentiment": sentiment,
            "score": round(score[sentiment], 3),
            "published_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
        })
    return sorted(news, key=lambda x: x["published_at"], reverse=True)


def compute_risk_level(score: float) -> str:
    if score < 25:
        return "LOW"
    elif score < 50:
        return "MEDIUM"
    elif score < 75:
        return "HIGH"
    return "CRITICAL"


def generate_financial_metrics(company: str) -> dict:
    return {
        "revenue": round(random.uniform(1e9, 50e9), 0),
        "net_income": round(random.uniform(1e8, 5e9), 0),
        "total_debt": round(random.uniform(5e8, 20e9), 0),
        "total_equity": round(random.uniform(2e9, 30e9), 0),
        "current_ratio": round(random.uniform(0.8, 3.5), 2),
        "debt_to_equity": round(random.uniform(0.2, 3.0), 2),
        "roe": round(random.uniform(0.05, 0.35), 3),
        "roa": round(random.uniform(0.02, 0.18), 3),
        "pe_ratio": round(random.uniform(8, 45), 1),
        "beta": round(random.uniform(0.5, 2.5), 2),
        "volatility_30d": round(random.uniform(0.1, 0.6), 3),
        "var_95": round(random.uniform(0.02, 0.12), 4),
    }
