# DeFi Analytics

I built a small analytics pipeline over real DeFi protocol data from
the public DefiLlama APIs. It pulls daily TVL history for eight
protocols and a current yields snapshot, saves both snapshots in
`data/`, and computes everything from those saved files, so the run is
reproducible offline.

## What the current snapshot says

Fetched 2026-10-22 (exact time in `data/data_card.json`). Latest TVL,
largest first: Lido 23.00B USD, Aave V3 16.87B, MakerDAO 5.62B, Uniswap
V3 1.69B, Compound 1.50B, Curve 1.28B, Convex 0.58B, Balancer 0.02B.
Balancer reads low because that is what DefiLlama reports for the
balancer-v2 slug now; I report the data as it comes rather than
adjusting it. Ninety day changes range from Balancer down 37.6 percent
to Lido up 32.1 percent, and every protocol shows a maximum drawdown of
at least 33 percent inside the window, which says more about the year
in crypto than about any single protocol.

The APY spread scan covers 522 pools with at least 1M USD TVL across
the eight projects. Median pool APY runs from 5.28 percent on
convex-finance down to 0.0 percent on compound-v3 (many of its listed
pools report zero), a 5.28 point spread. The cleaner comparison is the
same symbol across projects: USDC medians are 3.66 percent on aave-v3
and 3.22 percent on compound-v3, a gap of 0.45 points. A spread like
that is a rate difference, not an arbitrage trade; moving funds has
costs and risks this script does not model, and I do not call it one.

## Deleted claims from the original

The first version of this repo generated its own synthetic data and
then reported on it as if it were the market. Specifically:

- It claimed a 22 percent arbitrage opportunity window that informed a
  1.2M USD capital reallocation. The data was made up, the committed
  output file recorded 99.7 percent rather than 22, and the 1.2M figure
  was a hard coded string the script wrote into its own report. All
  deleted.
- It reported 87 percent clustering accuracy for wallet segmentation.
  The wallets were simulated from hand built distributions and the
  committed output recorded a 0.24 score. The clustering step is
  removed entirely in this version because I have no real wallet
  dataset to run it on, and clustering self generated data proves
  nothing.

## Run it

```
python3 scripts/fetch_data.py   # refreshes the snapshots in data/
python3 defi_analyzer.py        # writes outputs/metrics.json and charts
pytest tests/
```

## Results location

`outputs/metrics.json` holds every number quoted above, with the two
charts at `outputs/tvl_trends.png` and `outputs/apy_spread.png`.
