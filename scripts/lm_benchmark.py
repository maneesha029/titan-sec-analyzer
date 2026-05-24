from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.risk_shift import build_risk_timeseries


def load_lm_dictionary(path: str = "data/LM_dictionary.csv") -> dict[str, set[str]]:
    lm_path = Path(path)
    if not lm_path.exists():
        raise FileNotFoundError(
            "LM dictionary not found. Download the Loughran-McDonald master dictionary to data/LM_dictionary.csv."
        )

    lm = pd.read_csv(lm_path)
    return {
        "uncertainty": set(lm[lm["Uncertainty"] > 0]["Word"].str.lower()),
        "litigation": set(lm[lm["Litigious"] > 0]["Word"].str.lower()),
        "negative": set(lm[lm["Negative"] > 0]["Word"].str.lower()),
    }


def score_with_lm(text: str, lm_dict: dict[str, set[str]]) -> dict[str, float]:
    words = text.lower().split()
    total = max(len(words), 1)
    return {
        f"lm_{dimension}": sum(1 for word in words if word in terms) / total
        for dimension, terms in lm_dict.items()
    }


def _load_yearly_texts(ticker: str, data_dir: str = "data/sec") -> dict[int, str]:
    base_dir = Path(data_dir) / ticker.upper()
    texts: dict[int, str] = {}

    if not base_dir.exists():
        return texts

    for path in sorted(base_dir.glob("*.txt")):
        try:
            year = int(path.stem)
        except ValueError:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            texts[year] = text

    return texts


def benchmark_titan_vs_lm(titan_scores: pd.DataFrame, lm_scores: pd.DataFrame) -> dict[str, dict[str, float]]:
    results: dict[str, dict[str, float]] = {}
    if titan_scores.empty or lm_scores.empty:
        return results

    joined = titan_scores.join(lm_scores, how="inner")
    if joined.empty:
        return results

    comparisons = [
        ("uncertainty_score", "lm_uncertainty", "uncertainty_correlation_with_LM"),
        ("litigation_risk", "lm_litigation", "litigation_correlation_with_LM"),
        ("uncertainty_score", "lm_negative", "uncertainty_vs_negative_LM"),
    ]

    for left_col, right_col, label in comparisons:
        if left_col not in joined.columns or right_col not in joined.columns:
            continue
        if len(joined[[left_col, right_col]].dropna()) < 2:
            continue

        r, p = pearsonr(joined[left_col], joined[right_col])
        results[label] = {"r": round(float(r), 3), "p": round(float(p), 3)}

    return results


def _safe_pearson(left: pd.Series, right: pd.Series) -> dict[str, float] | None:
    pair = pd.concat([left, right], axis=1).dropna()
    if len(pair) < 2 or pair.iloc[:, 0].nunique() < 2 or pair.iloc[:, 1].nunique() < 2:
        return None

    r, p = pearsonr(pair.iloc[:, 0], pair.iloc[:, 1])
    return {"r": round(float(r), 3), "p": round(float(p), 3), "n": int(len(pair))}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark Titan risk scores against the Loughran-McDonald lexicon.")
    parser.add_argument("tickers", nargs="*", default=["AAPL", "MSFT", "GOOG", "JPM", "XOM"])
    parser.add_argument("--lm-dictionary", default="data/LM_dictionary.csv")
    parser.add_argument("--data-dir", default="data/sec")
    parser.add_argument("--output-dir", default="docs")
    args = parser.parse_args()

    lm_dict = load_lm_dictionary(args.lm_dictionary)
    combined_rows = []
    per_ticker_results = {}

    for ticker in args.tickers:
        texts = _load_yearly_texts(ticker, data_dir=args.data_dir)
        if not texts:
            continue

        titan_df = build_risk_timeseries(ticker, filings_dir=args.data_dir).set_index("year")
        lm_rows = []
        for year, text in texts.items():
            row = score_with_lm(text, lm_dict)
            row["year"] = year
            row["ticker"] = ticker
            lm_rows.append(row)

        lm_df = pd.DataFrame(lm_rows).set_index("year")
        if titan_df.empty or lm_df.empty:
            continue

        joined = titan_df.join(lm_df.drop(columns=["ticker"]), how="inner")
        if joined.empty:
            continue

        joined = joined.reset_index()
        joined["ticker"] = ticker
        combined_rows.append(joined)

        per_ticker_results[ticker] = {
            "uncertainty_vs_lm_uncertainty": _safe_pearson(joined["uncertainty_score"], joined["lm_uncertainty"]),
            "litigation_vs_lm_litigious": _safe_pearson(joined["litigation_risk"], joined["lm_litigation"]),
            "uncertainty_vs_lm_negative": _safe_pearson(joined["uncertainty_score"], joined["lm_negative"]),
            "observations": int(len(joined)),
        }

    if not combined_rows:
        raise SystemExit("No overlapping Titan and LM observations were found.")

    all_joined = pd.concat(combined_rows, ignore_index=True)
    results = {
        "combined": {
            "uncertainty_vs_lm_uncertainty": _safe_pearson(all_joined["uncertainty_score"], all_joined["lm_uncertainty"]),
            "litigation_vs_lm_litigious": _safe_pearson(all_joined["litigation_risk"], all_joined["lm_litigation"]),
            "uncertainty_vs_lm_negative": _safe_pearson(all_joined["uncertainty_score"], all_joined["lm_negative"]),
            "observations": int(len(all_joined)),
        },
        "per_ticker": per_ticker_results,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "lm_benchmark_results.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    csv_path = output_dir / "lm_benchmark_results.csv"
    all_joined.to_csv(csv_path, index=False)

    print(json.dumps(results, indent=2))
    print(f"Saved {output_path}")
    print(f"Saved {csv_path}")


if __name__ == "__main__":
    main()
