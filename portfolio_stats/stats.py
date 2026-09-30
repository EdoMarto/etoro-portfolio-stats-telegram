"""Compute portfolio statistics from priced positions. Pure, no I/O."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .models import Portfolio, Position


@dataclass
class PortfolioStats:
    currency: str
    as_of: datetime
    cash: float
    invested_value: float  # sum of market values of priced positions
    total_value: float  # invested + cash
    total_cost: float  # cost basis of priced positions
    total_pnl: float
    total_pnl_pct: float
    positions: list[Position]  # priced, sorted by market value (desc)
    unpriced: list[Position]  # positions with no price available
    allocation_by_type: dict[str, float]  # value per asset type, cash included
    weights: dict[str, float]  # symbol -> % of total value


def compute_stats(portfolio: Portfolio) -> PortfolioStats:
    priced = [p for p in portfolio.positions if p.current_price is not None]
    unpriced = [p for p in portfolio.positions if p.current_price is None]

    invested = sum(p.market_value for p in priced)
    cost = sum(p.cost_basis for p in priced)
    total = invested + portfolio.cash
    pnl = invested - cost
    pnl_pct = (pnl / cost * 100) if cost else 0.0

    allocation: dict[str, float] = {}
    for p in priced:
        allocation[p.asset_type] = allocation.get(p.asset_type, 0.0) + p.market_value
    if portfolio.cash:
        allocation["cash"] = allocation.get("cash", 0.0) + portfolio.cash

    weights = {p.symbol: (p.market_value / total * 100 if total else 0.0) for p in priced}
    priced.sort(key=lambda p: p.market_value, reverse=True)

    return PortfolioStats(
        currency=portfolio.currency,
        as_of=portfolio.as_of,
        cash=portfolio.cash,
        invested_value=invested,
        total_value=total,
        total_cost=cost,
        total_pnl=pnl,
        total_pnl_pct=pnl_pct,
        positions=priced,
        unpriced=unpriced,
        allocation_by_type=allocation,
        weights=weights,
    )
