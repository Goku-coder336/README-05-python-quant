# ⚖️ The Triad Verdict

A multi-agent debate framework for futures trading research on **NQ (Nasdaq 100), ES (S&P 500) and GC (Gold)**, with institutional risk rules and an event-driven backtester.

It started from the "Bull Claude vs Bear Claude" idea: make the system argue with itself before trading. The central question is not *"why should I take this trade?"* but *"why might I be WRONG?"*

> Research code on Yahoo continuous front-month futures data. Not investment advice.

---

## Quick start

```bash
pip install -r requirements.txt
python -m triad_verdict              # download 10y of data, run the full ablation, write reports/
python -m triad_verdict --offline    # reuse the CSVs already in data/
python -m pytest -q tests            # 16 validation tests
python -m triad_verdict.validation  # out-of-sample test on unseen 2000-2016 data (~3 min)
```

Options: `--period 5y`, `--capital 500000`, `--cooldown 0` (strict permanent freeze), `--log-level DEBUG` (every fill and close).

Outputs:

| File | Contents |
|---|---|
| `data/*_historical.csv` | Cleaned daily OHLCV per market |
| `reports/backtest_report.md` | Ablation table, benchmarks, veto audit, per-asset stats, today's full debate transcript |
| `reports/trades_*.csv` | Every trade: entry/exit, stop, target, R-multiple, exit reason, Skeptic doubt at entry |
| `reports/equity_*.csv` | Daily mark-to-market equity per variant |

---

## The agents

```
                ┌───────────────────┐      ┌───────────────────┐
                │ 🏛️ The Historian   │      │ ⚡ The Realist      │
                │ slow, multi-regime │      │ fast, session      │
                └─────────┬─────────┘      └─────────┬─────────┘
                          │  AgentSignal (score −1..+1, evidence)
                          ▼                          ▼
                ┌──────────────────────────────────────────────┐
                │ ⚖️ The Arbiter: confidence matrix              │
                │ vol-regime weights × earned trust → lean        │
                └─────────────────────┬────────────────────────┘
                                      │ "I lean LONG. Convince me otherwise."
                                      ▼
                ┌──────────────────────────────────────────────┐
                │ 🔍 The Skeptic: pre-mortem, can veto           │
                │ lists failure modes → doubt 0..1               │
                └─────────────────────┬────────────────────────┘
                                      ▼
            Verdict + TradePlan (Kelly × (1 − doubt), 2.5 ATR stop, ≥ 1:2 target)
```

| Agent | Looks at | Signals |
|---|---|---|
| 🏛️ **Historian** | What does the past say? | MA50/MA200 trend regime and 200-day slope · 6-month time-series momentum in vol units · **seasonality** (same calendar month, prior years only) · **volume profile** (point of control and 70% value area over 120 bars; is price accepted above or below value?) · damped in high-vol regimes |
| ⚡ **Realist** | What is price doing right now? | **VWAP deviation** in ATR units (moderate = momentum, beyond 2.5 ATR = snap-back risk) · **ATR expansion** (ATR5/ATR20) confirmed by where the bar closed · RSI(14) · 20-day momentum in vol units |
| 🔍 **Skeptic** *(new)* | Why might this be wrong? | Event risk (FOMC, payrolls next session: the futures version of "earnings tomorrow") · overextension from VWAP · RSI exhaustion · volatility shock · Historian-vs-Realist conflict · counter-trend · NQ/ES peer divergence · cold streak on this market |
| ⚖️ **Arbiter** | Final call and size | Dynamic confidence matrix, Kelly sizing, all risk gates |

### Five additions beyond the brief

1. **The Skeptic as a separate pre-mortem agent with partial power.** It never proposes trades. Flags combine as independent failure probabilities, `doubt = 1 − Π(1 − severityᵢ)`. At 55%+ doubt it **vetoes**; below that it **shrinks the position** by `(1 − doubt)`. A bear does not have to win the argument to matter.
2. **The Skeptic audits itself.** Every challenged idea, taken or vetoed, is shadow-tracked with the same stop and target. Once the shadow trade resolves, each flag is graded: did the trade it warned about actually lose? A flag's weight scales with its *lift*, `P(loss | flag) / P(loss)`. Warnings that do not predict losses fade, and ones that do get louder. This is walk-forward only.
3. **Earned trust in the confidence matrix.** Base weights depend on the volatility regime (Historian 60/40 in calm markets, Realist 60/40 in turbulent ones). Each weight is then multiplied by that agent's Beta-posterior hit rate on that market, graded 5 bars after each call.
4. **Correlation-aware risk.** Long NQ plus long ES is effectively one bet. Positions with a 60-day correlation above 0.7 share a 3% cluster risk budget.
5. **Typed messages with the rules built into the type.** `TradePlan` cannot be constructed with risk above 2%, reward:risk below 1:2, or a stop or target on the wrong side of entry. A bug or a bad config fails loudly instead of trading.

