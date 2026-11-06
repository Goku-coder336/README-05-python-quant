"""Performance statistics."""
from __future__ import annotations

from datetime import date
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from .config import TriadConfig
from .schemas import BacktestMetrics, Trade

TRADING_DAYS = 252


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1).min()) if len(equity) else 0.0


def sharpe_ratio(returns: pd.Series, rf_annual: float = 0.0) -> float:
    ex = returns - rf_annual / TRADING_DAYS
    sd = ex.std(ddof=1)
    return float(ex.mean() / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else 0.0


def sortino_ratio(returns: pd.Series, rf_annual: float = 0.0) -> float:
    ex = returns - rf_annual / TRADING_DAYS
    downside = np.sqrt((np.minimum(ex, 0) ** 2).mean())
    return float(ex.mean() / downside * np.sqrt(TRADING_DAYS)) if downside > 0 else 0.0


def compute_metrics(cfg: TriadConfig, equity: pd.Series, trades: Sequence[Trade], vetoes: int,
                    exposure: float, breaker: Optional[date], breaker_trips: int = 0) -> BacktestMetrics:
    rets = equity.pct_change().dropna()
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    final = float(equity.iloc[-1])
    total = final / cfg.initial_capital - 1
    cagr = (final / cfg.initial_capital) ** (1 / years) - 1 if final > 0 else -1.0
    mdd = max_drawdown(equity)
    wins = [t.pnl for t in trades if t.pnl > 0]
    losses = [t.pnl for t in trades if t.pnl <= 0]
    pf = sum(wins) / abs(sum(losses)) if losses and sum(losses) != 0 else float("inf") if wins else 0.0
    return BacktestMetrics(
        label=cfg.label, start=equity.index[0].date(), end=equity.index[-1].date(),
        initial_capital=cfg.initial_capital, final_equity=round(final, 2),
        total_return=total, cagr=cagr, ann_volatility=float(rets.std() * np.sqrt(TRADING_DAYS)),
        sharpe=sharpe_ratio(rets, cfg.risk_free_rate), sortino=sortino_ratio(rets, cfg.risk_free_rate),
        max_drawdown=mdd, calmar=cagr / abs(mdd) if mdd < 0 else 0.0,
        n_trades=len(trades), win_rate=len(wins) / len(trades) if trades else 0.0,
        profit_factor=min(pf, 999.0), avg_r=float(np.mean([t.r_multiple for t in trades])) if trades else 0.0,
        exposure=exposure, vetoes=vetoes, circuit_breaker_tripped=breaker, breaker_trips=breaker_trips,
    )
