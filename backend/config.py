"""
configuration setting for the portfolio backtesting engine
central place for all default values and constants
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class ContributionFrequency(Enum):
    # how often the user contributes to the portfolio
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"

class RebalanceFrequency(Enum):
    # how often the user rebalances the portfolio
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NONE = "none"

# default date range for simulation
DEFAULT_START_DATE = datetime(2000, 1, 1)
DEFAULT_END_DATE = datetime(2025, 6, 31)

# default portfolio settings
DEFAULT_INTIAL_INVESTMENT = 10000
DEFAULT_MONTHLY_CONTRIBUTION = 500
DEFAULT_CONTRIBUTION_FREQUENCY = ContributionFrequency.MONTHLY
DEFAULT_REBALANCE_FREQUENCY = RebalanceFrequency.NONE

# data settings
YAHOO_FINANCE_CACHE_DAYS = 7
DATA_DIR = "data"
ETF_PRICES_FILE = "etf_prices.csv"
EVENTS_FILE = "events.json"

# performance calculation settings
RISK_FREE_RATE = 0.02
TRADING_DAYS_PER_YEAR = 252

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_DEBUG = True

# supported ETFs
SUPPORTED_ETFS = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust",
    "VOO": "Vanguard S&P 500 ETF",
    "VOOG": "Vanguard S&P 500 Growth ETF",
    "VOOV": "Vanguard S&P 500 Value ETF",
    "VWO": "Vanguard FTSE Emerging Markets ETF",
    "EEM": "iShares MSCI Emerging Markets ETF",
    "IWM": "iShares Russell 2000 ETF",
    "GLD": "SPDR Gold Trust",
    "SLV": "iShares Silver Trust",
    "USO": "United States Oil Fund, LP",
    "BIL": "iShares U.S. Long Bond ETF",
    "VGT": "Vanguard Information Technology ETF",
    "VTI": "Vanguard Total Stock Market ETF",
    "VXUS": "Vanguard Total International Stock Market ETF",
    "VEA": "Vanguard FTSE All-World ex-US Small-Cap ETF",
    "AGG": "iShares Core US Aggregate Bond ETF",
    "BND": "iShares Core US Aggregate Bond ETF",
    "XLF": "SPDR S&P Financials ETF",
    "XLE": "SPDR S&P Energy ETF",
    "XLI": "SPDR S&P Industrials ETF",
    "VNQ": "Vanguard Real Estate ETF",
    "VHT": "Vanguard Health Care ETF",
    "VCR": "Vanguard Consumer Staples ETF",
    "VIG": "Vanguard Dividend Appreciation ETF",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "BNDX": "Vanguard Total International Bond ETF",
}

# default portfolio allocation
DEFAULT_ALLOCATION = {
    "SPY": 0.40,
    "VXUS": 0.20,
    "VNQ": 0.30,
    "BND": 0.10,
}

# event overlay settings
SIGNIFICANT_EVENTS = [
    {"date": "2006-09-15", "event": "Lehman Brothers Bankruptcy", "type": "crisis"},
    {"date": "2009-03-09", "event": "S&P 500 Bottom (Great Recession)", "type": "recovery"},
    {"date": "2020-03-23", "event": "COVID-19 Market Bottom", "type": "crisis"},
    {"date": "2021-01-06", "event": "GameStop Short Squeeze", "type": "volatility"},
    {"date": "2022-01-03", "event": "Fed Rate Hike Cycle Begins", "type": "policy"},
]

def validate_date_range(start_date: date, end_date:date) -> bool:
    """check if date range is reasonable"""
    if start_date >= end_date:
        return False
    if start_date < date(1990, 1, 1):
        return False
    if end_date > datetime.today().date():
        return False
    return True

def validate_allocation(allocation: Dict[str, float]) -> bool:
    """check if allocation sum up to 100%"""
    if not allocation:
        return False
    total = sum(allocation.values())
    return abs(total - 1.0) < 1e-6

def get_etf_symbol(symbol: str) -> Optional[str]:
    """get ETF full name from symbol"""
    return SUPPORTED_ETFS.get(symbol.upper())