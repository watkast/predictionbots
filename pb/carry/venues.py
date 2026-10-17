"""Venue facts and fee schedules for the carry venture (verified 2026-10-17).

Everything below was read from the cited pages on 2026-10-17. Numbers marked
*unverified* could not be read from a public page in this session and must be
checked against the account's fee tab before any real money.

Coinbase (US-legal path A)
--------------------------
* ``BTC-PERP-INTX`` (International Exchange perps via Advanced Trade API) **ended
  2026-10-01**; international derivatives moved to a Deribit-powered JSON-RPC
  gateway (``https://drb.coinbase.com/api/v2``) that is not for US persons.
  https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/guides/perpetual
* US perpetual-style futures trade on Coinbase Derivatives Exchange (DCM) through
  Coinbase Financial Markets (FCM). Product ids follow ``{code}-{ddMMMyy}-CDE``;
  the BTC perp-style contract is ``BIP-20DEC30-CDE`` (placeholder 5-year expiry).
  ``future_product_details.contract_expiry_type`` is ``EXPIRING`` with a
  non-empty ``funding_rate``; ``funding_interval`` is ``"3600s"``.
  https://nautilustrader.io/docs/latest/integrations/coinbase/
* Contract specs (CFTC self-certification, 2025-06-26): nano Bitcoin Perp-Style
  Futures ``BIP`` = 0.01 BTC, tick $5 index / $0.05 per contract; funding rate
  computed hourly from twenty 3-minute premium samples (75 % current hour /
  25 % previous hour), cash adjustment aggregated twice daily (mid-day and
  end-of-day margin runs); daily settlement 15:00 CT; initial expiry Dec-2030.
  nano Ether perp-style = 0.10 ETH. Position limit 6.5 M BIP.
  https://www.cftc.gov/sites/default/files/filings/ptc/25/06/ptc06262524818.pdf
  https://www.marketsmedia.com/coinbase-derivatives-to-launch-us-perpetual-style-futures-on-july-21
* Fees: "$0.15 charge per contract to cover exchange, NFA, and clearing fees" on
  top of volume-based commission "as low as 0.005 % maker"; taker "as low as
  0.02 %" (top tier). Crypto futures max leverage 10x.
  https://www.coinbase.com/futures/nol-19mar26-cde
  https://cryptoslate.com/coinbase-starts-cftc-regulated-perpetuals-for-us-traders-offering-10x-leverage-and-0-02-fees/
  Entry-tier commission is *unverified* (the fee tab needs a login); we assume
  0.02 % taker / 0.01 % maker + $0.15/contract as the base case and expose both.
* Spot leg: Coinbase Advanced spot tiers (as of training data, *unverified*
  today): Intro 0.60 % maker / 1.20 % taker; $1k-10k 0.40 / 0.75; $10k-50k
  0.25 / 0.40; $50k-100k 0.15 / 0.25. This is the dominant cost for a small
  operator and the reason the Kraken path is the default.
* API: one CDP API key (``organizations/{org}/apiKeys/{id}``) + EC private key,
  ES256 JWT per request, 120 s expiry; legacy keys are dead.
  REST base ``https://api.coinbase.com/api/v3/brokerage``. Public (no auth):
  ``GET /market/products/{product_id}`` (has ``future_product_details``) and
  ``GET /market/products/{product_id}/candles?start=&end=&granularity=ONE_HOUR``
  (unix-second params, max 350 candles).
  https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/public/get-public-product-candles
  https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/products/get-product
  There is no Coinbase funding-*history* endpoint for US products; the live
  ``funding_rate`` must be sampled and logged (scripts/carry_paper.py does).

Kraken Derivatives US (US-legal path B, default)
-------------------------------------------------
* Perps listed on Bitnomial Exchange (CFTC DCM, owned by Payward) and cleared
  through NinjaTrader Clearing d/b/a Kraken Derivatives US (FCM, NFA 0309379).
  16 USD-quoted perps at launch incl. ``PBTCUC`` (Bitcoin) and ``PETHUI``
  (Ether); contract specs page lists ``PBTCUCZ50`` = 0.01 BTC and
  ``PETHIUZ50`` = 0.5 ETH. USD collateral only at launch. Funding is a periodic
  long/short payment aggregated through the day and settled once daily at
  15:00 CT as a cash adjustment; liquidation fee $10 (perps only).
  https://support.kraken.com/gb/articles/us-perpetual-futures
  https://support.kraken.com/gb/articles/contract-specifications
* Fees (per contract, per side): commission $0.0003 + exchange/clearing $0.001
  + NFA $0.01 = **$0.0113 all-in**, no maker/taker split published.
  https://support.kraken.com/gb/articles/us-futures-fees
* Bitnomial public funding API (no auth): ``GET https://bitnomial.com/exchange/api/v1/funding-rates/``
  with ``base_symbol``/``product_id``, ``begin_time``/``end_time`` (ISO-8601),
  ``limit``, ``order``, ``cursor``; fields ``product_id, price_index, mark_price,
  interest_rate, funding_rate, interval_start, interval_end``; 8-hour intervals
  at 00:00/08:00/16:00 UTC. Example base symbol ``BTCUC``.
  https://bitnomial.com/exchange/docs/api/rest/funding-rates
* Spot leg: Kraken Pro spot tiers: $0+ 0.40 % maker / 0.80 % taker;
  $2.5k+ 0.30 / 0.60; $10k+ 0.22 / 0.38; $25k+ 0.20 / 0.35; $50k+ 0.15 / 0.30;
  $100k+ 0.12 / 0.25.  https://www.kraken.com/features/fee-schedule
* Press: 8-hour funding, 9 assets at the June-2026 announcement, Kraken Pro UI.
  https://www.thetradenews.com/kraken-launches-first-cftc-regulated-perpetual-futures-for-us-traders/
  https://www.fow.com/insights/kraken-to-launch-first-cftc-regulated-perps
  Kraken Derivatives US trading API for the Bitnomial perps is *unverified*
  (not mentioned on any page read); the paper tick only needs the public
  Bitnomial funding endpoint.

Free historical data (offshore proxies; US perps are months old)
----------------------------------------------------------------
* Binance Vision: ``https://data.binance.vision/data/futures/um/monthly/fundingRate/{SYM}/{SYM}-fundingRate-{YYYY-MM}.zip``
  (CSV ``calc_time,funding_interval_hours,last_funding_rate``), perp klines
  ``.../data/futures/um/monthly/klines/{SYM}/1h/{SYM}-1h-{YYYY-MM}.zip`` and spot
  ``https://data.binance.vision/data/spot/monthly/klines/{SYM}/1h/{SYM}-1h-{YYYY-MM}.zip``
  (kline columns open_time,open,high,low,close,volume,close_time,...; spot
  timestamps are microseconds from 2025-01-01). https://github.com/binance/binance-public-data
  Live: ``GET https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000``.
* Bybit: ``GET https://api.bybit.com/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=200``
  (``fundingRate``, ``fundingRateTimestamp`` ms; endTime-only paging).
  https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
* OKX: ``GET https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP&limit=100``.
* Coinbase International/Deribit gateway history (not US):
  ``GET https://drb.coinbase.com/api/v2/public/get_funding_rate_history?instrument_name=BTC-PERPETUAL&start_timestamp=&end_timestamp=``
  (hourly ``interest_1h``/``interest_8h``).
  https://docs.cdp.coinbase.com/api-reference/market-data/public-get_funding_rate_history.md
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LegFees:
    """Cost of one leg, one side. ``bps`` on notional plus ``per_contract`` USD
    per contract of ``contract_size`` base units (0 for spot)."""

    maker_bps: float
    taker_bps: float
    per_contract: float = 0.0
    contract_size: float = 0.0  # base units per contract; 0 => notional-only

    def cost(self, notional: float, price: float, maker: bool) -> float:
        bps = self.maker_bps if maker else self.taker_bps
        c = notional * bps / 1e4
        if self.per_contract and self.contract_size and price > 0:
            contracts = notional / (self.contract_size * price)
            c += self.per_contract * contracts
        return c


@dataclass(frozen=True)
class VenueFees:
    name: str
    spot: LegFees
    perp: LegFees
    funding_interval_hours: float
    perp_max_leverage: float
    maintenance_margin_frac: float  # of notional; triggers liquidation
    liquidation_fee_usd: float = 0.0
    notes: str = ""


# Coinbase: Advanced spot $1k-10k tier (unverified today) + CDE perp-style.
COINBASE_BTC = VenueFees(
    name="coinbase",
    spot=LegFees(maker_bps=40.0, taker_bps=75.0),
    perp=LegFees(maker_bps=1.0, taker_bps=2.0, per_contract=0.15, contract_size=0.01),
    funding_interval_hours=1.0,  # accrues hourly, cash-adjusted twice daily
    perp_max_leverage=10.0,
    maintenance_margin_frac=0.05,  # ~half of 10 % initial at 10x; unverified
    liquidation_fee_usd=0.0,
    notes="BIP-20DEC30-CDE 0.01 BTC; $0.15/contract exchange+NFA+clearing; spot tier unverified",
)
COINBASE_ETH = VenueFees(
    name="coinbase",
    spot=LegFees(maker_bps=40.0, taker_bps=75.0),
    perp=LegFees(maker_bps=1.0, taker_bps=2.0, per_contract=0.15, contract_size=0.10),
    funding_interval_hours=1.0,
    perp_max_leverage=10.0,
    maintenance_margin_frac=0.05,
    notes="nano Ether perp-style 0.10 ETH",
)

# Kraken: Pro spot $10k+ tier + Kraken Derivatives US / Bitnomial perps.
KRAKEN_BTC = VenueFees(
    name="kraken",
    spot=LegFees(maker_bps=22.0, taker_bps=38.0),
    perp=LegFees(maker_bps=0.0, taker_bps=0.0, per_contract=0.0113, contract_size=0.01),
    funding_interval_hours=8.0,
    perp_max_leverage=10.0,  # unverified; "varies by asset"
    maintenance_margin_frac=0.05,  # unverified
    liquidation_fee_usd=10.0,
    notes="PBTCUC 0.01 BTC; $0.0113/contract/side all-in; funding settled daily 15:00 CT",
)
KRAKEN_ETH = VenueFees(
    name="kraken",
    spot=LegFees(maker_bps=22.0, taker_bps=38.0),
    perp=LegFees(maker_bps=0.0, taker_bps=0.0, per_contract=0.0113, contract_size=0.5),
    funding_interval_hours=8.0,
    perp_max_leverage=10.0,
    maintenance_margin_frac=0.05,
    liquidation_fee_usd=10.0,
    notes="PETHUI 0.5 ETH (contract-specs page)",
)

VENUES: dict[str, dict[str, VenueFees]] = {
    "coinbase": {"BTC": COINBASE_BTC, "ETH": COINBASE_ETH},
    "kraken": {"BTC": KRAKEN_BTC, "ETH": KRAKEN_ETH},
}

# Live funding endpoints polled by scripts/carry_paper.py (all public, no auth).
LIVE_FUNDING_SOURCES: dict[str, dict] = {
    "coinbase": {
        "kind": "coinbase_product",
        "url": "https://api.coinbase.com/api/v3/brokerage/market/products/{product_id}",
        "products": {"BTC": "BIP-20DEC30-CDE", "ETH": None},  # ETH id discovered via product list
        "list_url": "https://api.coinbase.com/api/v3/brokerage/market/products?product_type=FUTURE",
        "interval_hours": 1.0,
    },
    "bitnomial": {
        "kind": "bitnomial_funding",
        "url": "https://bitnomial.com/exchange/api/v1/funding-rates/",
        "products": {"BTC": "BTCUC", "ETH": "ETHUI"},  # ETH base symbol unverified
        "interval_hours": 8.0,
    },
    "binance": {
        "kind": "binance_funding",
        "url": "https://fapi.binance.com/fapi/v1/fundingRate",
        "products": {"BTC": "BTCUSDT", "ETH": "ETHUSDT"},
        "interval_hours": 8.0,
    },
    "bybit": {
        "kind": "bybit_funding",
        "url": "https://api.bybit.com/v5/market/funding/history",
        "products": {"BTC": "BTCUSDT", "ETH": "ETHUSDT"},
        "interval_hours": 8.0,
    },
    "okx": {
        "kind": "okx_funding",
        "url": "https://www.okx.com/api/v5/public/funding-rate-history",
        "products": {"BTC": "BTC-USDT-SWAP", "ETH": "ETH-USDT-SWAP"},
        "interval_hours": 8.0,
    },
}


def venue_fees(venue: str, asset: str, overrides: dict | None = None) -> VenueFees:
    """Look up a schedule and apply flat overrides like ``{"spot.taker_bps": 60}``."""
    base = VENUES[venue][asset.upper()]
    if not overrides:
        return base
    spot = dict(base.spot.__dict__)
    perp = dict(base.perp.__dict__)
    top = {k: v for k, v in base.__dict__.items() if k not in ("spot", "perp")}
    for k, v in overrides.items():
        if k.startswith("spot."):
            spot[k[5:]] = v
        elif k.startswith("perp."):
            perp[k[5:]] = v
        elif k in top:
            top[k] = v
        else:
            raise KeyError(k)
    return VenueFees(spot=LegFees(**spot), perp=LegFees(**perp), **top)


def annualize(rate_per_interval: float, interval_hours: float) -> float:
    return rate_per_interval * (8760.0 / interval_hours)
