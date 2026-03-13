# README-05-python-quant
python-portfolio-optimisation
# Quantitative Portfolio Optimisation — Python Financial Modelling

> 🐍 Python for Finance | Individual Report | MSc Finance & Economics

---

## Project Overview

A full Python-based quantitative analysis covering portfolio optimisation, return forecasting, Value at Risk (VaR), Expected Shortfall (ES), and CAPM/FAMA model comparison — applied to a **10-asset equity portfolio** using real market data from 2019–2024.

**Assets:** Apple · Microsoft · Nvidia · Amazon · Meta · JP Morgan Chase + 4 others

---

## Key Results

| Analysis | Result |
|---|---|
| Optimal Sharpe Ratio | **7.04** |
| Largest Weight | Apple (AAPL): **41.3%** |
| VaR 95% (Weighted) | **−25.62%** |
| VaR 95% (Average) | **−39.16%** |
| Expected Shortfall | **−0.02069** |
| AR(1) MSE — Weighted | **0.000107** ✅ |
| AR(1) MSE — Average | 0.000230 |
| Best Forecast Model | CAPM (lower MSE than FAMA) |

---

## Analysis Modules

### 1. Markowitz Portfolio Optimisation (MPT)

Finds the optimal asset weights to maximise the Sharpe ratio using the variance-covariance matrix and expected returns.

| Asset | Weight | Direction |
|---|---|---|
| Apple (AAPL) | 41.3% | Long |
| Microsoft (MSFT) | 35.9% | Long |
| Nvidia (NVDA) | 30.0% | Long |
| Amazon (AMZN) | Negative | Short |
| Meta (META) | Negative | Short |
| JP Morgan (JPM) | Negative | Short |

> Sharpe Ratio of **7.04** — strong risk-adjusted return on the optimised allocation.

---

### 2. CAPM vs FAMA Forecasting

Compared two models across rolling and recursive estimation windows (Scully vs Mulder framework):

| Model | Method | MSE |
|---|---|---|
| CAPM (Scully) | Rolling | Lower ✅ |
| CAPM (Scully) | Recursive | Lower ✅ |
| FAMA (Mulder) | Rolling | Higher |
| FAMA (Mulder) | Recursive | Significantly Higher ❌ |

CAPM outperforms FAMA on this dataset — single market return factor is sufficient.

---

### 3. Beta & Abnormal Returns

| Metric | Value | Interpretation |
|---|---|---|
| Beta (β) | 0.00791987 | Near-zero — almost no market sensitivity |
| Std Dev Abnormal Returns | 0.01258931 | Asset-specific risk persists |

---

### 4. AR(1) Return Forecasting

| Return Type | AR(1) MSE |
|---|---|
| Weighted Return | **0.000107** — better predictability |
| Average Return | 0.000230 |

Position-weighted returns are more forecastable using lag-1 autoregression.

---

### 5. Value at Risk & Expected Shortfall

| Metric | Average Return | Weighted Return |
|---|---|---|
| VaR (95%) | −39.16% | **−25.62%** ✅ |
| Expected Shortfall | 0.00095 | **0.00056** ✅ |
| Avg Return | 0.0205 | 0.0137 |

Weighted portfolio significantly reduces tail risk with only a modest return reduction.

---

## Repository Structure

```
python-portfolio-optimisation/
├── data/
│   └── asset_returns.csv
├── notebooks/
│   ├── 01_markowitz_optimisation.ipynb
│   ├── 02_capm_fama_forecasting.ipynb
│   ├── 03_return_distribution.ipynb
│   ├── 04_beta_abnormal_returns.ipynb
│   ├── 05_ar1_forecasting.ipynb
│   ├── 06_expected_shortfall.ipynb
│   └── 07_value_at_risk.ipynb
├── src/
│   ├── portfolio.py
│   └── risk_metrics.py
└── README.md
```

---

## Skills Demonstrated

`Markowitz MPT` `Sharpe Ratio` `VaR` `Expected Shortfall` `CAPM` `Fama-French`
`AR(1) Forecasting` `Rolling Window` `Beta Analysis` `Python` `pandas` `numpy` `scipy` `statsmodels`

---

## Academic Context

**Module:** Python for Quantitative Finance
**Degree:** MSc Finance & Economics
**Year:** 2024–2025
**Data:** Real equity data (AAPL, MSFT, NVDA, AMZN, META, JPM) — Feb 2019 to Feb 2024
