# eToro Portfolio Stats for Telegram

A small Python app that turns an eToro portfolio (or any broker's) into a Telegram update. It prices your
holdings with live market data, works out the numbers on your net worth and your positions, draws an
overview card and a few charts, and posts the lot to a Telegram chat. Run it by hand or on a schedule.

## Where the data comes from

The source is pluggable, set by `PORTFOLIO_SOURCE`:

* `etoro` uses the official [eToro public API](https://api-portal.etoro.com/). Create an API key pair
  (Settings > Trading > API Key Management) and set `ETORO_API_KEY` and `ETORO_USER_KEY`. The app reads
  your portfolio and balances and uses eToro's own current rates.
* `csv` reads your holdings from a CSV (format below). Works with any broker: export your positions, or
  just keep them by hand. Prices come from Yahoo Finance, so the CSV only needs quantities and average
  open prices. It's also a solid fallback for eToro (export from Settings > Account > Account Statement).
* `demo` is a sample portfolio, handy for trying the app without any data of your own.

One caveat on the eToro adapter: it targets the documented endpoints and auth (`x-api-key` / `x-user-key`
headers against `https://public-api.etoro.com/api/v1`) and reads the responses defensively, but I
couldn't run it against a live key. Check the field mapping in
[`providers/etoro.py`](portfolio_stats/providers/etoro.py) against your own account's responses. The
`csv` source needs no API access and works straight away.

## What you get

A rendered overview card with total value, invested amount, cash and profit/loss. An allocation pie chart
by asset type. A profit/loss bar chart by position. A value-over-time line chart, once there are at least
two runs on record. And a short text summary of the top holdings. It all goes to Telegram as a message
followed by an image album.

Everything is shown in one currency (`BASE_CURRENCY`, EUR by default). Yahoo quotes each instrument in its
own currency and the app converts with live FX rates; an eToro account in another currency, say USD, is
converted the same way.

### Example output

From `python -m portfolio_stats --source demo` with live prices, in EUR (the value-over-time chart shows
up once you've run it at least twice):

![Portfolio overview card](docs/screenshots/overview.png)

| Allocation by asset type | Profit / loss by position |
|---|---|
| ![Allocation pie chart](docs/screenshots/allocation.png) | ![Profit and loss bar chart](docs/screenshots/pnl.png) |

## Holdings CSV

`data/sample_holdings.csv` shows the format:

```csv
symbol,name,quantity,avg_open_price,asset_type
SWDA.MI,iShares Core MSCI World,155,110,etf
EIMI.MI,iShares Core MSCI EM IMI,124,45,etf
AGGH.MI,iShares Core Global Aggregate Bond,1875,4.90,bond
4GLD.DE,Xetra-Gold,51,95,commodity
ASML.AS,ASML Holding,2,1200,stock
BTC-USD,Bitcoin,0.03,55000,crypto
CASH,Cash balance,2500,1,cash
```

`symbol` is a [Yahoo Finance](https://finance.yahoo.com) ticker (for example `AAPL`, European ETFs like
`VWCE.DE`, crypto like `BTC-USD`); that's how prices get looked up. `avg_open_price` is your average buy
price in `BASE_CURRENCY`. For cash, use `asset_type=cash` with `quantity` as the amount and
`avg_open_price=1`. Your own CSV is git-ignored, so it never lands in the repo.

## Setup

You need Python 3.10 or newer.

```bash
pip install -r requirements.txt
cp .env.example .env      # then fill it in
```

For Telegram, create a bot with [@BotFather](https://t.me/BotFather) to get `TELEGRAM_BOT_TOKEN`, send it
a message, then grab your `TELEGRAM_CHAT_ID` from [@userinfobot](https://t.me/userinfobot). Put both in
`.env`.

## Run

```bash
# render only: print the summary and the image paths, don't post
python -m portfolio_stats --no-send

# use your CSV and post to Telegram
PORTFOLIO_SOURCE=csv PORTFOLIO_CSV=data/my_holdings.csv python -m portfolio_stats
```

Settings come from the environment (or `.env`), and `--source` overrides `PORTFOLIO_SOURCE` for a single
run.

To run it every evening with cron:

```cron
0 18 * * * cd /path/to/portfolio-stats && /path/to/python -m portfolio_stats
```

On Windows, use Task Scheduler with the same command. Each run appends a value snapshot to a local SQLite
file (`DB_PATH`), which is what feeds the value-over-time chart.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | (none) | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | (none) | Chat to post into |
| `PORTFOLIO_SOURCE` | `demo` | `demo`, `csv` or `etoro` |
| `PORTFOLIO_CSV` | `data/sample_holdings.csv` | Holdings CSV when the source is `csv` |
| `ETORO_API_KEY` / `ETORO_USER_KEY` | (none) | eToro API credentials when the source is `etoro` |
| `ETORO_ACCOUNT` | `real` | `real` or `demo` eToro account |
| `BASE_CURRENCY` | `EUR` | Currency everything is reported in |
| `DB_PATH` | `portfolio_history.db` | SQLite file for the value history |
| `OUTPUT_DIR` | `output` | Where the images are written |

If the Telegram variables aren't set, the app just prints the summary and writes the images locally.

## Tests

```bash
pytest
```

## A couple of notes

Prices come from Yahoo Finance via [`yfinance`](https://github.com/ranaroussi/yfinance), an unofficial
library, so treat the figures as indicative. And the app never places trades; it only reads prices and
reports on the holdings you give it.

## Built with

Python, yfinance, Matplotlib, SQLite and the Telegram Bot API.

## License

[MIT](LICENSE)
