"""
Seed the SQLite database with demo users and risk analyses for testing.
Run from the backend directory:
    python seed_data.py
"""
import os
import sys
import json
import random
from datetime import datetime, timedelta

# Load .env before importing anything that reads env vars
from dotenv import load_dotenv
load_dotenv()

from models.database import create_tables, SessionLocal, User, RiskAnalysis, UploadedDocument
from auth.jwt_handler import hash_password

DEMO_USERS = [
    {
        "email": "admin@bfsi.com",
        "username": "admin",
        "password": "Admin@123",
        "full_name": "Admin User",
    },
    {
        "email": "analyst@bfsi.com",
        "username": "analyst",
        "password": "Analyst@123",
        "full_name": "Risk Analyst",
    },
    {
        "email": "demo@bfsi.com",
        "username": "demo",
        "password": "Demo@123",
        "full_name": "Demo User",
    },
]

SAMPLE_ANALYSES = [
    {
        "company_name": "TechCorp Global",
        "ticker": "TCG",
        "overall_risk_score": 68.4,
        "market_risk_score": 72.1,
        "sentiment_score": 61.5,
        "financial_risk_score": 70.3,
        "compliance_risk_score": 65.8,
        "risk_level": "HIGH",
        "summary": (
            "TechCorp Global presents HIGH overall risk. Market volatility is elevated (beta 1.42, "
            "30-day vol 34%). Sentiment analysis reveals 38% negative media coverage driven by "
            "executive departures and supply-chain concerns. Financial leverage (Net Debt/EBITDA 2.1x) "
            "leaves limited headroom. Two SOX 404 material weaknesses and active regulatory inquiries "
            "($150M–$800M potential fines) elevate compliance risk materially."
        ),
        "market_analysis": json.dumps({
            "beta": 1.42, "volatility_30d": 0.34, "var_95": 0.058,
            "pe_ratio": 22.5, "price_trend": "bearish",
            "analysis": "Above-market beta with elevated volatility signals heightened systematic risk exposure."
        }),
        "sentiment_analysis": json.dumps({
            "overall_sentiment": "negative", "score": -0.38,
            "positive_articles": 12, "negative_articles": 19, "neutral_articles": 8,
            "top_headlines": [
                "TechCorp CFO departs amid strategic review",
                "Supply chain disruptions weigh on TechCorp Q4 outlook",
                "TechCorp beats Q2 estimates, upgrades guidance",
            ],
            "analysis": "Predominantly negative sentiment driven by executive turnover and operational concerns."
        }),
        "financial_analysis": json.dumps({
            "revenue": 18_400_000_000, "net_income": 2_100_000_000,
            "total_debt": 12_300_000_000, "total_equity": 31_800_000_000,
            "debt_to_equity": 0.39, "current_ratio": 1.87,
            "roe": 0.066, "roa": 0.038,
            "analysis": "Solid revenue growth, but limited EBITDA headroom and $3.1B near-term debt maturity risk."
        }),
        "compliance_analysis": json.dumps({
            "violations": ["SOX 404 Material Weakness x2", "GDPR regulatory inquiry"],
            "risk_score": 65.8,
            "rules_checked": ["Basel III", "GDPR", "SOX 404", "AML/KYC"],
            "analysis": "Active regulatory inquiries and internal control weaknesses require immediate remediation."
        }),
        "days_ago": 2,
    },
    {
        "company_name": "FinanceHub Ltd",
        "ticker": "FHL",
        "overall_risk_score": 54.2,
        "market_risk_score": 49.8,
        "sentiment_score": 52.3,
        "financial_risk_score": 56.7,
        "compliance_risk_score": 58.0,
        "risk_level": "MEDIUM",
        "summary": (
            "FinanceHub Ltd carries MEDIUM overall risk. CET1 ratio of 13.2% provides adequate capital "
            "buffer above Basel III minimums. NPL ratio rise to 3.2% warrants monitoring. FCA VREQ "
            "issued for AML/KYC deficiencies raises compliance risk. Stable sentiment with balanced "
            "positive/negative media coverage."
        ),
        "market_analysis": json.dumps({
            "beta": 0.89, "volatility_30d": 0.21, "var_95": 0.031,
            "pe_ratio": 11.2, "price_trend": "neutral",
            "analysis": "Below-market beta and moderate volatility indicate manageable market risk."
        }),
        "sentiment_analysis": json.dumps({
            "overall_sentiment": "neutral", "score": 0.05,
            "positive_articles": 15, "negative_articles": 13, "neutral_articles": 10,
            "top_headlines": [
                "FinanceHub CET1 ratio stable at 13.2%, above Basel III floor",
                "FCA issues VREQ to FinanceHub over AML due-diligence gaps",
                "FinanceHub Consumer Duty implementation completed on schedule",
            ],
            "analysis": "Balanced sentiment; regulatory action partially offset by strong capital position news."
        }),
        "financial_analysis": json.dumps({
            "total_assets_aum": 89_400_000_000, "cet1_ratio": 0.132,
            "npl_ratio": 0.032, "loan_loss_provisions": 1_200_000_000,
            "leverage_ratio": 0.054, "nii_sensitivity_200bp": 340_000_000,
            "analysis": "Capital ratios strong; rising NPL and FCA VREQ are the primary financial concerns."
        }),
        "compliance_analysis": json.dumps({
            "violations": ["FCA VREQ — AML/KYC correspondent banking", "3 products failed fair value test"],
            "risk_score": 58.0,
            "rules_checked": ["Basel III", "AML/KYC", "MiFID II", "GDPR", "PCI DSS"],
            "analysis": "VREQ remediation timeline 18 months; MiFID II and PCI DSS fully compliant."
        }),
        "days_ago": 5,
    },
    {
        "company_name": "EnergyMax Inc",
        "ticker": "EMX",
        "overall_risk_score": 41.7,
        "market_risk_score": 45.2,
        "sentiment_score": 38.9,
        "financial_risk_score": 43.1,
        "compliance_risk_score": 39.5,
        "risk_level": "MEDIUM",
        "summary": (
            "EnergyMax Inc presents MEDIUM overall risk. Positive sentiment following regulatory approval "
            "for new product line and strong Q3 results. Financial metrics are healthy with current ratio "
            "of 2.1 and manageable leverage. Compliance posture is stable with no active investigations."
        ),
        "market_analysis": json.dumps({
            "beta": 1.15, "volatility_30d": 0.28, "var_95": 0.041,
            "pe_ratio": 18.7, "price_trend": "bullish",
            "analysis": "Moderate beta; recent positive catalyst from regulatory product approval lifts outlook."
        }),
        "sentiment_analysis": json.dumps({
            "overall_sentiment": "positive", "score": 0.42,
            "positive_articles": 21, "negative_articles": 7, "neutral_articles": 9,
            "top_headlines": [
                "EnergyMax receives regulatory approval for next-gen energy storage line",
                "EnergyMax Q3 revenue beats estimates by 12%, upgrades FY guidance",
                "Analysts upgrade EnergyMax to Buy after strong balance sheet showing",
            ],
            "analysis": "Predominantly positive sentiment driven by product approvals and strong earnings."
        }),
        "financial_analysis": json.dumps({
            "revenue": 8_200_000_000, "net_income": 920_000_000,
            "total_debt": 3_400_000_000, "total_equity": 12_100_000_000,
            "debt_to_equity": 0.28, "current_ratio": 2.1,
            "roe": 0.076, "roa": 0.052,
            "analysis": "Low leverage, strong liquidity, and improving profitability signal low financial stress."
        }),
        "compliance_analysis": json.dumps({
            "violations": [],
            "risk_score": 39.5,
            "rules_checked": ["Dodd-Frank", "GDPR", "AML/KYC", "SOX 404"],
            "analysis": "No active violations; SOX 404 controls assessed as effective in latest review."
        }),
        "days_ago": 8,
    },
    {
        "company_name": "PharmaCare Corp",
        "ticker": "PCC",
        "overall_risk_score": 79.3,
        "market_risk_score": 75.6,
        "sentiment_score": 82.1,
        "financial_risk_score": 77.4,
        "compliance_risk_score": 82.0,
        "risk_level": "HIGH",
        "summary": (
            "PharmaCare Corp is rated HIGH risk. CEO resignation and ongoing credit rating downgrade "
            "have severely impacted market and sentiment scores. High leverage (D/E 2.7) combined with "
            "a Q3 earnings miss raises financial distress signals. Compliance risk elevated by multiple "
            "jurisdiction-specific regulatory inquiries."
        ),
        "market_analysis": json.dumps({
            "beta": 1.78, "volatility_30d": 0.48, "var_95": 0.087,
            "pe_ratio": 31.4, "price_trend": "bearish",
            "analysis": "High beta and volatility post-CEO departure; significant downside tail risk."
        }),
        "sentiment_analysis": json.dumps({
            "overall_sentiment": "negative", "score": -0.67,
            "positive_articles": 5, "negative_articles": 28, "neutral_articles": 6,
            "top_headlines": [
                "PharmaCare CEO resigns amid controversy, triggering market uncertainty",
                "Credit agency downgrades PharmaCare outlook to Negative",
                "PharmaCare misses Q3 revenue by 8%, cuts FY guidance",
            ],
            "analysis": "Strongly negative sentiment; leadership vacuum and earnings miss compound concerns."
        }),
        "financial_analysis": json.dumps({
            "revenue": 6_800_000_000, "net_income": -240_000_000,
            "total_debt": 9_100_000_000, "total_equity": 3_370_000_000,
            "debt_to_equity": 2.7, "current_ratio": 0.91,
            "roe": -0.071, "roa": -0.018,
            "analysis": "Negative net income, high leverage, and sub-1 current ratio signal financial stress."
        }),
        "compliance_analysis": json.dumps({
            "violations": ["GDPR inquiry — patient data handling", "SOX 404 material weakness — revenue recognition"],
            "risk_score": 82.0,
            "rules_checked": ["GDPR", "SOX 404", "IFRS 9", "AML/KYC"],
            "analysis": "Multiple active compliance issues across jurisdictions; remediation cost est. $80M–$200M."
        }),
        "days_ago": 12,
    },
    {
        "company_name": "RetailGiant Co",
        "ticker": "RGC",
        "overall_risk_score": 28.5,
        "market_risk_score": 31.2,
        "sentiment_score": 24.8,
        "financial_risk_score": 29.6,
        "compliance_risk_score": 28.3,
        "risk_level": "LOW",
        "summary": (
            "RetailGiant Co presents LOW overall risk. Record earnings, strong investor confidence, and "
            "a healthy balance sheet underpin the positive outlook. Regulatory compliance is up to date "
            "with PCI DSS and GDPR certifications current. Low beta and stable sentiment support the "
            "low-risk classification."
        ),
        "market_analysis": json.dumps({
            "beta": 0.72, "volatility_30d": 0.16, "var_95": 0.022,
            "pe_ratio": 15.3, "price_trend": "bullish",
            "analysis": "Low beta and minimal volatility; stable defensive retail characteristics."
        }),
        "sentiment_analysis": json.dumps({
            "overall_sentiment": "positive", "score": 0.61,
            "positive_articles": 24, "negative_articles": 4, "neutral_articles": 8,
            "top_headlines": [
                "RetailGiant reports record Q3 earnings, beats analyst estimates by 15%",
                "RetailGiant announces $500M strategic partnership expanding Asia-Pacific reach",
                "Analysts upgrade RetailGiant to Strong Buy on consistent execution",
            ],
            "analysis": "Strong positive sentiment; multiple positive catalysts reinforce low-risk view."
        }),
        "financial_analysis": json.dumps({
            "revenue": 34_500_000_000, "net_income": 4_100_000_000,
            "total_debt": 4_200_000_000, "total_equity": 22_800_000_000,
            "debt_to_equity": 0.18, "current_ratio": 2.8,
            "roe": 0.18, "roa": 0.11,
            "analysis": "Excellent liquidity, low leverage, high ROE — among the strongest financial profiles."
        }),
        "compliance_analysis": json.dumps({
            "violations": [],
            "risk_score": 28.3,
            "rules_checked": ["GDPR", "PCI DSS", "AML/KYC", "SOX 404"],
            "analysis": "Full compliance across all checked frameworks; PCI DSS Level 1 and GDPR certifications current."
        }),
        "days_ago": 15,
    },
]


