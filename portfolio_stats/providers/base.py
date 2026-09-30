"""The data-source interface. A provider knows how to read one portfolio."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Portfolio


class PortfolioProvider(ABC):
    @abstractmethod
    def get_portfolio(self) -> Portfolio:
        """Return the current holdings. Prices are filled in later, by the app."""
