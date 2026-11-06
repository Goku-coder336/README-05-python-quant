"""The Skeptic: a pre-mortem agent with veto power.

It never proposes trades. Once the Arbiter leans a direction, the Skeptic
answers "why might I be WRONG?" by listing concrete failure modes. Each flag
has a severity; they combine as independent failure probabilities:

    doubt = 1 - prod(1 - severity_i)

Doubt at or above the veto threshold kills the trade. Below it, the trade's
risk budget is multiplied by (1 - doubt). So the Skeptic does not have to win
the argument to matter: partial doubt makes the position smaller.

Self-calibration ("who audits the Skeptic?")
--------------------------------------------
Every challenged trade, taken or vetoed, is shadow-tracked with the same
2.5 ATR stop and a 1:2 target. When the shadow trade resolves (only from bars
that have already printed), each flag that was raised gets graded: did the
trade it warned about actually lose? A flag's severity is then scaled by its
*lift*, P(loss | flag) / P(loss), so warnings that do not predict losses fade
and warnings that do get louder. It is walk-forward: nothing is graded early.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping, Sequence

from ..calendar_risk import upcoming_events
from ..schemas import AgentSignal, Direction, MarketSnapshot, RiskFlag, SkepticBrief


@dataclass
class _Shadow:
    direction: int
    stop: float
    target: float
    codes: tuple[str, ...]
    armed: bool = False  # becomes live from the next bar (entry is next open)


class FlagLedger:
    """Walk-forward Beta posteriors of P(loss | flag) and P(loss)."""

    def __init__(self, prior_loss: float = 0.62, prior_strength: float = 12.0, max_bars: int = 60):
        self.prior_loss, self.k, self.max_bars = prior_loss, prior_strength, max_bars
        self.base = [0, 0]  # losses, total
        self.flag: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        self.open: dict[str, list[tuple[int, _Shadow]]] = defaultdict(list)

    def p_loss(self, code: str | None = None) -> float:
        losses, n = self.flag[code] if code else self.base
        return (self.prior_loss * self.k + losses) / (self.k + n)

    def lift(self, code: str) -> float:
        return self.p_loss(code) / self.p_loss()

    def track(self, asset: str, bar: int, close: float, atr: float, direction: int,
              codes: tuple[str, ...], stop_mult: float = 2.5, rr: float = 2.0) -> None:
        stop = close - direction * stop_mult * atr
        target = close + direction * rr * stop_mult * atr
        self.open[asset].append((bar, _Shadow(direction, stop, target, codes)))

    def resolve(self, asset: str, bar: int, high: float, low: float) -> None:
        keep = []
        for start, sh in self.open[asset]:
            if not sh.armed:
                sh.armed = bar > start
                if not sh.armed:
                    keep.append((start, sh))
                    continue
            d = sh.direction
            lost = (low <= sh.stop) if d > 0 else (high >= sh.stop)
            won = (high >= sh.target) if d > 0 else (low <= sh.target)
            if lost or won:
                self._grade(sh.codes, bool(lost))
            elif bar - start < self.max_bars:
                keep.append((start, sh))
        self.open[asset] = keep

    def _grade(self, codes: tuple[str, ...], lost: bool) -> None:
        self.base[0] += lost
        self.base[1] += 1
        for c in codes:
            self.flag[c][0] += lost
            self.flag[c][1] += 1


class SkepticAgent:
    name = "🔍 The Skeptic"

    def __init__(self, veto_threshold: float = 0.55, self_calibrate: bool = True):
        self.veto_threshold = veto_threshold
        self.self_calibrate = self_calibrate
        self.ledger = FlagLedger()

    def _calibrated(self, flags: list[RiskFlag]) -> list[RiskFlag]:
        if not self.self_calibrate:
            return flags
        out = []
        for f in flags:
            lift = self.ledger.lift(f.code)
            mult = max(0.25, min(1.5, 1 + 4 * (lift - 1)))
            n = self.ledger.flag[f.code][1]
            out.append(RiskFlag(code=f.code, severity=round(min(0.9, f.severity * mult), 4),
                                detail=f"{f.detail} [track record: {n} graded, "
                                       f"P(loss) {self.ledger.p_loss(f.code):.0%} vs base "
                                       f"{self.ledger.p_loss():.0%}, weight x{mult:.2f}]"))
        return out

    def challenge(
        self,
        s: MarketSnapshot,
        direction: Direction,
        historian: AgentSignal,
        realist: AgentSignal,
        peer_realists: Mapping[str, AgentSignal] | None = None,
        recent_outcomes: Sequence[bool] = (),
    ) -> SkepticBrief:
        d = direction.value
        flags: list[RiskFlag] = []

        # Event risk: the futures version of "earnings tomorrow".
        events = upcoming_events(s.date)
        if events:
            flags.append(RiskFlag(code="EVENT_RISK", severity=0.35,
                                  detail="scheduled catalyst next session: " + "; ".join(events)))

        # Chasing: already far from fair value in the trade's direction.
        stretch = s.vwap_dev_atr * d
        if stretch > 2.0:
            flags.append(RiskFlag(code="OVEREXTENDED", severity=min(0.45, 0.15 * stretch),
                                  detail=f"price is {stretch:.1f} ATR beyond VWAP in our direction"))
        rsi_against = (s.rsi14 > 75) if d > 0 else (s.rsi14 < 25)
        if rsi_against:
            flags.append(RiskFlag(code="RSI_EXHAUSTION", severity=0.2,
                                  detail=f"RSI {s.rsi14:.0f} already extreme in our direction"))

        # Volatility shock: stops get hit by noise, not by being wrong.
        expansion = s.atr5 / s.atr20
        if expansion > 1.6:
            flags.append(RiskFlag(code="VOL_SHOCK", severity=0.25,
                                  detail=f"short-term range x{expansion:.2f} of normal"))
        if s.vol_pct > 0.9:
            flags.append(RiskFlag(code="VOL_EXTREME", severity=0.15,
                                  detail=f"realised vol in top {1 - s.vol_pct:.0%} of past year"))

        # Disagreement between the two advocates.
        if historian.score * realist.score < 0 and min(abs(historian.score), abs(realist.score)) > 0.2:
            flags.append(RiskFlag(code="AGENT_CONFLICT", severity=0.3,
                                  detail=f"Historian {historian.score:+.2f} vs Realist {realist.score:+.2f}"))

        # Fighting the primary trend.
        trend = 1 if s.close > s.ma200 else -1
        if trend != d:
            flags.append(RiskFlag(code="COUNTER_TREND", severity=0.2,
                                  detail=f"trade is against the 200-day trend ({'up' if trend > 0 else 'down'})"))

        # Cross-asset confirmation (equity index peers).
        for peer, sig in (peer_realists or {}).items():
            if sig.score * d < -0.3:
                flags.append(RiskFlag(code="PEER_DIVERGENCE", severity=0.2,
                                      detail=f"{peer} tape points the other way ({sig.score:+.2f})"))

        # Our own recent record on this market.
        last = list(recent_outcomes)[-4:]
        if len(last) >= 3 and sum(last) == 0:
            flags.append(RiskFlag(code="COLD_STREAK", severity=0.25,
                                  detail=f"last {len(last)} trades on this market were losers"))

        flags = self._calibrated(flags)
        survive = 1.0
        for f in flags:
            survive *= 1.0 - f.severity
        doubt = round(1.0 - survive, 4)
        veto = doubt >= self.veto_threshold
        if not flags:
            summary = "No solid reason to be wrong found. Trade may proceed."
        else:
            worst = max(flags, key=lambda f: f.severity)
            summary = (f"{'VETO' if veto else 'Caution'}: {len(flags)} failure mode(s), "
                       f"worst = {worst.code}. Doubt {doubt:.0%}.")
        return SkepticBrief(agent=self.name, asset=s.asset, date=s.date, proposed_direction=direction,
                            flags=tuple(flags), doubt=doubt, veto=veto, summary=summary)
