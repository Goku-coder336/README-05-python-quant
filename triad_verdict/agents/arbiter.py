"""The Arbiter: weighs the debate and sizes the trade.

Confidence matrix
-----------------
Base weights depend on the volatility regime (slow history counts for more in
calm markets, the live tape for more in turbulent ones). Each weight is then
multiplied by the agent's *earned trust* on that market: a Beta posterior of
how often its direction was right over the next `trust_horizon` bars. Calls
are graded only once their horizon has passed, so this is walk-forward.

Sizing
------
    p        = Beta posterior of this market's trade win rate, nudged by conviction
    kelly    = p - (1 - p) / RR
    risk %   = min(2%, kelly_fraction * kelly) * (1 - skeptic doubt) * vol scalar
    units    = risk $ / (2.5 * ATR * contract multiplier)
"""
from __future__ import annotations

import math
from collections import defaultdict, deque
from typing import Optional

from ..config import AssetSpec, TriadConfig
from ..schemas import (Action, AgentSignal, Direction, MarketSnapshot, PortfolioContext,
                       SkepticBrief, TradePlan, Verdict, VolRegime)

BASE_MATRIX: dict[VolRegime, dict[str, float]] = {
    VolRegime.LOW: {"historian": 0.60, "realist": 0.40},
    VolRegime.NORMAL: {"historian": 0.50, "realist": 0.50},
    VolRegime.HIGH: {"historian": 0.40, "realist": 0.60},
}


class TrustLedger:
    """Walk-forward Beta(a, b) hit-rate per (agent, asset)."""

    def __init__(self, horizon: int, prior_strength: float):
        self.horizon = horizon
        self.prior = prior_strength / 2
        self.ab: dict[tuple[str, str], list[float]] = defaultdict(lambda: [self.prior, self.prior])
        self.pending: dict[str, deque] = defaultdict(deque)

    def record(self, asset: str, bar: int, close: float, calls: dict[str, float]) -> None:
        self.pending[asset].append((bar, close, calls))

    def resolve(self, asset: str, bar: int, close: float) -> None:
        q = self.pending[asset]
        while q and bar - q[0][0] >= self.horizon:
            _, c0, calls = q.popleft()
            move = math.copysign(1.0, close - c0) if close != c0 else 0.0
            for agent, score in calls.items():
                if abs(score) < 0.1 or move == 0:
                    continue
                hit = (score > 0) == (move > 0)
                self.ab[(agent, asset)][0 if hit else 1] += 1

    def hit_rate(self, agent: str, asset: str) -> float:
        a, b = self.ab[(agent, asset)]
        return a / (a + b)

    def multiplier(self, agent: str, asset: str) -> float:
        return max(0.5, min(1.5, 2.0 * self.hit_rate(agent, asset)))


