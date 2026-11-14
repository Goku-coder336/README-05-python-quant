"""Demo of the claude-drawing skill (cartoon style) on the French word-song reel:
"Le bel oiseau au chapeau, sur le bateau" -- a fine bird in a top hat, sitting on a little boat.
Drawn in animator order (blue pencil, ink, flat colour, cel shade, effects) so the stages
replay as a draw-on animation. Vertical 1080x1920 for Reels / Shorts.

python3 oiseau_drawing.py [out.png] [--stages DIR]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/claude-drawing/lib"))
from cartoon import Cartoon, WHITE, YELLOW  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "oiseau.png"
stages = sys.argv[sys.argv.index("--stages") + 1] if "--stages" in sys.argv else None

W, H = 1080, 1920
c = Cartoon(W, H, seed=7, boil=1.6)
E, R = Cartoon.ellipse_pts, Cartoon.rrect_pts

SKY, SKY_D = "#9fd3ea", "#7bbcd9"
SUN, SUN_L = "#ffc93f", "#ffe79a"
SEA, SEA_D, FOAM = "#3fa2c9", "#2b86b0", "#eaf6fb"
HULL, HULL_D, STRIPE = "#e8584a", "#b8392f", "#fdf3e3"
SAIL, SAIL_D, MAST = "#fbf1dc", "#e2cfaa", "#9a6a3c"
BIRD, BIRD_L, BIRD_D = "#7fa7d6", "#c9dcf2", "#5a82b6"
BEAK, BEAK_D = "#ffab3d", "#e2862a"
HAT, HAT_D, BAND = "#2d3b6a", "#1d2748", "#e8584a"


def rot(pts, cx, cy, deg):
    a = np.deg2rad(deg)
    p = np.asarray(pts, np.float32) - (cx, cy)
    m = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], np.float32)
    return p @ m.T + (cx, cy)


# ---------------------------------------------------------------- sky and sun
sky = R(0, 0, W, 1330, 0)
c.fill(sky, SKY, slop=0)
c.crayon(sky, SKY_D, pressure=np.clip((900 - c.YY) / 900, 0.05, 0.7), angle=25)
c.fill(E(820, 640, 96, 96), SUN, slop=2)
c.crayon(E(820, 640, 150, 150), SUN_L, pressure=0.4, angle=-30, clip=1 - c.mask(E(820, 640, 96, 96)))
c.outline(E(820, 640, 96, 96), 6)
for a in np.linspace(0, 330, 12):
    t = np.deg2rad(a)
    c.line([(820 + np.cos(t) * 118, 640 + np.sin(t) * 118), (820 + np.cos(t) * 150, 640 + np.sin(t) * 150)], 5, (4, 6), smooth=False)

# ---------------------------------------------------------------- sea
xs = np.linspace(0, W, 40)
sea_top = [(x, 1320 + 14 * np.sin(x / 70)) for x in xs]
sea = np.array(sea_top + [(W, H), (0, H)], np.float32)
c.fill(sea, SEA, slop=2)
c.crayon(sea, SEA_D, pressure=np.clip((c.YY - 1320) / 700, 0.1, 0.75), angle=0)
c.line(sea_top, 5, taper=(0, 0))
for y in (1480, 1600, 1720, 1840):
    for x0 in np.arange(-40 + (y % 3) * 60, W, 230):
        c.line([(x0, y), (x0 + 50, y - 14), (x0 + 100, y)], 4, (4, 6))

# ---------------------------------------------------------------- mast and sail
c.shape(R(628, 760, 650, 1270, 6), MAST, width=5)
sail = np.array([(660, 800), (660, 1215), (900, 1205)], np.float32)
c.shape(sail, SAIL, shade=(SAIL_D, 14, 0), width=6)
c.shape(np.array([(626, 760), (626, 700), (690, 730)], np.float32), HULL, width=4.5)  # pennant

# ---------------------------------------------------------------- hull
deck = 1250
hull = [(170, deck)] + [(x, deck) for x in np.linspace(200, 880, 12)] + [(920, deck)]
hull += [(860, 1360), (760, 1420)] + [(x, 1428 + 4 * np.sin(x / 40)) for x in np.linspace(700, 380, 8)] + [(300, 1420), (215, 1350)]
c.shape(np.array(hull, np.float32), HULL, shade=(HULL_D, 0, -24), width=7.5)
c.shape(R(205, 1282, 885, 1308, 8), STRIPE, width=4.5)
for x in (340, 480, 620, 760):  # portholes
    c.shape(E(x, 1360, 20, 20), STRIPE, width=4.5)

# ---------------------------------------------------------------- the bird: feet, body, wing, head, beak, eyes
for fx in (390, 455):
    c.line([(fx, 1218), (fx, deck), (fx - 18, deck + 4)], 6, (2, 4), smooth=False)
    c.line([(fx, deck), (fx + 20, deck + 4)], 6, (2, 4), smooth=False)
body = E(430, 1110, 150, 125, -8)
c.shape(body, BIRD, shade=(BIRD_D, 18, 18), width=7.5)
c.shape(E(470, 1150, 82, 70, -8), BIRD_L, width=0)
wing = rot(E(360, 1110, 92, 52), 360, 1110, 28)
c.shape(wing, BIRD_D, width=6)
for t in (-0.4, 0, 0.4):
    c.line([(320 + 30 * t, 1100 + 40 * t), (290 + 40 * t, 1150 + 30 * t)], 4, (3, 5))
tail = np.array([(285, 1080), (190, 1030), (205, 1095), (180, 1130), (290, 1130)], np.float32)
c.shape(tail, BIRD_D, width=6)

head = E(505, 950, 92, 88)
c.shape(head, BIRD, shade=(BIRD_D, 12, 14), width=7.5)
beak = np.array([(578, 935), (690, 972), (580, 1000)], np.float32)
c.shape(beak, BEAK, shade=(BEAK_D, 0, 10), width=6)
c.line([(582, 968), (668, 972)], 4, (2, 4))
for ex in (488, 545):
    c.shape(E(ex, 930, 24, 28), WHITE, width=5)
    c.fill(E(ex + 6, 936, 11, 13), "#1d1d1b", slop=0)
    c.glint([(ex + 2, 928), (ex + 4, 926)], 5)
c.fill(E(470, 985, 18, 11), "#ff8f8f", slop=1)  # blush

# ---------------------------------------------------------------- the hat (le chapeau), tilted
hx, hy = 505, 860
crown = rot(R(hx - 58, hy - 150, hx + 58, hy, 10), hx, hy, 12)
c.shape(crown, HAT, shade=(HAT_D, 14, 0), width=7)
band = rot(R(hx - 58, hy - 40, hx + 58, hy - 8, 2), hx, hy, 12)
c.shape(band, BAND, width=5)
brim = rot(E(hx, hy + 4, 105, 22), hx, hy, 12)
c.shape(brim, HAT, shade=(HAT_D, 0, 8), width=7)
c.glint(rot([(hx - 44, hy - 135), (hx - 44, hy - 60)], hx, hy, 12), 6)

# ---------------------------------------------------------------- foam in front of the hull, title, sparkles
for x0 in np.arange(150, 960, 120):
    c.fill(E(x0, 1432, 58, 16), FOAM, slop=2)
c.line([(140, 1430), (960, 1430)], 4, (6, 6))
c.letter("LE BEL OISEAU", 90, 260, 104, fill=YELLOW)
c.letter("AU CHAPEAU", 150, 400, 104, fill=YELLOW)
c.sparkle(700, 820, 26)
c.sparkle(300, 760, 20)
c.sparkle(940, 960, 18)

c.stage("paper", show=[])
c.stage("rough", show=["rough"], rough=0.9)
c.stage("ink", show=["rough", "ink"], rough=0.55)
c.stage("flat", show=["rough", "ink", "flat"])
c.stage("shade", show=["rough", "ink", "flat", "shade", "texture"])
c.stage("fx", show=["rough", "ink", "flat", "shade", "texture", "fx"])
c.save(out, stages_dir=stages)
print("wrote", out)
