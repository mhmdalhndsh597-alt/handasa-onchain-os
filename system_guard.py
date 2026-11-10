"""Read-only health guard for scheduled monitoring jobs.

GitHub Actions runners are ephemeral; this guard reports failures and exits non-zero.
It does not restart a daemon or alter a wallet.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from urllib.parse import urlparse


def rpc_call(url: str, method: str, params: list) -> object:
    if urlparse(url).scheme.lower() not in {"http", "https"}:
        raise ValueError("only HTTP(S) RPC URLs are allowed")
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=10) as response:  # nosec B310: scheme allowlist above
        result = json.loads(response.read().decode())
    if result.get("error"):
        raise RuntimeError(str(result["error"]))
    return result.get("result")


def check_rpc(url: str) -> dict:
    started = time.monotonic()
    block = rpc_call(url, "eth_blockNumber", [])
    return {"endpoint": urlparse(url).netloc, "status": "ok", "block": int(str(block), 16), "latency_ms": round((time.monotonic() - started) * 1000, 2)}


def main() -> int:
    urls = [value.strip() for value in os.environ.get("NETWORK_RPC_URLS", os.environ.get("NETWORK_RPC_URL", "")).split(",") if value.strip()]
    if not urls:
        print("No RPC endpoint configured")
        return 1
    results = []
    for url in urls:
        try:
            results.append(check_rpc(url))
        except Exception as exc:
            results.append({"endpoint": urlparse(url).netloc, "status": "failed", "error": str(exc)[:300]})
    print(json.dumps({"checked_at": time.time(), "results": results}, indent=2))
    return 0 if any(item["status"] == "ok" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
