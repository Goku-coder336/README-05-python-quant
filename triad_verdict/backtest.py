"""Event-driven backtester.

Each trading day is processed as a sequence of events through one queue:

    MarketEvent(open)  -> fill orders queued last night        (FillEvent)
    MarketEvent(bar)   -> stops / take-profits hit intrabar    (FillEvent)
    MarketEvent(close) -> mark-to-market, circuit breaker,
                          trail stops, grade agents,
                          run the debate                       (SignalEvent -> OrderEvent)

Orders decided at the close of day t fill at the open of day t+1, so no
decision ever sees the price it trades at.
"""
from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import numpy as np
import pandas as pd

from .agents import (ArbiterAgent, HistorianAgent, LegacyHistorian, LegacyRealist, RealistAgent,
                     SkepticAgent)
from .config import AssetSpec, TriadConfig
from .features import compute_features, ready_mask
from .metrics import compute_metrics
from .schemas import (Action, Debate, Direction, MarketSnapshot, PortfolioContext, Trade,
                      Verdict)

log = logging.getLogger("triad.backtest")

SNAP_FIELDS = list(MarketSnapshot.model_fields)


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class MarketEvent:
    phase: str  # "open" | "bar" | "close"
    bar: int
    date: date


@dataclass(frozen=True)
class SignalEvent:
    debate: Debate


@dataclass(frozen=True)
class OrderEvent:
    asset: str
    kind: str  # "ENTRY" | "EXIT"
    verdict: Verdict


@dataclass(frozen=True)
class FillEvent:
    asset: str
    kind: str
    price: float
    date: date
    reason: str
    verdict: Optional[Verdict] = None


@dataclass
class Position:
    asset: str
    direction: Direction
    units: float
    entry_price: float
    entry_date: date
    entry_bar: int
    stop: float
    initial_stop: float
    take_profit: float
    stop_distance: float
    risk_amount: float
    doubt: float
    commission_paid: float = 0.0

    def open_risk(self, spec: AssetSpec) -> float:
        """Cash lost if the current stop is hit (0 once the stop locks in profit)."""
        d = self.direction.value
        return max(0.0, d * (self.entry_price - self.stop)) * self.units * spec.multiplier


@dataclass
class BacktestResult:
    config: TriadConfig
    equity: pd.Series
    trades: list[Trade]
    verdicts: list[Verdict]
    debates: dict[str, Debate]
    metrics: object
    action_counts: dict[str, int] = field(default_factory=dict)
    breaker_date: Optional[date] = None
    vetoed_briefs: list = field(default_factory=list)
    cleared_briefs: list = field(default_factory=list)
    features: dict = field(default_factory=dict)


