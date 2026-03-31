from __future__ import annotations

import os


def _fallback_explanation(summary: dict, company_name: str) -> str:
    risk = summary["dominant_risk"]
    direction = summary["direction"]
    year = summary["year"]

    explanations = {
        "supply_chain": "manufacturing concentration, supplier dependency, and geopolitical constraints",
        "regulatory": "increased regulatory scrutiny, export controls, or compliance requirements",
        "litigation": "heightened legal exposure or intellectual property disputes",
        "cyber": "rising cybersecurity threats and data protection risks",
        "uncertainty": "macroeconomic volatility and unpredictable market conditions",
    }

    reason = explanations.get(risk, "multiple operational and market factors")
    return (
        f"In {year}, {company_name}'s risk profile {direction.lower()}d primarily due to "
        f"elevated {risk.replace('_', ' ')} exposure, likely driven by {reason}."
    )


def _openai_explanation(summary: dict, company_name: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_key_here":
        return None

    try:
        from langchain_openai import ChatOpenAI

        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)

        prompt = (
            "You are a financial risk analyst. Write 2-3 concise sentences with no hype.\n"
            f"Company: {company_name}\n"
            f"Year: {summary['year']}\n"
            f"Dominant risk: {summary['dominant_risk']}\n"
            f"Direction: {summary['direction']}\n"
            f"Net change: {summary['net_change']}\n"
            f"All deltas: {summary.get('all_changes', {})}\n"
            "Explain plausible drivers and investor implications with careful language."
        )
        response = llm.invoke(prompt)
        content = getattr(response, "content", "")
        if isinstance(content, list):
            content = " ".join([str(part) for part in content])
        text = str(content).strip()
        return text or None
    except Exception:
        return None


def explain_risk_shift(summary: dict, company_name: str):
    """Converts risk shift metrics into natural language insight."""
    if not summary:
        return "Insufficient historical data to generate risk explanation."

    ai_text = _openai_explanation(summary, company_name)
    if ai_text:
        return ai_text
    return _fallback_explanation(summary, company_name)