def seed():
    print("Creating database tables...")
    create_tables()

    db = SessionLocal()
    try:
        # ── Seed users ──────────────────────────────────────────────────────
        created_users = {}
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"  [SKIP] User already exists: {u['email']}")
                created_users[u["email"]] = existing
                continue
            user = User(
                email=u["email"],
                username=u["username"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_users[u["email"]] = user
            print(f"  [OK] Created user: {u['email']} / password: {u['password']}")

        db.commit()

        # ── Seed risk analyses for demo user ────────────────────────────────
        demo_user = created_users.get("demo@bfsi.com")
        admin_user = created_users.get("admin@bfsi.com")
        analyst_user = created_users.get("analyst@bfsi.com")

        for i, a in enumerate(SAMPLE_ANALYSES):
            # Spread analyses across users
            owner = [demo_user, admin_user, analyst_user][i % 3]
            existing = db.query(RiskAnalysis).filter(
                RiskAnalysis.user_id == owner.id,
                RiskAnalysis.company_name == a["company_name"],
            ).first()
            if existing:
                print(f"  [SKIP] Analysis already exists: {a['company_name']} for {owner.email}")
                continue
            created_at = datetime.utcnow() - timedelta(days=a["days_ago"])
            record = RiskAnalysis(
                user_id=owner.id,
                company_name=a["company_name"],
                ticker=a["ticker"],
                overall_risk_score=a["overall_risk_score"],
                market_risk_score=a["market_risk_score"],
                sentiment_score=a["sentiment_score"],
                financial_risk_score=a["financial_risk_score"],
                compliance_risk_score=a["compliance_risk_score"],
                risk_level=a["risk_level"],
                summary=a["summary"],
                market_analysis=a["market_analysis"],
                sentiment_analysis=a["sentiment_analysis"],
                financial_analysis=a["financial_analysis"],
                compliance_analysis=a["compliance_analysis"],
                created_at=created_at,
            )
            db.add(record)
            print(f"  [OK] Added analysis: {a['company_name']} ({a['risk_level']}) for {owner.email}")

        db.commit()
        print("\nDatabase seeded successfully.\n")

    finally:
        db.close()


def print_summary():
    print("=" * 60)
    print("DEMO CREDENTIALS")
    print("=" * 60)
    for u in DEMO_USERS:
        print(f"  Email:    {u['email']}")
        print(f"  Username: {u['username']}")
        print(f"  Password: {u['password']}")
        print()
    print("SAMPLE COMPANIES (for risk analysis)")
    print("=" * 60)
    for a in SAMPLE_ANALYSES:
        print(f"  {a['ticker']:4s}  {a['company_name']:<22s}  {a['risk_level']}")
    print()
    print("API docs:  http://localhost:8000/api/docs")
    print("Frontend:  http://localhost:5173")
    print("=" * 60)


if __name__ == "__main__":
    seed()
    print_summary()
