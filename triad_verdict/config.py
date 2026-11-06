"""Configuration for The Triad Verdict.

Every tunable lives here, as a Pydantic model, so a run is fully described by
one serialisable object (it is printed at the top of every report).
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class AssetSpec(BaseModel):
    """Contract specification for one futures market."""

    model_config = ConfigDict(frozen=True)

    name: str
    ticker: str
    multiplier: float = Field(gt=0, description="USD per 1.0 index/price point per contract")
    tick_size: float = Field(gt=0)
    commission_per_contract: float = Field(ge=0, description="USD per contract per side")
    qty_step: float = Field(
        default=0.1,
        gt=0,
        description="Smallest tradeable size in full-contract units (0.1 = one micro contract)",
    )
    equity_index: bool = False


DEFAULT_ASSETS: tuple[AssetSpec, ...] = (
    AssetSpec(name="NQ_Nasdaq100", ticker="NQ=F", multiplier=20.0, tick_size=0.25,
              commission_per_contract=2.5, equity_index=True),
    AssetSpec(name="ES_SP500", ticker="ES=F", multiplier=50.0, tick_size=0.25,
              commission_per_contract=2.5, equity_index=True),
    AssetSpec(name="GC_Gold", ticker="GC=F", multiplier=100.0, tick_size=0.10,
              commission_per_contract=2.5, equity_index=False),
)


class RiskConfig(BaseModel):
    """Institutional risk parameters. The hard limits are enforced again by the
    TradePlan schema, so a bad config cannot slip an oversized trade through."""

    max_risk_per_trade: float = Field(default=0.02, gt=0, le=0.02,
                                      description="Hard cap: 2% of equity at risk per trade")
    atr_period: int = Field(default=14, ge=2)
    atr_stop_mult: float = Field(default=2.5, gt=0, description="Initial and trailing stop = k x ATR")
    min_rr: float = Field(default=2.0, ge=2.0, description="Minimum reward:risk for the take-profit")
    max_rr: float = Field(default=3.0, ge=2.0)
    max_drawdown: float = Field(default=0.10, gt=0, lt=1,
                                description="Circuit breaker: freeze all trading at this drawdown")
    max_portfolio_heat: float = Field(default=0.06, gt=0, le=0.2,
                                      description="Sum of open risk across all positions")
    kelly_fraction: float = Field(default=0.15, gt=0, le=1.0,
                                  description="Fraction of full Kelly used before the 2% cap")
    high_vol_size_scalar: float = Field(default=0.75, gt=0, le=1.0)
    min_risk_fraction: float = Field(default=0.0025, ge=0,
                                     description="Skip trades whose final risk budget is below this")
    slippage_ticks: int = Field(default=1, ge=0)
    max_cluster_risk: float = Field(default=0.03, gt=0, le=0.06,
                                    description="Combined open risk allowed across highly correlated "
                                                "same-direction positions (e.g. long NQ + long ES)")
    cluster_corr_threshold: float = Field(default=0.7, ge=0, le=1)
    corr_window: int = Field(default=60, ge=20)
    breaker_cooldown_bars: Optional[int] = Field(
        default=None, ge=1,
        description="None = strict: freeze for the rest of the run. N = after N bars, reset the "
                    "high-water mark and resume at reduced risk until the old peak is recovered")
    post_breaker_risk_scalar: float = Field(default=0.5, gt=0, le=1)


class AgentConfig(BaseModel):
    entry_threshold: float = Field(default=0.25, ge=0, le=1)
    exit_threshold: float = Field(default=0.30, ge=0, le=1)
    veto_threshold: float = Field(default=0.55, gt=0, le=1,
                                  description="Skeptic doubt at or above this vetoes the trade")
    trust_horizon: int = Field(default=5, ge=1, description="Bars used to grade an agent's call")
    trust_prior_strength: float = Field(default=20.0, gt=0, description="Beta prior pseudo-count")
    win_prior_alpha: float = Field(default=4.0, gt=0)
    win_prior_beta: float = Field(default=6.0, gt=0)
    volume_profile_window: int = Field(default=120, ge=20)
    volume_profile_bins: int = Field(default=24, ge=8)


class TriadConfig(BaseModel):
    label: str = "Triad Verdict (full)"
    mode: Literal["triad", "prototype"] = "triad"
    use_skeptic: bool = True
    use_adaptive_trust: bool = True
    skeptic_self_calibration: bool = True
    trend_filter: bool = Field(default=False,
                               description="Never trade against the 200-day trend (close vs MA200)")
    initial_capital: float = Field(default=1_000_000.0, gt=0)
    data_period: str = "10y"
    warmup_bars: int = Field(default=260, ge=210,
                             description="Bars skipped before trading so every indicator is defined")
    risk_free_rate: float = 0.0
    assets: tuple[AssetSpec, ...] = DEFAULT_ASSETS
    risk: RiskConfig = RiskConfig()
    agents: AgentConfig = AgentConfig()

    def asset(self, name: str) -> AssetSpec:
        for spec in self.assets:
            if spec.name == name:
                return spec
        raise KeyError(name)
