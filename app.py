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
        st.session_state.company, st.session_state.filing = fetch_company_data(ticker)
        st.session_state.revenue_data = get_financial_trends(ticker)

# ================================
# LOCAL VARIABLES
# ================================
company = st.session_state.company
filing = st.session_state.filing
revenue_data = st.session_state.revenue_data

# ================================
# COMPANY & FINANCIAL DISPLAY
# ================================
if company:
    st.header(f"{company.name} Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("CIK", company.cik)
    col2.metric("Industry", company.industry)
    col3.write(f"**Latest Filing:** {filing.filing_date}")

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
if filing:
    result = run_risk_pipeline(filing)

    with st.expander("📄 Raw Risk Factors"):
        st.write(result["raw_text"])

    st.subheader("📊 Quantified Risk Signals")
    c1, c2, c3 = st.columns(3)
    c1.metric("Uncertainty Score", result["features"]["uncertainty_score"])
    c2.metric("Regulatory Risk", result["features"]["regulatory_risk_score"])
    c3.metric("Litigation Risk", result["features"]["litigation_risk_score"])
else:
    st.info("Run Intelligence Audit to analyze risk factors.")

# ================================
# MULTI-YEAR RISK SHIFT INTELLIGENCE
# ================================
st.markdown("---")
st.subheader("📈 Multi-Year Risk Shift Intelligence")

try:
    # Build risk timeseries
    risk_ts = build_risk_timeseries(
        ticker=ticker,
        filings_dir="data/filings"
    )

    if risk_ts is not None and not risk_ts.empty:
        st.caption("Item 1A risk signals extracted across annual filings (10-K)")

        # Multi-year line chart
        st.line_chart(
            risk_ts.set_index("year")[["uncertainty_score", "regulatory_risk", "litigation_risk"]]
        )

        # Risk shift tables
        shift_df = compute_risk_shift(risk_ts)
        pct_df = compute_risk_percent_change(risk_ts)
        
        # -------------------------------
        # STEP 1: RISK vs FORWARD RETURNS
        # -------------------------------
        from utils.market_returns import get_forward_returns

        if not risk_ts.empty:
            # Compute forward 6-month returns for the years we have
            returns_df = get_forward_returns(ticker, risk_ts['year'].tolist())
    
            # Merge returns with risk metrics
            risk_ts_with_returns = risk_ts.merge(returns_df, on="year", how="left")
    
            st.subheader("📈 Risk vs Forward Returns (6M)")
            st.dataframe(risk_ts_with_returns, use_container_width=True)
    
            # Optional: scatter or line chart
            st.subheader("Scatter: Risk Change vs Forward Return")
            st.line_chart(
                risk_ts_with_returns.set_index("year")[["uncertainty_score", "forward_return"]]
            )


        col1, col2 = st.columns(2)
        with col1:
            st.write("**Absolute Year-over-Year Change**")
            st.dataframe(shift_df, use_container_width=True)
        with col2:
            st.write("**Percentage Risk Change (%)**")
            st.dataframe(pct_df.round(2), use_container_width=True)

        # Latest risk summary
        summary = summarize_latest_shift(risk_ts)
        st.markdown(
            f"""
            ### 🧠 Latest Risk Intelligence ({summary['year']})
            • **Dominant Risk Driver:** {summary['dominant_risk']}  
            • **Direction:** {summary['direction']}  
            • **Net Risk Change:** {summary['net_change']:+.2f}
            """
        )

        # ================================
        # FORWARD 6-MONTH RETURNS
        # ================================
        from utils.market_returns import get_forward_returns

        returns_df = get_forward_returns(ticker, risk_ts['year'].tolist())
        risk_ts_with_returns = risk_ts.merge(returns_df, on="year", how="left")

        st.subheader("📈 Risk vs Forward Returns (6M)")
        st.dataframe(risk_ts_with_returns, use_container_width=True)

        # Scatter plot / line chart
        st.subheader("Scatter: Risk Change vs Forward Return")
        st.line_chart(
            risk_ts_with_returns.set_index("year")[["uncertainty_score", "forward_return"]]
        )

    else:
        st.warning("Insufficient historical filings for risk shift analysis.")


except Exception as e:
    st.error(f"Risk shift engine failed: {e}")