---

## Risk management

| Rule | Implementation |
|---|---|
| Max 2% risk per trade | `risk = min(2%, 0.15 × Kelly) × (1 − doubt) × 0.75 if high-vol`; units are floored to micro-contract steps (0.1), so actual risk ≤ budget. Hard-capped in `RiskConfig` and again in `TradePlan`. |
| Kelly | `p` = Beta posterior of this market's trade win rate (prior 40%), nudged by conviction; `f* = p − (1−p)/RR` |
| ATR trailing stop | Initial stop 2.5 × ATR(14) from the actual fill; then trails at close ∓ 2.5 × ATR and never loosens |
| Take-profit | 1:2 minimum, stretching to 1:3 when the Historian's trend supports the trade |
| Portfolio heat | Total open risk ≤ 6%; correlated cluster ≤ 3% |
| 10% circuit breaker | Drawdown measured on daily mark-to-market. On a trip: flatten everything at the close, cancel orders, freeze. `--cooldown 0` freezes for good (strict). The default `--cooldown 20` resumes after 20 bars at **half risk** until the old peak is regained. |

## Backtester

Event-driven: each day is processed as `MarketEvent(open) → FillEvent`, `MarketEvent(bar) → stop/target FillEvent`, `MarketEvent(close) → risk checks → SignalEvent → OrderEvent`. Decisions made at the close of day *t* fill at the **open of day t+1** with 1 tick of slippage. Gaps through a stop fill at the open. If a bar touches both stop and target, the stop is assumed to have been hit first. Commission is $2.50 per contract per side, and P&L uses real contract multipliers (NQ $20, ES $50, GC $100).

---

## Results (2017-11-20 → 2026-11-04, $1M, run on 2026-11-06)

| | Prototype (base rules) | Triad, no Skeptic | Skeptic: size haircut only | Triad, static Skeptic | **Triad Verdict (full)** | Triad, strict permanent freeze |
|---|---|---|---|---|---|---|
| Total return | +39.6% | +57.3% | +67.9% | +84.0% | **+80.7%** | +5.5% |
| Sharpe | 0.44 | 0.64 | 0.78 | 0.88 | **0.85** | 0.25 |
| Max drawdown | −21.7% | −14.7% | −13.4% | −13.1% | **−12.3%** | −10.1% |
| Trades / win rate | 355 / 40.0% | 287 / 44.3% | 298 / 41.3% | 274 / 44.2% | 290 / 43.4% | 20 / 25.0% |

Full table, benchmarks and today's debate: [`reports/backtest_report.md`](reports/backtest_report.md).

### What the numbers do and don't say

- **Each layer helps on this sample** (but see the out-of-sample section below: the gain over the prototype did not hold on unseen data). Going from the prototype rules to the full Triad roughly doubles Sharpe (0.44 → 0.85) and cuts max drawdown from −21.7% to −12.3%.
- **The Skeptic's value is mostly in sizing, not vetoes.** The veto audit replays every vetoed idea. Vetoed ideas would have won about as often as cleared ones (~40% vs ~39%), so vetoes are roughly neutral at picking losers. The doubt-based size haircut alone lifts Sharpe from 0.64 to 0.78. The first (static) Skeptic actively vetoed winners (45.6% vs 38.4% when it was the headline variant). Self-calibration narrowed that gap, but the static version still ended with a slightly higher Sharpe (0.88 vs 0.85). That is a reminder of how noisy differences of this size are on about 300 trades.
- **It does not beat passive on a risk-adjusted basis.** Equal-weight buy & hold of the three contracts had Sharpe ≈ 1.00 (with a −23% drawdown) over a decade of strong equity and gold markets. The Triad's case is drawdown control and a defined risk per idea, not out-earning a bull market.
- **The strict 10% freeze ends the test in April 2018.** All variants hit 10% in the Feb–Apr 2018 volatility shock. With a literal permanent freeze, the system then sits in cash for 8.5 years. That is why the default is a 20-bar cooldown with half-risk recovery. Because the breaker re-baselines after a cooldown, total max drawdown can exceed 10% (−12.3% here).
- **This is in-sample.** Indicator settings and thresholds were chosen up front and not optimised. Still, the ablation was run on the same decade it is reported on, so treat it as evidence, not proof. The natural next step is a walk-forward or out-of-sample split.

