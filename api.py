from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from services.alerts import build_regime_shift_alert, send_email_alert, send_slack_alert
from services.alpha_signal import analyze_risk_to_return, build_risk_return_dataset
from services.benchmarking import build_multi_ticker_comparison, build_sector_benchmark
from services.filing_rag import answer_question_over_filings
from utils.risk_shift import build_risk_timeseries


app = FastAPI(title="Titan SEC Analyzer API", version="0.1.0")


class BenchmarkRequest(BaseModel):
    ticker: str = Field(..., description="Anchor ticker")
    peers: list[str] = Field(default_factory=list, description="Peer tickers for benchmark")


class RAGRequest(BaseModel):
    ticker: str
    question: str
    years: list[int] | None = None
    top_k: int = 5


class AlertRequest(BaseModel):
    ticker: str
    recipients: list[str] = Field(default_factory=list)
    min_abs_change: int = 5
    send_email: bool = False
    send_slack: bool = False


@app.get("/")
def root() -> dict:
    return {
        "name": "Titan SEC Analyzer API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/risk/timeseries")
def risk_timeseries(ticker: str) -> dict:
    df = build_risk_timeseries(ticker=ticker)
    return {
        "ticker": ticker.upper(),
        "rows": 0 if df is None else int(len(df)),
        "data": [] if df is None else df.to_dict(orient="records"),
    }


@app.get("/risk/compare")
def risk_compare(tickers: str) -> dict:
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    frame = build_multi_ticker_comparison(ticker_list)
    return {
        "tickers": ticker_list,
        "rows": int(len(frame)),
        "data": frame.to_dict(orient="records"),
    }


@app.post("/risk/benchmark")
def risk_benchmark(request: BenchmarkRequest) -> dict:
    return build_sector_benchmark(anchor_ticker=request.ticker, peer_tickers=request.peers)


@app.get("/alpha/correlation")
def alpha_correlation(
    ticker: str,
    risk_column: str = "uncertainty_score",
    horizon_months: int = 6,
) -> dict:
    dataset = build_risk_return_dataset(
        ticker=ticker,
        risk_column=risk_column,
        horizon_months=horizon_months,
    )
    analysis = analyze_risk_to_return(dataset, risk_column=risk_column)

    return {
        "ticker": ticker.upper(),
        "dataset": dataset.to_dict(orient="records"),
        "analysis": analysis,
    }


@app.post("/ai/ask")
def ai_ask(request: RAGRequest) -> dict:
    return answer_question_over_filings(
        ticker=request.ticker,
        question=request.question,
        years=request.years,
        top_k=request.top_k,
    )


@app.post("/alerts/notify")
def alerts_notify(request: AlertRequest) -> dict:
    payload = build_regime_shift_alert(
        ticker=request.ticker,
        min_abs_change=request.min_abs_change,
    )

    if payload is None:
        return {
            "ticker": request.ticker.upper(),
            "triggered": False,
            "message": "No regime shift exceeded threshold.",
        }

    email_sent = send_email_alert(payload, request.recipients) if request.send_email else False
    slack_sent = send_slack_alert(payload) if request.send_slack else False

    return {
        "triggered": True,
        "payload": payload,
        "email_sent": email_sent,
        "slack_sent": slack_sent,
    }
