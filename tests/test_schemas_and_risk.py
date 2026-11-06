from datetime import date

import pytest
from pydantic import ValidationError

from triad_verdict.agents import ArbiterAgent, HistorianAgent, RealistAgent, SkepticAgent
from triad_verdict.backtest import TriadBacktester
from triad_verdict.config import RiskConfig, TriadConfig
from triad_verdict.schemas import Action, Direction, PortfolioContext, TradePlan

GOOD = dict(direction=Direction.LONG, entry_ref=100.0, stop=95.0, take_profit=110.0,
            stop_distance=5.0, rr=2.0, win_prob=0.4, kelly_full=0.1, risk_fraction=0.02,
            risk_amount=20_000, units=1.0)


def test_trade_plan_accepts_valid():
    TradePlan(**GOOD)


@pytest.mark.parametrize("override", [
    {"risk_fraction": 0.025},                      # > 2% of equity
    {"rr": 1.5},                                   # < 1:2
    {"take_profit": 105.0},                        # target closer than 2R
    {"stop": 101.0},                               # stop on the wrong side
    {"direction": Direction.FLAT},
])
def test_trade_plan_rejects_rule_breaks(override):
    with pytest.raises(ValidationError):
        TradePlan(**{**GOOD, **override})


def test_risk_config_cannot_exceed_two_percent():
    with pytest.raises(ValidationError):
        RiskConfig(max_risk_per_trade=0.03)
    with pytest.raises(ValidationError):
        RiskConfig(min_rr=1.5)


def _snapshots(synth, cfg):
    bt = TriadBacktester(cfg, {"ES_SP500": synth(seed=3)})
    ts = [t for t in bt.calendar if bt.ready["ES_SP500"].loc[t]]
    return bt, [bt._snapshot("ES_SP500", t) for t in ts[-200:]]


def test_every_entry_respects_stop_target_and_size(synth):
    cfg = TriadConfig()
    bt, snaps = _snapshots(synth, cfg)
    spec = cfg.asset("ES_SP500")
    arb, h, r = ArbiterAgent(cfg), HistorianAgent(), RealistAgent()
    entries = 0
    for s in snaps:
        ctx = PortfolioContext(equity=1_000_000, open_heat=0.0)
        v, _ = arb.deliberate(spec, s, h.analyze(s), r.analyze(s), ctx)
        if v.plan:
            entries += 1
            p = v.plan
            assert p.risk_fraction <= 0.02 + 1e-12
            assert p.stop_distance == pytest.approx(2.5 * s.atr14)
            assert abs(p.take_profit - p.entry_ref) >= 2 * p.stop_distance - 1e-9
            assert p.units * p.stop_distance * spec.multiplier == pytest.approx(p.risk_amount)
    assert entries > 0


def test_circuit_breaker_context_forces_skip(synth):
    cfg = TriadConfig()
    _, snaps = _snapshots(synth, cfg)
    arb, s = ArbiterAgent(cfg), snaps[-1]
    ctx = PortfolioContext(equity=1_000_000, open_heat=0.0, circuit_breaker_active=True)
    v, _ = arb.deliberate(cfg.asset("ES_SP500"), s, HistorianAgent().analyze(s),
                          RealistAgent().analyze(s), ctx)
    assert v.action == Action.SKIP


def test_skeptic_flags_payrolls_and_can_veto(synth):
    cfg = TriadConfig()
    _, snaps = _snapshots(synth, cfg)
    s = snaps[-1].model_copy(update={"date": date(2026, 11, 5), "vwap_dev_atr": 4.0, "rsi14": 85.0,
                                     "atr5": snaps[-1].atr20 * 2})
    h, r = HistorianAgent().analyze(s), RealistAgent().analyze(s)
    brief = SkepticAgent(0.55, self_calibrate=False).challenge(s, Direction.LONG, h, r)
    codes = {f.code for f in brief.flags}
    assert "EVENT_RISK" in codes  # 2026-11-06 is the first Friday: payrolls
    assert {"OVEREXTENDED", "RSI_EXHAUSTION", "VOL_SHOCK"} <= codes
    assert brief.veto
