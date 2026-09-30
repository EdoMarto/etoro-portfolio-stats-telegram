"""A sample portfolio, so the app can be tried without any real data."""

from __future__ import annotations

from ..models import Portfolio, Position
from .base import PortfolioProvider


class DemoProvider(PortfolioProvider):
    def get_portfolio(self) -> Portfolio:
        # A diversified, roughly balanced portfolio: global equity, emerging
        # markets, bonds, gold, a couple of single stocks and a small crypto slice.
        return Portfolio(
            positions=[
                Position("SWDA.MI", "iShares Core MSCI World", 155, 110, "etf"),
                Position("EIMI.MI", "iShares Core MSCI EM IMI", 124, 45, "etf"),
                Position("AGGH.MI", "iShares Core Global Aggregate Bond", 1875, 4.90, "bond"),
                Position("4GLD.DE", "Xetra-Gold", 51, 95, "commodity"),
                Position("ASML.AS", "ASML Holding", 2, 1200, "stock"),
                Position("AAPL", "Apple Inc.", 8, 250, "stock"),
                Position("BTC-USD", "Bitcoin", 0.03, 55000, "crypto"),
            ],
            cash=2500,
            currency="EUR",
        )
