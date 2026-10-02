"""Render the overview card and charts as PNG files with Matplotlib."""

from __future__ import annotations

import os
from datetime import datetime

import matplotlib

matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt  # noqa: E402

from .stats import PortfolioStats  # noqa: E402

# A small, colour-blind-friendly qualitative palette.
PALETTE = [
    "#2563eb", "#16a34a", "#f59e0b", "#db2777", "#7c3aed",
    "#0891b2", "#dc2626", "#65a30d", "#9333ea", "#ea580c",
]
GAIN = "#16a34a"
LOSS = "#dc2626"

plt.rcParams.update(
    {
        "figure.dpi": 130,
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def _money(value: float, currency: str) -> str:
    return f"{value:,.0f} {currency}"


def overview_card(stats: PortfolioStats, path: str) -> str:
    """A dark summary card with the headline numbers, the 'screenshot'."""
    fig = plt.figure(figsize=(7, 4))
    fig.patch.set_facecolor("#0f172a")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    ax.text(0.5, 0.9, "Portfolio overview", ha="center", color="#e2e8f0", fontsize=18, weight="bold")
    ax.text(0.5, 0.81, stats.as_of.strftime("%Y-%m-%d %H:%M"), ha="center", color="#94a3b8", fontsize=10)

    pnl_color = GAIN if stats.total_pnl >= 0 else LOSS
    rows = [
        ("Total value", _money(stats.total_value, stats.currency), "#e2e8f0"),
        ("Invested", _money(stats.invested_value, stats.currency), "#e2e8f0"),
        ("Cash", _money(stats.cash, stats.currency), "#e2e8f0"),
        ("Profit / loss", f"{_money(stats.total_pnl, stats.currency)}  ({stats.total_pnl_pct:+.1f}%)", pnl_color),
    ]
    y = 0.60
    for label, value, color in rows:
        ax.text(0.08, y, label, color="#94a3b8", fontsize=12)
        ax.text(0.92, y, value, color=color, fontsize=15, weight="bold", ha="right")
        y -= 0.135

    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def allocation_chart(stats: PortfolioStats, path: str) -> str:
    items = sorted(stats.allocation_by_type.items(), key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in items]
    values = [v for _, v in items]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(
        values,
        labels=labels,
        autopct=lambda pct: f"{pct:.0f}%",
        colors=PALETTE[: len(values)],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    ax.set_title("Allocation by asset type")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def pnl_chart(stats: PortfolioStats, path: str) -> str:
    top = stats.positions[:10]
    names = [p.symbol for p in top]
    pnls = [p.pnl or 0.0 for p in top]
    colors = [GAIN if x >= 0 else LOSS for x in pnls]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(names[::-1], pnls[::-1], color=colors[::-1])
    ax.axvline(0, color="#64748b", lw=1)
    ax.set_title(f"Profit / loss by position ({stats.currency})")
    ax.set_xlabel(stats.currency)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def networth_chart(series: list[tuple[datetime, float]], path: str, currency: str) -> str:
    xs = [d for d, _ in series]
    ys = [v for _, v in series]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, color=PALETTE[0], lw=2)
    ax.fill_between(xs, ys, color=PALETTE[0], alpha=0.12)
    ax.set_title("Total value over time")
    ax.set_ylabel(currency)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


def render_all(stats: PortfolioStats, series: list[tuple[datetime, float]], output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths = [
        overview_card(stats, os.path.join(output_dir, "overview.png")),
        allocation_chart(stats, os.path.join(output_dir, "allocation.png")),
    ]
    if stats.positions:
        paths.append(pnl_chart(stats, os.path.join(output_dir, "pnl.png")))
    if len(series) >= 2:
        paths.append(networth_chart(series, os.path.join(output_dir, "networth.png"), stats.currency))
    return paths
