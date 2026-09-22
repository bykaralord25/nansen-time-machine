# Nansen Time Machine

A historical onchain trading simulator built for the Nansen Meridian Buildathon.

Pick a token and a past date, look at the Nansen data that was available at the time, make a BUY / PASS / SHORT decision, then reveal what happened over the next 1, 7 or 30 days.

Live demo: https://nansen-time-machine.onrender.com

## Current build

- 250 historical snapshots across 25 Ethereum assets
- Dataset built from 1,000 Nansen API calls
- BUY / PASS / SHORT decisions
- 1d / 7d / 30d outcomes
- Decision Score
- Trader DNA session stats
- No future data shown before the decision

## How it works

Each snapshot contains historical token flow data and price context. The future price window stays hidden until the player locks a decision.

The dataset was built with:

- Historical Token Flow Summary
- Token OHLCV

For each of the 250 token/date combinations, the dataset builder made one flow request and three OHLCV requests. The app uses the resulting cached scenarios at runtime, so playing the demo does not use additional Nansen API credits.

The signal shown in the UI combines:

- Smart Trader net flow — 35%
- Whale net flow — 25%
- Top PnL net flow — 25%
- Exchange net flow — 15%, inverted

The individual values are shown as well, so the composite signal is not the only information available to the player.

## Example

AAVE on 2025-10-15 is a useful case. The +7 day snapshot produced a Strong Accumulation signal (100/100), but the price later moved -10.61%.

That is the point of the simulator: the signal is context, not the answer.

## Project structure

```text
Nansen API
  -> local cache
  -> scenario builder
  -> 250 historical scenarios
  -> Flask app
  -> Render
```

Raw API responses, request logs and API credentials are not included in the public repository. The derived scenario data needed by the demo is included.

## Run locally

```bash
python -m venv .venv
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5050`.

The cached scenarios do not require a Nansen API key. A key is only needed when rebuilding the dataset.

## Deployment

```bash
gunicorn run:app
```

## Stack

Python, Flask, Gunicorn, Nansen API, HTML/CSS/JavaScript, Render.

## Disclaimer

Built for the Nansen Meridian Buildathon. Historical results are for demonstration purposes and are not financial advice.
