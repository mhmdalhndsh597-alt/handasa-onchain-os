"""Read-only asset observability and reserve-evidence exporter.

This module observes public balances at a block. It does not prove ownership,
solvency, legal reserves, or entitlement, and never signs or submits transactions.
"""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

WEI = Decimal(10) ** 18
DEFAULT_RPC_FALLBACKS = (
    "https://ethereum-rpc.publicnode.com",
    "https://rpc.ankr.com/eth",
    "https://1rpc.io/eth",
)




def safe_urlopen(request: urllib.request.Request, timeout: int = 15):
    if urlparse(request.full_url).scheme.lower() not in {"http", "https"}:
        raise ValueError("only HTTP(S) URLs are allowed")
    return urllib.request.urlopen(request, timeout=timeout)  # nosec B310: scheme allowlist above


def rpc_call(rpc_url: str, method: str, params: list) -> object:
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    request = urllib.request.Request(rpc_url, data=payload, headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    with safe_urlopen(request) as response:
        result = json.loads(response.read().decode())
    if result.get("error"):
        raise RuntimeError(f"RPC error: {result['error']}")
    return result.get("result")


def read_json_env(name: str, default: dict) -> dict:
    raw = os.environ.get(name, "").strip()
    return json.loads(raw) if raw else default


def observe_native_balances(rpc_url: str, addresses: list[str], symbol: str, price_usd: Decimal, block: str) -> list[dict]:
    rows = []
    for address in addresses:
        balance = Decimal(int(str(rpc_call(rpc_url, "eth_getBalance", [address, block])), 16)) / WEI
        rows.append({"asset": symbol, "address": address, "balance": str(balance), "price_usd": str(price_usd), "value_usd": str(balance * price_usd)})
    return rows


def consolidate(rpc_url: str, addresses: list[str], prices: dict[str, Decimal], native_symbol: str = "NATIVE") -> dict:
    block_hex = str(rpc_call(rpc_url, "eth_blockNumber", []))
    block = int(block_hex, 16)
    if native_symbol not in prices:
        raise ValueError(f"missing price for {native_symbol}")
    rows = observe_native_balances(rpc_url, addresses, native_symbol, prices[native_symbol], block_hex)
    total = sum((Decimal(row["value_usd"]) for row in rows), Decimal("0"))
    return {"observed_at": datetime.now(timezone.utc).isoformat(), "block": block, "chain_id": os.environ.get("CHAIN_ID", "unknown"),
            "assets": rows, "total_value_usd": str(total), "price_source": os.environ.get("PRICE_SOURCE", "operator-supplied"),
            "ownership_verified": False, "proof_type": "public-balance-observation-only", "transaction_signing": False, "transaction_submission": False}


def main() -> int:
    try:
        urls = [item.strip() for item in os.environ.get("NETWORK_RPC_URLS", "").split(",") if item.strip()]
        primary = os.environ.get("NETWORK_RPC_URL", "").strip()
        if primary:
            urls.insert(0, primary)
        urls.extend(item for item in DEFAULT_RPC_FALLBACKS if item not in urls)
        addresses = [item.strip() for item in os.environ.get("WATCHED_ADDRESSES", "").split(",") if item.strip()]
        prices = {key: Decimal(str(value)) for key, value in read_json_env("ASSET_PRICES_USD", {}).items()}
        if not addresses:
            raise ValueError("WATCHED_ADDRESSES is not configured")
        errors = []
        report = None
        for url in urls:
            try:
                report = consolidate(url, addresses, prices, os.environ.get("NATIVE_SYMBOL", "NATIVE"))
                break
            except Exception as exc:
                errors.append(f"{urlparse(url).netloc}: {exc}")
        if report is None:
            raise RuntimeError("all read-only RPC fallbacks failed: " + " | ".join(errors))
        output = Path(os.environ.get("RESERVES_OUTPUT", "reports/reserves-latest.json"))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 0
    except Exception as exc:
        report = {"status": "degraded", "read_only": True, "reason": str(exc)[:500], "observed_at": datetime.now(timezone.utc).isoformat()}
        output = Path(os.environ.get("RESERVES_OUTPUT", "reports/reserves-latest.json"))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
