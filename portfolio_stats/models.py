"""Core data model: a portfolio is a list of positions plus cash."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Position:
    symbol: str  # Yahoo Finance ticker, e.g. "AAPL", "VWCE.DE", "BTC-USD"
    name: str
    quantity: float
    avg_open_price: float  # average buy price, in the portfolio currency
    asset_type: str = "stock"  # stock | etf | crypto | commodity | ...
    current_price: float | None = None  # filled in after pricing

    @property
    def cost_basis(self) -> float:
        return self.quantity * self.avg_open_price

    @property
    def market_value(self) -> float:
        """Current value. Only call once `current_price` is set."""
        assert self.current_price is not None
        return self.quantity * self.current_price

    @property
    def pnl(self) -> float | None:
        if self.current_price is None:
            return None
        return self.market_value - self.cost_basis

    @property
    def pnl_pct(self) -> float | None:
        if self.pnl is None or self.cost_basis == 0:
            return None
        return self.pnl / self.cost_basis * 100


@dataclass
class Portfolio:
    positions: list[Position]
    cash: float = 0.0
    currency: str = "USD"
    as_of: datetime = field(default_factory=datetime.now)
