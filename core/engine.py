import pandas as pd
from edgar import Company, set_identity
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure your email is in your .env file
set_identity(os.getenv("SEC_IDENTITY", "your.email@example.com"))

def fetch_company_data(ticker):
    """Fetches the company object and the latest 10-K filing"""
    try:
        company = Company(ticker)
        filing = company.get_filings(form="10-K").latest()
        return company, filing
    except Exception as e:
        print(f"Error fetching company: {e}")
        return None, None

def get_financial_trends(ticker):
    """
    Fetches standardized financial metrics (Revenue) 
    using the new 2026 edgartools API.
    """
    try:
        company = Company(ticker)
        # The new way: Get the financials object
        financials = company.get_financials()
        
        # Get the income statement specifically
        income_statement = financials.income_statement()
        
        # Convert the statement to a dataframe
        df = income_statement.to_dataframe()
        
        # Clean the data for the chart: 
        # We want rows that represent Total Revenue or Sales
        # Note: 'concept' is the column name in the new version
        revenue_df = df[df['concept'].str.contains('Revenue|Sales', case=False, na=False)]
        
        return revenue_df
    except Exception as e:
        print(f"Data extraction failed: {e}")
        return pd.DataFrame() # Return empty if fails
    
def extract_risk_factors(filing):
    """
    Extracts Item 1A (Risk Factors) using edgartools 3.x Data Objects.
    """
    try:
        # Convert the raw filing into a 'TenK' data object
        tenk = filing.obj()
        
        # Access the standardized 'risk_factors' attribute
        risks = tenk.risk_factors
        
        # Return a snippet or the full text (we'll start with 2000 chars for the UI)
        return risks[:4000] if risks else "Risk factors section not found."
    except Exception as e:
        return f"Error extracting risks: {str(e)}"
    
from sec_edgar_downloader import Downloader
import os

def download_10k_filings(ticker, years):
    dl = Downloader("YourName", "your@email.com")
    base_dir = f"data/filings/{ticker}"
    os.makedirs(base_dir, exist_ok=True)

    for year in years:
        try:
            dl.get(
                "10-K",
                ticker,
                after=f"{year}-01-01",
                before=f"{year}-12-31"
            )
        except:
            continue
def extract_and_save_item_1a(ticker, year, filing_text):
    save_dir = f"data/filings/{ticker}"
    os.makedirs(save_dir, exist_ok=True)

    if filing_text is None or len(filing_text.strip()) < 500:
        return False

    file_path = f"{save_dir}/{year}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(filing_text)

    return True
