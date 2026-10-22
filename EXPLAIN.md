# How this works, in plain words

Two files in data/ are the whole foundation. tvl_history.csv is daily
total value locked per protocol from DefiLlama, 18,029 rows across the
eight protocols. pools_snapshot.csv is the current yields list for the
same projects, 2,876 pools. The analyzer loads the files, aligns the TVL
series on dates, and computes changes, volatility, and drawdowns with
pandas. One data wrinkle worth knowing: DefiLlama sometimes returns
two points for a single day (an intraday revision). The first version
of the analyzer averaged duplicates through a pivot table and quoted a
Lido figure that matched no point the API ever returned. The analyzer
now deduplicates to the last point of each day before anything is
computed, and a test checks the headline TVL equals the raw snapshot
value exactly. The spread scan filters pools to at least 1M USD TVL so dust
pools cannot dominate the medians, then compares median APYs per
project and, separately, the same symbol (USDC) across projects, which
is the only like for like rate comparison in the file.

## What got re scoped from the original

The original script created the data, analysed it, and wrote a press
release about itself. Three specific fabrications are worth being able
to name in an interview: the arbitrage percentage contradicted the
repo's own committed output, the capital reallocation figure was a
string literal, and the clustering accuracy was contradicted by the
score in the same output file (0.24, and an Adjusted Rand Index is not
an accuracy anyway). The rebuild keeps the genuinely useful shape of
the project, protocol comparison over time plus a rate spread scan,
and throws away every number that did not come out of real data.
