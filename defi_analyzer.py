"""
DeFi analytics over real DefiLlama snapshots saved in data/.

What it computes, all from the saved files:

- Per protocol TVL summary over the most recent 365 days present in the
  snapshot: latest TVL, change over 30 and 90 days, daily return
  volatility, and maximum drawdown.
- An APY spread scan over current pools from the same eight projects:
  median APY per project for pools with at least 1M USD TVL, the spread
  between the highest and lowest project medians, and the widest same
  symbol APY gap across projects for USDC pools.
- Two charts: normalized TVL trends and median APY per project.

What it does not do: there is no wallet clustering in this version. The
original clustered wallet style data the script generated itself and
reported the result as wallet behaviour analysis. No real wallet
dataset is used here, so the step is removed rather than dressed up.
The original also claimed the scan surfaced an arbitrage window that
informed a real capital decision; the data was synthetic, the
committed output contradicted the claimed percentage, and the decision
figure was a hard coded string. None of that is carried over. An APY
spread between lending pools is not an arbitrage trade, and this script
calls it a spread.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
MIN_POOL_TVL = 1_000_000


def main() -> int:
    OUT.mkdir(exist_ok=True)
    tvl = pd.read_csv(DATA / "tvl_history.csv", parse_dates=["date"])
    pools = pd.read_csv(DATA / "pools_snapshot.csv")

    latest_date = tvl["date"].max()
    window_start = latest_date - pd.Timedelta(days=365)
    tvl = tvl[tvl["date"] >= window_start].copy()
    # DefiLlama can return two points for one day (an intraday update).
    # Keep the last one per protocol and day so every reported figure is
    # a value the API actually returned, never an average of two points.
    tvl = tvl.sort_values("date", kind="stable").drop_duplicates(subset=["date", "protocol"], keep="last")
    pivot = tvl.pivot_table(index="date", columns="protocol", values="tvl_usd").sort_index()
    pivot = pivot.ffill()

    summaries = {}
    for proto in pivot.columns:
        s = pivot[proto].dropna()
        if len(s) < 100:
            continue
        returns = s.pct_change().dropna()
        roll_max = s.cummax()
        drawdown = (s / roll_max - 1.0).min()
        summaries[proto] = {
            "latest_tvl_usd": float(s.iloc[-1]),
            "change_30d_pct": float((s.iloc[-1] / s.iloc[-31] - 1) * 100) if len(s) > 31 else None,
            "change_90d_pct": float((s.iloc[-1] / s.iloc[-91] - 1) * 100) if len(s) > 91 else None,
            "daily_return_volatility_pct": float(returns.std() * 100),
            "max_drawdown_pct": float(drawdown * 100),
            "days": int(len(s)),
        }

    big = pools[pools["tvl_usd"] >= MIN_POOL_TVL].copy()
    median_apy = big.groupby("project")["apy"].median().sort_values(ascending=False)
    spread = {
        "highest_project": str(median_apy.index[0]),
        "highest_median_apy_pct": float(median_apy.iloc[0]),
        "lowest_project": str(median_apy.index[-1]),
        "lowest_median_apy_pct": float(median_apy.iloc[-1]),
        "spread_percentage_points": float(median_apy.iloc[0] - median_apy.iloc[-1]),
        "pools_considered": int(len(big)),
        "min_pool_tvl_usd": MIN_POOL_TVL,
    }

    usdc = big[big["symbol"] == "USDC"]
    widest = None
    if len(usdc) >= 2:
        by_project = usdc.groupby("project")["apy"].median().sort_values(ascending=False)
        widest = {
            "symbol": "USDC",
            "highest_project": str(by_project.index[0]),
            "highest_median_apy_pct": float(by_project.iloc[0]),
            "lowest_project": str(by_project.index[-1]),
            "lowest_median_apy_pct": float(by_project.iloc[-1]),
            "gap_percentage_points": float(by_project.iloc[0] - by_project.iloc[-1]),
        }
        spread["widest_same_symbol_gap"] = widest

    card = json.loads((DATA / "data_card.json").read_text())
    metrics = {
        "repo": "defi-analytics-arbitrage",
        "data_snapshot": {
            "tvl_rows_in_window": int(len(tvl)),
            "latest_date": str(latest_date.date()),
            "fetched_at_unix": card["fetched_at_unix"],
            "protocols": sorted(summaries.keys()),
        },
        "protocol_summaries": summaries,
        "apy_spread_scan": spread,
        "note": "TVL and APY figures are computed from the DefiLlama snapshots in data/. An APY spread across lending pools is a rate difference, not an executable arbitrage. No wallet clustering is included; no real wallet dataset was available.",
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    (OUT / "analysis_report.json").write_text(json.dumps(metrics, indent=2) + "\n")

    normalized = pivot / pivot.iloc[0] * 100
    ax = normalized.plot(figsize=(10, 5))
    ax.set_ylabel("TVL, indexed to 100 at window start")
    ax.set_title("Protocol TVL, last 365 days of snapshot (DefiLlama)")
    plt.tight_layout()
    plt.savefig(OUT / "tvl_trends.png", dpi=110)
    plt.close()

    ax = median_apy.plot(kind="bar", figsize=(9, 4))
    ax.set_ylabel("Median APY percent (pools with TVL >= 1M USD)")
    ax.set_title("Median pool APY by project (DefiLlama yields snapshot)")
    plt.tight_layout()
    plt.savefig(OUT / "apy_spread.png", dpi=110)
    plt.close()

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
