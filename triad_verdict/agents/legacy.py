"""The original base_framework.py agents, kept as a benchmark.

Same rules as the prototype (MA50/MA200 cross; RSI > 55), wrapped in the
typed AgentSignal so they can run through the same risk engine.
"""
from __future__ import annotations

from ..schemas import AgentSignal, Evidence, MarketSnapshot


class LegacyHistorian:
    name = "🏛️ The Historian (prototype)"

    def analyze(self, s: MarketSnapshot) -> AgentSignal:
        bull = s.ma50 > s.ma200
        score = 0.75 if bull else -0.70
        ev = Evidence(factor="ma50_vs_ma200", value=s.ma50 / s.ma200 - 1, score=score, weight=1.0,
                      note="Bull regime." if bull else "Bear regime.")
        return AgentSignal(agent=self.name, asset=s.asset, date=s.date, score=score,
                           regime="BULL" if bull else "BEAR", evidence=(ev,), summary=ev.note)


class LegacyRealist:
    name = "⚡ The Realist (prototype)"

    def analyze(self, s: MarketSnapshot) -> AgentSignal:
        up = s.rsi14 > 55
        score = 0.65 if up else -0.60
        ev = Evidence(factor="rsi14", value=s.rsi14, score=score, weight=1.0,
                      note="Momentum positive." if up else "Momentum weak.")
        return AgentSignal(agent=self.name, asset=s.asset, date=s.date, score=score,
                           regime="momentum", evidence=(ev,), summary=ev.note)
