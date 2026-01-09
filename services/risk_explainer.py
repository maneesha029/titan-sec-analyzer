def explain_risk_shift(summary: dict, company_name: str):
    """
    Converts risk shift metrics into natural language insight
    """

    if not summary:
        return "Insufficient historical data to generate risk explanation."

    risk = summary["dominant_risk"]
    direction = summary["direction"]
    year = summary["year"]

    explanations = {
        "supply_chain": "manufacturing concentration, supplier dependency, and geopolitical constraints",
        "regulatory": "increased regulatory scrutiny, export controls, or compliance requirements",
        "litigation": "heightened legal exposure or intellectual property disputes",
        "cyber": "rising cybersecurity threats and data protection risks",
        "uncertainty": "macroeconomic volatility and unpredictable market conditions"
    }

    reason = explanations.get(risk, "multiple operational and market factors")

    return (
        f"In {year}, {company_name}'s risk profile {direction.lower()}d primarily due to "
        f"elevated {risk.replace('_', ' ')} exposure, likely driven by {reason}."
    )
