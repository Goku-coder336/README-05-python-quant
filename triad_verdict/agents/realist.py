"""The Realist: fast, session-level dynamics. Asks "what is price doing now?"."""
from __future__ import annotations

import math

from ..schemas import AgentSignal, Evidence, MarketSnapshot


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return float(max(lo, min(hi, x)))


class RealistAgent:
    name = "⚡ The Realist"

    def analyze(self, s: MarketSnapshot) -> AgentSignal:
        ev: list[Evidence] = []

        # 1. VWAP deviation in ATR units: moderate = momentum, extreme = snap-back risk.
        dev = s.vwap_dev_atr
        if abs(dev) <= 2.5:
            vw = _clip(math.tanh(dev / 1.5))
            note = f"{dev:+.2f} ATR from 20d VWAP: trend-side pressure"
        else:
            vw = -0.5 * math.copysign(1.0, dev)
            note = f"{dev:+.2f} ATR from 20d VWAP: stretched, fade risk"
        ev.append(Evidence(factor="vwap_deviation", value=dev, score=vw, weight=0.30, note=note))

        # 2. ATR expansion: a volatility breakout confirmed by where the bar closed.
        expansion = s.atr5 / s.atr20
        if expansion > 1.15:
            direction = math.copysign(1.0, s.mom5) if s.mom5 != 0 else 0.0
            closing_conf = 0.5 + 0.5 * abs(s.clv) if s.clv * direction > 0 else 0.5
            ax = _clip(direction * min(1.0, (expansion - 1.0) * 2) * closing_conf)
            note = f"range expanding x{expansion:.2f}; breakout {'up' if direction > 0 else 'down'}"
        else:
            ax = 0.0
            note = f"range x{expansion:.2f}: no expansion signal"
        ev.append(Evidence(factor="atr_expansion", value=expansion, score=ax, weight=0.20, note=note))

        # 3. RSI momentum.
        rs = _clip((s.rsi14 - 50) / 25)
        ev.append(Evidence(factor="rsi14", value=s.rsi14, score=rs, weight=0.25,
                           note=f"RSI {s.rsi14:.1f}"))

        # 4. 20-day momentum in vol units.
        hv = max(s.rv20, 1e-4) * math.sqrt(20 / 252)
        mo = _clip(math.tanh(s.mom20 / hv))
        ev.append(Evidence(factor="mom20", value=s.mom20, score=mo, weight=0.25,
                           note=f"20d return {s.mom20:+.1%} ({s.mom20 / hv:+.2f} vol units), "
                                f"volume x{s.volume_ratio:.2f} avg"))

        score = _clip(sum(e.score * e.weight for e in ev) / sum(e.weight for e in ev))
        tone = "expanding" if expansion > 1.15 else ("quiet" if expansion < 0.85 else "steady")
        return AgentSignal(
            agent=self.name, asset=s.asset, date=s.date, score=score,
            regime=f"{tone} session range", evidence=tuple(ev),
            summary=f"tape leans {'LONG' if score > 0 else 'SHORT'} ({score:+.2f}); {tone} volatility",
        )
