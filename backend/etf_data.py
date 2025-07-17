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
        
    def _download_etf_data(self, symbols: List[str], start_date: date, end_date: date) -> pd.DataFrame:
        """download etf price data from yfinance"""
        all_data = {}

        for symbol in symbols:
            try:
                logger.info(f"Downloading data for {symbol}")
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date)

                if data.empty:
                    logger.warning(f"No data found for {symbol}")
                    continue

                # clean the data
                data = self._clean_data(data, symbol)
                all_data[symbol] = data

            except Exception as e:
                logger.error(f"Error downloading {symbol}: {e}")
                continue

        if not all_data:
            raise ValueError("No ETF data could be downloaded")
        
        # combine all ETF data into single dataframe
        combined_data = self._combine_etf_data(all_data)
        return combined_data
    
    def _clean_etf_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """clean and prepare ETF data"""
        # forward fill missing values
        data = data.fillna(method='ffill')

        # remove any remaining NaN values
        data = data.dropna()

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns for {symbol}: {missing_cols}")

        data.columns = [f"{symbol}_{col}" for col in data.columns]

        return data
    
    def _combine_etf_data(self, all_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """combine etf data from different symbols into single dataframe"""
        start_dates = [df.index.min() for df in all_data.values()]
        end_dates = [df.index.max() for df in all_data.values()]

        common_start = max(start_dates)
        common_end = min(end_dates)

        combined = pd.DataFrame(index=pd.date_range(common_start, common_end, freq='D'))

        for symbol, data in all_data.items():
           daily_data = data.resample('D').last()

           for col in data.columns:
               combined[col] = daily_data[col]

        combined = combined.dropna()

        return combined
    
    def _cache_data(self, data: pd.DataFrame) -> None:
        """cache etf data to file"""
        try:
            data.to_csv(self.cache_file)
            logger.info(f"ETF data cached to {self.cache_file}")
        except Exception as e:
            logger.error(f"Error caching ETF data: {e}")

    def _load_cached_data(self, symbols: List[str], start_date: date, end_date: date) -> pd.DataFrame:
        """load and filter cached etf data"""
        data = pd.read_csv(self.cache_file, index_col=0, parse_dates=True)

        data = data[(data.index >= pd.Timestamp(start_date)) & (data.index <= pd.Timestamp(end_date))]

        symbol_cols = []
        for symbol in symbols:
            symbol_cols.extend([col for col in data.columns if col.startswith(f"{symbol}_")])

        data = data[symbol_cols]

        return data
    
    def get_etf_info(self, symbol: str) -> Optional[Dict]:
        """get basic information about each etf"""
        if symbol.upper() not in SUPPORTED_ETFS:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'symbol': symbol.upper(),
                'name': SUPPORTED_ETFS[symbol.upper()],
                'sector': info.get('sector', 'N/A'),
                'expense_ratio': info.get('expenseRatio', 'N/A'),
                'aum': info.get('totalAssets', 'N/A'),
                'inception_date': info.get('inceptionDate', 'N/A'),
                'category': info.get('category', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error getting info for {symbol}: {e}")
            return None
        
def get_etf_price(symbols: List[str], start_date: date, end_date: date) -> pd.DataFrame:
    manager = ETFDataManager()
    return manager.get_etf_data(symbols, start_date, end_date)
        
        