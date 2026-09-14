from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "data" / "call_plan.json"
CACHE_DIR = ROOT / "data" / "raw"
LEDGER_PATH = ROOT / "data" / "call_ledger.jsonl"
BASE_URL = "https://api.nansen.ai"
RETRYABLE = {429, 502, 503, 504}


def task_id(task: dict) -> str:
    raw = json.dumps({"path": task["path"], "payload": task["payload"]}, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()[:24]


def append_ledger(row: dict) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Run a small, safe, resumable Nansen dataset batch.")
    p.add_argument("--limit", type=int, default=10, help="Maximum uncached calls to attempt")
    p.add_argument("--execute", action="store_true", help="Actually send requests; otherwise dry-run")
    args = p.parse_args()

    if args.limit < 1 or args.limit > 100:
        raise SystemExit("For safety, --limit must be between 1 and 100.")

    load_dotenv(ROOT / ".env")
    key = os.getenv("NANSEN_API_KEY")
    if args.execute and not key:
        raise SystemExit("NANSEN_API_KEY missing from .env")
    if not PLAN_PATH.exists():
        raise SystemExit("data/call_plan.json missing. Run scripts/build_call_plan.py first.")

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    pending = [x for x in plan if not (CACHE_DIR / f"{task_id(x)}.json").exists()]
    selected = pending[: args.limit]

    print(f"Plan calls: {len(plan)} | Cached: {len(plan)-len(pending)} | Pending: {len(pending)}")
    print(f"Selected: {len(selected)} | Mode: {'EXECUTE' if args.execute else 'DRY-RUN'}")
    print(f"Estimated selected credits: {sum(x.get('estimated_credits', 0) for x in selected)}")
    if not args.execute:
        for i, t in enumerate(selected, 1):
            print(f"{i:02d}. {t['symbol']} {t['snapshot_date']} {t['kind']} -> {t['path']}")
        print("No API requests sent.")
        return

    ok = failed = credits = 0
    session = requests.Session()
    headers = {"apikey": key, "Content-Type": "application/json"}

    for i, task in enumerate(selected, 1):
        tid = task_id(task)
        status = None
        response = None
        error = None
        for attempt in range(4):
            try:
                response = session.post(BASE_URL + task["path"], headers=headers, json=task["payload"], timeout=45)
                status = response.status_code
                if status not in RETRYABLE:
                    break
                wait = int(response.headers.get("Retry-After", "0") or 0) or min(2 ** attempt, 8)
                time.sleep(wait)
            except requests.RequestException as exc:
                error = str(exc)
                if attempt == 3:
                    break
                time.sleep(min(2 ** attempt, 8))

        actual_credit = None
        if response is not None:
            raw_credit = response.headers.get("X-Nansen-Credits-Cost")
            try:
                actual_credit = int(float(raw_credit)) if raw_credit is not None else None
            except ValueError:
                actual_credit = None
            if actual_credit is not None:
                credits += actual_credit

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": tid,
            "symbol": task["symbol"],
            "snapshot_date": task["snapshot_date"],
            "kind": task["kind"],
            "path": task["path"],
            "status": status,
            "credits_cost": actual_credit,
            "request_id": response.headers.get("X-Request-Id") if response is not None else None,
            "credits_remaining": response.headers.get("X-Nansen-Credits-Remaining") if response is not None else None,
            "error": error,
        }
        append_ledger(row)

        if response is not None and response.ok:
            try:
                body = response.json()
            except ValueError:
                body = {"raw_text": response.text}
            (CACHE_DIR / f"{tid}.json").write_text(json.dumps({"task": task, "response": body}, ensure_ascii=False, indent=2), encoding="utf-8")
            ok += 1
            print(f"[{i}/{len(selected)}] OK {status} {task['symbol']} {task['kind']} credits={actual_credit}")
        else:
            failed += 1
            preview = response.text[:300].replace("\n", " ") if response is not None else error
            print(f"[{i}/{len(selected)}] FAIL status={status} {task['symbol']} {task['kind']} :: {preview}")

    print("---")
    print(f"Batch finished: OK={ok} FAILED={failed} actual_header_credits={credits}")
    print(f"Ledger: {LEDGER_PATH}")
    print(f"Cache: {CACHE_DIR}")


if __name__ == "__main__":
    main()
