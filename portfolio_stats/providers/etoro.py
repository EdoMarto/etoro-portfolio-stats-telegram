"""eToro adapter, using the official eToro public API.

eToro exposes a public REST API (https://api-portal.etoro.com/). Create an API
key pair under Settings -> Trading -> API Key Management and set:

    ETORO_API_KEY   -> sent as the `x-api-key` header
    ETORO_USER_KEY  -> sent as the `x-user-key` header
    ETORO_ACCOUNT   -> "real" (default) or "demo"

This provider reads your aggregated portfolio and balances, resolves each
instrument's symbol/name, and returns positions already priced with eToro's
current rates (so no extra price lookup is needed).

The field names below follow the API reference:
https://api-portal.etoro.com/api-reference — the response shapes are read
defensively (several candidate keys) so small schema differences don't break it.
Verify the mapping against your account's live responses; this adapter could not
be tested against a real key here.
"""

from __future__ import annotations

import logging
import uuid

import requests

from ..models import Portfolio, Position
from .base import PortfolioProvider

log = logging.getLogger(__name__)

BASE_URL = "https://public-api.etoro.com/api/v1"
_TIMEOUT = 30


def _first(mapping: dict, *keys, default=None):
    """Return the first present, non-None value among `keys`."""
    for key in keys:
        if isinstance(mapping, dict) and mapping.get(key) is not None:
            return mapping[key]
    return default


class EtoroProvider(PortfolioProvider):
    def __init__(self, api_key: str, user_key: str, account: str = "real", currency: str = "USD") -> None:
        if not api_key or not user_key:
            raise ValueError(
                "eToro API credentials missing. Set ETORO_API_KEY and ETORO_USER_KEY "
                "(create them at https://api-portal.etoro.com/ under API Key Management)."
            )
        self.account = account
        self.currency = currency
        self._session = requests.Session()
        self._session.headers.update({"x-api-key": api_key, "x-user-key": user_key, "Accept": "application/json"})
        self._instrument_cache: dict[int, dict] = {}

    # -- HTTP -----------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = self._session.get(
            f"{BASE_URL}{path}",
            params=params,
            headers={"x-request-id": str(uuid.uuid4())},
            timeout=_TIMEOUT,
        )
        if response.status_code == 429:
            raise RuntimeError(f"eToro rate limit hit; retry after {response.headers.get('Retry-After', '?')}s")
        response.raise_for_status()
        return response.json()

    # -- Instrument metadata --------------------------------------------------

    def _instrument(self, instrument_id: int) -> dict:
        if instrument_id not in self._instrument_cache:
            try:
                data = self._get(f"/market-data/instruments/{instrument_id}")
            except Exception as exc:
                log.warning("Instrument %s lookup failed: %s", instrument_id, exc)
                data = {}
            self._instrument_cache[instrument_id] = data
        return self._instrument_cache[instrument_id]

    def _symbol_and_name(self, instrument_id: int) -> tuple[str, str]:
        info = self._instrument(instrument_id)
        symbol = _first(info, "symbolFull", "symbol", "ticker", default=str(instrument_id))
        name = _first(info, "instrumentDisplayName", "name", "displayName", default=symbol)
        return str(symbol), str(name)

    @staticmethod
    def _asset_type(info: dict) -> str:
        raw = str(_first(info, "instrumentTypeId", "typeName", "type", default="")).lower()
        if "crypto" in raw:
            return "crypto"
        if "etf" in raw:
            return "etf"
        if "comm" in raw:
            return "commodity"
        return "stock"

    # -- Portfolio ------------------------------------------------------------

    def get_portfolio(self) -> Portfolio:
        snapshot = self._get("/trading/accounts", params={"accountType": self.account})
        rows = _first(snapshot, "positions", "openPositions", default=[])

        positions: list[Position] = []
        for row in rows:
            instrument_id = _first(row, "instrumentId", "InstrumentID", "instrumentID")
            if instrument_id is None:
                continue
            info = self._instrument(int(instrument_id))
            symbol, name = self._symbol_and_name(int(instrument_id))

            units = float(_first(row, "units", "amount", "quantity", default=0) or 0)
            open_rate = float(_first(row, "openRate", "avgOpenRate", "openPrice", default=0) or 0)
            current_rate = _first(row, "currentRate", "marketRate", "rate")

            position = Position(
                symbol=symbol,
                name=name,
                quantity=units,
                avg_open_price=open_rate,
                asset_type=self._asset_type(info),
                current_price=float(current_rate) if current_rate is not None else None,
            )
            positions.append(position)

        cash = self._fetch_cash()
        return Portfolio(positions=positions, cash=cash, currency=self.currency)

    def _fetch_cash(self) -> float:
        try:
            balances = self._get("/balances/aggregated", params={"accountType": self.account})
        except Exception as exc:
            log.warning("Balance lookup failed, treating cash as 0: %s", exc)
            return 0.0
        return float(_first(balances, "cash", "available", "credit", "balance", default=0) or 0)
