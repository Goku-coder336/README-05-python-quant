# 🧪 The Triad Verdict: Two Pre-Registered Improvements

Both rules were fixed **before** any result was seen, and nothing was tuned afterwards.

1. **Trend filter:** the Triad may only trade in the direction of the 200-day trend (no shorts while price is above its 200-day average, no longs while below). No new settings.
2. **Core + shield:** 50% equal-weight buy & hold of NQ, ES and GC, 50% Triad, rebalanced daily.

Caveat: the unseen period has now been looked at once before (the out-of-sample test), so it is a second look, not a pristine one. Two ideas were tested, which keeps multiple-testing luck low.

## Unseen period (2000-2016)

| | Buy & hold | Triad | Triad + trend filter | 50/50 hold + Triad | 50/50 hold + filtered Triad |
|---|---|---|---|---|---|
| Total return | +261.8% | +53.2% | +55.1% | +147.2% | +148.7% |
| CAGR | +8.8% | +2.8% | +2.9% | +6.1% | +6.2% |
| Sharpe | 0.63 | 0.40 | 0.41 | 0.70 | 0.71 |
| Max drawdown | -38.7% | -21.3% | -21.6% | -17.3% | -17.3% |
| Volatility | +15.1% | +7.8% | +7.8% | +9.0% | +9.0% |


Daily correlation between the Triad and buy & hold: **+0.15**. A low correlation is what lets a 50/50 mix be smoother than either half.

## Design period (2017-2026)

| | Buy & hold | Triad | Triad + trend filter | 50/50 hold + Triad | 50/50 hold + filtered Triad |
|---|---|---|---|---|---|
| Total return | +328.0% | +57.9% | +78.1% | +167.0% | +183.5% |
| CAGR | +15.6% | +4.7% | +5.9% | +10.3% | +11.0% |
| Sharpe | 1.04 | 0.64 | 0.75 | 1.09 | 1.13 |
| Max drawdown | -23.0% | -13.9% | -13.4% | -15.6% | -15.1% |
| Volatility | +15.0% | +7.6% | +8.2% | +9.4% | +9.6% |


Daily correlation between the Triad and buy & hold: **+0.31**. A low correlation is what lets a 50/50 mix be smoother than either half.

## By market era: return / Sharpe / max drawdown

| Era | Buy & hold | Triad | Triad + trend filter | 50/50 hold + Triad | 50/50 hold + filtered Triad |
|---|---|---|---|---|---|
| Dot-com bust & recovery | +95% / 0.81 / -27% | +16% / 0.34 / -21% | +15% / 0.31 / -22% | +53% / 0.87 / -9% | +52% / 0.86 / -9% |
| Global financial crisis | +0% / 0.12 / -38% | +25% / 1.46 / -6% | +24% / 1.42 / -6% | +14% / 0.56 / -17% | +13% / 0.55 / -17% |
| QE bull market | +86% / 0.79 / -10% | +5% / 0.14 / -17% | +9% / 0.21 / -18% | +42% / 0.64 / -11% | +44% / 0.68 / -9% |


| Era | Buy & hold | Triad | Triad + trend filter | 50/50 hold + Triad | 50/50 hold + filtered Triad |
|---|---|---|---|---|---|
| 2018-2019 vol shocks | +26% / 1.02 / -13% | +0% / 0.06 / -14% | +3% / 0.26 / -13% | +13% / 0.88 / -11% | +14% / 0.95 / -11% |
| 2020 COVID crash | +31% / 1.21 / -22% | +12% / 1.51 / -8% | +12% / 1.52 / -8% | +22% / 1.46 / -11% | +22% / 1.46 / -12% |
| 2022 bear market | -17% / -0.86 / -23% | -4% / -0.93 / -6% | -3% / -0.67 / -4% | -10% / -1.21 / -13% | -10% / -1.14 / -12% |
| 2023-2026 | +125% / 1.56 / -14% | +19% / 0.70 / -12% | +32% / 0.93 / -12% | +65% / 1.46 / -8% | +74% / 1.53 / -9% |

