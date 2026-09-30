"""Configuration, read from environment variables (and a local .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass


@dataclass
class Config:
    telegram_token: str | None
    telegram_chat_id: str | None
    source: str  # demo | csv | etoro
    csv_path: str
    base_currency: str
    db_path: str
    output_dir: str

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            telegram_token=os.environ.get("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID"),
            source=os.environ.get("PORTFOLIO_SOURCE", "demo"),
            csv_path=os.environ.get("PORTFOLIO_CSV", "data/sample_holdings.csv"),
            base_currency=os.environ.get("BASE_CURRENCY", "USD"),
            db_path=os.environ.get("DB_PATH", "portfolio_history.db"),
            output_dir=os.environ.get("OUTPUT_DIR", "output"),
        )
