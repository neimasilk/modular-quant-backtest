"""
Fundamental Data Fetcher for Value Investing Strategy

Fetches fundamental metrics from yfinance:
- P/E Ratio (Price to Earnings)
- P/B Ratio (Price to Book)
- P/S Ratio (Price to Sales)
- Debt/Equity Ratio
- ROE (Return on Equity)
- FCF Yield (Free Cash Flow / Market Cap)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List
import time


class FundamentalDataFetcher:
    """
    Fetches fundamental data for stocks from yfinance.

    Note: yfinance provides current fundamental data, not historical.
    For backtesting, we'll use current data and treat it as "point-in-time".
    This is a limitation - true backtesting requires historical fundamental data.
    """

    def __init__(self):
        self.cache = {}
        self.last_fetch = {}

    def get_fundamental_data(self, ticker: str, use_cache: bool = True) -> Dict[str, float]:
        """
        Get all fundamental metrics for a single ticker.

        Args:
            ticker: Stock symbol (e.g., "AAPL")
            use_cache: Whether to use cached results

        Returns:
            Dictionary with fundamental metrics
        """
        if use_cache and ticker in self.cache:
            return self.cache[ticker]

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Handle missing info
            if not info or info is None:
                return self._empty_metrics()

            metrics = {
                'ticker': ticker,
                'pe_ratio': self._get_pe_ratio(info),
                'pb_ratio': self._get_pb_ratio(info),
                'ps_ratio': self._get_ps_ratio(info),
                'debt_to_equity': self._get_debt_to_equity(info),
                'roe': self._get_roe(info),
                'fcf_yield': self._get_fcf_yield(info),
                'market_cap': self._get_market_cap(info),
                'dividend_yield': self._get_dividend_yield(info),
                'current_ratio': self._get_current_ratio(info),
                'earnings_yield': self._get_earnings_yield(info),
            }

            # Add timestamp
            metrics['fetch_date'] = datetime.now().strftime('%Y-%m-%d')

            # Cache the result
            self.cache[ticker] = metrics
            self.last_fetch[ticker] = time.time()

            return metrics

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return self._empty_metrics()

    def get_batch_fundamental_data(
        self,
        tickers: List[str],
        use_cache: bool = True,
        delay: float = 0.5
    ) -> pd.DataFrame:
        """
        Get fundamental data for multiple tickers.

        Args:
            tickers: List of stock symbols
            use_cache: Whether to use cached results
            delay: Delay between requests (seconds)

        Returns:
            DataFrame with fundamental metrics for all tickers
        """
        results = []

        for ticker in tickers:
            print(f"Fetching {ticker}...")
            metrics = self.get_fundamental_data(ticker, use_cache)
            results.append(metrics)

            # Rate limiting
            if not use_cache or ticker not in self.cache:
                time.sleep(delay)

        df = pd.DataFrame(results)
        df = df.set_index('ticker')

        return df

    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics dict (for missing data)."""
        return {
            'ticker': None,
            'pe_ratio': np.nan,
            'pb_ratio': np.nan,
            'ps_ratio': np.nan,
            'debt_to_equity': np.nan,
            'roe': np.nan,
            'fcf_yield': np.nan,
            'market_cap': np.nan,
            'dividend_yield': np.nan,
            'current_ratio': np.nan,
            'earnings_yield': np.nan,
            'fetch_date': None,
        }

    def _get_pe_ratio(self, info: dict) -> Optional[float]:
        """Get P/E ratio."""
        pe = info.get('trailingPE') or info.get('forwardPE')
        return self._safe_float(pe)

    def _get_pb_ratio(self, info: dict) -> Optional[float]:
        """Get P/B ratio."""
        pb = info.get('priceToBook')
        return self._safe_float(pb)

    def _get_ps_ratio(self, info: dict) -> Optional[float]:
        """Get P/S ratio."""
        ps = info.get('priceToSalesTrailing12Months')
        return self._safe_float(ps)

    def _get_debt_to_equity(self, info: dict) -> Optional[float]:
        """Get Debt/Equity ratio."""
        de = info.get('debtToEquity')
        return self._safe_float(de)

    def _get_roe(self, info: dict) -> Optional[float]:
        """Get Return on Equity (ROE)."""
        roe = info.get('returnOnEquity')
        val = self._safe_float(roe)
        # ROE is often stored as percentage (e.g., 15.5 for 15.5%)
        if val is not None and abs(val) > 1:
            val = val / 100
        return val

    def _get_fcf_yield(self, info: dict) -> Optional[float]:
        """Get FCF Yield (Free Cash Flow / Market Cap)."""
        try:
            fcf = info.get('freeCashflow')
            mc = info.get('marketCap')

            if fcf is not None and mc is not None and mc != 0:
                return fcf / mc
            return np.nan
        except:
            return np.nan

    def _get_market_cap(self, info: dict) -> Optional[float]:
        """Get Market Cap."""
        mc = info.get('marketCap')
        return self._safe_float(mc)

    def _get_dividend_yield(self, info: dict) -> Optional[float]:
        """Get Dividend Yield."""
        dy = info.get('dividendYield')
        val = self._safe_float(dy)
        # Dividend yield is often stored as percentage
        if val is not None and abs(val) > 1:
            val = val / 100
        return val

    def _get_current_ratio(self, info: dict) -> Optional[float]:
        """Get Current Ratio (Current Assets / Current Liabilities)."""
        cr = info.get('currentRatio')
        return self._safe_float(cr)

    def _get_earnings_yield(self, info: dict) -> Optional[float]:
        """Get Earnings Yield (inverse of P/E)."""
        pe = self._get_pe_ratio(info)
        if pe and pe > 0:
            return 1.0 / pe
        return np.nan

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float, handling None and invalid values."""
        try:
            if value is None:
                return np.nan
            return float(value)
        except (ValueError, TypeError):
            return np.nan


class ValueScreener:
    """
    Screens stocks based on value investing criteria.
    """

    def __init__(self, fetcher: FundamentalDataFetcher = None):
        self.fetcher = fetcher or FundamentalDataFetcher()

    def screen(
        self,
        tickers: List[str],
        max_pe: float = 15.0,
        max_pb: float = 1.5,
        max_debt_to_equity: float = 0.5,
        min_roe: float = 0.15,
        require_positive_fcf: bool = True
    ) -> pd.DataFrame:
        """
        Screen stocks by value criteria.

        Args:
            tickers: List of stock symbols
            max_pe: Maximum P/E ratio
            max_pb: Maximum P/B ratio
            max_debt_to_equity: Maximum debt/equity ratio
            min_roe: Minimum ROE (as decimal, e.g., 0.15 for 15%)
            require_positive_fcf: Require positive free cash flow

        Returns:
            DataFrame with passing stocks
        """
        df = self.fetcher.get_batch_fundamental_data(tickers)

        # Apply filters
        mask = pd.Series(True, index=df.index)

        if max_pe is not None:
            mask &= (df['pe_ratio'] <= max_pe) | (df['pe_ratio'].isna())

        if max_pb is not None:
            mask &= (df['pb_ratio'] <= max_pb) | (df['pb_ratio'].isna())

        if max_debt_to_equity is not None:
            mask &= (df['debt_to_equity'] <= max_debt_to_equity) | (df['debt_to_equity'].isna())

        if min_roe is not None:
            mask &= (df['roe'] >= min_roe) | (df['roe'].isna())

        if require_positive_fcf:
            mask &= (df['fcf_yield'] > 0) | (df['fcf_yield'].isna())

        return df[mask].copy()

    def score_stocks(
        self,
        tickers: List[str],
        pe_weight: float = 0.3,
        pb_weight: float = 0.3,
        roe_weight: float = 0.2,
        fcf_weight: float = 0.2
    ) -> pd.DataFrame:
        """
        Score stocks by value metrics (lower score = better value).

        Args:
            tickers: List of stock symbols
            pe_weight: Weight for P/E score
            pb_weight: Weight for P/B score
            roe_weight: Weight for ROE score (inverted)
            fcf_weight: Weight for FCF yield score (inverted)

        Returns:
            DataFrame with scores and rankings
        """
        df = self.fetcher.get_batch_fundamental_data(tickers)

        # Normalize each metric (0-1 scale, lower is better for P/E, P/B)
        scores = pd.DataFrame(index=df.index)

        # P/E score (lower is better)
        if 'pe_ratio' in df.columns:
            pe_max = df['pe_ratio'].quantile(0.95)  # Handle outliers
            pe_min = df['pe_ratio'].quantile(0.05)
            pe_valid = df['pe_ratio'].between(pe_min, pe_max)
            scores['pe_score'] = np.where(
                pe_valid,
                (df['pe_ratio'] - pe_min) / (pe_max - pe_min),
                df['pe_ratio'] / pe_max
            )
            scores['pe_score'] = scores['pe_score'].fillna(0.5)
        else:
            scores['pe_score'] = 0.5

        # P/B score (lower is better)
        if 'pb_ratio' in df.columns:
            pb_max = df['pb_ratio'].quantile(0.95)
            pb_min = df['pb_ratio'].quantile(0.05)
            pb_valid = df['pb_ratio'].between(pb_min, pb_max)
            scores['pb_score'] = np.where(
                pb_valid,
                (df['pb_ratio'] - pb_min) / (pb_max - pb_min),
                df['pb_ratio'] / pb_max
            )
            scores['pb_score'] = scores['pb_score'].fillna(0.5)
        else:
            scores['pb_score'] = 0.5

        # ROE score (higher is better, so invert)
        if 'roe' in df.columns:
            roe_max = df['roe'].quantile(0.95)
            roe_min = df['roe'].quantile(0.05)
            roe_valid = df['roe'].between(roe_min, roe_max)
            scores['roe_score'] = np.where(
                roe_valid,
                1 - (df['roe'] - roe_min) / (roe_max - roe_min),
                0.5
            )
            scores['roe_score'] = scores['roe_score'].fillna(0.5)
        else:
            scores['roe_score'] = 0.5

        # FCF yield score (higher is better, so invert)
        if 'fcf_yield' in df.columns:
            fcf_max = df['fcf_yield'].quantile(0.95)
            fcf_min = df['fcf_yield'].quantile(0.05)
            fcf_valid = df['fcf_yield'].between(fcf_min, fcf_max)
            scores['fcf_score'] = np.where(
                fcf_valid & (df['fcf_yield'] > 0),
                1 - (df['fcf_yield'] - fcf_min) / (fcf_max - fcf_min),
                0.5
            )
            scores['fcf_score'] = scores['fcf_score'].fillna(0.5)
        else:
            scores['fcf_score'] = 0.5

        # Combined score (weighted average)
        total_weight = pe_weight + pb_weight + roe_weight + fcf_weight
        scores['combined_score'] = (
            scores['pe_score'] * pe_weight +
            scores['pb_score'] * pb_weight +
            scores['roe_score'] * roe_weight +
            scores['fcf_score'] * fcf_weight
        ) / total_weight

        # Add original data
        result = pd.concat([df, scores], axis=1)
        result = result.sort_values('combined_score')

        return result

    def get_top_n(
        self,
        tickers: List[str],
        n: int = 20,
        scoring_method: str = 'combined'
    ) -> pd.DataFrame:
        """
        Get top N stocks by value score.

        Args:
            tickers: List of stock symbols
            n: Number of top stocks to return
            scoring_method: 'combined', 'pe', or 'pb'

        Returns:
            DataFrame with top N stocks
        """
        scored = self.score_stocks(tickers)

        if scoring_method == 'pe':
            scored = scored.sort_values('pe_ratio')
        elif scoring_method == 'pb':
            scored = scored.sort_values('pb_ratio')
        else:
            scored = scored.sort_values('combined_score')

        # Remove rows with NaN in key metrics
        scored = scored.dropna(subset=['pe_ratio', 'pb_ratio'], how='all')

        return scored.head(n)


# Common stock universes
DOW_JONES = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'BRK-B', 'JPM', 'V', 'JNJ',
    'WMT', 'PG', 'MA', 'HD', 'DIS', 'NVDA', 'PYPL', 'ADBE', 'NFLX',
    'CMCSA', 'INTC', 'CSCO', 'KO', 'PEP', 'MRK', 'ABBV', 'BAC'
]

SP500_TOP_50 = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B',
    'LLY', 'AVGO', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'XOM', 'MA', 'HD',
    'CVX', 'MRK', 'ABBV', 'PEP', 'KO', 'BAC', 'TMO', 'COST', 'LIN',
    'ABT', 'CRM', 'AMD', 'ORCL', 'DHR', 'MCD', 'QCOM', 'VZ', 'ADBE',
    'NFLX', 'CSCO', 'PFE', 'COP', 'WFC', 'CMCSA', 'INTC', 'IBM', 'AMGN',
    'GE', 'LOW'
]


def main():
    """Test the FundamentalDataFetcher."""
    print("=" * 70)
    print("Testing FundamentalDataFetcher")
    print("=" * 70)

    # Test 1: Single stock
    print("\n--- Test 1: Single Stock (AAPL) ---")
    fetcher = FundamentalDataFetcher()
    data = fetcher.get_fundamental_data('AAPL')
    for key, value in data.items():
        if key != 'ticker':
            print(f"  {key}: {value}")

    # Test 2: Batch stocks (DOW)
    print("\n--- Test 2: Batch Fetch (First 5 DOW stocks) ---")
    df = fetcher.get_batch_fundamental_data(DOW_JONES[:5])
    print(df[['pe_ratio', 'pb_ratio', 'roe', 'fcf_yield']].to_string())

    # Test 3: Value screening
    print("\n--- Test 3: Value Screen (PE < 20, PB < 3) ---")
    screener = ValueScreener(fetcher)
    screened = screener.screen(
        DOW_JONES[:10],
        max_pe=20,
        max_pb=3,
        min_roe=0.10
    )
    print(f"Passing stocks: {len(screened)}")
    if not screened.empty:
        print(screened[['pe_ratio', 'pb_ratio', 'roe']].to_string())

    # Test 4: Top N by value score
    print("\n--- Test 4: Top 5 by Combined Value Score ---")
    top5 = screener.get_top_n(DOW_JONES[:15], n=5)
    print(top5[['pe_ratio', 'pb_ratio', 'roe', 'fcf_yield', 'combined_score']].to_string())


if __name__ == "__main__":
    main()
