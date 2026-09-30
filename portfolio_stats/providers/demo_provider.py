"""A sample portfolio, so the app can be tried without any real data."""

from __future__ import annotations

from ..models import Portfolio, Position
from .base import PortfolioProvider


class DemoProvider(PortfolioProvider):
    def get_portfolio(self) -> Portfolio:
        return Portfolio(
            positions=[
                Position("AAPL", "Apple Inc.", 12, 150, "stock"),
                Position("MSFT", "Microsoft", 8, 280, "stock"),
                Position("VWCE.DE", "Vanguard FTSE All-World", 25, 95, "etf"),
                Position("BTC-USD", "Bitcoin", 0.4, 38000, "crypto"),
                Position("ETH-USD", "Ethereum", 3, 2200, "crypto"),
            ],
            cash=2500,
            currency="USD",
        )
