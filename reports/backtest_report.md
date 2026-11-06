# ⚖️ The Triad Verdict: Backtest Report

Period: **2017-11-20 → 2026-11-04** · Capital $1,000,000 · Assets: NQ=F, ES=F, GC=F

> Research backtest on Yahoo continuous front-month futures (unadjusted for rolls). Not investment advice.

## Risk rules enforced

- Max risk per trade **2%** of equity (hard cap in the `TradePlan` schema)
- Initial stop **2.5× ATR(14)**, then a trailing stop at the same distance that never loosens
- Take-profit at **1:2 to 1:3** reward:risk (1:2 floor enforced by schema)
- Circuit breaker: flatten and freeze all trading at **10%** drawdown
- Portfolio heat cap **6%**; sizing = 0.15× Kelly, then × (1 − Skeptic doubt), × 0.75 in high-vol regimes

## Results: ablation study

| Metric | Prototype (base rules) | Triad without Skeptic | Skeptic: size haircut only, no veto | Triad, static Skeptic | Triad, strict permanent freeze | Triad Verdict (full) |
|---|---|---|---|---|---|---|
| Total return | +39.56% | +57.27% | +67.92% | +83.95% | +5.51% | +80.69% |
| CAGR | +3.79% | +5.19% | +5.96% | +7.04% | +0.60% | +6.83% |
| Annualised volatility | 9.47% | 8.44% | 7.81% | 8.13% | 2.48% | 8.23% |
| Sharpe ratio | 0.44 | 0.64 | 0.78 | 0.88 | 0.25 | 0.85 |
| Sortino ratio | 0.61 | 0.90 | 1.11 | 1.26 | 0.39 | 1.20 |
| Max drawdown | -21.66% | -14.66% | -13.44% | -13.08% | -10.06% | -12.30% |
| Calmar ratio | 0.18 | 0.35 | 0.44 | 0.54 | 0.06 | 0.56 |
| Trades | 355 | 287 | 298 | 274 | 20 | 290 |
| Win rate | 40.0% | 44.3% | 41.3% | 44.2% | 25.0% | 43.4% |
| Profit factor | 1.22 | 1.37 | 1.49 | 1.57 | 1.47 | 1.52 |
| Avg R per trade | +0.10R | +0.15R | +0.14R | +0.20R | +0.05R | +0.17R |
| Exposure (asset-days in market) | 79.7% | 66.4% | 69.7% | 65.3% | 3.0% | 68.4% |
| Skeptic vetoes | 0 | 0 | 0 | 145 | 17 | 93 |
| Circuit-breaker trips (first) | 5 (2018-02-08) | 5 (2018-02-27) | 3 (2019-03-28) | 3 (2018-04-25) | 1 (2018-04-25) | 3 (2018-04-25) |
| Final equity | $1,395,597 | $1,572,726 | $1,679,194 | $1,839,511 | $1,055,139 | $1,806,873 |


### Benchmarks: unlevered buy & hold over the same window

| Buy & hold | Total return | Sharpe | Max drawdown |
|---|---|---|---|
| NQ_Nasdaq100 | +352.29% | 0.83 | -35.28% |
| ES_SP500 | +199.01% | 0.74 | -34.45% |
| GC_Gold | +219.55% | 0.83 | -26.69% |
| Equal-weight (daily rebalanced) | +277.99% | 1.03 | -23.02% |

The Triad risks at most 2% per idea and spends roughly a third of the time flat, so compare it on Sharpe and drawdown, not on raw return.

## 🔍 Veto audit: was the Skeptic right?

Every vetoed trade was replayed with the same 2.5 ATR stop and a 1:2 target, using bars *after* the decision. This end-of-run audit is for grading only. (The self-calibrating Skeptic runs its own walk-forward version of it, learning from each shadow trade only once it has resolved.)

| Group | Would-be wins | Would-be losses | Unresolved | Win rate |
|---|---|---|---|---|
| Trades the Skeptic **vetoed** | 35 | 52 | 6 | 40.2% |
| Trades the Skeptic **cleared** | 98 | 153 | 39 | 39.0% |

With a 1:2 target, break-even win rate is 33.3%. A useful Skeptic vetoes trades with a lower win rate than the ones it lets through. **In this run the vetoes were roughly neutral** (40.2% vetoed vs 39.0% cleared). Compare the 'size haircut only' column: that is where the Skeptic's value shows up.

Most common veto reasons: `OVEREXTENDED` ×74, `RSI_EXHAUSTION` ×49, `VOL_EXTREME` ×26, `AGENT_CONFLICT` ×25, `COUNTER_TREND` ×24, `VOL_SHOCK` ×16, `EVENT_RISK` ×13, `COLD_STREAK` ×12, `PEER_DIVERGENCE` ×4

## Per-asset breakdown (full Triad)

| Asset | Trades | Win rate | Avg R | Net P&L |
|---|---|---|---|---|
| ES_SP500 | 97 | 46.4% | +0.14R | $220,972 |
| GC_Gold | 96 | 39.6% | +0.16R | $249,829 |
| NQ_Nasdaq100 | 97 | 44.3% | +0.20R | $336,070 |

