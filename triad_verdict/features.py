"""Causal feature engineering.

Every column at row t uses only bars <= t (or, for seasonality, only prior
calendar years). `tests/test_no_lookahead.py` verifies this by truncating the
data and checking that past feature values do not change.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _wilder(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def _seasonality(close: pd.Series) -> pd.DataFrame:
    """Mean return of the current calendar month in *prior* years only."""
    monthly = close.resample("ME").last().pct_change().dropna()
    tbl = pd.DataFrame({"y": monthly.index.year, "m": monthly.index.month, "r": monthly.values})
    keys = pd.MultiIndex.from_arrays([close.index.year, close.index.month])
    cache: dict[tuple[int, int], tuple[float, int, float]] = {}
    for y, m in set(keys):
        prior = tbl.loc[(tbl.m == m) & (tbl.y < y), "r"]
        if len(prior):
            cache[(y, m)] = (float(prior.mean()), len(prior), float((prior > 0).mean()))
        else:
            cache[(y, m)] = (0.0, 0, 0.5)
    vals = np.array([cache[k] for k in keys])
    return pd.DataFrame(
        {"seasonal_mean": vals[:, 0], "seasonal_n": vals[:, 1].astype(int), "seasonal_hit": vals[:, 2]},
        index=close.index,
    )


def _volume_profile(tp: np.ndarray, vol: np.ndarray, window: int, bins: int) -> np.ndarray:
    """Rolling volume-at-price: point of control and 70% value area."""
    n = len(tp)
    out = np.full((n, 3), np.nan)
    for i in range(window - 1, n):
        px = tp[i - window + 1: i + 1]
        vv = vol[i - window + 1: i + 1]
        if vv.sum() <= 0:
            vv = np.ones_like(px)
        hist, edges = np.histogram(px, bins=bins, weights=vv)
        order = np.argsort(hist)[::-1]
        cum = np.cumsum(hist[order]) / hist.sum()
        chosen = order[: int(np.searchsorted(cum, 0.70) + 1)]
        poc_i = order[0]
        out[i] = (
            0.5 * (edges[poc_i] + edges[poc_i + 1]),
            edges[chosen.min()],
            edges[chosen.max() + 1],
        )
    return out


def compute_features(df: pd.DataFrame, vp_window: int = 120, vp_bins: int = 24,
                     atr_period: int = 14) -> pd.DataFrame:
    o, h, l, c, v = (df[k].astype(float) for k in ("Open", "High", "Low", "Close", "Volume"))
    f = pd.DataFrame(index=df.index)
    f["open"], f["high"], f["low"], f["close"], f["volume"] = o, h, l, c, v

    prev = c.shift(1)
    tr = pd.concat([h - l, (h - prev).abs(), (l - prev).abs()], axis=1).max(axis=1)
    f["atr14"] = _wilder(tr, atr_period)
    f["atr5"] = tr.rolling(5).mean()
    f["atr20"] = tr.rolling(20).mean()

    f["ma50"] = c.rolling(50).mean()
    f["ma200"] = c.rolling(200).mean()
    f["ma200_slope"] = f["ma200"].pct_change(20)

    d = c.diff()
    gain = _wilder(d.clip(lower=0), 14)
    loss = _wilder(-d.clip(upper=0), 14)
    f["rsi14"] = 100 - 100 / (1 + gain / (loss + 1e-12))

    tp = (h + l + c) / 3
    vol_sum = v.rolling(20).sum()
    vwap = (tp * v).rolling(20).sum() / vol_sum.replace(0, np.nan)
    f["vwap20"] = vwap.fillna(tp.rolling(20).mean())
    f["vwap_dev_atr"] = (c - f["vwap20"]) / f["atr14"]

    f["mom5"] = c.pct_change(5)
    f["mom20"] = c.pct_change(20)
    f["mom126"] = c.pct_change(126)

    ret = c.pct_change()
    f["rv20"] = ret.rolling(20).std() * np.sqrt(252)
    f["vol_pct"] = f["rv20"].rolling(252, min_periods=126).rank(pct=True)

    rng = (h - l).replace(0, np.nan)
    f["clv"] = (((c - l) - (h - c)) / rng).fillna(0.0)
    f["volume_ratio"] = (v / v.rolling(20).mean().replace(0, np.nan)).fillna(1.0)

    f = f.join(_seasonality(c))
    vp = _volume_profile(tp.to_numpy(), v.to_numpy(), vp_window, vp_bins)
    f["poc"], f["va_low"], f["va_high"] = vp[:, 0], vp[:, 1], vp[:, 2]
    return f


REQUIRED = ["atr14", "atr5", "atr20", "ma50", "ma200", "ma200_slope", "rsi14", "vwap20",
            "vwap_dev_atr", "mom126", "rv20", "vol_pct", "poc", "va_low", "va_high"]


def ready_mask(f: pd.DataFrame) -> pd.Series:
    return f[REQUIRED].notna().all(axis=1) & (f["atr14"] > 0) & (f["atr5"] > 0) & (f["atr20"] > 0)
