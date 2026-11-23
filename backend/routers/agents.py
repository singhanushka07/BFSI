from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import get_db, User, RiskAnalysis
from auth.jwt_handler import get_current_user
from agents.orchestrator import run_full_analysis
from data.mock_data import COMPANIES
from typing import Optional
import json

router = APIRouter(prefix="/api/agents", tags=["Risk Agents"])


class AnalysisRequest(BaseModel):
    company: str
    ticker: str
    sector: str = "Financial Services"
    collection_name: Optional[str] = None


class AnalysisResponse(BaseModel):
    id: int
    company_name: str
    ticker: str
    overall_risk_score: float
    risk_level: str
    market_risk_score: float
    sentiment_score: float
    financial_risk_score: float
    compliance_risk_score: float
    summary: str

    class Config:
        from_attributes = True


@router.post("/analyze")
def run_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run full 4-agent risk analysis for a company."""
    try:
        report = run_full_analysis(
            company=request.company,
            ticker=request.ticker,
            sector=request.sector,
            collection_name=request.collection_name,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    scores = report.get("scores", {})
    record = RiskAnalysis(
        user_id=current_user.id,
        company_name=request.company,
        ticker=request.ticker,
        overall_risk_score=report.get("overall_risk_score", 50),
        market_risk_score=scores.get("market", 50),
        sentiment_score=scores.get("sentiment", 50),
        financial_risk_score=scores.get("financial", 50),
        compliance_risk_score=scores.get("compliance", 50),
        risk_level=report.get("risk_level", "MEDIUM"),
        summary=report.get("summary", ""),
        market_analysis=json.dumps(report.get("agents", {}).get("market", {})),
        sentiment_analysis=json.dumps(report.get("agents", {}).get("sentiment", {})),
        financial_analysis=json.dumps(report.get("agents", {}).get("financial", {})),
        compliance_analysis=json.dumps(report.get("agents", {}).get("regulatory", {})),
        debate_analysis=json.dumps(report.get("debate", {})),
        guardrails_result=json.dumps(report.get("guardrails", {})),
        adjusted_risk_score=report.get("adjusted_risk_score"),
        trust_score=report.get("trust_score"),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {**report, "db_id": record.id}


@router.get("/history")
def get_analysis_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(RiskAnalysis)
        .filter(RiskAnalysis.user_id == current_user.id)
        .order_by(RiskAnalysis.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": r.id,
            "company": r.company_name,
            "ticker": r.ticker,
            "overall_score": r.overall_risk_score,
            "risk_level": r.risk_level,
            "market": r.market_risk_score,
            "sentiment": r.sentiment_score,
            "financial": r.financial_risk_score,
            "compliance": r.compliance_risk_score,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@router.get("/history/{analysis_id}")
def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(RiskAnalysis).filter(
        RiskAnalysis.id == analysis_id, RiskAnalysis.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": record.id,
        "company": record.company_name,
        "ticker": record.ticker,
        "overall_score": record.overall_risk_score,
        "risk_level": record.risk_level,
        "summary": record.summary,
        "scores": {
            "market": record.market_risk_score,
            "sentiment": record.sentiment_score,
            "financial": record.financial_risk_score,
            "compliance": record.compliance_risk_score,
        },
        "market_detail": json.loads(record.market_analysis or "{}"),
        "sentiment_detail": json.loads(record.sentiment_analysis or "{}"),
        "financial_detail": json.loads(record.financial_analysis or "{}"),
        "compliance_detail": json.loads(record.compliance_analysis or "{}"),
        "created_at": record.created_at.isoformat(),
    }


@router.get("/companies")
def get_sample_companies():
    """Return list of sample companies for demo."""
    return COMPANIES
