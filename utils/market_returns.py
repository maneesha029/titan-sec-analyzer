import yfinance as yf
import pandas as pd

def get_forward_returns(ticker, years):
    """
    Compute forward 6-month returns for given years.
    Returns a DataFrame with columns: year, forward_return (%)
    """
    stock = yf.Ticker(ticker)
    prices = stock.history(period="max")['Close']
    prices.index = pd.to_datetime(prices.index)

    returns = {}

    for year in years:
        start_date = f"{year}-12-31"
        end_date = pd.to_datetime(start_date) + pd.DateOffset(months=6)

        try:
            start_price = prices.loc[prices.index <= start_date].iloc[-1]
            end_price = prices.loc[prices.index >= end_date].iloc[0]
            returns[year] = (end_price - start_price) / start_price * 100
        except:
            returns[year] = None

    return pd.DataFrame(list(returns.items()), columns=["year", "forward_return"])

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
