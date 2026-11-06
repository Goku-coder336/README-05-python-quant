import numpy as np
import pandas as pd

from triad_verdict.features import compute_features


def test_features_do_not_change_when_future_is_removed(synth):
    df = synth(n=700, seed=7)
    full = compute_features(df)
    for cut in (400, 550, 699):
        part = compute_features(df.iloc[:cut])
        a, b = full.iloc[:cut], part
        pd.testing.assert_frame_equal(a, b, check_exact=False, rtol=1e-9, atol=1e-9)


def test_seasonality_uses_prior_years_only(synth):
    df = synth(n=300, seed=1)  # ~14 months: no month has a prior-year sample until year 2
    f = compute_features(df)
    first_year = f.index.year == f.index.year[0]
    assert (f.loc[first_year, "seasonal_n"] == 0).all()
    assert np.isfinite(f["seasonal_mean"]).all()
