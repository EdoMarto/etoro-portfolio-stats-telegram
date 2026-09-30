"""Read holdings from a CSV file.

Columns: symbol, name, quantity, avg_open_price, asset_type

Rows with asset_type "cash" are added to the portfolio's cash balance
(their `quantity * avg_open_price` is the amount); set avg_open_price to 1
and put the amount in quantity.

This is the recommended way to feed an eToro portfolio in: export your
account statement from eToro, then fill a CSV in this shape (see the README).
"""

from __future__ import annotations

import csv

from ..models import Portfolio, Position
from .base import PortfolioProvider


class CsvProvider(PortfolioProvider):
    def __init__(self, path: str, currency: str = "EUR") -> None:
        self.path = path
        self.currency = currency

    def get_portfolio(self) -> Portfolio:
        positions: list[Position] = []
        cash = 0.0

        with open(self.path, newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                symbol = (row.get("symbol") or "").strip()
                if not symbol:
                    continue
                asset_type = (row.get("asset_type") or "stock").strip().lower()
                quantity = float(row["quantity"])

                if asset_type == "cash":
                    unit = float(row.get("avg_open_price") or 1)
                    cash += quantity * unit
                    continue

                positions.append(
                    Position(
                        symbol=symbol,
                        name=(row.get("name") or symbol).strip(),
                        quantity=quantity,
                        avg_open_price=float(row["avg_open_price"]),
                        asset_type=asset_type,
                    )
                )

        return Portfolio(positions=positions, cash=cash, currency=self.currency)
