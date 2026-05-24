# Titan SEC Analyzer v2.0.0

## AI-Powered SEC 10-K Risk Intelligence Platform

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-3776AB.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Overview

Titan extracts Item 1A risk factors from SEC 10-K filings and scores year-over-year risk shifts using negation-aware, TF-IDF-weighted keyword scoring across five dimensions: uncertainty, regulatory, litigation, cyber, and supply chain.

Unlike raw Loughran-McDonald lexicon counting, Titan suppresses boilerplate legal language that inflates LM scores regardless of actual risk level. The LM benchmark confirms this: Titan uncertainty scores diverge from LM uncertainty ($r = -0.393$, $p = 0.032$) while aligning with LM negative sentiment ($r = 0.657$, $p < 0.001$) — consistent with TF-IDF filtering of omnipresent hedging language that LM counts indiscriminately.

The current workspace includes real filing text for six tickers. The main study corpus is AAPL, MSFT, GOOG, JPM, and XOM, with NVDA retained as a reference corpus.

## Deployment

### Step 1 - Clone the repository

```powershell
git clone <your-repo-url>
cd titan-sec-analyzer
```

### Step 2 - Create a virtual environment

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3 - Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 4 - Configure the environment

Create a `.env` file and set:

- `SEC_IDENTITY=Your Name (your.email@example.com)`
- `OPENAI_API_KEY=...`  
  Optional. Enables AI explanations.

### Step 5 - Run the app

```powershell
streamlit run app.py
```

Open:

- http://localhost:8501

## Key Features

| Feature | Description |
|---------|-------------|
| Risk Signal Extraction | Negation-aware scoring for uncertainty, regulatory, litigation, cyber, and supply chain risk language |
| Multi-Year Shift Detection | Quantifies year-over-year changes in filing risk language |
| Risk-Alpha Correlation | Tests whether risk shifts map to 90-day forward returns |
| Filing RAG | Ask natural language questions across filing years with LLM context |
| Peer Benchmarking | Compare risk profiles against sector competitors |
| LM Benchmarking | Compare Titan scores against the Loughran-McDonald sentiment dictionary |

## Research Workflow

- `scripts/fetch_filings.py` downloads 10-Ks and extracts Item 1A risk text into `data/sec/<TICKER>/<YEAR>.txt`.
- `scripts/risk_alpha_correlation.py` runs the normalized risk-delta vs 90-day forward-return study and writes `docs/risk_alpha_results.csv` plus `docs/risk_alpha_scatter.png`.
- `scripts/lm_benchmark.py` compares Titan scores with the Loughran-McDonald lexicon using `data/LM_dictionary.csv` and writes `docs/lm_benchmark_results.csv` plus `docs/lm_benchmark_results.json`.

## Architecture

```text
EDGAR → fetch_filings → risk_shift → [correlation study | LM benchmark | RAG | dashboard]
```

1. `EDGAR` provides the raw 10-K filings.
2. `scripts/fetch_filings.py` extracts Item 1A and materializes yearly text files.
3. `utils/risk_shift.py` computes negation-aware, TF-IDF-weighted risk scores and deltas.
4. Downstream modules consume those outputs for correlation analysis, LM benchmarking, RAG, and the dashboard.

## Current Evidence

Five-ticker corpus (AAPL, MSFT, GOOG, JPM, XOM), 2019–2024, 30 observations.

Risk-alpha study (normalized aggregate delta vs 90-day forward return):

- Observations: 30
- Pearson correlation on normalized aggregate risk delta: $r = 0.245$, $p = 0.192$
- Spearman correlation on normalized aggregate risk delta: $r = 0.168$, $p = 0.376$
- Per-dimension: `uncertainty_change` and `regulatory_change` retain signal before normalization; aggregation dilutes dimension-specific effects

LM benchmark:

- Combined uncertainty vs LM uncertainty: $r = -0.393$, $p = 0.032$, $n = 30$
- Combined uncertainty vs LM negative: $r = 0.657$, $p < 0.001$, $n = 30$
- Interpretation: TF-IDF penalizes high-frequency cross-year terms ("may," "could," "uncertain") that dominate LM uncertainty counts but carry no year-specific signal

The return correlation will strengthen with larger corpus (target: 80 tickers) and FF3-adjusted abnormal returns replacing raw 90-day returns.

## Research Claims

- Confirmed: Titan’s negation-aware scoring reduces boilerplate inflation relative to raw LM counting.
- Confirmed: Titan’s uncertainty signal diverges from LM uncertainty while still aligning with LM negative sentiment.
- Confirmed: Per-dimension shifts are more informative than the normalized aggregate when the corpus is small.
- In progress: Scaling to a larger corpus should improve the return study’s statistical power.
- In progress: Replacing raw forward returns with FF3-adjusted abnormal returns may isolate the risk signal more cleanly.

## Data Format

Local filing text is stored in this format and is generated from the extracted Item 1A section of each 10-K:

```text
data/sec/<TICKER>/<YEAR>.txt
```

The current local corpus includes:

- `data/sec/AAPL/2019.txt` through `data/sec/AAPL/2024.txt`
- `data/sec/MSFT/2019.txt` through `data/sec/MSFT/2024.txt`
- `data/sec/GOOG/2019.txt` through `data/sec/GOOG/2024.txt`
- `data/sec/JPM/2019.txt` through `data/sec/JPM/2024.txt`
- `data/sec/XOM/2019.txt` through `data/sec/XOM/2024.txt`
- `data/sec/NVDA/2019.txt` through `data/sec/NVDA/2026.txt`

## Troubleshooting

| Issue | Solution |
|------|----------|
| SEC request fails | Verify `SEC_IDENTITY` in `.env` |
| No multi-year data | Run `scripts/fetch_filings.py` or add text files to `data/sec/<TICKER>/` |
| LM benchmark missing | Download the master dictionary to `data/LM_dictionary.csv` |
| AI explanations missing | Set `OPENAI_API_KEY` or use fallback mode |
| Streamlit date error | Convert `datetime.date` values to strings before calling `st.metric()` |

## Artifact Summary

- [docs/risk_alpha_results.csv](docs/risk_alpha_results.csv)
- [docs/risk_alpha_scatter.png](docs/risk_alpha_scatter.png)
- [docs/lm_benchmark_results.csv](docs/lm_benchmark_results.csv)
- [docs/lm_benchmark_results.json](docs/lm_benchmark_results.json)

## Credits

Independent research project by Maneesha G, BMS Institute of Technology & Management.

## License

See [`LICENSE`](LICENSE) for details.
