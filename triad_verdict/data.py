"""Market data pipeline: download from Yahoo Finance, clean, cache to CSV."""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

import pandas as pd

from .config import AssetSpec

log = logging.getLogger("triad.data")

OHLCV = ["Open", "High", "Low", "Close", "Volume"]


def clean_ohlcv(df: pd.DataFrame, drop_today: bool = True, drop_partial: bool = True) -> pd.DataFrame:
    """Flatten yfinance columns and remove bars that would corrupt indicators."""
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[[c for c in OHLCV if c in df.columns]]
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df.index.name = "Date"
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    bad = (df["High"] < df["Low"]) | (df[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
    if bad.any():
        log.warning("dropping %d malformed bars", int(bad.sum()))
        df = df[~bad]
    df["Volume"] = df["Volume"].fillna(0.0).clip(lower=0)
    if drop_partial and len(df) > 21:
        typical = df["Volume"].iloc[-21:-1].median()
        if typical > 0 and df["Volume"].iloc[-1] < 0.35 * typical:
            log.warning("final bar %s has %.0f%% of typical volume: treating it as an incomplete "
                        "session and dropping it", df.index[-1].date(), 100 * df["Volume"].iloc[-1] / typical)
            df = df.iloc[:-1]
    if drop_today and len(df):
        today = pd.Timestamp(datetime.now(timezone.utc).date())
        if df.index[-1] >= today:
            log.info("dropping in-progress bar %s", df.index[-1].date())
            df = df.iloc[:-1]
    return df


class DataPipeline:
    def __init__(self, assets: tuple[AssetSpec, ...], target_dir: str = "data"):
        self.assets = assets
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)

    def path(self, spec: AssetSpec) -> str:
        return os.path.join(self.target_dir, f"{spec.name}_historical.csv")

    def download_market_data(self, period: str = "10y", interval: str = "1d") -> dict[str, pd.DataFrame]:
        import yfinance as yf

        store: dict[str, pd.DataFrame] = {}
        for spec in self.assets:
            log.info("downloading %s (%s) period=%s", spec.name, spec.ticker, period)
            raw = yf.download(spec.ticker, period=period, interval=interval,
                              auto_adjust=False, progress=False)
            if raw is None or raw.empty:
                log.error("no data for %s; trying cache", spec.ticker)
                cached = self.load_cached(spec)
                if cached is not None:
                    store[spec.name] = cached
                continue
            df = clean_ohlcv(raw)
            df.to_csv(self.path(spec))
            log.info("  %s: %d bars %s -> %s, saved %s", spec.name, len(df),
                     df.index[0].date(), df.index[-1].date(), self.path(spec))
            store[spec.name] = df
        return store

    def load_cached(self, spec: AssetSpec) -> pd.DataFrame | None:
        p = self.path(spec)
        if not os.path.exists(p):
            return None
        df = pd.read_csv(p, index_col="Date", parse_dates=True)
        return clean_ohlcv(df, drop_today=False, drop_partial=False)

    def load_all_cached(self) -> dict[str, pd.DataFrame]:
        out = {}
        for spec in self.assets:
            df = self.load_cached(spec)
            if df is None:
                raise FileNotFoundError(f"no cached data at {self.path(spec)}; run without --offline")
            out[spec.name] = df
        return out
