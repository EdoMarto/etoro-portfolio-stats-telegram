from ..config import Config
from .base import PortfolioProvider
from .csv_provider import CsvProvider
from .demo_provider import DemoProvider
from .etoro import EtoroProvider


def build_provider(source: str, config: Config) -> PortfolioProvider:
    if source == "demo":
        return DemoProvider()
    if source == "csv":
        return CsvProvider(config.csv_path, currency=config.base_currency)
    if source == "etoro":
        return EtoroProvider(
            api_key=config.etoro_api_key,
            user_key=config.etoro_user_key,
            account=config.etoro_account,
            currency=config.base_currency,
        )
    raise ValueError(f"Unknown PORTFOLIO_SOURCE: {source!r} (use demo, csv or etoro)")


__all__ = ["PortfolioProvider", "CsvProvider", "DemoProvider", "EtoroProvider", "build_provider"]
