from __future__ import annotations

import os
import re

import pandas as pd

NEGATIONS = {"no", "not", "without", "never", "neither", "nor"}

# -------------------------------
# CONFIG
# -------------------------------
RISK_KEYWORDS = {
    "uncertainty": ["uncertain", "uncertainty", "may", "might", "could", "risk"],
    "regulatory": ["regulation", "regulatory", "law", "laws", "compliance", "government"],
    "litigation": ["litigation", "lawsuit", "legal proceeding", "settlement", "court"],
    "cyber": ["cyber", "security breach", "data breach", "hack", "attack"],
    "supply_chain": ["supply", "supplier", "manufacturing", "shortage", "logistics"],
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", (text or "").lower())


def _normalize_keyword(keyword: str) -> tuple[str, ...]:
    return tuple(_tokenize(keyword))


def score_with_negation(text: str, keywords: list[str], negation_window: int = 3) -> float:
    """
    Scores keyword hits but discounts matches when preceded by a negation
    in the prior three-word window.
    """
    words = _tokenize(text)
    if not words:
        return 0.0

    score = 0.0
    normalized_keywords = [_normalize_keyword(keyword) for keyword in keywords if keyword]

    for keyword_parts in normalized_keywords:
        if not keyword_parts:
            continue

        span = len(keyword_parts)
        if span > len(words):
            continue

        for index in range(len(words) - span + 1):
            if tuple(words[index : index + span]) != keyword_parts:
                continue

            prior_window = words[max(0, index - negation_window) : index]
            if any(token in NEGATIONS for token in prior_window):
                score -= 0.5
            else:
                score += 1.0

    return max(score, 0.0)


def compute_tfidf_risk_scores(filing_texts: dict[int, str]) -> pd.DataFrame:
    """
    Computes TF-IDF weighted risk scores per year.
    """
    if not filing_texts:
        return pd.DataFrame()

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError as exc:  # pragma: no cover - exercised only when sklearn is missing
        raise ImportError("scikit-learn is required for TF-IDF risk scoring.") from exc

    years = sorted(filing_texts.keys())
    corpus = [filing_texts[year] for year in years]

    rows: dict[str, list[float]] = {"year": years}
    for dimension, keywords in RISK_KEYWORDS.items():
        vectorizer = TfidfVectorizer(vocabulary=keywords, ngram_range=(1, 2), lowercase=True)
        matrix = vectorizer.fit_transform(corpus).toarray()
        rows[f"{dimension}_tfidf_score"] = matrix.sum(axis=1).tolist()

    return pd.DataFrame(rows)

# -------------------------------
# LOAD MULTI-YEAR FILINGS
# -------------------------------
def load_risk_filings(company: str):
    """
    Loads saved Item 1A text files from:
    data/<COMPANY>/*.txt
    """
    base_path = os.path.join("data", "sec", company.upper())

    filings = {}

    if not os.path.exists(base_path):
        return filings

    for file in sorted(os.listdir(base_path)):
        if file.endswith(".txt"):
            year = os.path.splitext(file)[0]
            with open(os.path.join(base_path, file), "r", encoding="utf-8") as f:
                filings[year] = f.read().lower()

    return filings
# -------------------------------
# BUILD RISK METRICS TABLE
# -------------------------------
def build_risk_timeseries(ticker, filings_dir="data/sec"):
    company_path = os.path.join(filings_dir, ticker.upper())

    if not os.path.exists(company_path):
        return pd.DataFrame()

    filing_texts: dict[int, str] = {}

    for file in sorted(os.listdir(company_path)):
        if not file.endswith(".txt"):
            continue

        year = int(os.path.splitext(file)[0])
        with open(os.path.join(company_path, file), "r", encoding="utf-8") as f:
            text = f.read().strip().lower()

        if text:
            filing_texts[year] = text

    if not filing_texts:
        return pd.DataFrame()

    rows = []
    for year in sorted(filing_texts.keys()):
        text = filing_texts[year]
        word_count = len(text.split())
        rows.append(
            {
                "year": year,
                "word_count": word_count,
                "uncertainty_score": score_with_negation(text, RISK_KEYWORDS["uncertainty"]),
                "regulatory_risk": score_with_negation(text, RISK_KEYWORDS["regulatory"]),
                "litigation_risk": score_with_negation(text, RISK_KEYWORDS["litigation"]),
                "cyber_risk": score_with_negation(text, RISK_KEYWORDS["cyber"]),
                "supply_chain_risk": score_with_negation(text, RISK_KEYWORDS["supply_chain"]),
            }
        )

    base_df = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)

    try:
        tfidf_df = compute_tfidf_risk_scores(filing_texts).sort_values("year").reset_index(drop=True)
    except ImportError:
        return base_df

    return base_df.merge(tfidf_df, on="year", how="left")





# -------------------------------
# RISK SHIFT CALCULATION
# -------------------------------
def compute_risk_shift(df: pd.DataFrame):
    """
    Computes year-over-year risk deltas
    """
    if df.empty or len(df) < 2:
        return pd.DataFrame()

    shift_df = df.copy()
    for col in df.columns:
        if col == "year":
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            shift_df[f"{col}_change"] = df[col].diff()

    return shift_df


def compute_aggregate_risk_delta(df: pd.DataFrame) -> pd.Series:
    change_cols = [col for col in df.columns if col.endswith("_change") and col != "year_change"]
    if not change_cols:
        return pd.Series(dtype=float)

    return df[change_cols].abs().sum(axis=1)


# -------------------------------
# HIGH-LEVEL SUMMARY (UI READY)
# -------------------------------
def summarize_latest_shift(df: pd.DataFrame):
    if df.empty or len(df) < 2:
        return {}

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    deltas = {
        "uncertainty": latest["uncertainty_score"] - prev["uncertainty_score"],
        "regulatory": latest["regulatory_risk"] - prev["regulatory_risk"],
        "litigation": latest["litigation_risk"] - prev["litigation_risk"],
        "cyber": latest["cyber_risk"] - prev["cyber_risk"],
        "supply_chain": latest["supply_chain_risk"] - prev["supply_chain_risk"],
    }

    dominant_risk = max(deltas, key=lambda k: abs(deltas[k]))

    return {
        "latest_year": int(latest["year"]),
        "year": int(latest["year"]),
        "dominant_risk": dominant_risk,
        "direction": "Increase" if deltas[dominant_risk] > 0 else "Decrease",
        "net_change": int(deltas[dominant_risk]),
        "all_changes": {k: int(v) for k, v in deltas.items()}
    }


def compute_risk_percent_change(df: pd.DataFrame):
    """
    Computes percentage change in risk metrics YoY
    """
    if df.empty or len(df) < 2:
        return pd.DataFrame()

    pct_df = df.copy()
    for col in df.columns:
        if col != "year":
            pct_df[col + "_pct_change"] = df[col].pct_change() * 100

    return pct_df