Exit reasons: TRAILING_STOP 192, TAKE_PROFIT 44, STOP_LOSS 44, CIRCUIT_BREAKER 6, SIGNAL_FLIP 3, END_OF_DATA 1


## 🗣️ Latest debate: today's Triad Verdict

#### NQ_Nasdaq100: close of 2026-11-04

**🏛️ The Historian** (+0.21, BULL trend / HIGH vol): BULL regime; history leans LONG (+0.21)
- `trend_regime` +0.84 (w 0.35): BULL structure, MA200 slope +1.44%/20d
- `tsmom_126d` -0.03 (w 0.20): 6m return -0.5% = -0.03 vol units
- `seasonality` +0.75 (w 0.15): month avg +4.12% over 9 yrs, up 78% of the time
- `volume_profile` -0.43 (w 0.30): POC 29,602.95, VA 28,223.21-30,658.05: inside value area, below POC

**⚡ The Realist** (-0.65, expanding session range): tape leans SHORT (-0.65); expanding volatility
- `vwap_deviation` -0.77 (w 0.30): -1.51 ATR from 20d VWAP: trend-side pressure
- `atr_expansion` -0.41 (w 0.20): range expanding x1.41; breakout down
- `rsi14` -0.48 (w 0.25): RSI 38.1
- `mom20` -0.88 (w 0.25): 20d return -9.0% (-1.39 vol units), volume x1.41 avg

**🔍 The Skeptic** (doubt 64%): VETO: 3 failure mode(s), worst = AGENT_CONFLICT. Doubt 64%.
- `AGENT_CONFLICT` severity 0.45: Historian +0.21 vs Realist -0.65 [track record: 39 graded, P(loss) 69% vs base 54%, weight x1.50]
- `COUNTER_TREND` severity 0.30: trade is against the 200-day trend (up) [track record: 36 graded, P(loss) 63% vs base 54%, weight x1.50]
- `COLD_STREAK` severity 0.06: last 4 trades on this market were losers [track record: 87 graded, P(loss) 35% vs base 54%, weight x0.25]

**⚖️ The Arbiter rules: `SKIP`** (composite -0.300)
- weights {'historian': 0.41, 'realist': 0.59} in HIGH-vol regime -> composite -0.300
- Skeptic: VETO: 3 failure mode(s), worst = AGENT_CONFLICT. Doubt 64%.
- VETOED by the Skeptic

#### ES_SP500: close of 2026-11-04

**🏛️ The Historian** (+0.47, BULL trend / NORMAL vol): BULL regime; history leans LONG (+0.47)
- `trend_regime` +0.81 (w 0.35): BULL structure, MA200 slope +1.09%/20d
- `tsmom_126d` +0.45 (w 0.20): 6m return +4.5% = +0.49 vol units
- `seasonality` +0.75 (w 0.15): month avg +4.17% over 9 yrs, up 78% of the time
- `volume_profile` -0.05 (w 0.30): POC 7,739.93, VA 7,405.38-7,797.61: inside value area, below POC

**⚡ The Realist** (-0.22, expanding session range): tape leans SHORT (-0.22); expanding volatility
- `vwap_deviation` -0.06 (w 0.30): -0.09 ATR from 20d VWAP: trend-side pressure
- `atr_expansion` -0.49 (w 0.20): range expanding x1.49; breakout down
- `rsi14` -0.00 (w 0.25): RSI 49.9
- `mom20` -0.43 (w 0.25): 20d return -1.7% (-0.46 vol units), volume x1.34 avg

**⚖️ The Arbiter rules: `SKIP`** (composite +0.129)
- weights {'historian': 0.5073, 'realist': 0.4927} in NORMAL-vol regime -> composite +0.129
- |composite| below entry threshold 0.25

#### GC_Gold: close of 2026-11-04

**🏛️ The Historian** (-0.38, BEAR trend / NORMAL vol): BEAR regime; history leans SHORT (-0.38)
- `trend_regime` -0.79 (w 0.35): BEAR structure, MA200 slope -0.90%/20d
- `tsmom_126d` -0.66 (w 0.20): 6m return -13.2% = -0.79 vol units
- `seasonality` +0.11 (w 0.15): month avg +0.41% over 9 yrs, up 56% of the time
- `volume_profile` +0.04 (w 0.30): POC 4,050.25, VA 4,002.48-4,543.79: inside value area, above POC

**⚡ The Realist** (+0.04, expanding session range): tape leans LONG (+0.04); expanding volatility
- `vwap_deviation` -0.06 (w 0.30): -0.10 ATR from 20d VWAP: trend-side pressure
- `atr_expansion` +0.77 (w 0.20): range expanding x1.41; breakout up
- `rsi14` -0.12 (w 0.25): RSI 46.9
- `mom20` -0.24 (w 0.25): 20d return -1.6% (-0.24 vol units), volume x1.46 avg

**⚖️ The Arbiter rules: `HOLD`** (composite -0.176)
- weights {'historian': 0.5207, 'realist': 0.4793} in NORMAL-vol regime -> composite -0.176
- position open; trailing stop manages it
