# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-01-11

### Critical Fixes (Ref: review.md)

Based on the code review "Jujur dan Keras", the following critical issues have been addressed to improve the system's robustness and validity:

1.  **Removed "Fake AI" Signals (Self-Fulfilling Prophecy)**
    *   **Issue:** The prototype previously used `add_signal_impact=True`, which artificially moved prices based on AI signals, creating a self-fulfilling prophecy in backtests.
    *   **Fix:** Disabled `add_signal_impact` by default in `prepare_data` and `main.py`. Backtests now run on unmodified price data (random walk/mock or real), ensuring that performance metrics reflect true predictive power, not artificial manipulation.

2.  **Professional Stop-Loss Implementation**
    *   **Issue:** The strategy used a manual `check_stop_loss()` function inside `next()`, which evaluated prices at `Close`. This caused "Look-Ahead Bias" where intraday stop-losses were executed at the closing price, underestimating risk.
    *   **Fix:** Refactored `AdaptiveStrategy` to use the backtesting library's built-in `sl` (Stop Loss) and `tp` (Take Profit) parameters in `self.buy()` and `self.sell()`. This ensures the engine correctly handles intraday High/Low execution.

3.  **Mitigated Overfitting with Optimizable Parameters**
    *   **Issue:** Trading thresholds (e.g., `0.2`, `-0.5`) were hardcoded, leading to curve-fitting on specific datasets (NVDA 2023).
    *   **Fix:** Refactored `AdaptiveStrategy` to use class attributes (e.g., `self.aggr_entry_thresh`) instead of hardcoded constants. Updated `main.py` to support parameter optimization (`--optimize`), allowing for systematic finding of robust parameters rather than guessing.

4.  **Realistic "Production" Claims**
    *   **Issue:** The `README.md` claimed the system was "Production Ready" despite lacking robust error handling and using CSVs.
    *   **Fix:** Downgraded the claim to "**Robust Prototype**". Added `try-except` blocks in `main.py` and `backtest_engine.py` to handle runtime errors gracefully.

5.  **Infrastructure Improvements**
    *   **Feature:** Verified `data_miner.py` integration with `rclone` for Google Drive syncing, addressing data persistence needs.
    *   **Feature:** Added `--verbose` flag to `main.py` for better debugging and transparency during execution.