# --------------------------------------------------------------------------
# Engine
# --------------------------------------------------------------------------
class TriadBacktester:
    def __init__(self, cfg: TriadConfig, data: dict[str, pd.DataFrame]):
        self.cfg = cfg
        self.specs = {s.name: s for s in cfg.assets if s.name in data}
        self.features = {
            name: compute_features(df, cfg.agents.volume_profile_window, cfg.agents.volume_profile_bins,
                                   cfg.risk.atr_period)
            for name, df in data.items() if name in self.specs
        }
        self.ready = {n: ready_mask(f) for n, f in self.features.items()}
        if cfg.mode == "prototype":
            self.historian, self.realist = LegacyHistorian(), LegacyRealist()
        else:
            self.historian, self.realist = HistorianAgent(), RealistAgent()
        self.skeptic = (SkepticAgent(cfg.agents.veto_threshold, cfg.skeptic_self_calibration)
                        if cfg.use_skeptic else None)
        self.arbiter = ArbiterAgent(cfg)

        self.calendar = sorted(set().union(*[f.index for f in self.features.values()]))
        self.bar_index = {ts: i for i, ts in enumerate(self.calendar)}
        self.last_close: dict[str, float] = {}
        self.queue: deque = deque()
        self.cash = cfg.initial_capital  # realised equity
        self.positions: dict[str, Position] = {}
        self.pending_orders: dict[str, OrderEvent] = {}
        self.trades: list[Trade] = []
        self.verdicts: list[Verdict] = []
        self.last_debate: dict[str, Debate] = {}
        self.outcomes: dict[str, list[bool]] = defaultdict(list)
        self.equity_curve: list[tuple[date, float]] = []
        self.peak = cfg.initial_capital
        self.frozen = False
        self.frozen_until: Optional[int] = None
        self.breaker_date: Optional[date] = None
        self.breaker_trips = 0
        self.recovery_target: Optional[float] = None
        self.returns = pd.DataFrame({n: f["close"].pct_change() for n, f in self.features.items()})
        self.vetoes = 0
        self.vetoed_briefs: list = []
        self.cleared_briefs: list = []
        self.action_counts: dict[str, int] = defaultdict(int)
        self.exposed_days = 0

    # ---------------------------------------------------------------- utils
    def _row(self, asset: str, ts) -> Optional[pd.Series]:
        f = self.features[asset]
        if ts not in f.index:
            return None
        return f.loc[ts]

    def _snapshot(self, asset: str, ts) -> Optional[MarketSnapshot]:
        if ts not in self.features[asset].index or not self.ready[asset].loc[ts]:
            return None
        row = self.features[asset].loc[ts]
        payload = {k: row[k] for k in SNAP_FIELDS if k in row.index}
        payload.update(asset=asset, date=ts.date(), seasonal_n=int(row["seasonal_n"]))
        return MarketSnapshot(**payload)

    def _slip(self, spec: AssetSpec) -> float:
        return self.cfg.risk.slippage_ticks * spec.tick_size

    def _commission(self, spec: AssetSpec, units: float) -> float:
        return spec.commission_per_contract * units

    def _mtm_equity(self, ts) -> float:
        eq = self.cash
        for name, pos in self.positions.items():
            row = self._row(name, ts)
            px = row["close"] if row is not None else self.last_close.get(name, pos.entry_price)
            eq += pos.direction.value * (px - pos.entry_price) * pos.units * self.specs[name].multiplier
        return eq

    def _open_heat(self, equity: float) -> float:
        return sum(p.open_risk(self.specs[n]) for n, p in self.positions.items()) / max(equity, 1e-9)

    # --------------------------------------------------------------- events
    def run(self) -> BacktestResult:
        warm = self.cfg.warmup_bars
        start_idx = min(warm, len(self.calendar) - 1)
        log.info("[%s] backtesting %s -> %s (%d bars, warm-up %d)", self.cfg.label,
                 self.calendar[start_idx].date(), self.calendar[-1].date(),
                 len(self.calendar) - start_idx, warm)
        for i in range(start_idx, len(self.calendar)):
            ts = self.calendar[i]
            for phase in ("open", "bar", "close"):
                self.queue.append(MarketEvent(phase, i, ts))
                self._drain()
        # Close anything still open at the last close so P&L is realised.
        last = self.calendar[-1]
        for name in list(self.positions):
            row = self._row(name, last)
            if row is not None:
                self._close_position(name, float(row["close"]), last.date(), "END_OF_DATA", i)
        equity = pd.Series(dict(self.equity_curve), name="equity")
        equity.index = pd.to_datetime(equity.index)
        exposure = self.exposed_days / max(1, len(equity) * len(self.specs))
        metrics = compute_metrics(self.cfg, equity, self.trades, self.vetoes, exposure, self.breaker_date,
                                  self.breaker_trips)
        return BacktestResult(self.cfg, equity, self.trades, self.verdicts, self.last_debate, metrics,
                              dict(self.action_counts), self.breaker_date, self.vetoed_briefs,
                              self.cleared_briefs, self.features)

    def _drain(self) -> None:
        while self.queue:
            ev = self.queue.popleft()
            if isinstance(ev, MarketEvent):
                getattr(self, f"_on_{ev.phase}")(ev)
            elif isinstance(ev, SignalEvent):
                self._on_signal(ev)
            elif isinstance(ev, FillEvent):
                self._on_fill(ev)

    # open: fill last night's orders --------------------------------------
    def _on_open(self, ev: MarketEvent) -> None:
        for name in list(self.pending_orders):
            row = self._row(name, ev.date)
            if row is None:
                continue  # market closed today: order waits
            order = self.pending_orders.pop(name)
            spec = self.specs[name]
            if order.kind == "EXIT" and name in self.positions:
                d = self.positions[name].direction.value
                self.queue.append(FillEvent(name, "EXIT", row["open"] - d * self._slip(spec),
                                            ev.date.date(), "SIGNAL_FLIP"))
            elif order.kind == "ENTRY" and name not in self.positions and not self.frozen:
                plan = order.verdict.plan
                px = row["open"] + plan.direction.value * self._slip(spec)
                self.queue.append(FillEvent(name, "ENTRY", px, ev.date.date(), order.verdict.action.value,
                                            order.verdict))

    # bar: intrabar stop / take-profit -----------------------------------
    def _on_bar(self, ev: MarketEvent) -> None:
        for name, pos in list(self.positions.items()):
            row = self._row(name, ev.date)
            if row is None:
                continue
            spec, d = self.specs[name], pos.direction.value
            o, h, l = row["open"], row["high"], row["low"]
            stop_hit = (l <= pos.stop) if d > 0 else (h >= pos.stop)
            tp_hit = (h >= pos.take_profit) if d > 0 else (l <= pos.take_profit)
            if stop_hit:  # conservative: if both touched, assume the stop came first
                gapped = (o <= pos.stop) if d > 0 else (o >= pos.stop)
                px = (o if gapped else pos.stop) - d * self._slip(spec)
                reason = "TRAILING_STOP" if d * (pos.stop - pos.initial_stop) > 0 else "STOP_LOSS"
                self.queue.append(FillEvent(name, "EXIT", px, ev.date.date(), reason))
            elif tp_hit:
                gapped = (o >= pos.take_profit) if d > 0 else (o <= pos.take_profit)
                px = o if gapped else pos.take_profit
                self.queue.append(FillEvent(name, "EXIT", px, ev.date.date(), "TAKE_PROFIT"))

    # close: risk checks, trailing, the debate ---------------------------
    def _on_close(self, ev: MarketEvent) -> None:
        ts = ev.date
        for name in self.specs:
            row = self._row(name, ts)
            if row is not None:
                self.last_close[name] = float(row["close"])
        equity = self._mtm_equity(ts)
        rc = self.cfg.risk
        if self.frozen and self.frozen_until is not None and ev.bar >= self.frozen_until:
            self.frozen, self.frozen_until = False, None
            self.recovery_target = self.peak
            self.peak = equity  # re-baseline the breaker; reduced risk until the old peak is regained
            log.warning("[%s] breaker cooldown over on %s: resuming at %gx risk until equity regains %.0f",
                        self.cfg.label, ts.date(), rc.post_breaker_risk_scalar, self.recovery_target)
        if self.recovery_target is not None and equity >= self.recovery_target:
            log.info("[%s] %s: pre-breaker peak recovered, full risk restored", self.cfg.label, ts.date())
            self.recovery_target = None
        if not self.frozen:
            self.peak = max(self.peak, equity)
        dd = 1 - equity / self.peak
        if not self.frozen and dd >= rc.max_drawdown:
            self.frozen = True
            self.breaker_trips += 1
            self.breaker_date = self.breaker_date or ts.date()
            if rc.breaker_cooldown_bars:
                self.frozen_until = ev.bar + rc.breaker_cooldown_bars
            log.warning("[%s] CIRCUIT BREAKER: drawdown %.2f%% on %s, flattening and freezing%s",
                        self.cfg.label, dd * 100, ts.date(),
                        f" for {rc.breaker_cooldown_bars} bars" if rc.breaker_cooldown_bars else " permanently")
            for name in list(self.positions):
                d = self.positions[name].direction.value
                px = self.last_close[name] - d * self._slip(self.specs[name])
                self._close_position(name, px, ts.date(),
                                     "CIRCUIT_BREAKER", ev.bar)
            self.pending_orders.clear()
            equity = self._mtm_equity(ts)
        self.equity_curve.append((ts.date(), equity))
        self.exposed_days += len(self.positions)

        # Chandelier-style trailing stop: never loosens.
        k = self.cfg.risk.atr_stop_mult
        for name, pos in self.positions.items():
            row = self._row(name, ts)
            if row is None or np.isnan(row["atr14"]):
                continue
            d = pos.direction.value
            candidate = row["close"] - d * k * row["atr14"]
            if d * (candidate - pos.stop) > 0:
                pos.stop = float(candidate)

        # Grade agents (and the Skeptic's flags) on calls that have now resolved.
        for name in self.specs:
            row = self._row(name, ts)
            if row is not None:
                self.arbiter.trust.resolve(name, ev.bar, float(row["close"]))
                if self.skeptic is not None:
                    self.skeptic.ledger.resolve(name, ev.bar, float(row["high"]), float(row["low"]))

        snaps = {n: self._snapshot(n, ts) for n in self.specs}
        signals = {}
        for n, s in snaps.items():
            if s is not None:
                signals[n] = (self.historian.analyze(s), self.realist.analyze(s))
                self.arbiter.trust.record(n, ev.bar, s.close,
                                          {"historian": signals[n][0].score, "realist": signals[n][1].score})
        for n, s in snaps.items():
            if s is None:
                continue
            h, r = signals[n]
            spec = self.specs[n]
            pos = self.positions.get(n)
            corr_long, corr_short = self._correlated_risk(n, ts, equity)
            ctx = PortfolioContext(
                equity=max(equity, 1.0), open_heat=self._open_heat(equity),
                position_direction=pos.direction if pos else Direction.FLAT,
                circuit_breaker_active=self.frozen,
                recent_outcomes=tuple(self.outcomes[n][-20:]),
                correlated_risk_long=corr_long, correlated_risk_short=corr_short,
                risk_scalar=rc.post_breaker_risk_scalar if self.recovery_target is not None else 1.0,
            )
            peers = {p: signals[p][1] for p in signals
                     if p != n and spec.equity_index and self.specs[p].equity_index}
            skeptic_fn = None
            if self.skeptic is not None:
                def skeptic_fn(direction, s=s, h=h, r=r, peers=peers, n=n):
                    return self.skeptic.challenge(s, direction, h, r, peers, self.outcomes[n])
            verdict, brief = self.arbiter.deliberate(spec, s, h, r, ctx, skeptic_fn)
            if brief is not None:
                self.skeptic.ledger.track(n, ev.bar, s.close, s.atr14, brief.proposed_direction.value,
                                          tuple(f.code for f in brief.flags), rc.atr_stop_mult, rc.min_rr)
            self.queue.append(SignalEvent(Debate(historian=h, realist=r, skeptic=brief, verdict=verdict)))

    def _on_signal(self, ev: SignalEvent) -> None:
        v = ev.debate.verdict
        self.last_debate[v.asset] = ev.debate
        self.action_counts[v.action.value] += 1
        if v.action != Action.HOLD:
            self.verdicts.append(v)
        if v.action == Action.SKIP and any("VETOED" in x for x in v.rationale):
            self.vetoes += 1
            self.vetoed_briefs.append(ev.debate.skeptic)
        elif ev.debate.skeptic is not None and v.plan is not None:
            self.cleared_briefs.append(ev.debate.skeptic)
            log.debug("%s %s vetoed: %s", v.date, v.asset, ev.debate.skeptic.summary)
        if v.action in (Action.ENTER_LONG, Action.ENTER_SHORT):
            self.pending_orders[v.asset] = OrderEvent(v.asset, "ENTRY", v)
        elif v.action == Action.EXIT:
            self.pending_orders[v.asset] = OrderEvent(v.asset, "EXIT", v)

    def _on_fill(self, ev: FillEvent) -> None:
        spec = self.specs[ev.asset]
        if ev.kind == "EXIT":
            if ev.asset in self.positions:
                self._close_position(ev.asset, ev.price, ev.date, ev.reason, self._bar_of(ev.date))
            return
        # ENTRY: rebuild stop/TP around the actual fill, keeping R and RR.
        order_plan = ev.verdict.plan
        d = order_plan.direction.value
        stop = ev.price - d * order_plan.stop_distance
        tp = ev.price + d * order_plan.rr * order_plan.stop_distance
        fee = self._commission(spec, order_plan.units)
        self.cash -= fee
        self.positions[ev.asset] = Position(
            asset=ev.asset, direction=order_plan.direction, units=order_plan.units, entry_price=ev.price,
            entry_date=ev.date, entry_bar=self._bar_of(ev.date), stop=stop, initial_stop=stop,
            take_profit=tp, stop_distance=order_plan.stop_distance,
            risk_amount=order_plan.stop_distance * order_plan.units * spec.multiplier,
            doubt=ev.verdict.doubt, commission_paid=fee,
        )
        log.debug("%s FILL %s %s %.2f x%g stop %.2f tp %.2f", ev.date, ev.asset,
                  order_plan.direction.name, ev.price, order_plan.units, stop, tp)

    # --------------------------------------------------------------- helpers
    def _correlated_risk(self, asset: str, ts, equity: float) -> tuple[float, float]:
        """Open risk in positions highly correlated with `asset`, split by which
        new direction (long/short) would stack on top of it."""
        if not self.positions:
            return 0.0, 0.0
        rc = self.cfg.risk
        window = self.returns.loc[:ts].tail(rc.corr_window)
        long_r = short_r = 0.0
        for other, pos in self.positions.items():
            if other == asset:
                continue
            rho = window[asset].corr(window[other])
            if np.isnan(rho) or abs(rho) < rc.cluster_corr_threshold:
                continue
            risk = pos.open_risk(self.specs[other]) / max(equity, 1e-9)
            # A long here behaves like (pos.direction * sign(rho)) exposure to `other`.
            if pos.direction.value * np.sign(rho) > 0:
                long_r += risk
            else:
                short_r += risk
        return long_r, short_r

    def _bar_of(self, d: date) -> int:
        return self.bar_index[pd.Timestamp(d)]

    def _close_position(self, asset: str, price: float, when: date, reason: str, bar: int) -> None:
        pos = self.positions.pop(asset)
        spec = self.specs[asset]
        d = pos.direction.value
        fee = self._commission(spec, pos.units)
        gross = d * (price - pos.entry_price) * pos.units * spec.multiplier
        self.cash += gross - fee
        pnl = gross - fee - pos.commission_paid
        r_mult = pnl / pos.risk_amount if pos.risk_amount > 0 else 0.0
        self.outcomes[asset].append(bool(pnl > 0))
        self.trades.append(Trade(
            asset=asset, direction=pos.direction, entry_date=pos.entry_date, exit_date=when,
            entry_price=round(pos.entry_price, 4), exit_price=round(float(price), 4), units=pos.units,
            initial_stop=round(pos.initial_stop, 4), take_profit=round(pos.take_profit, 4),
            risk_amount=round(pos.risk_amount, 2), pnl=round(pnl, 2), r_multiple=round(r_mult, 3),
            exit_reason=reason, bars_held=max(0, bar - pos.entry_bar), doubt_at_entry=pos.doubt,
        ))
        log.debug("%s CLOSE %s %s @ %.2f pnl %.0f (%.2fR) %s", when, asset, pos.direction.name,
                  price, pnl, r_mult, reason)
