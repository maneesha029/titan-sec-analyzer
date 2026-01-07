import streamlit as st
from core.engine import fetch_company_data, get_financial_trends

st.set_page_config(page_title="Titan SEC 2026", layout="wide")

st.title("🔱 Titan SEC Analyzer")
st.caption("Live Forensic Analysis of SEC Filings")

# Sidebar for Input
ticker = st.sidebar.text_input("Enter Ticker (e.g., NVDA, TSLA, AAPL)", value="NVDA").upper()

if st.sidebar.button("Run Intelligence Audit"):
    with st.spinner(f"Accessing EDGAR Servers for {ticker}..."):
        company, filing = fetch_company_data(ticker)
        
        if company:
            st.header(f"{company.name} Analysis")
            
            # Display Key Metadata
            col1, col2, col3 = st.columns(3)
            col1.metric("CIK", company.cik)
            col2.metric("Industry", company.industry)
            col3.write(f"**Latest Filing:** {filing.filing_date}")

            # Display Revenue Chart
            st.subheader("Revenue Performance (Live XBRL)")
            revenue_data = get_financial_trends(ticker)
            if not revenue_data.empty:
                #st.line_chart(revenue_data.set_index('end')['val'])
                st.write(revenue_data)
                st.write(revenue_data.columns)

        else:
            st.error("Company not found. Please check the Ticker.")

# ... existing imports ...
revenue_data = get_financial_trends(ticker)
st.write(revenue_data.columns)
st.write("DEBUG: revenue_data")
st.write(revenue_data)

st.write("DEBUG: columns")
st.write(list(revenue_data.columns))



if not revenue_data.empty:
    st.subheader("📈 Revenue Growth (Standardized)")
    # Streamlit can display this new dataframe format directly
    st.dataframe(revenue_data)
else:
    st.warning("Could not extract standardized financial data for this ticker.")