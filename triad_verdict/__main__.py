"""CLI: python -m triad_verdict [--offline] [--period 10y]"""
from __future__ import annotations

import argparse
import logging
import sys

from .backtest import TriadBacktester
from .config import RiskConfig, TriadConfig
from .data import DataPipeline
from .report import write_report

log = logging.getLogger("triad")


def variants(base: TriadConfig) -> list[TriadConfig]:
    """Ablation ladder. The last entry is the headline system."""
    strict_risk = base.risk.model_copy(update=dict(breaker_cooldown_bars=None))
    return [
        base.model_copy(update=dict(label="Prototype (base rules)", mode="prototype",
                                    use_skeptic=False, use_adaptive_trust=False)),
        base.model_copy(update=dict(label="Triad without Skeptic", use_skeptic=False)),
        base.model_copy(update=dict(label="Skeptic: size haircut only, no veto",
                                    agents=base.agents.model_copy(update=dict(veto_threshold=1.0)))),
        base.model_copy(update=dict(label="Triad, static Skeptic", skeptic_self_calibration=False)),
        base.model_copy(update=dict(label="Triad, strict permanent freeze", risk=strict_risk)),
        base.model_copy(update=dict(label="Triad Verdict (full)")),
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The Triad Verdict multi-agent backtest")
    ap.add_argument("--period", default="10y", help="yfinance period (default 10y)")
    ap.add_argument("--capital", type=float, default=1_000_000)
    ap.add_argument("--offline", action="store_true", help="use cached CSVs in --data-dir")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--report-dir", default="reports")
    ap.add_argument("--cooldown", type=int, default=20,
                    help="bars to stay frozen after the 10%% breaker trips (0 = freeze for good)")
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args(argv)

    logging.basicConfig(level=args.log_level.upper(), stream=sys.stdout,
                        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s", datefmt="%H:%M:%S")
    risk = RiskConfig(breaker_cooldown_bars=args.cooldown or None)
    base = TriadConfig(initial_capital=args.capital, data_period=args.period, risk=risk)
    pipe = DataPipeline(base.assets, args.data_dir)
    data = pipe.load_all_cached() if args.offline else pipe.download_market_data(args.period)
    if not data:
        log.error("no market data available")
        return 1

    results = []
    for cfg in variants(base):
        res = TriadBacktester(cfg, data).run()
        m = res.metrics
        log.info("[%s] return %+.2f%% | Sharpe %.2f | maxDD %.2f%% | trades %d | win %.1f%% | vetoes %d",
                 cfg.label, m.total_return * 100, m.sharpe, m.max_drawdown * 100, m.n_trades,
                 m.win_rate * 100, m.vetoes)
        results.append(res)

    main_res = results[-1]
    path = write_report(results, main_res.debates, args.report_dir, data)
    log.info("report written to %s", path)
    for d in main_res.debates.values():
        v = d.verdict
        log.info("TODAY %-13s %-11s composite %+.3f doubt %.0f%%", v.asset, v.action.value,
                 v.composite_score, v.doubt * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
