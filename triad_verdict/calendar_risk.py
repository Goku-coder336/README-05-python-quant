"""Scheduled macro-event calendar used by The Skeptic.

The futures analogue of "earnings tomorrow" is a scheduled macro release.
These dates are published in advance, so using them is not look-ahead.

FOMC: statement/decision dates (second day of each meeting, plus the 2020
emergency cuts). Check against federalreserve.gov before relying on them and
extend the list each year.
NFP: approximated as the first Friday of each month; BLS occasionally moves
it (e.g. holidays, shutdowns).
"""
from __future__ import annotations

from datetime import date, timedelta

_FOMC = """
2016-01-27 2016-03-16 2016-04-27 2016-06-15 2016-07-27 2016-09-21 2016-11-02 2016-12-14
2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19
2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-03-03 2020-03-15 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16 2026-10-28 2026-12-09
"""
FOMC_DATES: frozenset[date] = frozenset(date.fromisoformat(s) for s in _FOMC.split())


def _first_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    return d + timedelta(days=(4 - d.weekday()) % 7)


def _next_business_day(d: date) -> date:
    d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def upcoming_events(asof: date) -> list[str]:
    """Scheduled events falling on the next business day, i.e. during the
    session in which a new trade would be filled and first held."""
    nxt = _next_business_day(asof)
    events = []
    if nxt in FOMC_DATES:
        events.append(f"FOMC decision {nxt.isoformat()}")
    if nxt == _first_friday(nxt.year, nxt.month):
        events.append(f"US payrolls (NFP) {nxt.isoformat()}")
    return events
