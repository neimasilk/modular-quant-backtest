# EXP-2025-005: Real News Sentiment Analysis

**Status:** Active | **Completed:** 2025-01-11
**Created:** 2025-01-11
**Author:** Trae

## Hypothesis
Replacing heuristic sentiment (derived from price) with LLM-analyzed sentiment will provide uncorrelated signals that improve Sharpe ratio and reduce drawdown.

## Strategy
- **Signal Source:** Price context analyzed by DeepSeek LLM
- **Processing:** DeepSeek API analyzes price trends for sentiment (-1.0 to 1.0)
- **Lag:** Sentiment from Day T is used for trading on Day T+1 (no look-ahead)
- **Frequency:** Weekly sampling, forward-filled for daily trading

## Execution

### 1. Created NewsFetcher Module (`src/data/news_fetcher.py`)
- Fetches sentiment using DeepSeek API
- Uses price context (5-day returns, volatility) as input
- Caches results to minimize API calls
- Weekly sampling to reduce API costs

### 2. Created NewsSentimentStrategy (`run_exp_2025_005.py`)
- Variant of AdaptiveStrategy using News_Sentiment instead of AI_Stock_Sentiment
- Minimum confidence threshold (0.5) for acting on signals

### 3. Comparison Backtest
- Compared: Buy & Hold, Heuristic Sentiment, News Sentiment (LLM)
- Period: 2023-01-01 to 2024-01-01
- Ticker: NVDA

## Results

### Backtest Comparison

| Strategy | Return % | Sharpe | Max DD % | Win Rate % | # Trades |
|----------|----------|--------|---------|------------|----------|
| Buy & Hold | **229.45** | 1.41 | -18.01 | N/A | 0 (1) |
| Heuristic Sentiment | -9.52 | -0.40 | -26.93 | 56.00 | 25 |
| News Sentiment (LLM) | -15.05 | **-0.67** | **-29.34** | 53.85 | 26 |

### Sentiment Correlation Analysis
- **Correlation (Heuristic vs News): 0.152** → LOW correlation
- LLM provides UNCORRELATED signals as expected

## Analysis

### What Worked
1. **Uncorrelated Signals Confirmed**: LLM sentiment (0.152 correlation) provides different signals than heuristic price-based sentiment
2. **Technical Implementation**: NewsFetcher module successfully integrates with DeepSeek API
3. **Caching System**: Reduces API costs for repeated runs

### What Didn't Work
1. **LLM Sentiment Underperformed**: -15.05% vs -9.52% for heuristic
2. **Both Strategies Lose**: Heuristic and LLM both significantly underperformed Buy & Hold
3. **Super Bull Market**: NVDA 2023 was exceptional (+229%), regime-based strategies struggled

### Root Cause Analysis
1. **Bull Market Weakness**: Adaptive strategy is defensive by design. In super-strong uptrends:
   - Defensive mode triggers too early (short signals)
   - Mean reversion sells too early (misses big gains)
   - Aggressive mode thresholds still too conservative

2. **LLM Limitations**:
   - Weekly sampling + forward fill creates lag
   - LLM sees price context but still generates conservative scores
   - Price-based sentiment is inherently correlated with past returns (look-ahead bias not fully eliminated)

3. **NVDA 2023 Exceptionality**:
   - +229% gain is historical outlier
   - Strategy not designed for parabolic moves
   - Stop-losses trigger during volatility

## Decision

**Status: PARTIAL SUCCESS - ARCHIVE FOR FUTURE REFERENCE**

### Rationale
- Hypothesis partially validated: LLM provides uncorrelated signals
- BUT: Performance worse than heuristic
- Strategy needs redesign for strong bull markets

## Next Steps

### Recommended Follow-up Experiments
1. **EXP-2025-006**: Test LLM sentiment in bear/sideways markets (2022)
   - Hypothesis: LLM sentiment will outperform in downtrends

2. **EXP-2025-007**: Hybrid approach - combine heuristic + LLM sentiment
   - Weighted average of both signals
   - Use LLM as confirmation filter

3. **EXP-2025-008**: Bull market adaptation
   - Disable shorting in strong uptrends
   - Lower entry thresholds further
   - Momentum-based overrides

## Files Created
- `src/data/news_fetcher.py` - News sentiment fetching module
- `run_exp_2025_005.py` - Comparison backtest script
- `experiments/active/EXP-2025-005-real-news-sentiment/data/news_sentiment_data.csv`
- `experiments/active/EXP-2025-005-real-news-sentiment/results/comparison.csv`
- `experiments/active/EXP-2025-005-real-news-sentiment/results/equity_curves.csv`

## Lessons Learned

1. **LLM sentiment ≠ fundamental news**: Without actual news headlines, LLM just rephrases price action
2. **Weekly sampling too coarse**: Creates significant lag in fast-moving markets
3. **Bull market weakness**: Adaptive strategy needs aggressive mode improvements
4. **Uncorrelated ≠ profitable**: Different signals can both be wrong

## Conclusion

EXP-2025-005 successfully implemented LLM-based sentiment analysis and confirmed that LLM provides uncorrelated signals compared to heuristic sentiment. However, the LLM approach underperformed the heuristic baseline (-15.05% vs -9.52%).

The primary finding is that **price-based sentiment (even when analyzed by LLM) contains look-ahead bias elements that reduce effectiveness**. For true uncorrelated signals, we would need:
1. Actual news headlines (expensive)
2. Alternative data sources (social media, options flow, etc.)
3. Different ML approach (unsupervised, anomaly detection)

**Recommendation**: Archive this experiment and focus on regime-specific strategy improvements rather than sentiment signal engineering.
