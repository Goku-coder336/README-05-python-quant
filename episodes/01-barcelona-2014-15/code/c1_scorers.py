"""C1a (Messi paradox) and C1b (scorer split). Verified run in CLAUDE.md only.

Clip times are seconds from the start of the script line the clip is placed on.
"""
import sys

from common import (Clip, ep, prog, interp_keys, title_block, W, TEXT, MUTED, FAINT, LINE,
                    MESSI, NEYMAR, SUAREZ, OTHER, GOAL_BLOCK, BARCA, PANEL, text_width)

# Verified figures (CLAUDE.md)
GROUP_TOTAL, GROUP_MESSI = 15, 8
KO_TOTAL, KO_MESSI = 16, 2
KO_AFTER_QF = [("Suárez", 4, SUAREZ), ("Neymar", 3, NEYMAR), ("Rakitić", 1, OTHER), ("Messi", 0, MESSI)]
SPLIT = [("Neymar", 3, 7, NEYMAR), ("Suárez", 2, 5, SUAREZ), ("Messi", 8, 2, MESSI)]


def mix(c1, c2, f):
    import matplotlib.colors as mc
    a = mc.to_rgb(c1)
    b = mc.to_rgb(c2)
    return tuple(a[i] + (b[i] - a[i]) * f for i in range(3))


# ======================================================================= C1a
def c1a():
    """L01 to L05 (0:00 to 0:25). 27 s."""
    c = Clip("C1a_messi_paradox", 27.0)
    BS, GAP = 54, 10
    X0 = 400
    rows = [
        # label, sub, y, total, messi, t_blocks, t_gold, t_number
        ("Group stage", "15 Barcelona goals", 560, GROUP_TOTAL, GROUP_MESSI, 0.3, 1.2, 4.2),
        ("Knockouts", "16 Barcelona goals", 290, KO_TOTAL, KO_MESSI, 7.8, 10.2, 11.0),
    ]
    T_DIM = 21.0  # 'supplier' in L04

    def draw(t):
        title_block(c, "Who scored Barcelona's goals?",
                    "Champions League 2014/15 · one block = one goal", alpha=ep(t, 0, 0.6))
        # legend
        a = ep(t, 0.2, 0.6)
        c.box(80, 850, 26, 26, r=5, fc=MESSI, alpha=a)
        c.text(118, 855, "Messi", size=19, alpha=a)
        c.box(230, 850, 26, 26, r=5, fc=GOAL_BLOCK, alpha=a)
        c.text(268, 855, "Other Barcelona scorers", size=19, alpha=a)

        dim = 1 - 0.5 * ep(t, T_DIM, 0.8)
        for label, sub, y, total, messi, tb, tg, tn in rows:
            ra = ep(t, tb - 0.3, 0.5)
            c.text(80, y + 30, label, size=30, weight="semibold", alpha=ra)
            c.text(80, y - 8, sub, size=18, color=MUTED, alpha=ra)
            for i in range(total):
                ba = ep(t, tb + i * 0.07, 0.3)
                if ba <= 0:
                    continue
                x = X0 + i * (BS + GAP)
                rise = (1 - ba) * 14
                fc = GOAL_BLOCK
                alpha = ba
                if i < messi:
                    g = ep(t, tg + i * (0.12 if messi > 2 else 0.25), 0.35)
                    fc = mix(GOAL_BLOCK, MESSI, g)
                    if g > 0:
                        alpha = ba * (1 - (1 - dim) * g)
                c.box(x, y - 20 + rise, BS, BS, r=7, fc=fc, alpha=alpha)
            # headline number
            na = ep(t, tn, 0.45)
            if na > 0:
                s = 1 + 0.25 * (1 - na)
                xr = 1840
                c.tokens(xr, y - 6, [(f"{messi}", MESSI, "bold"), (f" of {total}", TEXT, "bold")],
                         size=64 * s, alpha=na, ha="right")
                c.text(xr, y - 50, "scored by Messi", size=18, color=MUTED, ha="right", alpha=na)

    zoom = lambda t: 1 + 0.04 * ep(t, 12.0, 15.0) if t > 12 else 1.0
    return c, draw, zoom


