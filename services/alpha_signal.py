from __future__ import annotations

import numpy as np
import pandas as pd

from utils.market_returns import get_forward_returns
from utils.risk_shift import build_risk_timeseries


def build_risk_return_dataset(
    ticker: str,
    filings_dir: str = "data/sec",
    risk_column: str = "uncertainty_score",
    horizon_months: int = 6,
) -> pd.DataFrame:
    """Joins yearly risk values with forward returns for signal validation."""
    risk_df = build_risk_timeseries(ticker=ticker, filings_dir=filings_dir)
    if risk_df is None or risk_df.empty or risk_column not in risk_df.columns:
        return pd.DataFrame()

    returns_df = get_forward_returns(
        ticker=ticker,
        years=risk_df["year"].tolist(),
        horizon_months=horizon_months,
    )

    merged = risk_df[["year", risk_column]].merge(returns_df, on="year", how="inner")
    merged = merged.dropna(subset=[risk_column, "forward_return"]).sort_values("year")
    return merged.reset_index(drop=True)


def analyze_risk_to_return(
    dataset: pd.DataFrame,
    risk_column: str = "uncertainty_score",
    return_column: str = "forward_return",
) -> dict:
    """Computes directional and linear relationship between risk and future returns."""
    if dataset is None or dataset.empty or len(dataset) < 3:
        return {
            "observations": 0 if dataset is None else int(len(dataset)),
            "message": "Need at least 3 observations for a meaningful signal test.",
        }

    x = dataset[risk_column].astype(float).to_numpy()
    y = dataset[return_column].astype(float).to_numpy()

    corr = float(np.corrcoef(x, y)[0, 1])
    slope, intercept = np.polyfit(x, y, 1)
    y_pred = (slope * x) + intercept
    residual = y - y_pred
    ss_res = float(np.sum(residual**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 0.0 if ss_tot == 0 else float(1 - (ss_res / ss_tot))

    predicts_drawdown = bool(slope < 0 and corr < 0)

    return {
        "observations": int(len(dataset)),
        "correlation": round(corr, 4),
        "beta_slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r_squared": round(r_squared, 4),
        "predicts_drawdown": predicts_drawdown,
        "interpretation": (
            "Higher risk has historically been associated with weaker forward returns."
            if predicts_drawdown
            else "No stable negative risk-to-return relationship detected in this sample."
        ),
    }
