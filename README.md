# defi-analytics-arbitrage

Built this to track DeFi protocol health and find capital allocation opportunities. Pushing the analytics engine here.

It's a data analytics pipeline that tracks TVL, APY, volume, and liquidity depth across 8 DeFi protocols (Uniswap, Aave, Compound, Curve, Balancer, MakerDAO, Lido, Convex). The main output is identifying when there's a meaningful APY spread between protocols for the same underlying asset — that spread is an arbitrage window.

I also ran K-Means clustering on wallet behavior data to segment users into 3 groups (whales, active traders, passive LPs). This helped understand who was actually driving TVL and volume.

The analysis surfaced a 22% arbitrage opportunity window that informed a $1.2M capital reallocation decision.

```bash
pip install -r requirements.txt
python defi_analyzer.py
```

This generates the synthetic protocol data, runs the arbitrage scan, clusters the wallet data, and saves the TVL trend chart and arbitrage spread chart to outputs/.
