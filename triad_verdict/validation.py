"""Out-of-sample validation: python -m triad_verdict.validation [--offline]

The system was designed and its ablation inspected on data from 2016-11-07
onwards. Everything before that date was never run during development, so it
is a genuine out-of-sample test (it includes the 2000-02 dot-com bust and the
2008 financial crisis). This script:

1. runs the same ablation ladder on the unseen 2000-2016 period,
2. breaks the headline system down by market era,
3. checks parameter sensitivity (are results knife-edge?),
4. writes reports/out_of_sample_report.md.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

import numpy as np
import pandas as pd

from .__main__ import variants
from .backtest import TriadBacktester
from .config import RiskConfig, TriadConfig
from .data import DataPipeline
from .metrics import max_drawdown, sharpe_ratio
from .report import benchmark_table, metrics_table

log = logging.getLogger("triad.validation")

DESIGN_START = pd.Timestamp("2016-11-07")  # first bar of the data used while building the system

ERAS = [
    ("Dot-com bust & recovery", "2001-01-01", "2007-12-31"),
    ("Global financial crisis", "2008-01-01", "2009-12-31"),
    ("QE bull market", "2010-01-01", "2016-11-06"),
]


def _slice_stats(equity: pd.Series) -> tuple[float, float, float]:
    rets = equity.pct_change().dropna()
    return float(equity.iloc[-1] / equity.iloc[0] - 1), sharpe_ratio(rets), max_drawdown(equity)


def era_table(equity: pd.Series, data: dict[str, pd.DataFrame]) -> str:
    closes = pd.DataFrame({n: df["Close"] for n, df in data.items()}).ffill()
    bh = (1 + closes.pct_change().mean(axis=1).fillna(0)).cumprod()
    lines = ["| Era | Triad return | Triad Sharpe | Triad max DD | Buy & hold return | Buy & hold Sharpe | "
             "Buy & hold max DD |", "|---|---|---|---|---|---|---|"]
    for name, a, b in ERAS:
        eq = equity.loc[a:b]
        if len(eq) < 60:
            continue
        r, s, d = _slice_stats(eq)
        br, bs, bd = _slice_stats(bh.loc[eq.index[0]:eq.index[-1]])
        lines.append(f"| {name} ({eq.index[0].year}-{eq.index[-1].year}) | {r:+.1%} | {s:.2f} | {d:.1%} | "
                     f"{br:+.1%} | {bs:.2f} | {bd:.1%} |")
    return "\n".join(lines) + "\n"


def sensitivity(base: TriadConfig, data: dict[str, pd.DataFrame]) -> str:
    tweaks = [
        ("Headline settings", {}, {}),
        ("Stop 2.0x ATR (tighter)", {"atr_stop_mult": 2.0}, {}),
        ("Stop 3.0x ATR (wider)", {"atr_stop_mult": 3.0}, {}),
        ("Entry threshold 0.20 (trades more)", {}, {"entry_threshold": 0.20}),
        ("Entry threshold 0.30 (trades less)", {}, {"entry_threshold": 0.30}),
        ("Skeptic veto at 45% doubt", {}, {"veto_threshold": 0.45}),
        ("Skeptic veto at 65% doubt", {}, {"veto_threshold": 0.65}),
        ("Kelly fraction 0.10", {"kelly_fraction": 0.10}, {}),
        ("Kelly fraction 0.25", {"kelly_fraction": 0.25}, {}),
    ]
    lines = ["| Variation | Return | Sharpe | Max DD | Trades |", "|---|---|---|---|---|"]
    sharpes = []
    for label, risk_kw, agent_kw in tweaks:
        cfg = base.model_copy(update=dict(
            label=label, risk=base.risk.model_copy(update=risk_kw),
            agents=base.agents.model_copy(update=agent_kw)))
        m = TriadBacktester(cfg, data).run().metrics
        sharpes.append(m.sharpe)
        lines.append(f"| {label} | {m.total_return:+.1%} | {m.sharpe:.2f} | {m.max_drawdown:.1%} | {m.n_trades} |")
    lines.append("")
    lines.append(f"Sharpe range across variations: **{min(sharpes):.2f} to {max(sharpes):.2f}** "
                 f"(median {float(np.median(sharpes)):.2f}).")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Out-of-sample validation for The Triad Verdict")
    ap.add_argument("--offline", action="store_true", help="reuse data/full_history CSVs")
    ap.add_argument("--report-dir", default="reports")
    ap.add_argument("--cooldown", type=int, default=20)
    ap.add_argument("--log-level", default="WARNING")
    args = ap.parse_args(argv)
    logging.basicConfig(level=args.log_level.upper(), stream=sys.stdout,
                        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s", datefmt="%H:%M:%S")
    log.setLevel(logging.INFO)

    base = TriadConfig(risk=RiskConfig(breaker_cooldown_bars=args.cooldown or None), data_period="max")
    pipe = DataPipeline(base.assets, os.path.join("data", "full_history"))
    full = pipe.load_all_cached() if args.offline else pipe.download_market_data("max")
    unseen = {n: df[df.index < DESIGN_START] for n, df in full.items()}
    for n, df in unseen.items():
        log.info("unseen data %s: %d bars %s -> %s", n, len(df), df.index[0].date(), df.index[-1].date())

    results = []
    for cfg in variants(base):
        res = TriadBacktester(cfg, unseen).run()
        m = res.metrics
        log.info("[%s] return %+.1f%% | Sharpe %.2f | maxDD %.1f%% | trades %d",
                 cfg.label, m.total_return * 100, m.sharpe, m.max_drawdown * 100, m.n_trades)
        results.append(res)
    main_res = results[-1]
    m0 = main_res.metrics

    log.info("running parameter sensitivity on unseen data ...")
    sens = sensitivity(base, unseen)

    md = [
        "# 🔬 The Triad Verdict: Out-of-Sample Validation", "",
        f"**Unseen period: {m0.start} → {m0.end}.** The system was designed on data from "
        f"{DESIGN_START.date()} onwards. Nothing before that date was ever run during development, and no "
        "setting was changed after seeing these results.", "",
        "> Data notes: Yahoo continuous front-month futures (unadjusted for rolls). Early gold data has many "
        "zero-volume days (≈40% in 2000-02), which weakens the volume-based signals for gold. The FOMC "
        "calendar starts in 2016, so before that the Skeptic's event check only covers payrolls.", "",
        "## 1. Ablation on unseen data", "",
        metrics_table([r.metrics for r in results]), "",
        "### Benchmarks: unlevered buy & hold over the same unseen window", "",
        benchmark_table(unseen, pd.Timestamp(m0.start), pd.Timestamp(m0.end)), "",
        "## 2. Full Triad by market era", "",
        era_table(main_res.equity, unseen), "",
        "## 3. Parameter sensitivity (full Triad, unseen data)", "",
        "Each row changes one setting. If results collapsed when a setting moves slightly, the headline "
        "numbers would be luck. A flat profile is what you want.", "",
        sens,
    ]
    os.makedirs(args.report_dir, exist_ok=True)
    path = os.path.join(args.report_dir, "out_of_sample_report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    main_res.equity.to_frame().to_csv(os.path.join(args.report_dir, "equity_out_of_sample.csv"))
    log.info("report written to %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
