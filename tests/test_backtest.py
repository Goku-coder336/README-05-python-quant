import math
import pandas as pd

from triad_verdict.backtest import TriadBacktester
from triad_verdict.config import RiskConfig, TriadConfig


def _data(synth, crash_at=None):
    return {
        "NQ_Nasdaq100": synth(seed=11, start_price=12000, crash_at=crash_at),
        "ES_SP500": synth(seed=12, start_price=4000, crash_at=crash_at),
        "GC_Gold": synth(seed=13, start_price=1900, drift=0.0002),
    }


def test_backtest_runs_and_metrics_are_sane(synth):
    res = TriadBacktester(TriadConfig(), _data(synth)).run()
    m = res.metrics
    assert math.isfinite(m.sharpe) and math.isfinite(m.total_return)
    assert -1 < m.max_drawdown <= 0
    assert res.equity.notna().all()
    for t in res.trades:
        assert t.exit_date >= t.entry_date
        # A stopped trade can lose a little more than 1R (gaps, slippage, fees) but not wildly more.
        assert t.r_multiple > -2.0


def test_strict_circuit_breaker_freezes_everything(synth):
    cfg = TriadConfig(risk=RiskConfig(max_drawdown=0.03, breaker_cooldown_bars=None))
    res = TriadBacktester(cfg, _data(synth, crash_at=500)).run()
    assert res.breaker_date is not None
    assert all(t.entry_date <= res.breaker_date for t in res.trades)
    after = res.equity[res.equity.index.date > res.breaker_date]
    assert after.nunique() == 1  # flat book: equity frozen


def test_cooldown_breaker_resumes(synth):
    cfg = TriadConfig(risk=RiskConfig(max_drawdown=0.03, breaker_cooldown_bars=10))
    res = TriadBacktester(cfg, _data(synth, crash_at=500)).run()
    assert res.metrics.breaker_trips >= 1
    assert any(t.entry_date > res.breaker_date for t in res.trades)


def test_no_trade_risks_more_than_two_percent(synth):
    res = TriadBacktester(TriadConfig(), _data(synth)).run()
    eq = res.equity
    for t in res.trades:
        prior = eq[eq.index.date < t.entry_date]
        equity_at_entry = prior.iloc[-1] if len(prior) else res.config.initial_capital
        assert t.risk_amount <= 0.02 * equity_at_entry * 1.0001


def test_trend_filter_never_trades_against_200_day_trend(synth):
    data = _data(synth)
    bt = TriadBacktester(TriadConfig(trend_filter=True), data)
    res = bt.run()
    assert res.trades
    for t in res.trades:
        f = bt.features[t.asset]
        signal_day = f.index[f.index.get_loc(pd.Timestamp(t.entry_date)) - 1]
        row = f.loc[signal_day]
        trend = 1 if row["close"] > row["ma200"] else -1
        assert t.direction.value == trend
