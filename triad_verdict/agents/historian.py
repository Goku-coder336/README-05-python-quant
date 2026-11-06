"""The Historian: slow, multi-regime context. Asks "what does the past say?"."""
from __future__ import annotations

import math

import numpy as np

from ..schemas import AgentSignal, Evidence, MarketSnapshot, VolRegime


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return float(max(lo, min(hi, x)))


class HistorianAgent:
    name = "🏛️ The Historian"

    def analyze(self, s: MarketSnapshot) -> AgentSignal:
        ev: list[Evidence] = []

        # 1. Trend regime: MA50/MA200 structure plus slope of the 200-day.
        if s.ma50 > s.ma200 and s.close > s.ma200:
            base, label = 1.0, "BULL"
        elif s.ma50 < s.ma200 and s.close < s.ma200:
            base, label = -1.0, "BEAR"
        else:
            base, label = 0.3 * float(np.sign(s.ma50 - s.ma200)), "TRANSITION"
        slope = _clip(s.ma200_slope / 0.03)
        trend = _clip(0.7 * base + 0.3 * slope)
        ev.append(Evidence(factor="trend_regime", value=s.ma50 / s.ma200 - 1, score=trend, weight=0.35,
                           note=f"{label} structure, MA200 slope {s.ma200_slope:+.2%}/20d"))

        # 2. Time-series momentum (6 months), scaled by realised vol.
        horizon_vol = max(s.rv20, 1e-4) * math.sqrt(126 / 252)
        tsm = _clip(math.tanh(s.mom126 / horizon_vol))
        ev.append(Evidence(factor="tsmom_126d", value=s.mom126, score=tsm, weight=0.20,
                           note=f"6m return {s.mom126:+.1%} = {s.mom126 / horizon_vol:+.2f} vol units"))

        # 3. Seasonality: same calendar month in prior years.
        if s.seasonal_n >= 3:
            consistency = abs(s.seasonal_hit - 0.5) * 2
            seas = _clip(math.tanh(s.seasonal_mean / 0.02) * (0.5 + 0.5 * consistency) * min(1.0, s.seasonal_n / 8))
            note = (f"month avg {s.seasonal_mean:+.2%} over {s.seasonal_n} yrs, "
                    f"up {s.seasonal_hit:.0%} of the time")
        else:
            seas, note = 0.0, "fewer than 3 prior years: ignored"
        ev.append(Evidence(factor="seasonality", value=s.seasonal_mean, score=seas, weight=0.15, note=note))

        # 4. Volume profile: is price accepted above/below the value area?
        width = max(s.va_high - s.va_low, 1e-9)
        if s.close > s.va_high:
            vp = _clip(0.5 + (s.close - s.va_high) / width)
            vnote = "accepted ABOVE value area (buyers in control)"
        elif s.close < s.va_low:
            vp = _clip(-0.5 - (s.va_low - s.close) / width)
            vnote = "accepted BELOW value area (sellers in control)"
        else:
            vp = _clip((s.close - s.poc) / (width / 2) * 0.5)
            vnote = f"inside value area, {'above' if s.close >= s.poc else 'below'} POC"
        ev.append(Evidence(factor="volume_profile", value=(s.close - s.poc) / width, score=vp, weight=0.30,
                           note=f"POC {s.poc:,.2f}, VA {s.va_low:,.2f}-{s.va_high:,.2f}: {vnote}"))

        score = sum(e.score * e.weight for e in ev) / sum(e.weight for e in ev)
        regime = s.vol_regime
        if regime == VolRegime.HIGH:
            score *= 0.75  # regimes break down in vol spikes: history is less reliable
        score = _clip(score)
        return AgentSignal(
            agent=self.name, asset=s.asset, date=s.date, score=score,
            regime=f"{label} trend / {regime.value} vol", evidence=tuple(ev),
            summary=f"{label} regime; history leans {'LONG' if score > 0 else 'SHORT'} ({score:+.2f})",
        )
