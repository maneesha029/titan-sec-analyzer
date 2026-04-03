# Titan SEC Analyzer v2.0.0

## AI-Powered SEC 10-K Risk Intelligence Platform

[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-3776AB.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Overview

Titan SEC Analyzer turns unstructured SEC 10-K filings into actionable risk signals. Instead of reading long filings line by line, the app extracts Item 1A risk factors, tracks how those risks evolve over time, and highlights the biggest changes in a company’s risk profile.

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
| Risk Signal Extraction | NLP-driven scoring for uncertainty, regulatory, litigation, cyber, and supply chain risks |
| Multi-Year Shift Detection | Quantifies how risk profiles change year-over-year |
| Risk-Alpha Correlation | Maps risk changes to forward stock returns |
| Filing RAG | Ask natural language questions across filing years with LLM context |
| Peer Benchmarking | Compare risk profiles against sector competitors |

## Data Format

Local filing text is stored in this format:

```text
data/sec/<TICKER>/<YEAR>.txt
```

## Screenshots

### Dashboard Overview

![Titan SEC Analyzer dashboard](assets/screenshots/dashboard-overview.png)

### Multi-Year Risk Evolution

![Titan SEC Analyzer risk chart](assets/screenshots/multi-year-risk-evolution.png)

### AI Risk Interpretation

![Titan SEC Analyzer AI interpretation](assets/screenshots/ai-risk-interpretation.png)

If you have not added the image files yet, place them in `assets/screenshots/` using the file names above.

## Troubleshooting

| Issue | Solution |
|------|----------|
| SEC request fails | Verify `SEC_IDENTITY` in `.env` |
| No multi-year data | Add text files to `data/sec/<TICKER>/` |
| AI explanations missing | Set `OPENAI_API_KEY` or use fallback mode |
| Streamlit date error | Convert `datetime.date` values to strings before calling `st.metric()` |

## Credits

Titan SEC Analyzer was built for SEC filing analysis and risk intelligence research.

## License

See [`LICENSE`](LICENSE) for details.
