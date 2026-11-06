"""Markdown + CSV reporting, including the Skeptic veto audit."""
from __future__ import annotations

import os
import re
from collections import Counter
from typing import Sequence

import pandas as pd

from .backtest import BacktestResult
from .schemas import BacktestMetrics, Debate, SkepticBrief


# --------------------------------------------------------------------------
# Veto audit: "was the Bear right?"
# --------------------------------------------------------------------------
def simulate_counterfactual(feat: pd.DataFrame, brief: SkepticBrief, atr_mult: float, rr: float,
                            max_bars: int = 60) -> str:
    """Replay a vetoed trade: enter next open, 2.5 ATR stop, 2R target.
    Returns WIN, LOSS or OPEN. Uses future bars on purpose: this is grading
    only, never fed back into decisions."""
    idx = feat.index.get_indexer([pd.Timestamp(brief.date)])[0]
    if idx < 0 or idx + 1 >= len(feat):
        return "OPEN"
    d = brief.proposed_direction.value
    atr = feat["atr14"].iloc[idx]
    entry = feat["open"].iloc[idx + 1]
    stop, tp = entry - d * atr_mult * atr, entry + d * rr * atr_mult * atr
    for j in range(idx + 1, min(idx + 1 + max_bars, len(feat))):
        h, l = feat["high"].iloc[j], feat["low"].iloc[j]
        if (l <= stop) if d > 0 else (h >= stop):
            return "LOSS"
        if (h >= tp) if d > 0 else (l <= tp):
            return "WIN"
    return "OPEN"


def veto_audit(res: BacktestResult) -> dict:
    rc = res.config.risk
    out = {"vetoed": Counter(), "cleared": Counter()}
    for key, briefs in (("vetoed", res.vetoed_briefs), ("cleared", res.cleared_briefs)):
        for b in briefs:
            out[key][simulate_counterfactual(res.features[b.asset], b, rc.atr_stop_mult, rc.min_rr)] += 1
    out["flags"] = Counter(f.code for b in res.vetoed_briefs for f in b.flags)
    return out


def _rate(c: Counter) -> float | None:
    n = c["WIN"] + c["LOSS"]
    return c["WIN"] / n if n else None


def _audit_verdict(audit: dict) -> str:
    v, c = _rate(audit["vetoed"]), _rate(audit["cleared"])
    if v is None or c is None:
        return ""
    if v < c - 0.03:
        return (f"**In this run the vetoes added edge**: vetoed ideas won {v:.1%} vs {c:.1%} for "
                "cleared ones.")
    if v > c + 0.03:
        return (f"**In this run the vetoes cost edge**: vetoed ideas would have won {v:.1%} vs "
                f"{c:.1%} for cleared ones. Any benefit comes from the doubt-based size haircut, "
                "not from picking which trades to kill.")
    return (f"**In this run the vetoes were roughly neutral** ({v:.1%} vetoed vs {c:.1%} cleared). "
            "Compare the 'size haircut only' column: that is where the Skeptic's value shows up.")


def _wr(c: Counter) -> str:
    n = c["WIN"] + c["LOSS"]
    return f"{c['WIN'] / n:.1%}" if n else "n/a"


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------
def _pct(x: float) -> str:
    return f"{x:+.2%}"


