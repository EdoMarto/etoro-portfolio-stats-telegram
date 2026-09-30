"""Entry point: load holdings, price them, compute stats, render and post."""

from __future__ import annotations

import argparse
import html
import logging
import sys

from .charts import render_all
from .config import Config
from .history import load_series, record_snapshot
from .models import Portfolio
from .prices import fetch_prices, get_fx_rate
from .providers import build_provider
from .stats import PortfolioStats, compute_stats
from .telegram import send_message, send_photo_group

log = logging.getLogger("portfolio_stats")


def _money(value: float, currency: str) -> str:
    return f"{value:,.2f} {currency}"


def build_message(stats: PortfolioStats) -> str:
    esc = html.escape
    marker = "\U0001f7e2" if stats.total_pnl >= 0 else "\U0001f534"  # green / red circle

    lines = [
        f"<b>\U0001f4ca Portfolio update</b> — {esc(stats.as_of.strftime('%Y-%m-%d %H:%M'))}",
        "",
        f"\U0001f4b0 <b>Total value:</b> {_money(stats.total_value, stats.currency)}",
        f"\U0001f4c8 <b>Invested:</b> {_money(stats.invested_value, stats.currency)}",
        f"\U0001f4b5 <b>Cash:</b> {_money(stats.cash, stats.currency)}",
        f"{marker} <b>P/L:</b> {_money(stats.total_pnl, stats.currency)} ({stats.total_pnl_pct:+.1f}%)",
    ]

    if stats.positions:
        lines += ["", "<b>Top holdings</b>"]
        for p in stats.positions[:5]:
            weight = stats.weights.get(p.symbol, 0.0)
            pl = f"{p.pnl_pct:+.1f}%" if p.pnl_pct is not None else "n/a"
            lines.append(f"• {esc(p.symbol)} — {_money(p.market_value, stats.currency)} ({weight:.0f}%, {pl})")

    if stats.unpriced:
        missing = ", ".join(p.symbol for p in stats.unpriced)
        lines += ["", f"⚠️ No price for: {esc(missing)}"]

    return "\n".join(lines)


def _convert(portfolio: Portfolio, target: str) -> None:
    """Convert a portfolio's monetary fields into `target` at the current FX rate."""
    rate = get_fx_rate(portfolio.currency, target)
    if not rate:
        log.warning("No FX rate %s->%s; keeping values in %s", portfolio.currency, target, portfolio.currency)
        return
    for position in portfolio.positions:
        position.avg_open_price *= rate
        if position.current_price is not None:
            position.current_price *= rate
    portfolio.cash *= rate
    portfolio.currency = target


def run(config: Config, source: str, send: bool) -> None:
    provider = build_provider(source, config)
    portfolio = provider.get_portfolio()

    # A provider may report in a different currency (e.g. an eToro account in USD).
    # Convert everything it already priced into the base currency at the current rate.
    if portfolio.currency.upper() != config.base_currency.upper():
        _convert(portfolio, config.base_currency)

    # Only price positions the provider did not already price (eToro returns rates itself).
    to_price = [p.symbol for p in portfolio.positions if p.current_price is None]
    if to_price:
        log.info("Pricing %d position(s) via Yahoo Finance", len(to_price))
        prices = fetch_prices(to_price, config.base_currency)
        for position in portfolio.positions:
            if position.current_price is None:
                position.current_price = prices.get(position.symbol)

    stats = compute_stats(portfolio)
    record_snapshot(config.db_path, stats)
    series = load_series(config.db_path)

    charts = render_all(stats, series, config.output_dir)
    message = build_message(stats)
    log.info("Rendered %d image(s)", len(charts))

    can_send = bool(config.telegram_token and config.telegram_chat_id)
    if not send or not can_send:
        if not can_send:
            log.warning("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set — not posting.")
        print(message)
        print("\nImages:")
        for path in charts:
            print(f"  {path}")
        return

    send_message(config.telegram_token, config.telegram_chat_id, message)
    send_photo_group(config.telegram_token, config.telegram_chat_id, charts)
    log.info("Posted to Telegram chat %s", config.telegram_chat_id)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # The summary contains emoji; keep console output working on code pages like cp1252.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Publish portfolio statistics to Telegram.")
    parser.add_argument("--source", choices=["demo", "csv", "etoro"], help="override PORTFOLIO_SOURCE")
    parser.add_argument("--no-send", action="store_true", help="render only, do not post to Telegram")
    args = parser.parse_args(argv)

    config = Config.from_env()
    run(config, source=args.source or config.source, send=not args.no_send)


if __name__ == "__main__":
    main()
