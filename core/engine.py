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