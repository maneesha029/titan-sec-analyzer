from __future__ import annotations

from typing import Iterable

import pandas as pd

from utils.risk_shift import build_risk_timeseries


def _latest_risk_row(ticker: str, filings_dir: str) -> dict | None:
    df = build_risk_timeseries(ticker=ticker, filings_dir=filings_dir)
    if df is None or df.empty:
        return None

    latest = df.sort_values("year").iloc[-1]
    risk_cols = [
        "uncertainty_score",
        "regulatory_risk",
        "litigation_risk",
        "cyber_risk",
        "supply_chain_risk",
    ]
    composite_score = float(latest[risk_cols].sum())

    return {
        "ticker": ticker.upper(),
        "year": int(latest["year"]),
        "uncertainty_score": float(latest["uncertainty_score"]),
        "regulatory_risk": float(latest["regulatory_risk"]),
        "litigation_risk": float(latest["litigation_risk"]),
        "cyber_risk": float(latest["cyber_risk"]),
        "supply_chain_risk": float(latest["supply_chain_risk"]),
        "composite_risk": composite_score,
    }


def build_multi_ticker_comparison(
    tickers: Iterable[str],
    filings_dir: str = "data/sec",
) -> pd.DataFrame:
    """Builds a latest-year risk snapshot for a set of tickers."""
    rows = []
    for ticker in tickers:
        row = _latest_risk_row(ticker=ticker, filings_dir=filings_dir)
        if row is not None:
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    frame = pd.DataFrame(rows)
    return frame.sort_values(["composite_risk", "ticker"], ascending=[False, True]).reset_index(drop=True)


def build_sector_benchmark(
    anchor_ticker: str,
    peer_tickers: Iterable[str],
    filings_dir: str = "data/sec",
) -> dict:
    """Compares one ticker versus peer risk distribution and returns ranking stats."""
    universe = [anchor_ticker, *peer_tickers]
    snapshot = build_multi_ticker_comparison(universe, filings_dir=filings_dir)

    if snapshot.empty:
        return {
            "ticker": anchor_ticker.upper(),
            "peer_count": 0,
            "message": "No benchmark data found for the provided ticker universe.",
        }

    anchor = snapshot[snapshot["ticker"] == anchor_ticker.upper()]
    if anchor.empty:
        return {
            "ticker": anchor_ticker.upper(),
            "peer_count": int(len(snapshot) - 1),
            "message": "Anchor ticker has no local filing history in data/sec.",
        }

    anchor_score = float(anchor.iloc[0]["composite_risk"])
    peer_scores = snapshot[snapshot["ticker"] != anchor_ticker.upper()]["composite_risk"]

    if peer_scores.empty:
        percentile = 100.0
        z_score = 0.0
    else:
        percentile = float((peer_scores < anchor_score).mean() * 100)
        std = float(peer_scores.std(ddof=0))
        z_score = 0.0 if std == 0 else float((anchor_score - peer_scores.mean()) / std)

    rank = int(snapshot["composite_risk"].rank(method="min", ascending=False)[snapshot["ticker"] == anchor_ticker.upper()].iloc[0])

    return {
        "ticker": anchor_ticker.upper(),
        "as_of_year": int(anchor.iloc[0]["year"]),
        "peer_count": int(len(snapshot) - 1),
        "composite_risk": anchor_score,
        "sector_percentile": round(percentile, 2),
        "z_score": round(z_score, 4),
        "rank_high_risk": rank,
        "snapshot": snapshot.to_dict(orient="records"),
    }
