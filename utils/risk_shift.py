import os
from collections import Counter
import pandas as pd

# -------------------------------
# CONFIG
# -------------------------------
RISK_KEYWORDS = {
    "uncertainty": [
        "uncertain", "uncertainty", "may", "might", "could", "risk"
    ],
    "regulatory": [
        "regulation", "regulatory", "law", "laws", "compliance", "government"
    ],
    "litigation": [
        "litigation", "lawsuit", "legal proceeding", "settlement", "court"
    ],
    "cyber": [
        "cyber", "security breach", "data breach", "hack", "attack"
    ],
    "supply_chain": [
        "supply", "supplier", "manufacturing", "shortage", "logistics"
    ],
}

# -------------------------------
# LOAD MULTI-YEAR FILINGS
# -------------------------------
def load_risk_filings(company: str):
    """
    Loads saved Item 1A text files from:
    data/<COMPANY>/*.txt
    """
    base_path = os.path.join("data", "filings", company.upper())

    filings = {}

    if not os.path.exists(base_path):
        return filings

    for file in sorted(os.listdir(base_path)):
        if file.endswith("_10K.txt"):
            year = file.split("_")[0]
            with open(os.path.join(base_path, file), "r", encoding="utf-8") as f:
                filings[year] = f.read().lower()

    return filings


# -------------------------------
# RISK KEYWORD COUNTER
# -------------------------------
def count_risk_keywords(text: str):
    counts = {}

    for category, keywords in RISK_KEYWORDS.items():
        total = 0
        for word in keywords:
            total += text.count(word)
        counts[category] = total

    counts["total_words"] = len(text.split())
    return counts


# -------------------------------
# BUILD RISK METRICS TABLE
# -------------------------------
def build_risk_timeseries(company: str):
    filings = load_risk_filings(company)
    rows = []

    for year, text in filings.items():
        metrics = count_risk_keywords(text)
        metrics["year"] = int(year)
        rows.append(metrics)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("year")
    return df


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
        if col != "year":
            shift_df[col + "_change"] = df[col].diff()

    return shift_df


# -------------------------------
# HIGH-LEVEL SUMMARY (UI READY)
# -------------------------------
def summarize_latest_shift(df: pd.DataFrame):
    if df.empty or len(df) < 2:
        return {}

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    summary = {
        "year": int(latest["year"]),
        "total_risk_change": int(latest["total_words"] - previous["total_words"]),
        "uncertainty_shift": int(latest["uncertainty"] - previous["uncertainty"]),
        "regulatory_shift": int(latest["regulatory"] - previous["regulatory"]),
        "litigation_shift": int(latest["litigation"] - previous["litigation"]),
        "cyber_shift": int(latest["cyber"] - previous["cyber"]),
        "supply_chain_shift": int(latest["supply_chain"] - previous["supply_chain"]),
    }

    return summary

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

