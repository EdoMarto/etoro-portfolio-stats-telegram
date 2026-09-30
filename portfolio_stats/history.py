"""Persist a value snapshot per run in SQLite, so we can chart value over time."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from .stats import PortfolioStats


def init_db(path: str) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                ts          TEXT PRIMARY KEY,
                currency    TEXT,
                total_value REAL,
                total_cost  REAL,
                total_pnl   REAL,
                cash        REAL
            )
            """
        )


def record_snapshot(path: str, stats: PortfolioStats) -> None:
    init_db(path)
    with sqlite3.connect(path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?, ?, ?, ?)",
            (
                stats.as_of.isoformat(timespec="seconds"),
                stats.currency,
                stats.total_value,
                stats.total_cost,
                stats.total_pnl,
                stats.cash,
            ),
        )


def load_series(path: str) -> list[tuple[datetime, float]]:
    init_db(path)
    with sqlite3.connect(path) as conn:
        rows = conn.execute("SELECT ts, total_value FROM snapshots ORDER BY ts").fetchall()
    return [(datetime.fromisoformat(ts), value) for ts, value in rows]
