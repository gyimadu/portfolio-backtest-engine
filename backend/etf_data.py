"""
ETF data management module
handles fetching, caching, and cleaning of price data from yfinance
"""

import pandas as pd
import yfinance as yf
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

from config import (
    DATA_DIR,
    ETF_PRICES_FILE,
    YAHOO_FINANCE_CACHE_DAYS,
    SUPPORTED_ETFS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETFDataManager:
    """manages etf price data fetching, caching, and cleaning"""
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cache_file = self.data_dir / ETF_PRICES_FILE

    def get_etf_data(self, symbols: List[str], start_date: date, end_date: date) -> pd.DataFrame:
        """get etf price data from yfinance"""
        # validate symbols
        valid_symbols = [s for s in symbols if s.upper() in SUPPORTED_ETFS]
        if not valid_symbols:
            raise ValueError("No valid ETF symbols provided")
        
        # check fro fresh cached data
        if self._is_cache_fresh(valid_symbols, start_date, end_date):
            logger.info("Using cached ETF Data")
            return self._load_cached_data(valid_symbols, start_date, end_date)
        
        # download fresh price data
        logger.info(f"Downloading fresh ETF data for {valid_symbols}")
        data = self._download_etf_data(valid_symbols, start_date, end_date)
        
        # save to cache
        self._cache_data(data)
        
        return data
    
    def _is_cache_fresh(self, symbols: List[str], start_date: date, end_date: date) -> bool:
        """check if cached data is fresh enough"""
        if not self.cache_file.exists():
            return False
        
        # check if cache is too old
        cache_age = datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
        if cache_age.days > YAHOO_FINANCE_CACHE_DAYS:
            return False
        
        # check if cached data covers our date range
        try:
            cached_data = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)
            cached_symbols = [col.split('_')[0] for col in cached_data.columns if '_close' in col]
            
            if not all(symbol in cached_symbols for symbol in symbols):
                return False
            
            if cached_data.index.min() > pd.Timestamp(start_date) or cached_data.index.max() < pd.Timestamp(end_date):
                return False
                
            return True
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return False
        
        
        