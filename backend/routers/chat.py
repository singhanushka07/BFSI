"""Conversational Risk Chat: chat with analysis results using RAG + context memory."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import get_db, User, RiskAnalysis, ChatMessage
from auth.jwt_handler import get_current_user
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Risk Chat"])


class ChatRequest(BaseModel):
    analysis_id: int
    message: str


class ChatResponse(BaseModel):
    response: str
    message_id: int


def _build_analysis_context(record: RiskAnalysis) -> str:
    """Build a context string from a risk analysis record."""
    sections = [
        f"Company: {record.company_name} ({record.ticker})",
        f"Overall Risk Score: {record.overall_risk_score}/100 ({record.risk_level})",
        f"Market Risk: {record.market_risk_score}/100",
        f"Sentiment Score: {record.sentiment_score}/100",
        f"Financial Risk: {record.financial_risk_score}/100",
        f"Compliance Risk: {record.compliance_risk_score}/100",
        f"\nSummary: {record.summary}",
    ]

    for label, field in [
        ("Market Analysis", record.market_analysis),
        ("Sentiment Analysis", record.sentiment_analysis),
        ("Financial Analysis", record.financial_analysis),
        ("Compliance Analysis", record.compliance_analysis),
    ]:
        if field:
            try:
                data = json.loads(field)
                analysis_text = data.get("analysis", "")
                if analysis_text:
                    sections.append(f"\n{label}:\n{analysis_text[:600]}")
            except (json.JSONDecodeError, AttributeError):
                pass

    if record.debate_analysis:
        try:
            debate = json.loads(record.debate_analysis)
            if debate.get("devils_advocate"):
                da = debate["devils_advocate"]
                sections.append(f"\nDevil's Advocate Analysis:\n{da.get('analysis', '')[:400]}")
                challenges = da.get("challenges", [])
                if challenges:
                    sections.append("Challenges raised:")
                    for c in challenges[:5]:
                        sections.append(f"  - [{c.get('severity', '')}] {c.get('target_agent', '')}: {c.get('challenge', '')}")
            if debate.get("judge"):
                judge = debate["judge"]
                sections.append(f"\nJudge Verdict:\n{judge.get('verdict', '')[:400]}")
                if judge.get("adjusted_overall"):
                    sections.append(f"Adjusted Overall Score: {judge['adjusted_overall']}/100 (Impact: {judge.get('debate_impact', 'N/A')})")
        except (json.JSONDecodeError, AttributeError):
            pass

    if record.guardrails_result:
        try:
            guardrails = json.loads(record.guardrails_result)
            if guardrails.get("trust_score"):
                sections.append(f"\nTrust Score: {guardrails['trust_score']}/100")
                for agent_key, ag in guardrails.get("agents", {}).items():
                    issues = ag.get("issues", [])
                    if issues:
                        sections.append(f"  {agent_key}: {len(issues)} issue(s) flagged")
        except (json.JSONDecodeError, AttributeError):
            pass

    return "\n".join(sections)


@router.post("/message", response_model=ChatResponse)
def send_chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(RiskAnalysis).filter(
        RiskAnalysis.id == request.analysis_id,
        RiskAnalysis.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.analysis_id == request.analysis_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    recent_history = history[-20:] if len(history) > 20 else history

    context = _build_analysis_context(record)

    messages = [
        ("system", (
            "You are a financial risk analyst assistant for the BFSI Multi-Agent Risk Assessment Platform. "
            "The user is reviewing a risk analysis. Use the analysis context below to answer their questions. "
            "You can explain scores, compare agent assessments, discuss what-if scenarios, "
            "and provide additional financial context. Be precise and reference the source data.\n\n"
            f"ANALYSIS CONTEXT:\n{context}"
        )),
    ]

    for msg in recent_history:
        messages.append(("human" if msg.role == "user" else "assistant", msg.content))

    messages.append(("human", request.message))

    prompt = ChatPromptTemplate.from_messages(messages)

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        chain = prompt | llm
        response = chain.invoke({})
        ai_response = response.content.strip()
    except Exception as e:
        logger.error(f"[Chat] LLM call failed: {e}")
        ai_response = (
            "I'm having trouble processing your request right now. "
            "Please try again in a moment, or rephrase your question."
        )

    user_msg = ChatMessage(
        analysis_id=request.analysis_id,
        user_id=current_user.id,
        role="user",
        content=request.message,
    )
    ai_msg = ChatMessage(
        analysis_id=request.analysis_id,
        user_id=current_user.id,
        role="assistant",
        content=ai_response,
    )
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ChatResponse(response=ai_response, message_id=ai_msg.id)


@router.get("/history/{analysis_id}")
def get_chat_history(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(RiskAnalysis).filter(
        RiskAnalysis.id == analysis_id,
        RiskAnalysis.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.analysis_id == analysis_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.delete("/history/{analysis_id}")
def clear_chat_history(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(RiskAnalysis).filter(
        RiskAnalysis.id == analysis_id,
        RiskAnalysis.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.query(ChatMessage).filter(ChatMessage.analysis_id == analysis_id).delete()
    db.commit()
    return {"status": "cleared", "analysis_id": analysis_id}