# ======================================================================= C1b
def c1b():
    """Part 1 (0 to 5 s): L38, knockout tally after two rounds.
    Part 2 (from 5 s): L67 to L74, group v knockouts for the three forwards.
    Total 39 s."""
    c = Clip("C1b_scorer_split", 39.0)
    P1_OUT = 4.9   # part 1 fades out
    P2_IN = 5.25   # part 2 fades in (L67 starts at 5.0 s)

    def part1(t, fade):
        title_block(c, "Knockout goals after two rounds", "Round of 16 and quarter-final",
                    alpha=fade * ep(t, 0, 0.5))
        a = fade * ep(t, 1.0, 0.5)
        c.tokens(1840, 990, [("8", TEXT, "bold"), (" goals", MUTED, "regular")], size=34,
                 alpha=a, ha="right")
        BS, GAP, X0 = 72, 12, 640
        times = [2.0, 2.7, 3.4, 4.1]  # Suárez four, Neymar three, Rakitić one, Messi none
        for k, ((name, n, col), tr) in enumerate(zip(KO_AFTER_QF, times)):
            y = 700 - k * 140
            ra = fade * ep(t, tr - 0.2, 0.4)
            c.text(X0 - 40, y + 18, name, size=34, weight="semibold", ha="right", alpha=ra)
            for i in range(n):
                ba = fade * ep(t, tr + i * 0.09, 0.3)
                c.box(X0 + i * (BS + GAP), y - (1 - ba) * 12, BS, BS, r=8, fc=col, alpha=ba)
            if n == 0:
                # empty slot outline for Messi
                c.box(X0, y, BS, BS, r=8, fc="none", ec=FAINT, lw=2, alpha=ra)
            xn = X0 + max(n, 1) * (BS + GAP) + 18
            c.text(xn, y + 14, str(n), size=44, weight="bold", color=col if n else MESSI, alpha=ra)

    def part2(t, fade):
        title_block(c, "Same three forwards. The goals moved.",
                    "Champions League 2014/15 · one block = one goal", alpha=fade)
        ha = fade
        c.text(560, 800, "Group stage", size=26, weight="semibold", color=MUTED, ha="center", alpha=ha)
        c.text(1360, 800, "Knockouts", size=26, weight="semibold", color=MUTED, ha="center", alpha=ha)
        BS, GAP = 54, 10
        XL, XR = 960 - 150, 960 + 150
        # row emphasis: (start, end) of each forward's line
        focus = {"Neymar": (10.0, 14.0), "Suárez": (14.0, 17.0), "Messi": (17.0, 21.0)}
        t_ko = {"Neymar": 12.6, "Suárez": 15.9, "Messi": 19.4}
        for k, (name, g, ko, col) in enumerate(SPLIT):
            y = 620 - k * 150
            # emphasis factor for this row
            active = [nm for nm, (s, e) in focus.items() if s <= t < e]
            emph = 1.0
            if active and active[0] != name:
                emph = 0.35
            if t >= 25.0 and t < 28.8 and name == "Messi":
                emph = 0.35  # L73 overlay is about Neymar and Suárez
            ra = fade * emph
            c.text(960, y + 14, name, size=32, weight="semibold", ha="center", alpha=ra * ep(t, 5.4, 0.4))
            # group blocks (leftwards), built on L67
            tg = 5.8 + k * 0.6
            for i in range(g):
                ba = ep(t, tg + i * 0.06, 0.3)
                x = XL - (i + 1) * BS - i * GAP
                c.box(x, y - (1 - ba) * 12, BS, BS, r=7, fc=col, alpha=ra * ba)
            na = ep(t, tg + g * 0.06, 0.3)
            c.text(XL - g * (BS + GAP) - 14, y + 12, str(g), size=42, weight="bold", ha="right",
                   alpha=ra * na)
            # knockout blocks (rightwards), on the forward's own line
            tk = t_ko[name]
            for i in range(ko):
                ba = ep(t, tk + i * 0.08, 0.3)
                x = XR + i * (BS + GAP)
                c.box(x, y - (1 - ba) * 12, BS, BS, r=7, fc=col, alpha=ra * ba)
            na = ep(t, tk + ko * 0.08, 0.3)
            c.text(XR + ko * (BS + GAP) + 12, y + 12, str(ko), size=42, weight="bold", alpha=ra * na)

        # overlays, L73
        a1 = ep(t, 25.3, 0.5) * fade
        c.tokens(520, 170, [("Neymar", NEYMAR, "bold"), (" + ", TEXT, "bold"), ("Suárez", SUAREZ, "bold"),
                            (": 12 of 16", TEXT, "bold")], size=34, alpha=a1, ha="center")
        c.text(520, 125, "knockout goals", size=18, color=MUTED, ha="center", alpha=a1)
        a2 = ep(t, 28.8, 0.5) * fade
        c.tokens(1400, 170, [("Messi", MESSI, "bold"), (": top assister, 6", TEXT, "bold")],
                 size=34, alpha=a2, ha="center")
        c.text(1400, 125, "assists in the competition", size=18, color=MUTED, ha="center", alpha=a2)

    def draw(t):
        if t < P2_IN:
            part1(t, 1 - prog(t, P1_OUT, 0.35))
        if t >= P2_IN:
            part2(t, ep(t, P2_IN, 0.5))

    return c, draw, None


CLIPS = {"C1a": c1a, "C1b": c1b}

if __name__ == "__main__":
    for key in sys.argv[1:] or CLIPS:
        clip, draw, zoom = CLIPS[key]()
        print("rendered", clip.render(draw, zoom=zoom))
