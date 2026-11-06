import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def synthetic_ohlcv(n=900, seed=0, drift=0.0004, vol=0.012, start_price=4000.0, crash_at=None,
                    start="2015-01-01"):
    """Geometric random walk with realistic OHLC structure and optional crash."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    if crash_at is not None:
        rets[crash_at:crash_at + 15] = -0.03
    close = start_price * np.exp(np.cumsum(rets))
    open_ = np.r_[start_price, close[:-1]] * (1 + rng.normal(0, vol / 4, n))
    span = np.abs(rng.normal(0, vol, n)) * close
    high = np.maximum(open_, close) + span / 2
    low = np.minimum(open_, close) - span / 2
    vol_ = rng.integers(100_000, 300_000, n).astype(float)
    idx = pd.bdate_range(start, periods=n)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol_},
                        index=idx)


@pytest.fixture
def synth():
    return synthetic_ohlcv
