"""Test two pre-registered improvements on both periods:
python -m triad_verdict.improvements [--offline]

Both rules were fixed before any result was seen, and nothing is tuned afterwards:

1. Trend filter: never trade against the 200-day trend.
2. Core + shield: 50% equal-weight buy & hold, 50% Triad, rebalanced daily.

Each is reported on the unseen period (2000-2016) and the design period
(2016-2026), against buy & hold and the unchanged Triad.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

import pandas as pd

from .backtest import TriadBacktester
from .config import RiskConfig, TriadConfig
from .data import DataPipeline
from .metrics import TRADING_DAYS, max_drawdown, sharpe_ratio
from .validation import DESIGN_START, ERAS

log = logging.getLogger("triad.improvements")


def buy_hold_returns(data: dict[str, pd.DataFrame]) -> pd.Series:
    closes = pd.DataFrame({n: df["Close"] for n, df in data.items()}).ffill()
    return closes.pct_change().mean(axis=1)


def stats(rets: pd.Series) -> dict:
    rets = rets.dropna()
    eq = (1 + rets).cumprod()
    years = len(rets) / TRADING_DAYS
    return {"Total return": eq.iloc[-1] - 1, "CAGR": eq.iloc[-1] ** (1 / years) - 1,
            "Sharpe": sharpe_ratio(rets), "Max drawdown": max_drawdown(eq),
            "Volatility": rets.std() * TRADING_DAYS ** 0.5}


def table(cols: dict[str, pd.Series]) -> str:
    rows = {k: stats(v) for k, v in cols.items()}
    out = ["| | " + " | ".join(rows) + " |", "|---|" + "---|" * len(rows)]
    for metric in ("Total return", "CAGR", "Sharpe", "Max drawdown", "Volatility"):
        fmt = "{:.2f}" if metric == "Sharpe" else "{:+.1%}"
        out.append(f"| {metric} | " + " | ".join(fmt.format(r[metric]) for r in rows.values()) + " |")
    return "\n".join(out) + "\n"


def era_sharpes(cols: dict[str, pd.Series], eras) -> str:
    out = ["| Era | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for name, a, b in eras:
        cells = []
        for r in cols.values():
            sl = r.loc[a:b].dropna()
            if len(sl) < 60:
                cells.append("n/a")
                continue
            s = stats(sl)
            cells.append(f"{s['Total return']:+.0%} / {s['Sharpe']:.2f} / {s['Max drawdown']:.0%}")
        out.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def run_period(base: TriadConfig, data: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.Series], float]:
    triad = TriadBacktester(base.model_copy(update=dict(label="Triad")), data).run()
    filt = TriadBacktester(base.model_copy(update=dict(label="Triad + trend filter", trend_filter=True)),
                           data).run()
    idx = triad.equity.index
    bh = buy_hold_returns(data).reindex(idx).fillna(0.0)
    r_t = triad.equity.pct_change().fillna(0.0)
    r_f = filt.equity.pct_change().fillna(0.0)
    cols = {
        "Buy & hold": bh,
        "Triad": r_t,
        "Triad + trend filter": r_f,
        "50/50 hold + Triad": 0.5 * bh + 0.5 * r_t,
        "50/50 hold + filtered Triad": 0.5 * bh + 0.5 * r_f,
    }
    corr = float(r_t.corr(bh))
    for k, v in cols.items():
        s = stats(v)
        log.info("  %-28s return %+7.1f%% | Sharpe %.2f | maxDD %6.1f%%", k, s["Total return"] * 100,
                 s["Sharpe"], s["Max drawdown"] * 100)
    return {k: v.iloc[1:] for k, v in cols.items()}, corr


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true", help="reuse data/full_history CSVs")
    ap.add_argument("--report-dir", default="reports")
    ap.add_argument("--log-level", default="WARNING")
    args = ap.parse_args(argv)
    logging.basicConfig(level=args.log_level.upper(), stream=sys.stdout,
                        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s", datefmt="%H:%M:%S")
    log.setLevel(logging.INFO)

    base = TriadConfig(risk=RiskConfig(breaker_cooldown_bars=20))
    pipe = DataPipeline(base.assets, os.path.join("data", "full_history"))
    full = pipe.load_all_cached() if args.offline else pipe.download_market_data("max")

    # The design period keeps a warm-up of history before DESIGN_START so trading starts on it.
    warm = pd.Timedelta(days=int(base.warmup_bars * 1.5))
    periods = {
        "Unseen period (2000-2016)": {n: df[df.index < DESIGN_START] for n, df in full.items()},
        "Design period (2017-2026)": {n: df[df.index >= DESIGN_START - warm] for n, df in full.items()},
    }
    md = ["# 🧪 The Triad Verdict: Two Pre-Registered Improvements", "",
          "Both rules were fixed **before** any result was seen, and nothing was tuned afterwards.", "",
          "1. **Trend filter:** the Triad may only trade in the direction of the 200-day trend "
          "(no shorts while price is above its 200-day average, no longs while below). No new settings.",
          "2. **Core + shield:** 50% equal-weight buy & hold of NQ, ES and GC, 50% Triad, rebalanced daily.", "",
          "Caveat: the unseen period has now been looked at once before (the out-of-sample test), so it "
          "is a second look, not a pristine one. Two ideas were tested, which keeps multiple-testing luck low.", ""]
    all_cols = {}
    for label, data in periods.items():
        log.info("%s", label)
        cols, corr = run_period(base, data)
        all_cols[label] = cols
        md += [f"## {label}", "", table(cols), "",
               f"Daily correlation between the Triad and buy & hold: **{corr:+.2f}**. A low correlation is "
               "what lets a 50/50 mix be smoother than either half.", ""]
    md += ["## By market era: return / Sharpe / max drawdown", "",
           era_sharpes(all_cols["Unseen period (2000-2016)"], ERAS + []), "",
           era_sharpes(all_cols["Design period (2017-2026)"],
                       [("2018-2019 vol shocks", "2018-01-01", "2019-12-31"),
                        ("2020 COVID crash", "2020-01-01", "2020-12-31"),
                        ("2022 bear market", "2022-01-01", "2022-12-31"),
                        ("2023-2026", "2023-01-01", "2026-12-31")]), ""]
    os.makedirs(args.report_dir, exist_ok=True)
    path = os.path.join(args.report_dir, "improvements_report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    log.info("report written to %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
