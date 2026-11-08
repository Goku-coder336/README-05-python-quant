"""Render every Episode 1 clip to ../clips/. Usage: python render_all.py [C1a C3 ...]"""
import sys
import time
from multiprocessing import Pool

import c1_scorers
import c2_route
import c3_final

ALL = {**c1_scorers.CLIPS, **c2_route.CLIPS, **c3_final.CLIPS}
ORDER = ["C3", "C2a", "C1b", "C2b", "C2d", "C1a", "C2f", "C2c", "C2", "C4", "C5", "C2e"]


def job(key):
    t0 = time.time()
    clip, draw, zoom = ALL[key]()
    out = clip.render(draw, zoom=zoom)
    return f"{key}: {out} ({time.time() - t0:.0f} s)"


if __name__ == "__main__":
    print("Checking StatsBomb figures against CLAUDE.md:")
    c3_final.check_figures(c3_final.load_events())
    keys = sys.argv[1:] or ORDER
    with Pool(4) as pool:
        for line in pool.imap_unordered(job, keys):
            print(line, flush=True)
