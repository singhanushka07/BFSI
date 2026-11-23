"""SSE streaming endpoint for real-time agent analysis progress."""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import SessionLocal, User, RiskAnalysis
from auth.jwt_handler import decode_token
from agents.market_risk import run_market_risk_agent
from agents.sentiment import run_sentiment_agent
from agents.financial_report import run_financial_report_agent
from agents.regulatory import run_regulatory_agent
from agents.orchestrator import aggregator_node, RiskState
from typing import Optional
import asyncio
import json
import time

router = APIRouter(prefix="/api/agents", tags=["Streaming Analysis"])


class StreamAnalysisRequest(BaseModel):
    company: str
    ticker: str
    sector: str = "Financial Services"
    collection_name: Optional[str] = None


def _get_user_from_token(token: str) -> User:
    payload = decode_token(token)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    finally:
        db.close()


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


AGENT_STEPS = [
    ("market_risk", "Market Risk Agent", run_market_risk_agent),
    ("sentiment", "Sentiment Agent", run_sentiment_agent),
    ("financial_report", "Financial Report Agent (RAG)", run_financial_report_agent),
    ("regulatory", "Regulatory Compliance Agent", run_regulatory_agent),
]


@router.post("/analyze-stream")
async def stream_analysis(
    request: StreamAnalysisRequest,
    token: str = Query(..., description="JWT token for authentication"),
):
    user = _get_user_from_token(token)

    async def generate():
        state = RiskState(
            company=request.company,
            ticker=request.ticker,
            sector=request.sector,
            collection_name=request.collection_name,
            market_result=None,
            sentiment_result=None,
            financial_result=None,
            regulatory_result=None,
            mcp_calls=[],
            final_report=None,
            error=None,
        )

        total_steps = 7
        step = 0

        for i, (agent_key, agent_label, agent_fn) in enumerate(AGENT_STEPS):
            step += 1
            yield _sse_event("agent_start", {
                "agent": agent_key,
                "label": agent_label,
                "step": step,
                "total_steps": total_steps,
                "timestamp": time.time(),
            })
            await asyncio.sleep(0.05)

            try:
                if agent_key == "market_risk":
                    result = await asyncio.to_thread(
                        agent_fn, request.company, request.ticker
                    )
                elif agent_key == "sentiment":
                    result = await asyncio.to_thread(
                        agent_fn, request.company, request.ticker
                    )
                elif agent_key == "financial_report":
                    result = await asyncio.to_thread(
                        agent_fn, request.company, request.ticker, request.collection_name
                    )
                elif agent_key == "regulatory":
                    result = await asyncio.to_thread(
                        agent_fn, request.company, request.ticker, request.sector
                    )

                agent_mcp_calls = result.pop("mcp_calls", [])
                state["mcp_calls"] = state["mcp_calls"] + agent_mcp_calls
                state[f"{agent_key}_result"] = result

                yield _sse_event("agent_complete", {
                    "agent": agent_key,
                    "label": agent_label,
                    "score": result.get("score", 50),
                    "risk_level": result.get("risk_level", "MEDIUM"),
                    "step": step,
                    "total_steps": total_steps,
                    "timestamp": time.time(),
                })

            except Exception as e:
                yield _sse_event("agent_error", {
                    "agent": agent_key,
                    "error": str(e),
                    "timestamp": time.time(),
                })
                state["error"] = f"{agent_label} failed: {str(e)}"

            await asyncio.sleep(0.05)

        # Aggregator
        step += 1
        yield _sse_event("agent_start", {
            "agent": "aggregator",
            "label": "LangGraph Aggregator",
            "step": step,
            "total_steps": total_steps,
            "timestamp": time.time(),
        })
        await asyncio.sleep(0.05)

        state = await asyncio.to_thread(aggregator_node, state)

        yield _sse_event("agent_complete", {
            "agent": "aggregator",
            "label": "LangGraph Aggregator",
            "score": state["final_report"].get("overall_risk_score", 50),
            "risk_level": state["final_report"].get("risk_level", "MEDIUM"),
            "step": step,
            "total_steps": total_steps,
            "timestamp": time.time(),
        })
        await asyncio.sleep(0.05)

        # Guardrails validation
        step += 1
        yield _sse_event("agent_start", {
            "agent": "guardrails",
            "label": "Guardrails Validator",
            "step": step,
            "total_steps": total_steps,
            "timestamp": time.time(),
        })
        await asyncio.sleep(0.05)

        try:
            from agents.guardrails import validate_all_agents
            guardrails_result = await asyncio.to_thread(validate_all_agents, state["final_report"])
            state["final_report"]["guardrails"] = guardrails_result
            state["final_report"]["trust_score"] = guardrails_result.get("trust_score", 0)

            yield _sse_event("guardrails_complete", {
                "trust_score": guardrails_result.get("trust_score", 0),
                "agents": {k: v.get("confidence_score", 0) for k, v in guardrails_result.get("agents", {}).items()},
                "step": step,
                "total_steps": total_steps,
                "timestamp": time.time(),
            })
        except Exception as e:
            yield _sse_event("agent_error", {
                "agent": "guardrails",
                "error": str(e),
                "timestamp": time.time(),
            })
        await asyncio.sleep(0.05)

        # Devil's Advocate + Judge debate
        step += 1
        yield _sse_event("debate_start", {
            "step": step,
            "total_steps": total_steps + 1,
            "timestamp": time.time(),
        })

        try:
            from agents.devils_advocate import run_devils_advocate_agent
            from agents.judge import run_judge_agent

            all_results = {
                "market": state.get("market_result", {}),
                "sentiment": state.get("sentiment_result", {}),
                "financial": state.get("financial_result", {}),
                "regulatory": state.get("regulatory_result", {}),
            }
            guardrails_data = state["final_report"].get("guardrails")

            yield _sse_event("agent_start", {
                "agent": "devils_advocate",
                "label": "Devil's Advocate Agent",
                "step": step,
                "total_steps": total_steps + 1,
                "timestamp": time.time(),
            })
            await asyncio.sleep(0.05)

            da_result = await asyncio.to_thread(run_devils_advocate_agent, all_results, guardrails_data)

            yield _sse_event("agent_complete", {
                "agent": "devils_advocate",
                "label": "Devil's Advocate Agent",
                "challenges_count": len(da_result.get("challenges", [])),
                "step": step,
                "total_steps": total_steps + 1,
                "timestamp": time.time(),
            })
            await asyncio.sleep(0.05)

            step += 1
            yield _sse_event("agent_start", {
                "agent": "judge",
                "label": "Judge Agent",
                "step": step,
                "total_steps": total_steps + 1,
                "timestamp": time.time(),
            })
            await asyncio.sleep(0.05)

            original_scores = state["final_report"].get("scores", {})
            judge_result = await asyncio.to_thread(
                run_judge_agent, all_results, da_result, original_scores
            )

            state["final_report"]["debate"] = {
                "devils_advocate": da_result,
                "judge": judge_result,
            }
            if judge_result.get("adjusted_overall"):
                state["final_report"]["adjusted_risk_score"] = judge_result["adjusted_overall"]
                state["final_report"]["adjusted_scores"] = judge_result.get("adjusted_scores", {})

            yield _sse_event("agent_complete", {
                "agent": "judge",
                "label": "Judge Agent",
                "debate_impact": judge_result.get("debate_impact", "minimal"),
                "adjusted_overall": judge_result.get("adjusted_overall"),
                "step": step,
                "total_steps": total_steps + 1,
                "timestamp": time.time(),
            })

        except Exception as e:
            yield _sse_event("agent_error", {
                "agent": "debate",
                "error": str(e),
                "timestamp": time.time(),
            })

        await asyncio.sleep(0.05)

        # Save to DB
        report = state["final_report"]
        scores = report.get("scores", {})
        db = SessionLocal()
        try:
            record = RiskAnalysis(
                user_id=user.id,
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
            report["db_id"] = record.id
        finally:
            db.close()

        yield _sse_event("analysis_complete", report)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
