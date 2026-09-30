from portfolio_stats.models import Portfolio, Position
from portfolio_stats.stats import compute_stats


def test_compute_stats_basic():
    portfolio = Portfolio(
        positions=[
            Position("AAPL", "Apple", 10, 100, "stock", current_price=150),
            Position("MSFT", "Microsoft", 5, 200, "stock", current_price=180),
        ],
        cash=500,
        currency="USD",
    )
    stats = compute_stats(portfolio)

    assert stats.invested_value == 10 * 150 + 5 * 180  # 2400
    assert stats.total_cost == 10 * 100 + 5 * 200  # 2000
    assert stats.total_pnl == 400
    assert round(stats.total_pnl_pct, 1) == 20.0
    assert stats.total_value == 2900  # invested + cash
    # sorted by market value, Apple (1500) before Microsoft (900)
    assert [p.symbol for p in stats.positions] == ["AAPL", "MSFT"]


def test_unpriced_positions_are_separated():
    portfolio = Portfolio(
        positions=[
            Position("AAPL", "Apple", 10, 100, "stock", current_price=150),
            Position("XYZ", "Unknown", 1, 10, "stock", current_price=None),
        ],
    )
    stats = compute_stats(portfolio)

    assert [p.symbol for p in stats.positions] == ["AAPL"]
    assert [p.symbol for p in stats.unpriced] == ["XYZ"]