def metrics_table(ms: Sequence[BacktestMetrics]) -> str:
    rows = [
        ("Total return", lambda m: _pct(m.total_return)),
        ("CAGR", lambda m: _pct(m.cagr)),
        ("Annualised volatility", lambda m: f"{m.ann_volatility:.2%}"),
        ("Sharpe ratio", lambda m: f"{m.sharpe:.2f}"),
        ("Sortino ratio", lambda m: f"{m.sortino:.2f}"),
        ("Max drawdown", lambda m: f"{m.max_drawdown:.2%}"),
        ("Calmar ratio", lambda m: f"{m.calmar:.2f}"),
        ("Trades", lambda m: str(m.n_trades)),
        ("Win rate", lambda m: f"{m.win_rate:.1%}"),
        ("Profit factor", lambda m: f"{m.profit_factor:.2f}"),
        ("Avg R per trade", lambda m: f"{m.avg_r:+.2f}R"),
        ("Exposure (asset-days in market)", lambda m: f"{m.exposure:.1%}"),
        ("Skeptic vetoes", lambda m: str(m.vetoes)),
        ("Circuit-breaker trips (first)", lambda m: f"{m.breaker_trips} ({m.circuit_breaker_tripped})"
                                                   if m.breaker_trips else "0"),
        ("Final equity", lambda m: f"${m.final_equity:,.0f}"),
    ]
    head = "| Metric | " + " | ".join(m.label for m in ms) + " |\n"
    head += "|---|" + "---|" * len(ms) + "\n"
    return head + "".join(f"| {name} | " + " | ".join(fn(m) for m in ms) + " |\n" for name, fn in rows)


def per_asset_table(res: BacktestResult) -> str:
    df = trades_frame(res)
    if df.empty:
        return "_No trades._\n"
    g = df.groupby("asset")
    t = pd.DataFrame({
        "trades": g.size(), "win_rate": g["pnl"].apply(lambda x: (x > 0).mean()),
        "avg_R": g["r_multiple"].mean(), "net_pnl": g["pnl"].sum(),
    })
    lines = ["| Asset | Trades | Win rate | Avg R | Net P&L |", "|---|---|---|---|---|"]
    for a, r in t.iterrows():
        lines.append(f"| {a} | {int(r.trades)} | {r.win_rate:.1%} | {r.avg_R:+.2f}R | ${r.net_pnl:,.0f} |")
    reasons = df["exit_reason"].value_counts()
    lines += ["", "Exit reasons: " + ", ".join(f"{k} {v}" for k, v in reasons.items())]
    return "\n".join(lines) + "\n"


def debate_markdown(d: Debate) -> str:
    v = d.verdict
    out = [f"#### {v.asset}: close of {v.date}", ""]
    for sig in (d.historian, d.realist):
        out.append(f"**{sig.agent}** ({sig.score:+.2f}, {sig.regime}): {sig.summary}")
        for e in sig.evidence:
            out.append(f"- `{e.factor}` {e.score:+.2f} (w {e.weight:.2f}): {e.note}")
        out.append("")
    if d.skeptic:
        out.append(f"**{d.skeptic.agent}** (doubt {d.skeptic.doubt:.0%}): {d.skeptic.summary}")
        for f in d.skeptic.flags:
            out.append(f"- `{f.code}` severity {f.severity:.2f}: {f.detail}")
        out.append("")
    out.append(f"**⚖️ The Arbiter rules: `{v.action.value}`** (composite {v.composite_score:+.3f})")
    for r in v.rationale:
        out.append(f"- {r}")
    if v.plan:
        p = v.plan
        out.append(f"- Plan: {p.direction.name} {p.units:g} contracts, ref {p.entry_ref:,.2f}, "
                   f"stop {p.stop:,.2f}, take-profit {p.take_profit:,.2f} (1:{p.rr}), "
                   f"risk {p.risk_fraction:.2%} of equity")
    return "\n".join(out) + "\n"


def trades_frame(res: BacktestResult) -> pd.DataFrame:
    return pd.DataFrame([t.model_dump(mode="json") for t in res.trades])


def benchmark_table(data: dict[str, pd.DataFrame], start, end) -> str:
    """Unlevered buy & hold on each contract's price, plus an equal-weight mix."""
    from .metrics import max_drawdown, sharpe_ratio
    closes = pd.DataFrame({n: df["Close"] for n, df in data.items()}).loc[start:end].ffill().dropna()
    rets = closes.pct_change().dropna()
    rets["Equal-weight (daily rebalanced)"] = rets.mean(axis=1)
    lines = ["| Buy & hold | Total return | Sharpe | Max drawdown |", "|---|---|---|---|"]
    for col in rets:
        eq = (1 + rets[col]).cumprod()
        lines.append(f"| {col} | {_pct(eq.iloc[-1] - 1)} | {sharpe_ratio(rets[col]):.2f} | "
                     f"{max_drawdown(eq):.2%} |")
    return "\n".join(lines) + "\n"


