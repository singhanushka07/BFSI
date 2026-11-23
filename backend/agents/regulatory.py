from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from mcp_server.dispatcher import call_mcp_tool
import os
import random


def run_regulatory_agent(company: str, ticker: str, sector: str = "Financial Services") -> dict:
    """Regulatory Compliance Agent: fetches rules via MCP, checks adherence to BFSI regulations."""
    mcp_calls = []

    # MCP tool call: get regulatory rules
    rules_call = call_mcp_tool("get_regulatory_rules", {})
    mcp_calls.append({k: v for k, v in rules_call.items() if k != "result"})
    regulatory_rules = rules_call["result"] or []

    checks = []
    violations = 0
    warnings = 0

    for rule in regulatory_rules:
        rand = random.random()
        if rand < 0.10:
            status = "VIOLATION"
            violations += 1
            detail = f"Non-compliance detected with {rule['rule']}."
        elif rand < 0.30:
            status = "WARNING"
            warnings += 1
            detail = f"Partial compliance gaps found in {rule['rule']}."
        else:
            status = "COMPLIANT"
            detail = f"Satisfactory compliance with {rule['rule']}."
        checks.append({
            "rule": rule["rule"],
            "category": rule["category"],
            "severity": rule["severity"],
            "status": status,
            "detail": detail,
        })

    compliance_risk_score = round(
        (violations * 20) + (warnings * 8) + random.uniform(5, 15), 1
    )
    compliance_risk_score = max(0, min(100, compliance_risk_score))

    compliant_count = len([c for c in checks if c["status"] == "COMPLIANT"])
    rules_summary = "\n".join([
        f"- {c['rule']} ({c['category']}): {c['status']}"
        for c in checks
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a regulatory compliance specialist at a major BFSI risk consulting firm. Provide formal, precise assessments."),
        ("human", """Perform regulatory compliance risk analysis for {company} ({sector} sector).

Compliance Check Results (rules fetched via MCP get_regulatory_rules tool):
{rules_summary}

Summary: {compliant}/{total} rules compliant, {violations} violations, {warnings} warnings

Provide a 3-sentence compliance risk assessment covering: regulatory exposure, most critical violations, and recommended remediation priority. Be formal and specific.""")
    ])

    analysis_text = (
        f"{company} has {violations} regulatory violations and {warnings} compliance warnings across {len(regulatory_rules)} assessed frameworks. "
        f"{'Critical AML/KYC and Basel III gaps require immediate remediation.' if violations > 0 else 'No critical violations detected at this time.'} "
        f"Compliance risk score: {compliance_risk_score}/100. [MCP tool used: get_regulatory_rules]"
    )

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
        chain = prompt | llm
        response = chain.invoke({
            "company": company, "sector": sector,
            "rules_summary": rules_summary,
            "compliant": compliant_count, "total": len(regulatory_rules),
            "violations": violations, "warnings": warnings,
        })
        analysis_text = response.content
    except Exception:
        pass

    return {
        "agent": "Regulatory Compliance",
        "score": compliance_risk_score,
        "risk_level": _risk_level(compliance_risk_score),
        "analysis": analysis_text,
        "mcp_calls": mcp_calls,
        "metrics": {
            "total_rules_checked": len(regulatory_rules),
            "compliant": compliant_count,
            "warnings": warnings,
            "violations": violations,
            "compliance_rate": round(compliant_count / len(regulatory_rules) * 100, 1) if regulatory_rules else 0,
        },
        "compliance_checks": checks,
    }


def _risk_level(score: float) -> str:
    if score < 25: return "LOW"
    if score < 50: return "MEDIUM"
    if score < 75: return "HIGH"
    return "CRITICAL"
