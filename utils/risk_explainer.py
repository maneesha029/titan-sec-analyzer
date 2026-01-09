def build_risk_prompt(company, summary):
    """
    Converts structured risk shift data into an LLM-ready prompt
    """

    return f"""
You are a financial risk analyst.

Company: {company}

Year Analyzed: {summary['year']}

Key Risk Shifts:
- Dominant Risk Driver: {summary['dominant_risk']}
- Direction of Change: {summary['direction']}
- Net Risk Change: {summary['net_change']}

Write a concise, professional explanation (2–3 sentences)
explaining WHY this risk shift may have occurred and
what it could imply for investors.
Avoid speculation beyond reasonable financial logic.
"""
def generate_risk_explanation(prompt: str):
    """
    Temporary deterministic explanation layer.
    Can be replaced with OpenAI / Claude / Gemini later.
    """

    return (
        "The company's risk profile shows a noticeable shift driven primarily "
        "by increased exposure in the dominant risk category. "
        "This change may reflect evolving operational and regulatory pressures, "
        "which could influence future financial performance and investor sentiment."
    )