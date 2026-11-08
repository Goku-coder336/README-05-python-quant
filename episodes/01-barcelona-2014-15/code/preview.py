"""Render still frames of a clip for checking: python preview.py C1a 4.5 12 26 --out DIR"""
import argparse
import os

from PIL import Image

import c1_scorers
import c2_route
import c3_final

ALL = {**c1_scorers.CLIPS, **c2_route.CLIPS, **c3_final.CLIPS}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("times", nargs="+", type=float)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    clip, draw, zoom = ALL[a.clip]()
    imgs = clip.render(draw, zoom=zoom, frames=a.times)
    os.makedirs(a.out, exist_ok=True)
    for t, im in zip(a.times, imgs):
        p = os.path.join(a.out, f"{a.clip}_{t:05.1f}.png")
        Image.fromarray(im).save(p)
        print(p)
