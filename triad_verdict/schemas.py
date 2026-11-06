"""Pydantic message schemas passed between agents, the arbiter and the backtester.

Agents never hand each other raw dicts: every message is validated on
construction, and the hard risk rules (2% max risk, RR >= 2, stop on the
correct side of entry) are part of the TradePlan type itself.
"""
from __future__ import annotations

import math
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Direction(int, Enum):
    SHORT = -1
    FLAT = 0
    LONG = 1

    @classmethod
    def from_score(cls, score: float, dead_zone: float = 0.0) -> "Direction":
        if score > dead_zone:
            return cls.LONG
        if score < -dead_zone:
            return cls.SHORT
        return cls.FLAT


class Action(str, Enum):
    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    EXIT = "EXIT"
    HOLD = "HOLD"
    SKIP = "SKIP"


class VolRegime(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"


class _Msg(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# --------------------------------------------------------------------------
# Market data
# --------------------------------------------------------------------------
class MarketSnapshot(_Msg):
    """Everything an agent may know at the close of bar `date` (no future data)."""

    asset: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    atr14: float = Field(gt=0)
    atr5: float = Field(gt=0)
    atr20: float = Field(gt=0)
    ma50: float
    ma200: float
    ma200_slope: float
    rsi14: float = Field(ge=0, le=100)
    vwap20: float
    vwap_dev_atr: float
    mom5: float
    mom20: float
    mom126: float
    rv20: float = Field(ge=0)
    vol_pct: float = Field(ge=0, le=1)
    clv: float
    volume_ratio: float
    seasonal_mean: float
    seasonal_n: int = Field(ge=0)
    seasonal_hit: float = Field(ge=0, le=1)
    poc: float
    va_low: float
    va_high: float

    @field_validator("*", mode="before")
    @classmethod
    def _no_nan(cls, v, info):
        if isinstance(v, float) and math.isnan(v):
            raise ValueError(f"{info.field_name} is NaN (indicator not warmed up)")
        return v

    @property
    def vol_regime(self) -> VolRegime:
        if self.vol_pct >= 0.67:
            return VolRegime.HIGH
        if self.vol_pct <= 0.33:
            return VolRegime.LOW
        return VolRegime.NORMAL


# --------------------------------------------------------------------------
# Agent messages
# --------------------------------------------------------------------------
class Evidence(_Msg):
    factor: str
    value: float
    score: float = Field(ge=-1, le=1)
    weight: float = Field(ge=0)
    note: str


class AgentSignal(_Msg):
    agent: str
    asset: str
    date: date
    score: float = Field(ge=-1, le=1, description="-1 strong short .. +1 strong long")
    regime: str
    evidence: tuple[Evidence, ...]
    summary: str

    @property
    def direction(self) -> Direction:
        return Direction.from_score(self.score, dead_zone=0.05)

    @property
    def confidence(self) -> float:
        return abs(self.score)


class RiskFlag(_Msg):
    code: str
    severity: float = Field(ge=0, le=1)
    detail: str


class SkepticBrief(_Msg):
    agent: str
    asset: str
    date: date
    proposed_direction: Direction
    flags: tuple[RiskFlag, ...]
    doubt: float = Field(ge=0, le=1)
    veto: bool
    summary: str


class PortfolioContext(_Msg):
    """What the Arbiter is told about the book before ruling."""

    equity: float = Field(gt=0)
    open_heat: float = Field(ge=0, description="Sum of open risk as a fraction of equity")
    position_direction: Direction = Direction.FLAT
    circuit_breaker_active: bool = False
    recent_outcomes: tuple[bool, ...] = ()
    correlated_risk_long: float = Field(default=0.0, ge=0,
                                        description="Open risk that a new LONG here would add to (corr-adjusted)")
    correlated_risk_short: float = Field(default=0.0, ge=0)
    risk_scalar: float = Field(default=1.0, gt=0, le=1, description="<1 while recovering from a breaker trip")


class TradePlan(_Msg):
    direction: Direction
    entry_ref: float = Field(gt=0, description="Reference price (signal close); fill is next open")
    stop: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    stop_distance: float = Field(gt=0)
    rr: float = Field(ge=2.0, description="Reward:risk, hard floor 1:2")
    win_prob: float = Field(ge=0, le=1)
    kelly_full: float
    risk_fraction: float = Field(gt=0, le=0.02, description="Hard cap 2% of equity")
    risk_amount: float = Field(gt=0)
    units: float = Field(gt=0, description="Contracts (fractional = micro contracts)")

    @model_validator(mode="after")
    def _levels_consistent(self) -> "TradePlan":
        if self.direction == Direction.FLAT:
            raise ValueError("TradePlan needs LONG or SHORT")
        d = self.direction.value
        if d * (self.entry_ref - self.stop) <= 0:
            raise ValueError("stop must sit on the losing side of entry")
        if d * (self.take_profit - self.entry_ref) <= 0:
            raise ValueError("take-profit must sit on the winning side of entry")
        reward = abs(self.take_profit - self.entry_ref)
        if reward + 1e-9 < 2.0 * self.stop_distance:
            raise ValueError("take-profit is closer than 2R")
        return self


class Verdict(_Msg):
    asset: str
    date: date
    action: Action
    composite_score: float
    weights: dict[str, float]
    vol_regime: VolRegime
    doubt: float = Field(ge=0, le=1)
    plan: Optional[TradePlan] = None
    rationale: tuple[str, ...]

    @model_validator(mode="after")
    def _plan_iff_entry(self) -> "Verdict":
        entering = self.action in (Action.ENTER_LONG, Action.ENTER_SHORT)
        if entering != (self.plan is not None):
            raise ValueError("entry verdicts need a TradePlan and only entries may carry one")
        return self


class Debate(_Msg):
    """One full round: the transcript shown in reports."""

    historian: AgentSignal
    realist: AgentSignal
    skeptic: Optional[SkepticBrief]
    verdict: Verdict


# --------------------------------------------------------------------------
# Backtest records
# --------------------------------------------------------------------------
class Trade(_Msg):
    asset: str
    direction: Direction
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    units: float
    initial_stop: float
    take_profit: float
    risk_amount: float
    pnl: float
    r_multiple: float
    exit_reason: str
    bars_held: int
    doubt_at_entry: float


class BacktestMetrics(_Msg):
    label: str
    start: date
    end: date
    initial_capital: float
    final_equity: float
    total_return: float
    cagr: float
    ann_volatility: float
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    n_trades: int
    win_rate: float
    profit_factor: float
    avg_r: float
    exposure: float
    vetoes: int
    circuit_breaker_tripped: Optional[date] = None
    breaker_trips: int = 0
