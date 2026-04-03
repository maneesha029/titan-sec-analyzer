# ================================
# Titan SEC Analyzer 2026 - ENHANCED
# ================================
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import time
from dotenv import load_dotenv
import yfinance as yf

load_dotenv()

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Titan SEC Analyzer",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
body { background-color: #0F2F51; }
.metric-container {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #30363d;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

from core.engine import fetch_company_data, get_financial_trends
from services.risk_pipeline import run_risk_pipeline
from utils.risk_shift import (
    build_risk_timeseries,
    compute_risk_shift,
    compute_risk_percent_change,
    summarize_latest_shift
)
from services.risk_explainer import explain_risk_shift

def has_openai_key() -> bool:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key and key != "your_openai_key_here")

# Session state
if "company" not in st.session_state:
    st.session_state.company = None
if "filing" not in st.session_state:
    st.session_state.filing = None
if "revenue_data" not in st.session_state:
    st.session_state.revenue_data = None

# ================================
# SIDEBAR
# ================================
st.sidebar.title("Titan SEC Analyzer")
st.sidebar.markdown("---")

DEFAULT_TICKERS = ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "INTC"]

ticker = st.sidebar.selectbox(
    "Select Company",
    DEFAULT_TICKERS,
    index=DEFAULT_TICKERS.index("NVDA")
)

custom_ticker = st.sidebar.text_input("Or custom ticker", "").upper()
if custom_ticker:
    ticker = custom_ticker

if has_openai_key():
    st.sidebar.success("🤖 AI Mode: Enabled")
else:
    st.sidebar.warning("⚠️ AI Mode: Fallback (set OPENAI_API_KEY)")

# ================================
# MAIN BUTTON
# ================================
if st.sidebar.button("🚀 Run Intelligence Audit", type="primary", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("📡 Connecting to EDGAR...")
    progress_bar.progress(25)
    st.session_state.company, st.session_state.filing = fetch_company_data(ticker)
    
    status_text.text("💰 Fetching financial trends...")
    progress_bar.progress(50)
    st.session_state.revenue_data = get_financial_trends(ticker)
    
    status_text.text("🔍 Building risk signals...")
    progress_bar.progress(75)
    
    status_text.text("✅ Complete!")
    progress_bar.progress(100)
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    st.success(f"✅ {ticker} analysis complete")

company = st.session_state.company
filing = st.session_state.filing
revenue_data = st.session_state.revenue_data

# ================================
# COMPANY DISPLAY
# ================================
if company:
    st.header(f"🏢 {company.name}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("CIK", company.cik)
    col2.metric("Industry", company.industry if company.industry else "N/A")
    col3.metric("Latest Filing", str(filing.filing_date) if filing else "N/A")
    
    if revenue_data is not None and not revenue_data.empty:
        with st.expander("📊 Financial Trends"):
            st.dataframe(revenue_data, use_container_width=True)

# ================================
# RISK ANALYSIS
# ================================
if filing:
    result = run_risk_pipeline(filing)
    
    with st.expander("📄 Raw Risk Factors (Item 1A)"):
        st.text(result["raw_text"][:5000] + "..." if len(result["raw_text"]) > 5000 else result["raw_text"])
    
    st.subheader("📊 Current Risk Signals")
    c1, c2, c3 = st.columns(3)
    c1.metric("🔮 Uncertainty", result["features"]["uncertainty_score"])
    c2.metric("⚖️ Regulatory", result["features"]["regulatory_risk_score"])
    c3.metric("⚔️ Litigation", result["features"]["litigation_risk_score"])
    
    # ================================
    # MULTI-YEAR ANALYSIS
    # ================================
    st.markdown("---")
    st.subheader("📈 Multi-Year Risk Evolution")
    
    try:
        risk_ts = build_risk_timeseries(ticker=ticker, filings_dir="data/sec")
        
        if risk_ts is not None and not risk_ts.empty:
            # Year filter
            min_y, max_y = int(risk_ts['year'].min()), int(risk_ts['year'].max())
            yr_range = st.slider("Year Range", min_y, max_y, (min_y, max_y), key="year_slider")
            risk_ts = risk_ts[(risk_ts['year'] >= yr_range[0]) & (risk_ts['year'] <= yr_range[1])]
            
            # Time series chart
            st.line_chart(risk_ts.set_index("year")[["uncertainty_score", "regulatory_risk", "litigation_risk"]])
            
            # Radar chart
            if len(risk_ts) >= 2:
                latest = risk_ts.iloc[-1]
                avg = risk_ts.iloc[:-1].mean()
                radar_df = pd.DataFrame({
                    'Risk': ['Uncertainty', 'Regulatory', 'Litigation'],
                    'Current': [latest['uncertainty_score'], latest['regulatory_risk'], latest['litigation_risk']],
                    'Historical Avg': [avg['uncertainty_score'], avg['regulatory_risk'], avg['litigation_risk']]
                })
                fig = px.line_polar(radar_df, r='Current', theta='Risk', line_close=True, 
                                    title=f"{ticker} Risk Profile vs Historical")
                st.plotly_chart(fig, use_container_width=True)
            
            # Shift tables
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**YoY Absolute Change**")
                st.dataframe(compute_risk_shift(risk_ts), use_container_width=True)
            with col_b:
                st.write("**YoY % Change**")
                st.dataframe(compute_risk_percent_change(risk_ts).round(2), use_container_width=True)
            
            # Download
            csv = risk_ts.to_csv(index=False)
            st.download_button("📥 Download Risk Data", csv, f"{ticker}_risk.csv", "text/csv")
            
            # AI Summary
            summary = summarize_latest_shift(risk_ts)
            if summary:
                st.subheader("🤖 AI Risk Interpretation")
                explanation = explain_risk_shift(summary, company.name if company else ticker)
                st.info(explanation)
                
    except Exception as e:
        st.error(f"Risk analysis error: {e}")
else:
    st.info("👈 Select a ticker and click 'Run Intelligence Audit' to begin")