# Nansen Time Machine ⏪

**Could you have spotted the move before it happened?**

Nansen Time Machine is a point-in-time onchain trading simulator built for the **Nansen Meridian Buildathon**. It drops a player into a historical market snapshot, hides the future, exposes only temporally-correct Nansen data, asks for a **BUY / PASS / SHORT** decision, and then reveals what happened next.

> The product is deliberately different from another alert dashboard: it turns Nansen historical intelligence into an interactive test of decision quality.

## Demo flow

1. Pick a historical token/date.
2. See only data available at that point in time.
3. Inspect Smart Money, whale, exchange and Top PnL flows.
4. Lock BUY / PASS / SHORT.
5. Reveal +24h / +7d / +30d.
6. Receive a decision score.
7. Later: build a persistent **Trader DNA** profile.

## Why the data is point-in-time

The project uses Nansen historical/backtesting endpoints specifically to avoid look-ahead bias. Historical flow cohorts resolve labels at the query end date, and historical buyer/seller labels are also resolved at that historical date rather than using today's labels.

## Repo status

**v0.2 — repo-ready prototype**

- [x] playable web UI
- [x] server-side API key handling
- [x] Nansen client
- [x] verified wrappers for historical Smart Money holdings, historical flow summary, historical who-bought/sold and OHLCV
- [x] request ledger with Nansen request IDs / credit headers
- [x] resumable cache
- [x] dry-run 1,000-call build manifest
- [x] safety guard against placeholder token addresses
- [ ] final verified 25-token universe
- [ ] execute 1,000+ meaningful calls
- [ ] convert raw responses into production scenarios
- [ ] Trader DNA
- [ ] leaderboard + share card
- [ ] deploy public demo

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5050

## Nansen API key

Never commit your key.

```bash
copy .env.example .env
```

Edit `.env` locally:

```env
NANSEN_API_KEY=your_key_here
```

`.env` is gitignored.

## The 1,000-call dataset plan

The buildathon asks builders to make 1,000 API calls. We use them for the actual product dataset rather than making meaningless requests.

Default plan:

**25 tokens × 10 historical dates × 4 meaningful data calls = 1,000 Nansen API calls**

Per token/date:

1. Smart Money historical holdings
2. Historical token flow summary
3. Historical who bought/sold
4. OHLCV covering the pre-snapshot context and reveal window

First validate the token list:

```bash
python scripts/validate_tokens.py
```

Then generate the manifest:

```bash
python scripts/build_call_plan.py
```

Preview without sending anything:

```bash
python scripts/run_dataset.py
```

Only after checking the token universe and credits:

```bash
python scripts/run_dataset.py --execute
```

Every response is cached. If the process stops, rerunning it skips completed tasks instead of wasting calls.

Check the audit trail:

```bash
python scripts/call_stats.py
```

## Security / credit safety

- Nansen API key is server-side only.
- `.env` is excluded from Git.
- Dataset execution is **dry-run by default**.
- Placeholder token addresses deliberately block production execution until verified.
- 429 responses respect `Retry-After`.
- API response metadata records request IDs and actual credit usage.
- Cached tasks are not repeated.

## Nansen endpoints used

- `POST /api/v1/smart-money/historical-holdings`
- `POST /api/v1beta1/tgm/historical-token-flow-summary`
- `POST /api/v1beta1/tgm/historical-who-bought-sold`
- `POST /api/v1/tgm/token-ohlcv`

The first three provide historical/temporally-correct intelligence; OHLCV supplies the market context and post-decision reveal.

## Architecture

```text
Browser
  │
  ▼
Flask app
  │
  ├── scenario cache ──► playable Time Machine
  │
  └── NansenClient
          │
          ├── historical Smart Money holdings
          ├── historical flow summary
          ├── historical who bought/sold
          └── OHLCV
                │
                ▼
          raw response cache
                │
                ▼
          scenario builder (next)
```

## 30–60 second demo script

**0–5s** — “Could you spot the move before it happened?”  
**5–15s** — Enter a historical snapshot; future is hidden.  
**15–28s** — Show Smart Money / whales / exchange / Top PnL signals.  
**28–35s** — Lock BUY.  
**35–45s** — Reveal +7 days.  
**45–55s** — Show market return + Decision Score.  
**55–60s** — “Built from 1,000+ Nansen API calls. No look-ahead bias.”

## Disclaimer

This is an educational buildathon project, not financial advice. Simulated historical performance does not imply future results.
