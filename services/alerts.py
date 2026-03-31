from __future__ import annotations

import json
import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

from utils.risk_shift import build_risk_timeseries, summarize_latest_shift


def build_regime_shift_alert(
    ticker: str,
    filings_dir: str = "data/sec",
    min_abs_change: int = 5,
) -> dict | None:
    """Builds an alert payload when latest dominant risk shift breaches threshold."""
    df = build_risk_timeseries(ticker=ticker, filings_dir=filings_dir)
    if df is None or df.empty or len(df) < 2:
        return None

    summary = summarize_latest_shift(df)
    if not summary:
        return None

    net_change = int(summary["net_change"])
    if abs(net_change) < min_abs_change:
        return None

    return {
        "ticker": ticker.upper(),
        "year": int(summary["year"]),
        "dominant_risk": summary["dominant_risk"],
        "direction": summary["direction"],
        "net_change": net_change,
        "all_changes": summary["all_changes"],
        "message": (
            f"{ticker.upper()} regime shift detected in {summary['year']}: "
            f"{summary['dominant_risk']} moved {net_change:+d}."
        ),
    }


def send_slack_alert(payload: dict, webhook_url: str | None = None) -> bool:
    """Sends shift alert to Slack using webhook URL."""
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return False

    try:
        import requests

        response = requests.post(url, json={"text": payload["message"]}, timeout=15)
        return response.status_code < 300
    except Exception:
        return False


def send_email_alert(payload: dict, recipients: Iterable[str]) -> bool:
    """Sends shift alert via SMTP credentials from environment variables."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("ALERT_FROM_EMAIL", smtp_user)

    if not smtp_host or not smtp_user or not smtp_password or not sender:
        return False

    recipient_list = [r.strip() for r in recipients if r and r.strip()]
    if not recipient_list:
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Titan Alert: {payload['ticker']} risk regime shift"
    msg["From"] = sender
    msg["To"] = ", ".join(recipient_list)
    msg.set_content(f"{payload['message']}\n\nDetails:\n{json.dumps(payload, indent=2)}")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as client:
            client.starttls()
            client.login(smtp_user, smtp_password)
            client.send_message(msg)
        return True
    except Exception:
        return False