def write_report(results: Sequence[BacktestResult], live: dict[str, Debate], out_dir: str,
                 data: dict[str, pd.DataFrame]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    main = results[-1]
    cfg = main.config
    m0 = main.metrics
    md = [
        "# ⚖️ The Triad Verdict: Backtest Report", "",
        f"Period: **{m0.start} → {m0.end}** · Capital ${cfg.initial_capital:,.0f} · "
        f"Assets: {', '.join(a.ticker for a in cfg.assets)}", "",
        "> Research backtest on Yahoo continuous front-month futures (unadjusted for rolls). "
        "Not investment advice.", "",
        "## Risk rules enforced", "",
        f"- Max risk per trade **{cfg.risk.max_risk_per_trade:.0%}** of equity (hard cap in the `TradePlan` schema)",
        f"- Initial stop **{cfg.risk.atr_stop_mult}× ATR({cfg.risk.atr_period})**, then a trailing stop at the same distance that never loosens",
        f"- Take-profit at **1:{cfg.risk.min_rr:g} to 1:{cfg.risk.max_rr:g}** reward:risk (1:2 floor enforced by schema)",
        f"- Circuit breaker: flatten and freeze all trading at **{cfg.risk.max_drawdown:.0%}** drawdown",
        f"- Portfolio heat cap **{cfg.risk.max_portfolio_heat:.0%}**; sizing = {cfg.risk.kelly_fraction:g}× Kelly, "
        "then × (1 − Skeptic doubt), × 0.75 in high-vol regimes", "",
        "## Results: ablation study", "",
        metrics_table([r.metrics for r in results]), "",
        "### Benchmarks: unlevered buy & hold over the same window", "",
        benchmark_table(data, pd.Timestamp(m0.start), pd.Timestamp(m0.end)),
        "The Triad risks at most 2% per idea and spends roughly a third of the time flat, so compare "
        "it on Sharpe and drawdown, not on raw return.", "",
    ]
    if main.config.use_skeptic:
        audit = veto_audit(main)
        md += [
            "## 🔍 Veto audit: was the Skeptic right?", "",
            "Every vetoed trade was replayed with the same 2.5 ATR stop and a 1:2 target, using bars "
            "*after* the decision. This end-of-run audit is for grading only. (The self-calibrating "
            "Skeptic runs its own walk-forward version of it, learning from each shadow trade only "
            "once it has resolved.)", "",
            "| Group | Would-be wins | Would-be losses | Unresolved | Win rate |", "|---|---|---|---|---|",
            f"| Trades the Skeptic **vetoed** | {audit['vetoed']['WIN']} | {audit['vetoed']['LOSS']} | "
            f"{audit['vetoed']['OPEN']} | {_wr(audit['vetoed'])} |",
            f"| Trades the Skeptic **cleared** | {audit['cleared']['WIN']} | {audit['cleared']['LOSS']} | "
            f"{audit['cleared']['OPEN']} | {_wr(audit['cleared'])} |", "",
            "With a 1:2 target, break-even win rate is 33.3%. A useful Skeptic vetoes trades with a "
            "lower win rate than the ones it lets through. "
            + _audit_verdict(audit), "",
            "Most common veto reasons: " + ", ".join(f"`{k}` ×{v}" for k, v in audit["flags"].most_common()), "",
        ]
    md += ["## Per-asset breakdown (full Triad)", "", per_asset_table(main), "",
           "## 🗣️ Latest debate: today's Triad Verdict", ""]
    for d in live.values():
        md.append(debate_markdown(d))
    path = os.path.join(out_dir, "backtest_report.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    for r in results:
        slug = re.sub(r"[^a-z0-9]+", "_", r.config.label.lower().split("(")[0]).strip("_")
        trades_frame(r).to_csv(os.path.join(out_dir, f"trades_{slug}.csv"), index=False)
        r.equity.to_frame().to_csv(os.path.join(out_dir, f"equity_{slug}.csv"))
    return path