class ArbiterAgent:
    name = "⚖️ The Arbiter"

    def __init__(self, cfg: TriadConfig):
        self.cfg = cfg
        self.trust = TrustLedger(cfg.agents.trust_horizon, cfg.agents.trust_prior_strength)

    # ------------------------------------------------------------------
    def weights(self, asset: str, regime: VolRegime) -> dict[str, float]:
        base = dict(BASE_MATRIX[regime])
        if self.cfg.use_adaptive_trust:
            for k in base:
                base[k] *= self.trust.multiplier(k, asset)
        total = sum(base.values())
        return {k: round(v / total, 4) for k, v in base.items()}

    def composite(self, asset: str, regime: VolRegime, h: AgentSignal, r: AgentSignal) -> tuple[float, dict]:
        if self.cfg.mode == "prototype":
            # Original base_framework rule: the more confident agent wins outright.
            pick = h if h.confidence > r.confidence else r
            w = {"historian": 1.0 if pick is h else 0.0, "realist": 1.0 if pick is r else 0.0}
            return pick.score, w
        w = self.weights(asset, regime)
        return w["historian"] * h.score + w["realist"] * r.score, w

    def win_probability(self, outcomes: tuple[bool, ...], conviction: float) -> float:
        a = self.cfg.agents.win_prior_alpha + sum(outcomes)
        b = self.cfg.agents.win_prior_beta + len(outcomes) - sum(outcomes)
        p = a / (a + b) + 0.15 * (conviction - self.cfg.agents.entry_threshold)
        return float(min(0.65, max(0.20, p)))

    # ------------------------------------------------------------------
    def deliberate(
        self,
        spec: AssetSpec,
        s: MarketSnapshot,
        historian: AgentSignal,
        realist: AgentSignal,
        ctx: PortfolioContext,
        skeptic_fn=None,
    ) -> tuple[Verdict, Optional[SkepticBrief]]:
        """skeptic_fn(direction) -> SkepticBrief, called only if a trade is on the table."""
        rc, ac = self.cfg.risk, self.cfg.agents
        regime = s.vol_regime
        score, w = self.composite(spec.name, regime, historian, realist)
        why: list[str] = [f"weights {w} in {regime.value}-vol regime -> composite {score:+.3f}"]

        def verdict(action: Action, plan=None, doubt=0.0, extra: str | None = None):
            if extra:
                why.append(extra)
            return Verdict(asset=spec.name, date=s.date, action=action, composite_score=round(score, 4),
                           weights=w, vol_regime=regime, doubt=doubt, plan=plan, rationale=tuple(why))

        if ctx.circuit_breaker_active:
            return verdict(Action.SKIP, extra="CIRCUIT BREAKER active: trading frozen"), None

        threshold = 0.0 if self.cfg.mode == "prototype" else ac.entry_threshold
        exit_threshold = 0.0 if self.cfg.mode == "prototype" else ac.exit_threshold

        if ctx.position_direction != Direction.FLAT:
            pos = ctx.position_direction.value
            if score * pos < 0 and abs(score) >= exit_threshold:
                return verdict(Action.EXIT, extra="debate has flipped against the open position"), None
            return verdict(Action.HOLD, extra="position open; trailing stop manages it"), None

        if abs(score) < max(threshold, 1e-9):
            return verdict(Action.SKIP, extra=f"|composite| below entry threshold {threshold}"), None

        direction = Direction.from_score(score)
        if self.cfg.trend_filter:
            trend = Direction.LONG if s.close > s.ma200 else Direction.SHORT
            if direction != trend:
                return verdict(Action.SKIP, extra=f"trend filter: no {direction.name} trades while price is "
                                                  f"{'above' if trend == Direction.LONG else 'below'} the 200-day average"), None
        brief: Optional[SkepticBrief] = None
        doubt = 0.0
        if skeptic_fn is not None:
            brief = skeptic_fn(direction)
            doubt = brief.doubt
            why.append(f"Skeptic: {brief.summary}")
            if brief.veto:
                return verdict(Action.SKIP, doubt=doubt, extra="VETOED by the Skeptic"), brief

        # Reward:risk. Wider target when the slow trend supports the trade.
        alignment = max(0.0, historian.score * direction.value)
        rr = round(rc.min_rr + (rc.max_rr - rc.min_rr) * alignment, 2)

        p = self.win_probability(ctx.recent_outcomes, abs(score))
        kelly = p - (1 - p) / rr
        if kelly <= 0:
            return verdict(Action.SKIP, doubt=doubt,
                           extra=f"negative Kelly edge (p={p:.2f}, RR={rr})"), brief
        risk_frac = min(rc.max_risk_per_trade, rc.kelly_fraction * kelly)
        risk_frac *= (1.0 - doubt)
        if regime == VolRegime.HIGH:
            risk_frac *= rc.high_vol_size_scalar
        risk_frac *= ctx.risk_scalar
        heat_room = rc.max_portfolio_heat - ctx.open_heat
        corr_risk = ctx.correlated_risk_long if direction == Direction.LONG else ctx.correlated_risk_short
        cluster_room = rc.max_cluster_risk - corr_risk
        risk_frac = min(risk_frac, heat_room, cluster_room)
        if risk_frac < rc.min_risk_fraction:
            return verdict(Action.SKIP, doubt=doubt,
                           extra=f"risk budget {risk_frac:.2%} below minimum (heat {ctx.open_heat:.2%}, "
                                 f"correlated {corr_risk:.2%})"), brief

        stop_dist = rc.atr_stop_mult * s.atr14
        risk_cash = risk_frac * ctx.equity
        raw_units = risk_cash / (stop_dist * spec.multiplier)
        units = math.floor(raw_units / spec.qty_step + 1e-9) * spec.qty_step
        units = round(units, 6)
        if units <= 0:
            return verdict(Action.SKIP, doubt=doubt,
                           extra=f"risk budget ${risk_cash:,.0f} buys less than one micro contract"), brief
        actual_risk = units * stop_dist * spec.multiplier
        d = direction.value
        plan = TradePlan(
            direction=direction, entry_ref=s.close,
            stop=s.close - d * stop_dist, take_profit=s.close + d * rr * stop_dist,
            stop_distance=stop_dist, rr=rr, win_prob=round(p, 4), kelly_full=round(kelly, 4),
            risk_fraction=actual_risk / ctx.equity, risk_amount=actual_risk, units=units,
        )
        if corr_risk > 0:
            why.append(f"correlated book already risks {corr_risk:.2%}: cluster cap applies")
        if ctx.risk_scalar < 1:
            why.append(f"post-circuit-breaker recovery: risk x{ctx.risk_scalar:g}")
        why.append(f"p(win)={p:.2f}, RR=1:{rr}, full Kelly={kelly:.3f}, doubt haircut {doubt:.0%} "
                   f"-> risk {plan.risk_fraction:.2%} (${actual_risk:,.0f}), {units:g} contracts")
        action = Action.ENTER_LONG if direction == Direction.LONG else Action.ENTER_SHORT
        return verdict(action, plan=plan, doubt=doubt), brief
