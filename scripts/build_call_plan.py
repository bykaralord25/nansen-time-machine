from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS_PATH = ROOT / "config" / "tokens.json"
OUT_PATH = ROOT / "data" / "call_plan.json"

SNAPSHOT_DATES = [
    "2025-10-15",
    "2025-11-15",
    "2025-12-15",
    "2026-01-15",
    "2026-02-15",
    "2026-03-15",
    "2026-04-15",
    "2026-05-15",
    "2026-06-15",
    "2026-07-15",
]


def iso_add(d: str, days: int) -> str:
    return (date.fromisoformat(d) + timedelta(days=days)).isoformat()


def main() -> None:
    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    if len(tokens) != 25:
        raise SystemExit(f"Expected 25 tokens, found {len(tokens)}")

    calls = []
    for token in tokens:
        for snapshot in SNAPSHOT_DATES:
            common = {
                "symbol": token["symbol"],
                "chain": token["chain"],
                "token_address": token["token_address"],
                "snapshot_date": snapshot,
            }

            # 1 historical intelligence call + 3 price-context/reveal calls.
            # 25 tokens x 10 dates x 4 calls = exactly 1,000 meaningful calls.
            calls.append({
                **common,
                "kind": "historical_flow_summary",
                "path": "/api/v1beta1/tgm/historical-token-flow-summary",
                "payload": {
                    "chain": token["chain"],
                    "token_address": token["token_address"],
                    "date_range": {"from": iso_add(snapshot, -7), "to": snapshot},
                    "apply_blacklist_filter": True,
                },
                "estimated_credits": 5,
            })

            calls.append({
                **common,
                "kind": "ohlcv_context",
                "path": "/api/v1/tgm/token-ohlcv",
                "payload": {
                    "chain": token["chain"],
                    "token_address": token["token_address"],
                    "date": {"from": iso_add(snapshot, -7), "to": snapshot},
                    "timeframe": "1d",
                },
                "estimated_credits": 1,
            })

            calls.append({
                **common,
                "kind": "ohlcv_reveal_7d",
                "path": "/api/v1/tgm/token-ohlcv",
                "payload": {
                    "chain": token["chain"],
                    "token_address": token["token_address"],
                    "date": {"from": snapshot, "to": iso_add(snapshot, 7)},
                    "timeframe": "1d",
                },
                "estimated_credits": 1,
            })

            calls.append({
                **common,
                "kind": "ohlcv_reveal_30d",
                "path": "/api/v1/tgm/token-ohlcv",
                "payload": {
                    "chain": token["chain"],
                    "token_address": token["token_address"],
                    "date": {"from": iso_add(snapshot, 8), "to": iso_add(snapshot, 30)},
                    "timeframe": "1d",
                },
                "estimated_credits": 1,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(calls, indent=2), encoding="utf-8")
    estimated = sum(x["estimated_credits"] for x in calls)
    print(f"Wrote {len(calls)} calls to {OUT_PATH}")
    print(f"Estimated credits: {estimated}")
    print("Plan: 250 historical snapshots, exactly 1,000 meaningful API calls.")


if __name__ == "__main__":
    main()
