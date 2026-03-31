<!-- <div align="center">

<img src="https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
<img src="https://img.shields.io/badge/EDGAR-SEC%20Data-1a1a2e?style=for-the-badge"/>
<img src="https://img.shields.io/badge/OpenAI-GPT--4o-10a37f?style=for-the-badge&logo=openai&logoColor=white"/>
<img src="https://img.shields.io/badge/Status-Production%20Ready-22c55e?style=for-the-badge"/>

# ? TITAN — SEC Risk Intelligence Platform

### Autonomous AI that reads 10-K filings, quantifies risk, and explains what changed — across years, sectors, and market cycles.

[**?? Live Demo**](https://titan-sec-analyzer.streamlit.app/) • [**?? Sample Report**](docs/sample-report.pdf) • [**?? Docs**](docs/) 

---

</div>

## The Problem This Solves

Every quarter, thousands of 10-K filings are published on SEC EDGAR. Buried inside are risk factor disclosures that reveal **how companies actually see their future** — regulatory headwinds, litigation exposure, supply chain fragility, macroeconomic bets.

Analysts spend days reading these manually. Models trained on price data miss the signal entirely.

**Titan automates forensic risk intelligence** — transforming unstructured SEC text into quantitative signals, detecting regime shifts, and correlating risk evolution with forward market returns.

---

## What It Does

```
SEC EDGAR  ?  Item 1A Risk Factors  ?  Quantified Risk Signals  ?  AI Interpretation  ?  Alpha Insights
```

| Module | Description |
|---|---|
| ?? **EDGAR Ingestion** | Pulls live 10-K filings for any ticker via `edgartools` |
| ?? **Risk Quantification** | Converts prose into 4 signal types: Uncertainty, Regulatory, Litigation, Supply Chain |
| ?? **Regime Detection** | YoY delta analysis to flag structural risk shifts, not just noise |
| ?? **Market Correlation** | Maps risk levels to 6-month forward returns — tests if risk is priced in |
| ?? **AI Interpretation** | GPT-4o explains *why* risk changed, not just *that* it changed |
| ?? **Dominant Risk Intel** | Surfaces the single biggest emerging risk per filing |

---

## Screenshots

> *(Add 2–3 screenshots of your Streamlit app here)*

```
?? Tip: Record a 30-second Loom demo and add the GIF here — it increases README clicks by ~4x
```

---

## Architecture

```
+---------------------------------------------------------+
¦                     TITAN PLATFORM                      ¦
¦                                                         ¦
¦  +----------+    +----------+    +------------------+  ¦
¦  ¦  EDGAR   ¦---?¦  Parser  ¦---?¦  Risk Quantifier ¦  ¦
¦  ¦  Client  ¦    ¦ Item 1A  ¦    ¦  (4 signal types)¦  ¦
¦  +----------+    +----------+    +------------------+  ¦
¦                                           ¦             ¦
¦  +----------------------------------------?----------+ ¦
¦  ¦              Time-Series Engine                   ¦ ¦
¦  ¦   YoY Deltas  •  Regime Shift Detection           ¦ ¦
¦  ¦   Risk vs Forward Returns  •  Sector Benchmarks   ¦ ¦
¦  +---------------------------------------------------+ ¦
¦                           ¦                             ¦
¦  +------------------------?--------------------------+ ¦
¦  ¦              AI Intelligence Layer                ¦ ¦
¦  ¦      GPT-4o Interpretation  •  RAG over Filings  ¦ ¦
¦  +---------------------------------------------------+ ¦
¦                           ¦                             ¦
¦  +------------------------?--------------------------+ ¦
¦  ¦           Streamlit Dashboard (Dark UI)           ¦ ¦
¦  ¦   Charts  •  Risk Cards  •  Filing Comparator     ¦ ¦
¦  +---------------------------------------------------+ ¦
+---------------------------------------------------------+
```

---

## Quickstart

### Prerequisites

```bash
Python 3.10+
OpenAI API Key
```

### Installation

```bash
git clone https://github.com/yourusername/titan-sec-analyzer
cd titan-sec-analyzer
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Run

```bash
streamlit run app.py
```

---

## Usage

```python
# Analyze any ticker — Titan handles the rest
ticker = "NVDA"
years = [2021, 2022, 2023, 2024]

titan = TitanAnalyzer(ticker)
risk_series = titan.build_risk_timeseries(years)
regime_shifts = titan.detect_shifts(risk_series)
intel = titan.ai_interpret(regime_shifts)
```

---

## Risk Signal Framework

Titan extracts 4 quantitative risk signals from raw 10-K text:

| Signal | What It Measures | Example Keywords |
|---|---|---|
| **Uncertainty Index** | Hedging language, forward-looking disclaimers | *may, could, uncertain, estimate* |
| **Regulatory Pressure** | Government, compliance, policy exposure | *regulation, SEC, compliance, legislation* |
| **Litigation Exposure** | Legal proceedings, claims, settlements | *lawsuit, litigation, dispute, indemnification* |
| **Supply Chain Risk** | Third-party dependencies, concentration risk | *supplier, concentration, single-source, delay* |

Each signal is normalized (0–1) and tracked across fiscal years to compute YoY deltas.

---

## Roadmap

- [x] Multi-year risk ingestion
- [x] Regime shift detection
- [x] GPT-4o AI interpretation
- [x] Market return correlation
- [ ] Multi-ticker sector benchmarking
- [ ] Agentic RAG (ask natural language questions over filings)
- [ ] Email/Slack alerts on regime shift detection
- [ ] FastAPI backend for quant pipeline integration
- [ ] Institutional-grade PDF report export

---

## Tech Stack

| Layer | Tech |
|---|---|
| Language | Python 3.10+ |
| SEC Data | `edgartools` (EDGAR + XBRL) |
| NLP/AI | OpenAI GPT-4o |
| Data | `pandas`, `numpy` |
| Frontend | Streamlit (custom dark UI) |
| Visualization | Native Streamlit charts |
| Deployment | Streamlit Community Cloud |

---

## Why This Matters for Markets

Most quantitative signals are derived from price data (momentum, mean reversion) or structured financials (P/E, revenue growth). **Text-based risk signals are underexplored** because they're hard to extract at scale.

Titan demonstrates that:
1. Risk factor language is **systematically measurable**
2. Regime shifts in risk language **precede** market repricing
3. AI can make this signal **actionable**, not just observable

This is the foundation for a new class of alternative data products.

---

## About

Built by **Maneesha G** — [LinkedIn](https://www.linkedin.com/in/maneesha-g-6b29ba353)

*Quantitative Research × AI × Market Intelligence*

---

## Disclaimer

This project is for research and educational purposes only. Not financial advice. SEC filings are public data. Market return data sourced from public APIs.

---

<div align="center">

If this was useful, ? the repo and [connect on LinkedIn](https://www.linkedin.com/in/maneesha-g-6b29ba353).

</div> -->
