from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import RiskEngine


TICKERS = ["AAPL", "MSFT", "GOOG", "JPM", "XOM"]
FORWARD_DAYS = 90
DATA_DIR = Path("data/sec")
OUTPUT_DIR = Path("docs")


def _load_prices(ticker: str) -> pd.Series:
    frame = yf.download(
        ticker,
        start="2018-01-01",
        end="2025-01-01",
        auto_adjust=True,
        progress=False,
    )
    if frame is None or frame.empty or "Close" not in frame:
        return pd.Series(dtype=float)

    close = frame["Close"]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return close


def _forward_return(filing_year: int, prices: pd.Series) -> float | None:
    filing_date = pd.Timestamp(f"{filing_year}-03-15")
    forward_date = filing_date + pd.Timedelta(days=FORWARD_DAYS)

    try:
        p0_value = prices.asof(filing_date)
        p90_value = prices.asof(forward_date)
        if isinstance(p0_value, pd.Series):
            p0_value = p0_value.iloc[0]
        if isinstance(p90_value, pd.Series):
            p90_value = p90_value.iloc[0]
        p0 = float(p0_value)
        p90 = float(p90_value)
    except Exception:
        return None

    if not np.isfinite(p0) or not np.isfinite(p90) or p0 == 0:
        return None

    return float((p90 - p0) / p0)


def _safe_correlation(x: pd.Series, y: pd.Series, kind: str = "pearson") -> tuple[float, float]:
    if x.nunique(dropna=True) < 2 or y.nunique(dropna=True) < 2:
        return float("nan"), float("nan")

    if kind == "pearson":
        r, p = pearsonr(x, y)
    else:
        r, p = spearmanr(x, y)

    return float(r), float(p)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, float | int | str]] = []
    delta_columns = [
        "uncertainty_score_change",
        "regulatory_risk_change",
        "litigation_risk_change",
        "cyber_risk_change",
        "supply_chain_risk_change",
    ]

    for ticker in TICKERS:
        ticker_dir = DATA_DIR / ticker
        if not ticker_dir.exists():
            print(f"{ticker}: no local filing data, skipping")
            continue

        engine = RiskEngine(ticker=ticker, filings_dir=str(DATA_DIR))
        risk_df = engine.get_risk_history()
        if risk_df is None or risk_df.empty:
            print(f"{ticker}: insufficient risk history, skipping")
            continue

        available_delta_columns = [col for col in delta_columns if col in risk_df.columns]
        if not available_delta_columns:
            print(f"{ticker}: no delta columns, skipping")
            continue

        if "word_count" not in risk_df.columns:
            print(f"{ticker}: missing word_count, skipping")
            continue

        prices = _load_prices(ticker)
        if prices.empty:
            print(f"{ticker}: no price history, skipping")
            continue

        for _, row in risk_df.iterrows():
            year = int(row["year"])
            forward_return = _forward_return(year, prices)
            if forward_return is None:
                continue

            delta_values = {}
            for col in available_delta_columns:
                value = row[col]
                delta_values[col] = float(abs(value)) if pd.notna(value) else np.nan

            aggregate_delta = float(sum(value for value in delta_values.values() if np.isfinite(value)))
            normalized_aggregate_delta = float((aggregate_delta / max(float(row["word_count"]), 1.0)) * 1000.0)
            result = {
                "ticker": ticker,
                "year": year,
                "aggregate_risk_delta": aggregate_delta,
                "normalized_aggregate_risk_delta": normalized_aggregate_delta,
                "word_count": float(row["word_count"]),
                "forward_return_90d": forward_return,
            }
            result.update(delta_values)
            results.append(result)

    df = pd.DataFrame(results)
    if df.empty:
        raise SystemExit("No overlapping risk and return observations were found.")

    csv_path = OUTPUT_DIR / "risk_alpha_results.csv"
    df.to_csv(csv_path, index=False)

    pearson_r, pearson_p = _safe_correlation(df["normalized_aggregate_risk_delta"], df["forward_return_90d"], kind="pearson")
    spearman_r, spearman_p = _safe_correlation(df["normalized_aggregate_risk_delta"], df["forward_return_90d"], kind="spearman")

    print("=" * 60)
    print("Risk-Alpha Correlation Results")
    print(f"Tickers: {TICKERS}")
    print(f"Observations: {len(df)}")
    print(f"Pearson  r = {pearson_r:.3f}, p = {pearson_p:.3f}")
    print(f"Spearman r = {spearman_r:.3f}, p = {spearman_p:.3f}")
    print()

    if np.isfinite(pearson_p) and pearson_p < 0.05:
        direction = "negative" if pearson_r < 0 else "positive"
        print(
            f"Significant {direction} correlation: higher risk shifts {'precede lower' if pearson_r < 0 else 'precede higher'} forward returns."
        )
    elif np.isnan(pearson_p):
        print("Correlation is undefined because one of the series is constant across the five-ticker sample.")
    else:
        print(f"No significant correlation (p={pearson_p:.3f}); risk shifts do not show a stable predictive relationship here.")

    print()
    print("Per-dimension correlations:")
    for col in available_delta_columns:
        sub = df[[col, "forward_return_90d"]].dropna()
        if len(sub) < 3:
            continue
        dim_r, dim_p = _safe_correlation(sub[col], sub["forward_return_90d"], kind="pearson")
        if np.isnan(dim_p):
            print(f"  {col:28} r=nan, p=nan (constant input)")
        else:
            print(f"  {col:28} r={dim_r:.3f}, p={dim_p:.3f}")

    fig, ax = plt.subplots(figsize=(8, 5))
    for ticker in df["ticker"].unique():
        sub = df[df["ticker"] == ticker]
        ax.scatter(sub["normalized_aggregate_risk_delta"], sub["forward_return_90d"], label=ticker, s=60)

    if df["normalized_aggregate_risk_delta"].nunique(dropna=True) > 1 and df["forward_return_90d"].nunique(dropna=True) > 1:
        slope, intercept = np.polyfit(df["normalized_aggregate_risk_delta"], df["forward_return_90d"], 1)
        x_line = np.linspace(df["normalized_aggregate_risk_delta"].min(), df["normalized_aggregate_risk_delta"].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", alpha=0.5, label=f"r={pearson_r:.3f}, p={pearson_p:.3f}")
    else:
        ax.set_xlabel("Normalized Aggregate Risk Delta (per 1,000 words)")
        ax.set_ylabel("90-Day Forward Return")
        ax.set_title("Risk Profile Shifts vs Forward Equity Returns")
        ax.axhline(0, color="gray", linewidth=0.5)
        ax.legend()
        plot_path = OUTPUT_DIR / "risk_alpha_scatter.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        print(f"Saved {csv_path}")
        print(f"Saved {plot_path}")
        print("=" * 60)
        return

    ax.set_xlabel("Normalized Aggregate Risk Delta (per 1,000 words)")
    ax.set_ylabel("90-Day Forward Return")
    ax.set_title("Risk Profile Shifts vs Forward Equity Returns")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.legend()
    plt.tight_layout()

    plot_path = OUTPUT_DIR / "risk_alpha_scatter.png"
    plt.savefig(plot_path, dpi=150)
    print(f"Saved {csv_path}")
    print(f"Saved {plot_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
