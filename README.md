# Nansen Time Machine

Nansen Time Machine is a historical onchain trading simulator built for the **Nansen Meridian Buildathon**.

Pick a token and a past date, look at the Nansen data that was available at that point in time, make a **BUY / PASS / SHORT** decision, and then reveal what happened over the next 1, 7 or 30 days.

**Live demo:** https://nansen-time-machine.onrender.com

Instead of checking an alert after the move has already happened, go back to that moment and make the decision based only on the information you had at the time.

## Current build

The public version currently includes:

- 250 historical snapshots
- 25 Ethereum assets
- Dataset built from 1,000 Nansen API calls
- BUY / PASS / SHORT decisions
- +1d / +7d / +30d historical outcomes
- Decision Score
- Session-based Trader DNA
- Historical Nansen flow data
- Public deployment on Render

The future outcome is kept hidden until a decision is locked.

## How a round works

1. Choose a token and historical date.
2. Open the snapshot without seeing the future price move.
3. Review Smart Trader, whale, exchange and Top PnL flows.
4. Choose BUY, PASS or SHORT.
5. Lock the decision.
6. Reveal the historical outcome.
7. Get a Decision Score and update the current Trader DNA session.

This makes it possible to test a decision against historical onchain data without accidentally using information from the future.

## Dataset

The production dataset was built from exactly **1,000 Nansen API calls**:

**25 tokens × 10 historical dates × 4 calls = 1,000 calls**

For each token/date combination the dataset builder used:

- 1 × Historical Token Flow Summary
- 3 × Token OHLCV requests

That produces 250 playable historical scenarios.

The API calls were used to build the actual dataset for the application. The public demo runs from cached, derived scenario data, so visitors can play without consuming additional Nansen API credits.

Raw API responses, request logs and API credentials are not included in this public repository.

## Point in time approach

Avoiding look ahead bias is one of the main parts of the project.

The decision screen is built from historical data for the selected snapshot. Future price data is kept separate and is only shown after the player commits to BUY, PASS or SHORT.

The project is not trying to present an onchain signal as a guaranteed prediction. The interesting part is comparing what the data suggested at the time with what actually happened afterward.

### Example: AAVE

One of the scenarios is **AAVE · 2025-10-15 · +7 days**.

The snapshot produced a **Strong Accumulation (100/100)** composite signal. After the decision is revealed, the actual seven day move is **-10.61%**.

That mismatch is useful. A strong historical flow signal can still lead to a bad trade, and the simulator lets the player see that directly instead of only showing examples where the signal worked.

## Signals

Each production snapshot contains the underlying flow values and a simple composite signal.

The current weighting is:

- Smart Trader net flow — 35%
- Whale net flow — 25%
- Top PnL net flow — 25%
- Exchange net flow — 15% (direction inverted)

The individual values remain visible in the UI. The composite is there as a summary, not as a replacement for the underlying data.

## Decision Score

After the future is revealed, the app scores the locked decision against the historical outcome.

The score is meant to make repeated rounds easier to compare. It is part of the simulator rather than a trading recommendation or prediction model.

## Trader DNA

Trader DNA tracks the current session across multiple decisions.

Instead of judging the player from a single round, it starts building a small profile from the decisions made during the session. This makes the app more useful as a repeatable historical exercise rather than a one shot demo.

## Architecture

```text
Nansen API
   |
   |-- Historical Token Flow Summary
   |-- Token OHLCV
   |
   v
local resumable cache
   |
   v
scenario builder
   |
   v
250 derived historical scenarios
   |
   v
Flask + Gunicorn
   |
   v
Render
   |
   v
Browser
   |-- BUY / PASS / SHORT
   |-- future reveal
   |-- Decision Score
   `-- Trader DNA
```

Keeping the generated scenarios separate from the live API also means the public demo does not need to expose an API key.

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
python run.py
```

Open:

```text
http://127.0.0.1:5050
```

No Nansen API key is required to play the cached production scenarios. A key is only needed for the dataset generation tools.

## Deployment

Production is served with Gunicorn on Render:

```bash
gunicorn run:app
```

Live demo: https://nansen-time-machine.onrender.com

## Quick demo route

For a short walkthrough:

1. Open **AAVE · 2025-10-15**.
2. Select the **+7 day** horizon.
3. Look at the historical flow values and the 100/100 accumulation signal.
4. Lock a BUY decision.
5. Reveal the actual **-10.61%** move.
6. Check the Decision Score and Trader DNA update.

This scenario is a good example because the onchain signal and the later price move disagree.

## Stack

Python · Flask · Gunicorn · Nansen API · HTML/CSS/JavaScript · Render

## Disclaimer

Built for the Nansen Meridian Buildathon. Historical simulations are for demonstration and research purposes and are not financial advice.
