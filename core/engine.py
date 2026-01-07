from edgar import set_identity, Company
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()
set_identity(os.getenv("SEC_IDENTITY"))

def fetch_company_data(ticker):
    """Fetches live company info and latest 10-K filing"""
    try:
        company = Company(ticker)
        # Get the latest 10-K (Annual Report)
        filing = company.get_filings(form="10-K").latest()
        return company, filing
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None, None

def get_financial_trends(ticker):
    """Pulls XBRL facts (Revenue, etc.) for Plotly charts"""
    company = Company(ticker)
    facts = company.get_facts().to_pandas()
    # 2026 Hack: Filter for 'Revenues' to keep it simple for now
    return facts[facts['fact'] == 'Revenues']