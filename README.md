# Nansen Time Machine ⏪

**Could you spot the move before it happened?**

Nansen Time Machine is a point-in-time onchain trading simulator built for the **Nansen Meridian Buildathon**. It drops a player into a historical market snapshot, hides the future, exposes only historical Nansen intelligence available for that snapshot, asks for a **BUY / PASS / SHORT** decision, and then reveals what happened next.

**Live demo:** https://nansen-time-machine.onrender.com

> Not another alert dashboard. Time Machine turns historical onchain intelligence into an interactive test of decision quality.

## What is live

- **1,000 meaningful Nansen API calls completed**
- **250 historical snapshots**
- **25 Ethereum assets**
- **0 look-ahead bias by design**
- BUY / PASS / SHORT decisions
- +1d / +7d / +30d historical outcomes
- Decision Score
- Session-based **Trader DNA**
- Public Render deployment
- Visible **Powered by Nansen API** attribution

## Demo flow

1. Pick a token and historical date.
2. Enter the snapshot with the future hidden.
3. Inspect Smart Trader, whale, exchange and Top PnL flows.
4. Lock BUY / PASS / SHORT.
5. Reveal the historical outcome.
6. Receive a Decision Score.
7. Build your Trader DNA across multiple decisions.

## Dataset

The production dataset was built from exactly **1,000 meaningful Nansen API calls**:

**25 tokens × 10 historical dates × 4 calls = 1,000 calls**

For each of the 250 token/date snapshots:

- 1 × Historical Token Flow Summary
- 3 × OHLCV requests for historical context and future reveal windows

The build consumed the calls to create the actual playable dataset rather than generating throwaway traffic. The resulting app uses cached, derived scenarios at runtime, so visitors do not consume the project's Nansen API credits.

## Point-in-time design

The simulator is designed to avoid look-ahead bias. The player sees the historical intelligence first, commits to a decision, and only then receives the future price outcome. Historical flow data is queried for the relevant historical window rather than using future outcome data to construct the decision screen.

A useful example is **AAVE · 2025-10-15 · +7 days**: the snapshot shows a **Strong Accumulation (100/100)** composite signal, yet AAVE subsequently moved **-10.61%**. Time Machine therefore does not treat onchain intelligence as an oracle; it tests how a trader interprets the information available at the time.

## Data signals

Each production snapshot derives a composite signal from:

- Smart Trader net flow — 35%
- Whale net flow — 25%
- Top PnL net flow — 25%
- Exchange net flow — 15% (direction inverted for the composite)

The UI exposes the underlying flow values alongside the composite signal so the player can make their own decision.

## Architecture

```text
Nansen API
   │
   ├── Historical Token Flow Summary
   └── Token OHLCV
          │
          ▼
   local resumable cache
          │
          ▼
   scenario builder
          │
          ▼
250 derived historical scenarios
          │
          ▼
Flask + Gunicorn → Render → Browser
                         │
                         ├── BUY / PASS / SHORT
                         ├── future reveal
                         ├── Decision Score
                         └── Trader DNA
```

Raw Nansen API responses, request ledgers and API credentials are **not redistributed in this public repository**. The repository contains the derived scenario dataset required to run the public demo.

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5050`.

No Nansen API key is required to play the cached production scenarios. An API key is only needed for dataset-generation tooling.

## Deployment

Production is served with Gunicorn on Render:

```bash
gunicorn run:app
```

Live: https://nansen-time-machine.onrender.com

## 30–60 second demo

**0–5s** — “Could you spot the move before it happened?”  
**5–15s** — Select **AAVE · 2025-10-15**, +7 days, and enter the historical snapshot.  
**15–28s** — Show Smart Trader / whale / exchange / Top PnL flows and **Strong Accumulation 100/100**.  
**28–35s** — Lock **BUY**.  
**35–45s** — Reveal the future: **AAVE -10.61%**.  
**45–55s** — Show **Decision Score 33/100** and Trader DNA.  
**55–60s** — “1,000 Nansen API calls. 250 historical snapshots. Zero look-ahead bias.”

## Built with

Python · Flask · Gunicorn · Nansen API · HTML/CSS/JavaScript · Render

## Disclaimer

Educational buildathon project only. Not financial advice. Historical simulations do not imply future performance.
