from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from utils.risk_shift import (
    build_risk_timeseries,
    compute_aggregate_risk_delta,
    compute_risk_shift,
    summarize_latest_shift,
)


@dataclass
class RiskEngine:
    ticker: str
    filings_dir: str = "data/sec"

    def get_risk_timeseries(self) -> pd.DataFrame:
        return build_risk_timeseries(ticker=self.ticker, filings_dir=self.filings_dir)

    def get_risk_history(self) -> pd.DataFrame:
        risk_df = self.get_risk_timeseries()
        if risk_df is None or risk_df.empty:
            return pd.DataFrame()

        return compute_risk_shift(risk_df)

    def get_aggregate_risk_delta(self) -> pd.Series:
        risk_history = self.get_risk_history()
        if risk_history is None or risk_history.empty:
            return pd.Series(dtype=float)

        return compute_aggregate_risk_delta(risk_history)

    def get_latest_summary(self) -> dict:
        risk_df = self.get_risk_timeseries()
        if risk_df is None or risk_df.empty:
            return {}

        return summarize_latest_shift(risk_df)
