from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db, User, RiskAnalysis
from auth.jwt_handler import get_current_user
from data.mock_data import generate_risk_history, COMPANIES

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate stats for the dashboard overview cards."""
    analyses = db.query(RiskAnalysis).filter(RiskAnalysis.user_id == current_user.id).all()
    total = len(analyses)

    if not analyses:
        return {
            "total_analyses": 0,
            "avg_risk_score": 0,
            "high_risk_count": 0,
            "critical_risk_count": 0,
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "recent_analyses": [],
        }

    avg_score = sum(a.overall_risk_score for a in analyses) / total
    distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for a in analyses:
        distribution[a.risk_level] = distribution.get(a.risk_level, 0) + 1

    recent = sorted(analyses, key=lambda x: x.created_at, reverse=True)[:5]

    return {
        "total_analyses": total,
        "avg_risk_score": round(avg_score, 1),
        "high_risk_count": distribution["HIGH"],
        "critical_risk_count": distribution["CRITICAL"],
        "risk_distribution": distribution,
        "recent_analyses": [
            {
                "id": r.id,
                "company": r.company_name,
                "ticker": r.ticker,
                "score": r.overall_risk_score,
                "level": r.risk_level,
                "date": r.created_at.strftime("%b %d"),
            }
            for r in recent
        ],
    }


@router.get("/risk-trend/{company}")
def get_risk_trend(company: str, days: int = 30):
    """Return mock historical risk trend data for charts."""
    return {
        "company": company,
        "history": generate_risk_history(company, days=days),
    }


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Overview data: agent performance, score breakdown."""
    analyses = db.query(RiskAnalysis).filter(RiskAnalysis.user_id == current_user.id).all()

    if not analyses:
        return {
            "agent_averages": {
                "market": 50, "sentiment": 50, "financial": 50, "compliance": 50
            },
            "trend_data": generate_risk_history("Sample Corp", 14),
        }

    avg_market = sum(a.market_risk_score for a in analyses) / len(analyses)
    avg_sentiment = sum(a.sentiment_score for a in analyses) / len(analyses)
    avg_financial = sum(a.financial_risk_score for a in analyses) / len(analyses)
    avg_compliance = sum(a.compliance_risk_score for a in analyses) / len(analyses)

    latest = sorted(analyses, key=lambda x: x.created_at, reverse=True)[0]

    return {
        "agent_averages": {
            "market": round(avg_market, 1),
            "sentiment": round(avg_sentiment, 1),
            "financial": round(avg_financial, 1),
            "compliance": round(avg_compliance, 1),
        },
        "trend_data": generate_risk_history(latest.company_name, 14),
        "latest_analysis": {
            "company": latest.company_name,
            "score": latest.overall_risk_score,
            "level": latest.risk_level,
        },
    }
