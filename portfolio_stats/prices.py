"""Live price lookup via Yahoo Finance (yfinance)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def fetch_prices(symbols: list[str]) -> dict[str, float]:
    """Return {symbol: last_price} for the symbols that could be priced.

    Symbols use Yahoo Finance notation (e.g. "AAPL", "VWCE.DE", "BTC-USD").
    Symbols that cannot be resolved are simply left out of the result.
    """
    if not symbols:
        return {}

    import yfinance as yf

    prices: dict[str, float] = {}
    for symbol in symbols:
        price = _fetch_one(yf, symbol)
        if price is not None:
            prices[symbol] = price
        else:
            log.warning("No price available for %s", symbol)
    return prices


def _fetch_one(yf, symbol: str) -> float | None:
    ticker = yf.Ticker(symbol)
    # fast_info is cheap and usually enough.
    try:
        return float(ticker.fast_info["last_price"])
    except Exception:
        pass
    # Fall back to the last daily close.
    try:
        history = ticker.history(period="1d")
        if not history.empty:
            return float(history["Close"].iloc[-1])
    except Exception as exc:  # network error, bad symbol, ...
        log.warning("Price fetch failed for %s: %s", symbol, exc)
    return None
