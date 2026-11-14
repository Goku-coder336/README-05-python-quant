"""Demo 2 of the claude-drawing skill (cartoon style) on the French word-song reel:
"coupe le gâteau du château au couteau" -- the same bird in a top hat, on the same boat,
cutting a castle-shaped cake with a big knife. Same look as oiseau_drawing.py, so the two
work as a sequence. Vertical 1080x1920.

python3 oiseau_gateau.py [out.png] [--stages DIR]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.expanduser("~/.claude/skills/claude-drawing/lib"))
from cartoon import Cartoon, WHITE, YELLOW  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "gateau.png"
stages = sys.argv[sys.argv.index("--stages") + 1] if "--stages" in sys.argv else None

W, H = 1080, 1920
c = Cartoon(W, H, seed=11, boil=1.6)
E, R = Cartoon.ellipse_pts, Cartoon.rrect_pts

SKY, SKY_D = "#9fd3ea", "#7bbcd9"
SEA, SEA_D, FOAM = "#3fa2c9", "#2b86b0", "#eaf6fb"
HULL, HULL_D, STRIPE = "#e8584a", "#b8392f", "#fdf3e3"
BIRD, BIRD_L, BIRD_D = "#7fa7d6", "#c9dcf2", "#5a82b6"
BEAK, BEAK_D = "#ffab3d", "#e2862a"
HAT, HAT_D, BAND = "#2d3b6a", "#1d2748", "#e8584a"
CAKE, CAKE_D = "#f7a8c0", "#e17e9f"
ICING, ICING_D = "#fff4e2", "#ecd8b8"
ROOF, ROOF_D = "#7fa7d6", "#5a82b6"
STEEL, STEEL_D, HANDLE = "#e6ebef", "#aab6c0", "#9a6a3c"
CHERRY = "#d8333f"


def rot(pts, cx, cy, deg):
    a = np.deg2rad(deg)
    p = np.asarray(pts, np.float32) - (cx, cy)
    m = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]], np.float32)
    return p @ m.T + (cx, cy)


# ---------------------------------------------------------------- sky, a few clouds
sky = R(0, 0, W, 1330, 0)
c.fill(sky, SKY, slop=0)
c.crayon(sky, SKY_D, pressure=np.clip((900 - c.YY) / 900, 0.05, 0.7), angle=25)
for cx, cy, s in ((230, 640, 1.0), (860, 560, 0.8)):
    cloud = [(cx - 110 * s, cy, 70 * s), (cx - 20 * s, cy - 35 * s, 85 * s), (cx + 90 * s, cy, 68 * s)]
    m = None
    for x, y, r in cloud:
        mm = c.mask(E(x, y, r, r))
        m = mm if m is None else np.maximum(m, mm)
    m = m * (c.YY < cy + 30 * s)
    c.fill(m, WHITE, slop=2)
    c.shade(m, "#dfeef6", (0, -16))

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

# ---------------------------------------------------------------- the castle cake (le gâteau du château)
deck = 1250
# side turrets first, then the two tiers in front
for tx in (590, 870):
    c.shape(R(tx - 42, 900, tx + 42, deck, 8), CAKE, shade=(CAKE_D, 14, 0), width=6.5)
    c.shape(np.array([(tx - 58, 905), (tx, 770), (tx + 58, 905)], np.float32), ROOF, shade=(ROOF_D, 14, 0), width=6.5)
    c.line([(tx, 772), (tx, 715)], 4.5, (2, 3), smooth=False)
    c.shape(np.array([(tx, 715), (tx + 46, 730), (tx, 745)], np.float32), HULL, width=4)
    c.shape(R(tx - 14, 1000, tx + 14, 1036, 12), ICING_D, width=4)   # turret window
base = R(620, 1080, 840, deck, 10)
c.shape(base, CAKE, shade=(CAKE_D, 16, 0), width=7)
top_tier = np.array([(655, 1080), (655, 960), (680, 960), (680, 935), (705, 935), (705, 960), (730, 960),
                     (730, 935), (755, 935), (755, 960), (780, 960), (780, 935), (805, 935), (805, 1080)], np.float32)
c.shape(top_tier, CAKE, shade=(CAKE_D, 14, 0), width=6.5)
# icing drips along the tier edges
for y0, x0, x1 in ((1080, 620, 840), (960, 655, 805)):
    pts = [(x0, y0 - 6)]
    for x in np.linspace(x0, x1, 9)[1:-1]:
        pts += [(x - 9, y0 + 4), (x, y0 + 22 + 10 * np.sin(x)), (x + 9, y0 + 4)]
    pts += [(x1, y0 - 6), (x1, y0 - 18), (x0, y0 - 18)]
    c.shape(np.array(pts, np.float32), ICING, width=5)
door = np.array([(700, deck)] + [(730 + 30 * np.cos(t), 1185 - 30 * np.sin(t)) for t in np.linspace(np.pi, 0, 12)] + [(760, deck)], np.float32)
c.shape(door, CAKE_D, width=5.5)
for cx in (680, 730, 780):  # cherries on top
    c.shape(E(cx, 920, 15, 15), CHERRY, width=4.5)
    c.glint([(cx - 5, 914), (cx - 3, 912)], 4)
# the slice already cut: a gap line and crumbs on the deck
c.line([(740, 960), (742, 1080), (745, deck)], 6, (2, 4))
for x, y in ((612, 1240), (628, 1232), (600, 1236), (640, 1243)):
    c.shape(E(x, y, 7, 5), CAKE, width=3)

# ---------------------------------------------------------------- hull (same boat, no sail today)
hull = [(170, deck)] + [(x, deck) for x in np.linspace(200, 880, 12)] + [(920, deck)]
hull += [(860, 1360), (760, 1420)] + [(x, 1428 + 4 * np.sin(x / 40)) for x in np.linspace(700, 380, 8)] + [(300, 1420), (215, 1350)]
c.shape(np.array(hull, np.float32), HULL, shade=(HULL_D, 0, -24), width=7.5)
c.shape(R(205, 1282, 885, 1308, 8), STRIPE, width=4.5)
for x in (340, 480, 620, 760):
    c.shape(E(x, 1360, 20, 20), STRIPE, width=4.5)

# ---------------------------------------------------------------- the bird (same as before), leaning in with a knife
BX = -70
for fx in (390 + BX, 455 + BX):
    c.line([(fx, 1218), (fx, deck), (fx - 18, deck + 4)], 6, (2, 4), smooth=False)
    c.line([(fx, deck), (fx + 20, deck + 4)], 6, (2, 4), smooth=False)
tail = np.array([(285 + BX, 1080), (190 + BX, 1030), (205 + BX, 1095), (180 + BX, 1130), (290 + BX, 1130)], np.float32)
c.shape(tail, BIRD_D, width=6)
body = E(430 + BX, 1110, 150, 125, -8)
c.shape(body, BIRD, shade=(BIRD_D, 18, 18), width=7.5)
c.shape(E(470 + BX, 1150, 82, 70, -8), BIRD_L, width=0)
head = E(505 + BX, 950, 92, 88)
c.shape(head, BIRD, shade=(BIRD_D, 12, 14), width=7.5)
beak = np.array([(578 + BX, 935), (690 + BX, 972), (580 + BX, 1000)], np.float32)
c.shape(beak, BEAK, shade=(BEAK_D, 0, 10), width=6)
c.line([(582 + BX, 968), (668 + BX, 972)], 4, (2, 4))
for ex in (488 + BX, 545 + BX):  # eyes looking at the cake, one brow up
    c.shape(E(ex, 930, 24, 28), WHITE, width=5)
    c.fill(E(ex + 10, 934, 11, 13), "#1d1d1b", slop=0)
    c.glint([(ex + 6, 926), (ex + 8, 924)], 5)
c.line([(530 + BX, 888), (568 + BX, 878)], 6, (2, 4))
c.fill(E(470 + BX, 985, 18, 11), "#ff8f8f", slop=1)

# the knife (le couteau): big, held by the wing, blade down into the cake gap
kx, ky, ka = 548, 1078, 24
blade = rot(np.array([(kx, ky - 14), (kx + 230, ky - 4), (kx + 262, ky + 10), (kx, ky + 16)], np.float32), kx, ky, ka)
c.shape(blade, STEEL, shade=(STEEL_D, 0, 10), width=6)
c.glint(rot([(kx + 30, ky - 6), (kx + 190, ky - 1)], kx, ky, ka), 5)
handle = rot(R(kx - 110, ky - 18, kx + 4, ky + 18, 14), kx, ky, ka)
c.shape(handle, HANDLE, shade=("#7a5230", 0, 8), width=6)
for dx in (-80, -40):
    c.fill(rot(E(kx + dx, ky, 6, 6), kx, ky, ka), "#e9d7b6", slop=0)
# the wing reaching round to the handle
wing = rot(E(455 + BX, 1085, 105, 48), 455 + BX, 1085, 14)
c.shape(wing, BIRD_D, width=6)
for t in (-0.4, 0, 0.4):
    c.line([(500 + BX + 40 * t, 1075 + 14 * t), (535 + BX + 40 * t, 1100 + 14 * t)], 4, (3, 5))

# the hat, same as before
hx, hy = 505 + BX, 860
crown = rot(R(hx - 58, hy - 150, hx + 58, hy, 10), hx, hy, 12)
c.shape(crown, HAT, shade=(HAT_D, 14, 0), width=7)
c.shape(rot(R(hx - 58, hy - 40, hx + 58, hy - 8, 2), hx, hy, 12), BAND, width=5)
c.shape(rot(E(hx, hy + 4, 105, 22), hx, hy, 12), HAT, shade=(HAT_D, 0, 8), width=7)
c.glint(rot([(hx - 44, hy - 135), (hx - 44, hy - 60)], hx, hy, 12), 6)

# ---------------------------------------------------------------- foam, title, effects
for x0 in np.arange(150, 960, 120):
    c.fill(E(x0, 1432, 58, 16), FOAM, slop=2)
c.line([(140, 1430), (960, 1430)], 4, (6, 6))
c.letter("COUPE LE GÂTEAU", 540, 250, 92, fill=YELLOW, anchor="m")
c.letter("DU CHÂTEAU", 540, 365, 92, fill=YELLOW, anchor="m")
c.letter("AU COUTEAU !", 540, 480, 92, fill=YELLOW, anchor="m")
c.pop_lines(742, 1150, 40, 72, (150, 175, 200, 340, 5, 30))  # the "chop" where the knife meets the cake
c.sparkle(900, 690, 24)
c.sparkle(300, 770, 20)

c.stage("paper", show=[])
c.stage("rough", show=["rough"], rough=0.9)
c.stage("ink", show=["rough", "ink"], rough=0.55)
c.stage("flat", show=["rough", "ink", "flat"])
c.stage("shade", show=["rough", "ink", "flat", "shade", "texture"])
c.stage("fx", show=["rough", "ink", "flat", "shade", "texture", "fx"])
c.save(out, stages_dir=stages)
print("wrote", out)
