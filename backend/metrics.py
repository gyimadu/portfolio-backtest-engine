import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import date
import logging

from config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR
logger = logging.getLogger(__name__)

class PortfolioMetrics:
    """calculate portfolio performance metrics"""
    def __init__(self, portfolio_values: pd.Series, benchmark_values: Optional[pd.Series] = None) -> None:
        self.portfolio_values = portfolio_values
        self.benchmark_values = benchmark_values
        self.returns = self._calculate_returns(portfolio_values)

        if benchmark_values is not None:
            self.benchmark_returns = self._calculate_returns(benchmark_values)
        else:
            self.benchmark_returns = None

    def _calculate_all_metrics(self) -> Dict:
        """calculate all performance metrics"""
        metrics = {}

        metrics.update(self._calculate_return_metrics())
        metrics.update(self._calculate_risk_metrics())
        metrics.update(self._calculate_drawdown_metrics())
        metrics.update(self._calculate_rolling_metrics())

        if self.benchmark_returns is not None:
            metrics.update(self._calculate_benchmark_metrics())
        return metrics

    def _calculate_returns(self, values: pd.Series) -> pd.Series:
        """calculate daily returns"""
        return values.pct_change().dropna()

    def _calculate_return_metrics(self) -> Dict:
        total_return = (self.portfolio_values.iloc[-1] / self.portfolio_values.iloc[0] - 1)
        years = len(self.portfolio_values) / TRADING_DAYS_PER_YEAR
        # compound annual growth rate
        cagr = (self.portfolio_values.iloc[-1] / self.portfolio_values.iloc[0]) ** (1/years) - 1
        # annualized return 
        annualized_return = self.returns.mean() * TRADING_DAYS_PER_YEAR
        # best and worst periods
        rolling_1y = self.portfolio_values.pct_change(periods=TRADING_DAYS_PER_YEAR).dropna()
        best_year = rolling_1y.max()
        worst_year = rolling_1y.min()

        return {
            'total_return': total_return,
            'cagr': cagr,
            'annualized_return': annualized_return,
            'best_year': best_year,
            'worst_year': worst_year,
            'total_days': len(self.portfolio_values),
            'years': years,
        }

    def _calculate_risk_metrics(self) -> Dict:
        # standard deviation
        volatility = self.returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
        # sharpe ratio
        excess_returns = self.returns - (RISK_FREE_RATE / TRADING_DAYS_PER_YEAR)
        sharpe_ratio = excess_returns
