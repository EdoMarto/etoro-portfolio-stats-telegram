from .base import PortfolioProvider
from .csv_provider import CsvProvider
from .demo_provider import DemoProvider
from .etoro import EtoroProvider


def build_provider(source: str, csv_path: str, currency: str) -> PortfolioProvider:
    if source == "demo":
        return DemoProvider()
    if source == "csv":
        return CsvProvider(csv_path, currency=currency)
    if source == "etoro":
        return EtoroProvider()
    raise ValueError(f"Unknown PORTFOLIO_SOURCE: {source!r} (use demo, csv or etoro)")


__all__ = ["PortfolioProvider", "CsvProvider", "DemoProvider", "EtoroProvider", "build_provider"]
