# Mr. P — Night-1 kit (recorder · analyzer · backfill)

Goal of this kit: measure, on the exact series the market settles on, whether a
"zero-risk" late entry exists in the Polymarket US 15-minute BTC Up/Down market —
and under what conditions. Nothing here trades.

## What the market actually is (verified from the market rules + Polymarket US docs)
- Settles on **CF Benchmarks BRTI**, not Chainlink, not spot.
- Open value = simple average of the **60 one-second BRTI prints in [T-60s, T)** before the
  window start; close value = same statistic at the window end. Rounded to 2 decimals.
- **Up wins on a tie** (close >= open).
- Trading ends at the settlement instant. Windows open for trading ~90 s before they start.
- Kalshi's KXBTC15M uses the identical statistic on the identical index.

## Fastest path from an iPhone/iPad: a $4–6/month cloud box (10 minutes, Safari + an SSH app)
1. Create a droplet at digitalocean.com (Ubuntu 24.04, region New York, cheapest size, **password** auth
   — easier than SSH keys on mobile). Copy its IP. (AWS Lightsail in Virginia is the equivalent.)
2. Install **Termius** (free) → New host → the IP, user `root`, the password → connect.
3. Paste one line (installs everything, asks for the Polymarket key — Enter to skip — and starts two
   services: the recorder and a status page):
   ```bash
   curl -sSL https://raw.githubusercontent.com/watkast/predictionbots/mrp/mrp/bootstrap.sh | bash
   ```
4. It prints a status URL like `http://IP:8787/?k=TOKEN`. Bookmark it on the phone: it shows recorder
   health, the latest BRTI print, and the analyzer's gate report (refreshed every 10 minutes).
   `…/windows.csv?k=TOKEN` has the per-window detail.

Helper commands on the box afterwards: `mrp-logs` (live log), `mrp-report` (run the analyzer now,
accepts `--min-d 100` etc.), `mrp-update` (pull the latest code and restart), `mrp-keys` (rotate keys).
Re-running the one-liner is always safe.

No DigitalOcean? Any Ubuntu/Debian box works the same way (`bootstrap.sh` has no provider-specific
steps). macOS would need a launchd variant — ask.

## Manual install (any machine with Python 3.10+)
```bash
python3 -m venv .venv && source .venv/bin/activate      # optional
pip install -r requirements.txt
```

## Run the recorder (no API keys required)
```bash
python3 mrp_recorder.py
```
Leave it running on an always-on machine. It writes `./data/YYYY-MM-DD/HH.jsonl` and prints a
status line every minute. Ctrl-C stops it; restarting is safe (append-only files).

What it records (Layer A, public endpoints only):
- `pmus.idx` — every 1-second BRTI print (the settlement series), ~1 s latency
- `pmus.settle_avg` — in each window's final 70 s: samples collected so far, running average,
  and `need_rem_move`: how far the *remaining* prints must average from the current price
  to flip the result. This is the settlement gate, live.
- `pmus.book` — the live window's full order book at 1 Hz in the final 180 s (10 s cadence
  before that), plus the next window's book
- `pmus.state` — every market state transition (OPEN / HALTED / MATCH_AND_CLOSE_AUCTION / EXPIRED ...)
- `pmus.market` / `pmus.settlement` — price-to-beat stamp, settlement price, result, settlement latency

Optional layers (set env vars; see `.env.example`):
- **Kalshi** (`KALSHI_KEY_ID`, `KALSHI_PRIVATE_KEY_PATH`): push stream of BRTI with Kalshi's own
  running 60 s settlement average, plus KXBTC15M order books. Keys: kalshi.com → account → API keys
  (download the private key PEM).
- **Polymarket US WebSocket** (`POLYMARKET_KEY_ID`, `POLYMARKET_SECRET_KEY`): push order book for
  the live and next window. Keys: polymarket.us/developer.

## Analyze (after >= 1 night)
```bash
python3 mrp_analyze.py ./data --lot 10
python3 mrp_analyze.py ./data --lot 10 --min-d 100     # test a settlement-gate threshold of $100
```
Prints, per seconds-left checkpoint: flip rate, % of windows still OPEN, how many had an ask
<= 0.99 on the leading side with enough size, net per lot after the taker fee, and — the only
number that matters — `ok&flip`: entries the gates would have taken that then LOST.
Also prints the fastest BRTI moves observed over 1/5/10/15/30/60 s and every state transition seen.
Per-window detail lands in `windows.csv`.

Note on Polymarket US books: each market is one Up instrument. Buying **Down** means going short
Up at the **bid**, so the Down ask = 1 - best bid. The analyzer handles this.

## Backfill history (optional, public)
```bash
python3 mrp_backfill.py --days 30            # 1-second BRTI since ~Sept 22 launch, 1 request per hour of data
python3 mrp_analyze.py ./data_backfill
```
Derives every window's open/close/result from the index alone and cross-checks them against the
exchange's stamped values. Any `MISMATCH` line means our understanding of the rule is wrong — stop
and investigate before trusting anything else. With Kalshi keys, `--source kalshi` reaches further back.

## Night-1 "done" criteria
1. `settlement reproduction ... 100%` in the analyzer (we can compute the settlement ourselves).
2. The state-transition list tells us what the book does in the final seconds.
3. `ok&flip == 0` at the checkpoints we care about, and we know how many `entry_ok` windows/day exist.
