# ================================
# Titan SEC Analyzer 2026
# ================================

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.risk_shift import (
    build_risk_timeseries,
    compute_risk_shift,
    compute_risk_percent_change,
    summarize_latest_shift
)

st.set_page_config(
    page_title="Titan SEC Analyzer",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded"
)




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

# ================================
# RISK SHIFT ANALYSIS (YoY)
# ================================

st.subheader("📉 Risk Shift Analysis (Year-over-Year)")

risk_ts = build_risk_timeseries(
    ticker=ticker,
    filings_dir="data/filings"
)

if risk_ts is not None and not risk_ts.empty:
    shift_df = compute_risk_shift(risk_ts)
    pct_df = compute_risk_percent_change(risk_ts)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Absolute Risk Change**")
        st.dataframe(shift_df)

    with col2:
        st.write("**% Risk Change**")
        st.dataframe(pct_df)

    st.subheader("🧠 Latest Risk Interpretation")
    st.info(summarize_latest_shift(shift_df))

else:
    st.warning("Not enough historical filings to compute risk shift.")

st.markdown("---")
st.subheader("📊 Multi-Year Risk Shift Intelligence")

risk_df = build_risk_timeseries(ticker)

if not risk_df.empty:
    st.caption("Historical risk signal extracted from Item 1A (10-K filings)")
    st.dataframe(risk_df, use_container_width=True)

    shift_df = compute_risk_shift(risk_df)
    st.subheader("📉 Absolute Risk Change (YoY)")
    st.dataframe(shift_df, use_container_width=True)

    pct_df = compute_risk_percent_change(risk_df)
    st.subheader("📈 Risk Growth Rate (%)")
    st.dataframe(pct_df.round(2), use_container_width=True)

    summary = summarize_latest_shift(risk_df)

    st.subheader(f"⚠️ Latest Risk Delta ({summary['year']})")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Uncertainty", summary["uncertainty_shift"])
    c2.metric("Regulatory", summary["regulatory_shift"])
    c3.metric("Cyber", summary["cyber_shift"])
    c4.metric("Supply Chain", summary["supply_chain_shift"])
else:
    st.info("No historical risk filings found.")



if filing:
    result = run_risk_pipeline(filing)

    with st.expander("📄 Raw Risk Factors"):
        st.write(result["raw_text"])

    st.subheader("📊 Quantified Risk Signals")

    st.metric("Total Risk Words", result["features"]["word_count"])
    st.metric("Uncertainty Score", result["features"]["uncertainty_score"])
    st.metric("Regulatory Risk", result["features"]["regulatory_risk_score"])
    st.metric("Litigation Risk", result["features"]["litigation_risk_score"])
