# ================================
# Titan SEC Analyzer 2026
# ================================

import sys
import os
import streamlit as st
st.set_page_config(
    page_title="Titan SEC Analyzer",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from core.engine import fetch_company_data, get_financial_trends, extract_risk_factors
from services.risk_pipeline import run_risk_pipeline


# ================================
# SESSION STATE INITIALIZATION
# ================================
if "company" not in st.session_state:
    st.session_state.company = None

if "filing" not in st.session_state:
    st.session_state.filing = None

if "revenue_data" not in st.session_state:
    st.session_state.revenue_data = None

# ================================
# PAGE CONFIG & TITLE
# ================================
st.set_page_config(page_title="Titan SEC 2026", layout="wide")
st.title("🔱 Titan SEC Analyzer")
st.caption("Live Forensic Analysis of SEC Filings")

# ================================
# SIDEBAR INPUT
# ================================
ticker = st.sidebar.text_input(
    "Enter Ticker (e.g., NVDA, TSLA, AAPL)", value="NVDA"
).upper()

# ================================
# BUTTON: FETCH DATA
# ================================
if st.sidebar.button("Run Intelligence Audit"):
    with st.spinner(f"Accessing EDGAR Servers for {ticker}..."):
        # Fetch company and latest filing
        st.session_state.company, st.session_state.filing = fetch_company_data(ticker)
        # Fetch revenue / financial trends
        st.session_state.revenue_data = get_financial_trends(ticker)

# ================================
# LOCAL VARIABLES (SAFE TO USE)
# ================================
company = st.session_state.company
filing = st.session_state.filing
revenue_data = st.session_state.revenue_data

# ================================
# COMPANY & FINANCIAL DISPLAY
# ================================
if company:
    st.header(f"{company.name} Analysis")

    # Display Key Metadata
    col1, col2, col3 = st.columns(3)
    col1.metric("CIK", company.cik)
    col2.metric("Industry", company.industry)
    col3.write(f"**Latest Filing:** {filing.filing_date}")

    # Display Revenue Chart
    st.subheader("Revenue Performance (Live XBRL)")
    if revenue_data is not None and not revenue_data.empty:
        st.dataframe(revenue_data)
    else:
        st.warning("Could not extract standardized financial data for this ticker.")

else:
    st.info("Run Intelligence Audit to load company data.")

# ================================
# RISK ANALYSIS SECTION (Item 1A)
# ================================

from services.risk_pipeline import run_risk_pipeline

...

if filing:
    result = run_risk_pipeline(filing)

    with st.expander("📄 Raw Risk Factors"):
        st.write(result["raw_text"])

    st.subheader("📊 Quantified Risk Signals")

    st.metric("Total Risk Words", result["features"]["word_count"])
    st.metric("Uncertainty Score", result["features"]["uncertainty_score"])
    st.metric("Regulatory Risk", result["features"]["regulatory_risk_score"])
    st.metric("Litigation Risk", result["features"]["litigation_risk_score"])
