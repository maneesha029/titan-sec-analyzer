import yfinance as yf
import pandas as pd

def get_forward_returns(ticker, years, horizon_months=6):
    """
    Compute forward returns for given years.
    Returns a DataFrame with columns: year, forward_return (%)
    """
    stock = yf.Ticker(ticker)
    prices = stock.history(period="max")["Close"]
    prices.index = pd.to_datetime(prices.index)

    returns = {}

    for year in years:
        start_date = pd.to_datetime(f"{year}-12-31")
        end_date = start_date + pd.DateOffset(months=horizon_months)

        try:
            start_price = prices.loc[prices.index <= start_date].iloc[-1]
            end_price = prices.loc[prices.index >= end_date].iloc[0]
            returns[year] = (end_price - start_price) / start_price * 100
        except Exception:
            returns[year] = None

    return pd.DataFrame(
        list(returns.items()),
        columns=["year", "forward_return"],
    )


def validate_risk_signal(
    risk_df,
    ticker,
    risk_column="uncertainty_score",
    horizon_months=6,
):
    """Joins risk history and forward returns, then computes simple correlation."""
    if risk_df is None or risk_df.empty or risk_column not in risk_df.columns:
        return {
            "observations": 0,
            "correlation": None,
            "message": "Risk frame is empty or missing the requested column.",
        }

    returns_df = get_forward_returns(
        ticker=ticker,
        years=risk_df["year"].tolist(),
        horizon_months=horizon_months,
    )
    merged = risk_df[["year", risk_column]].merge(returns_df, on="year", how="inner")
    merged = merged.dropna()

    if len(merged) < 3:
        return {
            "observations": int(len(merged)),
            "correlation": None,
            "message": "Not enough overlap between risk and return history.",
        }

    correlation = float(merged[risk_column].corr(merged["forward_return"]))
    return {
        "observations": int(len(merged)),
        "correlation": round(correlation, 4),
        "dataset": merged.to_dict(orient="records"),
    }


def link_risk_to_returns(risk_ts, returns):
    combined = []

    for year, risk in risk_ts.items():
        if risk is None or year not in returns:
            continue

        combined.append({
            "year": year,
            "uncertainty": risk["uncertainty_score"],
            "forward_return": returns[year]
        })

    return combined
