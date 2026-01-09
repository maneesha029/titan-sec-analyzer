import re

RISK_KEYWORDS = {
    "regulatory": ["regulation", "compliance", "government", "law"],
    "litigation": ["lawsuit", "litigation", "legal", "court"],
    "supply_chain": ["supplier", "manufacturing", "shortage"],
    "uncertainty": ["may", "could", "might", "uncertain"]
}

def score_risks(text):
    if text is None:
        return None

    text = text.lower()
    scores = {}

    for risk, words in RISK_KEYWORDS.items():
        scores[risk] = sum(text.count(w) for w in words)

    scores["uncertainty_score"] = scores["uncertainty"]
    return scores

