import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def test_metrics_match_saved_tvl_snapshot():
    tvl = pd.read_csv(ROOT / "data" / "tvl_history.csv", parse_dates=["date"])
    metrics = json.loads((ROOT / "outputs" / "metrics.json").read_text())
    lido = tvl[tvl["protocol"] == "Lido"].sort_values("date")
    assert abs(lido.iloc[-1]["tvl_usd"] - metrics["protocol_summaries"]["Lido"]["latest_tvl_usd"]) < 1.0


def test_all_eight_protocols_present():
    metrics = json.loads((ROOT / "outputs" / "metrics.json").read_text())
    assert len(metrics["protocol_summaries"]) == 8


def test_no_invented_figures_in_analyzer_source():
    src = (ROOT / "defi_analyzer.py").read_text()
    for banned in ["1.2M", "$1.2", "87%", "22%"]:
        assert banned not in src
