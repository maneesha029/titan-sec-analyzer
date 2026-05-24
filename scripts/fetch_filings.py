from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path


def _read_filing_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_filing_year(text: str) -> int | None:
    match = re.search(r"FILED AS OF DATE:\s*(\d{8})", text)
    if match:
        return int(match.group(1)[:4])

    match = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d{8})", text)
    if match:
        return int(match.group(1)[:4])

    return None


def _extract_item_1a(text: str) -> str:
    cleaned = html.unescape(re.sub(r"<[^>]+>", " ", text))
    cleaned = re.sub(r"\s+", " ", cleaned)

    start_patterns = [
        r"item\s+1a\.?\s*risk factors",
        r"risk factors",
    ]
    end_pattern = r"item\s+1b\.|item\s+2\.|item\s+3\."

    start_index = -1
    for pattern in start_patterns:
        matches = list(re.finditer(pattern, cleaned, flags=re.IGNORECASE))
        if matches:
            start_index = matches[-1].start()
            break

    if start_index >= 0:
        tail = cleaned[start_index:]
        end_match = re.search(end_pattern, tail, flags=re.IGNORECASE)
        if end_match:
            return tail[: end_match.start()].strip()
        return tail.strip()

    return cleaned.strip()


def _download_filings(ticker: str, year_start: int, year_end: int, company_name: str, email: str) -> None:
    try:
        from sec_edgar_downloader import Downloader
    except ImportError as exc:
        raise SystemExit("sec-edgar-downloader is required. Install requirements first.") from exc

    downloader = Downloader(company_name, email)
    downloader.get("10-K", ticker, after=f"{year_start}-01-01", before=f"{year_end}-12-31")


def _materialize_local_risk_texts(ticker: str, output_root: Path, source_root: Path) -> int:
    ticker_dir = source_root / ticker.upper() / "10-K"
    if not ticker_dir.exists():
        return 0

    output_dir = output_root / ticker.upper()
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for filing_dir in sorted(ticker_dir.iterdir()):
        if not filing_dir.is_dir():
            continue

        submission_file = filing_dir / "full-submission.txt"
        if not submission_file.exists():
            continue

        filing_text = _read_filing_text(submission_file)
        year = _extract_filing_year(filing_text)
        if year is None:
            continue

        risk_text = _extract_item_1a(filing_text)
        if not risk_text:
            continue

        (output_dir / f"{year}.txt").write_text(risk_text, encoding="utf-8")
        written += 1

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Download SEC 10-K filings and extract Item 1A risk text.")
    parser.add_argument("tickers", nargs="*", default=["AAPL", "MSFT", "GOOG", "JPM", "XOM"], help="Tickers to fetch")
    parser.add_argument("--year-start", type=int, default=2019)
    parser.add_argument("--year-end", type=int, default=2024)
    parser.add_argument("--company-name", default=os.getenv("SEC_COMPANY_NAME", "Titan SEC Analyzer"))
    parser.add_argument("--email", default=os.getenv("SEC_IDENTITY", "your.email@example.com"))
    parser.add_argument("--download-root", default="sec-edgar-filings")
    parser.add_argument("--output-root", default="data/sec")
    args = parser.parse_args()

    source_root = Path(args.download_root)
    output_root = Path(args.output_root)

    for ticker in args.tickers:
        _download_filings(ticker, args.year_start, args.year_end, args.company_name, args.email)
        count = _materialize_local_risk_texts(ticker, output_root=output_root, source_root=source_root)
        print(f"{ticker.upper()}: wrote {count} yearly risk text files to {output_root / ticker.upper()}")


if __name__ == "__main__":
    main()
