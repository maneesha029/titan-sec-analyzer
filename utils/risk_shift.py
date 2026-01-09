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
# BUILD RISK METRICS TABLE
# -------------------------------
def build_risk_timeseries(ticker, filings_dir="data/filings"):
    import os
    import pandas as pd

    company_path = os.path.join(filings_dir, ticker.upper())

    if not os.path.exists(company_path):
        return pd.DataFrame()

    rows = []

    for file in sorted(os.listdir(company_path)):
        if not file.endswith(".txt"):
            continue

        year = int(file.split("_")[0])

        with open(os.path.join(company_path, file), "r", encoding="utf-8") as f:
            text = f.read()

        # 🔐 SAFETY RULE
        if text is None or text.strip() == "":
            continue

        text = text.lower()

        rows.append({
            "year": year,
            "uncertainty_score": text.count("uncertain"),
            "regulatory_risk": text.count("regulat"),
            "litigation_risk": text.count("litigat"),
            "cyber_risk": text.count("cyber"),
            "supply_chain_risk": text.count("supply")
        })

    return pd.DataFrame(rows).sort_values("year")




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