## Out-of-sample validation (unseen 2000–2016 data)

`python -m triad_verdict.validation` runs the same ladder on 2000-09 → 2016-11. That data was never used while building the system, and no setting was changed after seeing it. Full output: [`reports/out_of_sample_report.md`](reports/out_of_sample_report.md).

| Unseen 2000–2016 | Prototype (base rules) | Triad, no Skeptic | **Triad Verdict (full)** | Equal-weight buy & hold |
|---|---|---|---|---|
| Total return | +90.6% | +20.2% | **+53.2%** | +276.4% |
| Sharpe | 0.43 | 0.19 | **0.40** | 0.65 |
| Max drawdown | −25.4% | −28.8% | **−21.3%** | −38.7% |

**Verdict: the improvement over the prototype did not survive.** On unseen data the full Triad's Sharpe (0.40) is no better than the original prototype's (0.43), and buy & hold beat both. What did hold up:

- **Crisis protection.** In 2008–09 the Triad made +24.9% (Sharpe 1.45, worst drop −5.7%) while buy & hold went nowhere with a −37.8% drawdown.
- **The Skeptic still helps within the Triad.** Adding it lifts Sharpe from 0.19 to 0.40.
- **Shallower drawdowns** than holding: −21% vs −39%.

What did not hold up:

- **Bull markets.** In 2010–16 the Triad made only +4% while buy & hold made +83%.
- **Robustness.** Moving one setting at a time gives Sharpe anywhere from 0.17 to 0.62, so results depend on settings more than a robust system should. A tighter 2.0× ATR stop scored best (0.62). Adopting it now would be fitting to this test, though, so the headline settings are unchanged.
- **The 10% breaker with cooldown does not cap total drawdown.** Each restart re-baselines, so drawdown reached −21%. Only the strict permanent freeze held it to −10.4%.

**Honest conclusion:** treat this as a well-engineered research framework with a credible crisis-defence profile, not as a validated money-maker. The next steps would be a walk-forward design (re-choosing settings only on past data), adding a long-only trend bias for bull markets, and roll-adjusted futures data.

### Known limitations

- Yahoo `=F` series are unadjusted front-month continuations, so roll days add artificial jumps.
- The FOMC dates in `calendar_risk.py` are hard-coded (extend yearly). Payrolls is approximated as the first Friday of the month.
- No margin, financing or position limits are modelled. Daily bars only, so "session" dynamics are daily-session proxies.
- The final bar is dropped when its volume is below 35% of typical, because Yahoo often serves an in-progress session.

---

## Code map

```
triad_verdict/
├── config.py          # Pydantic configs: assets, RiskConfig (hard limits), AgentConfig
├── schemas.py         # Typed messages: MarketSnapshot, AgentSignal, SkepticBrief, TradePlan, Verdict, Trade
├── data.py            # yfinance download, cleaning, CSV cache
├── features.py        # causal indicators: ATR, VWAP, RSI, seasonality, volume profile
├── calendar_risk.py   # FOMC / payrolls calendar
├── agents/
│   ├── historian.py   # 🏛️ multi-regime context
│   ├── realist.py     # ⚡ session dynamics
│   ├── skeptic.py     # 🔍 pre-mortem + self-calibrating flag ledger
│   ├── arbiter.py     # ⚖️ confidence matrix, trust ledger, Kelly sizing
│   └── legacy.py      # original prototype rules, kept as the benchmark
├── backtest.py        # event-driven engine, portfolio, circuit breaker
├── metrics.py         # Sharpe, Sortino, drawdown, Calmar, profit factor
├── report.py          # markdown report, veto audit, CSV export
└── __main__.py        # CLI + ablation ladder
tests/                 # schema rules, risk sizing, no-look-ahead, breaker behaviour
```
