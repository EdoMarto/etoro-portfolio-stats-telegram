"""eToro adapter — intentionally not implemented.

eToro does not offer a public, self-service REST API that lets a retail user
read their own portfolio (balance and open positions). The only programmatic
options are partner/institutional APIs or scraping the web app, and scraping
breaks eToro's Terms of Service and is fragile.

The supported path is therefore a manual export:

    eToro app/site  ->  Settings  ->  Account  ->  Account Statement  ->  export

then shape the holdings into a CSV and use `PORTFOLIO_SOURCE=csv`. See README.

This class is kept as a clearly marked extension point: if you ever obtain
real API access, implement `get_portfolio()` here.
"""

from __future__ import annotations

from ..models import Portfolio
from .base import PortfolioProvider


class EtoroProvider(PortfolioProvider):
    def get_portfolio(self) -> Portfolio:
        raise NotImplementedError(
            "eToro has no public self-service API for reading your own portfolio. "
            "Export your eToro account statement and use PORTFOLIO_SOURCE=csv "
            "(PORTFOLIO_CSV pointing at your holdings file). See the README."
        )
