"""
Fetches real DeFi data from the public DefiLlama APIs and saves trimmed
snapshots into data/. Two sources, no API key:

- https://api.llama.fi/protocol/<slug> for daily TVL history per protocol
- https://yields.llama.fi/pools for current pool APYs

Slugs are tried in order per protocol and the one that resolves is
recorded in data/data_card.json. If a protocol cannot be fetched the
script fails loudly instead of inventing data.
"""

import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PROTOCOLS = {
    "Uniswap V3": ["uniswap-v3"],
    "Aave V3": ["aave-v3"],
    "Compound": ["compound-finance", "compound-v3"],
    "Curve": ["curve-finance", "curve-dex"],
    "Balancer": ["balancer-v2"],
    "MakerDAO": ["makerdao", "maker"],
    "Lido": ["lido"],
    "Convex": ["convex-finance"],
}

YIELD_PROJECTS = {
    "uniswap-v3",
    "aave-v3",
    "compound-finance",
    "compound-v3",
    "curve-dex",
    "balancer-v2",
    "makerdao",
    "lido",
    "convex-finance",
}


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "defi-analytics-rebuild/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    DATA.mkdir(exist_ok=True)
    fetched_at = int(time.time())
    resolved = {}
    tvl_rows = []
    for label, slugs in PROTOCOLS.items():
        payload = None
        used = None
        for slug in slugs:
            try:
                payload = get_json(f"https://api.llama.fi/protocol/{slug}")
                used = slug
                break
            except Exception as exc:  # recorded, then fail if none worked
                print(f"fetch failed for {label} via {slug}: {exc}")
        if payload is None:
            print(f"could not fetch any slug for {label}")
            return 1
        resolved[label] = used
        for point in payload.get("tvl", []):
            tvl_rows.append(
                {
                    "date": time.strftime("%Y-%m-%d", time.gmtime(point["date"])),
                    "protocol": label,
                    "tvl_usd": point["totalLiquidityUSD"],
                }
            )

    with open(DATA / "tvl_history.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["date", "protocol", "tvl_usd"])
        w.writeheader()
        w.writerows(sorted(tvl_rows, key=lambda r: (r["date"], r["protocol"])))

    pools_payload = get_json("https://yields.llama.fi/pools")
    pool_rows = []
    for pool in pools_payload.get("data", []):
        if pool.get("project") in YIELD_PROJECTS and pool.get("apy") is not None:
            pool_rows.append(
                {
                    "project": pool["project"],
                    "chain": pool.get("chain"),
                    "symbol": pool.get("symbol"),
                    "apy": pool["apy"],
                    "tvl_usd": pool.get("tvlUsd"),
                }
            )
    with open(DATA / "pools_snapshot.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["project", "chain", "symbol", "apy", "tvl_usd"])
        w.writeheader()
        w.writerows(pool_rows)

    card = {
        "source_tvl": "https://api.llama.fi/protocol/<slug> (DefiLlama, public API)",
        "source_yields": "https://yields.llama.fi/pools (DefiLlama, public API)",
        "fetched_at_unix": fetched_at,
        "resolved_slugs": resolved,
        "tvl_rows": len(tvl_rows),
        "pool_rows": len(pool_rows),
        "license_note": "DefiLlama data is public API output; snapshots are saved so the analysis is reproducible offline.",
    }
    (DATA / "data_card.json").write_text(json.dumps(card, indent=2) + "\n")
    print(json.dumps(card, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
