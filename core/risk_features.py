import re
from collections import Counter

from utils.risk_shift import score_with_negation

UNCERTAINTY_WORDS = [
    "may", "might", "could", "potentially", "uncertain", "adverse"
]

REGULATORY_WORDS = [
    "regulation", "regulatory", "compliance", "sec", "government", "law"
]

LITIGATION_WORDS = [
    "litigation", "lawsuit", "court", "claim", "settlement"
]

MACRO_WORDS = [
    "inflation", "interest rate", "recession", "geopolitical"
]

SUPPLY_CHAIN_WORDS = [
    "supplier", "manufacturing", "supply chain", "semiconductor", "chip", "china"
]


def _count_keywords(text, keywords):
    return score_with_negation(text, keywords)


def extract_risk_features(risk_text: str) -> dict:
    if not risk_text or len(risk_text) < 100:
        return {}

    sentences = re.split(r"[.!?]", risk_text)
    words = risk_text.split()

    features = {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": len(words) / max(len(sentences), 1),

        "uncertainty_score": _count_keywords(risk_text, UNCERTAINTY_WORDS),
        "regulatory_risk_score": _count_keywords(risk_text, REGULATORY_WORDS),
        "litigation_risk_score": _count_keywords(risk_text, LITIGATION_WORDS),
        "macro_risk_score": _count_keywords(risk_text, MACRO_WORDS),
        "supply_chain_risk_score": _count_keywords(risk_text, SUPPLY_CHAIN_WORDS),
    }

    return features
