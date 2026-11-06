# 🔬 The Triad Verdict: Out-of-Sample Validation

**Unseen period: 2001-09-14 → 2016-11-04.** The system was designed on data from 2016-11-07 onwards. Nothing before that date was ever run during development, and no setting was changed after seeing these results.

> Data notes: Yahoo continuous front-month futures (unadjusted for rolls). Early gold data has many zero-volume days (≈40% in 2000-02), which weakens the volume-based signals for gold. The FOMC calendar starts in 2016, so before that the Skeptic's event check only covers payrolls.

## 1. Ablation on unseen data

| Metric | Prototype (base rules) | Triad without Skeptic | Skeptic: size haircut only, no veto | Triad, static Skeptic | Triad, strict permanent freeze | Triad Verdict (full) |
|---|---|---|---|---|---|---|
| Total return | +90.62% | +20.18% | +29.88% | +71.77% | +27.23% | +53.23% |
| CAGR | +4.35% | +1.22% | +1.74% | +3.64% | +1.60% | +2.86% |
| Annualised volatility | 11.22% | 8.30% | 6.32% | 7.81% | 4.63% | 7.84% |
| Sharpe ratio | 0.43 | 0.19 | 0.30 | 0.49 | 0.37 | 0.40 |
| Sortino ratio | 0.60 | 0.26 | 0.43 | 0.70 | 0.53 | 0.55 |
| Max drawdown | -25.41% | -28.80% | -24.47% | -20.44% | -10.39% | -21.33% |
| Calmar ratio | 0.17 | 0.04 | 0.07 | 0.18 | 0.15 | 0.13 |
| Trades | 703 | 485 | 374 | 450 | 82 | 443 |
| Win rate | 39.7% | 38.4% | 38.5% | 39.3% | 42.7% | 38.8% |
| Profit factor | 1.17 | 1.08 | 1.18 | 1.28 | 1.54 | 1.22 |
| Avg R per trade | +0.09R | +0.06R | +0.09R | +0.10R | +0.18R | +0.09R |
| Exposure (asset-days in market) | 87.9% | 61.3% | 45.8% | 60.5% | 10.9% | 58.9% |
| Skeptic vetoes | 0 | 0 | 0 | 283 | 99 | 398 |
| Circuit-breaker trips (first) | 10 (2001-10-24) | 7 (2001-11-06) | 4 (2001-12-17) | 4 (2004-04-13) | 1 (2004-04-20) | 4 (2004-04-20) |
| Final equity | $1,906,225 | $1,201,766 | $1,298,751 | $1,717,666 | $1,272,328 | $1,532,343 |


### Benchmarks: unlevered buy & hold over the same unseen window

| Buy & hold | Total return | Sharpe | Max drawdown |
|---|---|---|---|
| NQ_Nasdaq100 | +272.02% | 0.48 | -53.85% |
| ES_SP500 | +100.19% | 0.33 | -57.11% |
| GC_Gold | +349.72% | 0.62 | -44.36% |
| Equal-weight (daily rebalanced) | +276.35% | 0.65 | -38.67% |


## 2. Full Triad by market era

| Era | Triad return | Triad Sharpe | Triad max DD | Buy & hold return | Buy & hold Sharpe | Buy & hold max DD |
|---|---|---|---|---|---|---|
| Dot-com bust & recovery (2001-2007) | +16.2% | 0.34 | -21.3% | +94.7% | 0.81 | -27.5% |
| Global financial crisis (2008-2009) | +24.9% | 1.45 | -5.7% | +0.2% | 0.12 | -37.8% |
| QE bull market (2010-2016) | +4.0% | 0.11 | -16.9% | +82.5% | 0.77 | -10.0% |


## 3. Parameter sensitivity (full Triad, unseen data)

Each row changes one setting. If results collapsed when a setting moves slightly, the headline numbers would be luck. A flat profile is what you want.

| Variation | Return | Sharpe | Max DD | Trades |
|---|---|---|---|---|
| Headline settings | +53.2% | 0.40 | -21.3% | 443 |
| Stop 2.0x ATR (tighter) | +112.7% | 0.62 | -19.7% | 492 |
| Stop 3.0x ATR (wider) | +37.3% | 0.34 | -22.4% | 396 |
| Entry threshold 0.20 (trades more) | +37.7% | 0.32 | -20.3% | 498 |
| Entry threshold 0.30 (trades less) | +22.4% | 0.22 | -21.0% | 411 |
| Skeptic veto at 45% doubt | +13.7% | 0.17 | -20.0% | 338 |
| Skeptic veto at 65% doubt | +35.9% | 0.31 | -19.7% | 463 |
| Kelly fraction 0.10 | +38.9% | 0.37 | -19.7% | 325 |
| Kelly fraction 0.25 | +25.3% | 0.24 | -22.1% | 472 |

Sharpe range across variations: **0.17 to 0.62** (median 0.32).
