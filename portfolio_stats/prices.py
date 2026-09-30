"""Live price lookup via Yahoo Finance (yfinance), converted to one currency.

Yahoo quotes each instrument in its native currency (e.g. AAPL and BTC-USD in
USD, VWCE.DE in EUR). Prices are converted to `target_currency` using Yahoo FX
rates, so the whole portfolio is expressed in a single currency.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def fetch_prices(symbols: list[str], target_currency: str = "EUR") -> dict[str, float]:
    """Return {symbol: price_in_target_currency} for the symbols that could be priced."""
    if not symbols:
        return {}

    import yfinance as yf

    target = target_currency.upper()
    fx_cache: dict[tuple[str, str], float | None] = {}
    prices: dict[str, float] = {}

    for symbol in symbols:
        price, currency = _price_and_currency(yf, symbol)
        if price is None:
            log.warning("No price available for %s", symbol)
            continue
        if not currency:
            log.warning("Unknown currency for %s; assuming %s", symbol, target)
            currency = target

        rate = _fx_rate(yf, currency, target, fx_cache)
        if rate is None:
            log.warning("No FX rate %s->%s for %s; skipping", currency, target, symbol)
            continue
        prices[symbol] = price * rate

    return prices


def get_fx_rate(base: str, quote: str) -> float | None:
    """Current FX rate to turn one unit of `base` into `quote` (None if unavailable)."""
    import yfinance as yf

    return _fx_rate(yf, base, quote, {})


def _price_and_currency(yf, symbol: str) -> tuple[float | None, str | None]:
    ticker = yf.Ticker(symbol)
    price: float | None = None
    currency: str | None = None

    try:
        fast = ticker.fast_info
        price = float(fast["last_price"])
        currency = fast["currency"]
    except Exception:
        pass

    if price is None:  # fall back to the last daily close
        try:
            history = ticker.history(period="1d")
            if not history.empty:
                price = float(history["Close"].iloc[-1])
        except Exception as exc:
            log.warning("Price fetch failed for %s: %s", symbol, exc)

    if currency is None:
        try:
            currency = ticker.fast_info["currency"]
        except Exception:
            currency = None

    return price, (currency.upper() if currency else None)


def _fx_rate(yf, base: str, quote: str, cache: dict[tuple[str, str], float | None]) -> float | None:
    base, quote = base.upper(), quote.upper()
    if base == quote:
        return 1.0

    key = (base, quote)
    if key in cache:
        return cache[key]

    rate = None
    pair = f"{base}{quote}=X"  # e.g. USDEUR=X
    try:
        rate = float(yf.Ticker(pair).fast_info["last_price"])
    except Exception:
        try:
            history = yf.Ticker(pair).history(period="1d")
            if not history.empty:
                rate = float(history["Close"].iloc[-1])
        except Exception as exc:
            log.warning("FX rate %s->%s failed: %s", base, quote, exc)

    cache[key] = rate
    return rate
