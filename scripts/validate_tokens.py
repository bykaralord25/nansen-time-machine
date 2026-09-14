from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS_PATH = ROOT / "config" / "tokens.json"
ETH_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")


def main() -> None:
    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    if len(tokens) != 25:
        errors.append(f"expected 25 tokens, found {len(tokens)}")

    symbols = set()
    addresses = set()
    for index, token in enumerate(tokens, start=1):
        symbol = str(token.get("symbol", "")).strip()
        chain = str(token.get("chain", "")).strip()
        address = str(token.get("token_address", "")).strip()

        if not symbol:
            errors.append(f"row {index}: missing symbol")
        if chain != "ethereum":
            errors.append(f"{symbol or index}: expected ethereum chain, got {chain!r}")
        if not ETH_ADDRESS.fullmatch(address):
            errors.append(f"{symbol or index}: invalid EVM token address")
        if symbol in symbols:
            errors.append(f"duplicate symbol: {symbol}")
        if address.lower() in addresses:
            errors.append(f"duplicate address: {address}")

        symbols.add(symbol)
        addresses.add(address.lower())

    if errors:
        print("TOKEN VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("TOKEN VALIDATION OK")
    print(f"Tokens: {len(tokens)}")
    print("Chain: ethereum")
    print("No placeholders, malformed addresses or duplicates found.")


if __name__ == "__main__":
    main()
