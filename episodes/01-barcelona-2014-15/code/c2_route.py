"""C2 route chart family: C2 (intro), C2a (group), C2b (R16), C2c (QF), C2d (SF),
C2e (final node), C2f (full run with totals). Verified run in CLAUDE.md only.

Clip times are seconds from the start of the script line the clip is placed on.
Scores are written Barcelona first, as in CLAUDE.md.
"""
import sys

import numpy as np

from common import (Clip, ep, prog, title_block, text_width, W, BG, PANEL, LINE, FAINT, MUTED,
                    TEXT, BARCA, OPP, MESSI, NEYMAR, SUAREZ, PLAYER_COL)

PAST = -10.0  # "already on screen" time

COLX = [256, 608, 960, 1312, 1664]
NODE_Y = 870
NODE_LABELS = ["Group F", "Round of 16", "Quarter-final", "Semi-final", "Final"]
CARD_W, CARD_H, CARD_GAP, CARD_TOP = 344, 92, 10, 820

# key: (column, slot, label, opponent, venue, result, score, scorers)
MATCHES = {
    "MD1": (0, 0, "MD1", "APOEL", "home", "W", "1-0", [("Piqué", 1)]),
    "MD2": (0, 1, "MD2", "PSG", "away", "L", "2-3", [("Messi", 1), ("Neymar", 1)]),
    "MD3": (0, 2, "MD3", "Ajax", "home", "W", "3-1", [("Neymar", 1), ("Messi", 1), ("Sandro", 1)]),
    "MD4": (0, 3, "MD4", "Ajax", "away", "W", "2-0", [("Messi", 2)]),
    "MD5": (0, 4, "MD5", "APOEL", "away", "W", "4-0", [("Messi", 3), ("Suárez", 1)]),
    "MD6": (0, 5, "MD6", "PSG", "home", "W", "3-1", [("Messi", 1), ("Neymar", 1), ("Suárez", 1)]),
    "R1": (1, 0, "Leg 1", "Man City", "away", "W", "2-1", [("Suárez", 2)]),
    "R2": (1, 1, "Leg 2", "Man City", "home", "W", "1-0", [("Rakitić", 1)]),
    "Q1": (2, 0, "Leg 1", "PSG", "away", "W", "3-1", [("Neymar", 1), ("Suárez", 2)]),
    "Q2": (2, 1, "Leg 2", "PSG", "home", "W", "2-0", [("Neymar", 2)]),
    "S1": (3, 0, "Leg 1", "Bayern", "home", "W", "3-0", [("Messi", 2), ("Neymar", 1)]),
    "S2": (3, 1, "Leg 2", "Bayern", "away", "L", "2-3", [("Neymar", 2)]),
    "F": (4, 0, "Final", "Juventus", "Berlin", "W", "3-1", [("Rakitić", 1), ("Suárez", 1), ("Neymar", 1)]),
}
AGG = {1: "Agg 3-1", 2: "Agg 5-1", 3: "Agg 5-3"}
HOME = ["MD1", "MD3", "MD6", "R2", "Q2", "S1"]
LOSSES = ["MD2", "S2"]
GROUP_KEYS = ["MD1", "MD2", "MD3", "MD4", "MD5", "MD6"]


def card_xy(key):
    col, slot = MATCHES[key][0], MATCHES[key][1]
    x = COLX[col] - CARD_W / 2
    top = CARD_TOP - slot * (CARD_H + CARD_GAP)
    return x, top


def bezier(p0, p1, p2, n=80):
    s = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.array, (p0, p1, p2))
    return (1 - s) ** 2 * p0 + 2 * (1 - s) * s * p1 + s ** 2 * p2


# ------------------------------------------------------------------ drawing
def draw_card(c, key, t, t_card, t_sc, dim=1.0, outline=None, hl=None):
    a = ep(t, t_card, 0.45) * dim
    if a <= 0:
        return
    col, slot, label, opp, venue, res, score, scorers = MATCHES[key]
    x, top = card_xy(key)
    rise = (1 - ep(t, t_card, 0.45)) * 18
    top -= rise
    y = top - CARD_H
    c.box(x, y, CARD_W, CARD_H, r=12, fc=PANEL, ec=LINE, lw=1.5, alpha=a)
    if outline:
        oc, oa, ls = outline
        if oa > 0:
            c.box(x - 3, y - 3, CARD_W + 6, CARD_H + 6, r=14, fc="none", ec=oc, lw=3.5, alpha=oa * dim)
    c.tokens(x + 16, top - 34, [(label, MUTED, "regular"), ("   ", MUTED, "regular"),
                                (opp, TEXT, "semibold")], size=18, alpha=a)
    c.text(x + CARD_W - 16, top - 74, venue, size=16, color=MUTED, ha="right", alpha=a)
    # result chip
    cw, ch = 88, 34
    cx, cy = x + CARD_W - 14 - cw, top - 48
    c.box(cx, cy, cw, ch, r=8, fc=BARCA if res == "W" else OPP, alpha=a, zorder=3)
    c.text(cx + cw / 2, cy + ch / 2 - 1, f"{res} {score}", size=18, weight="bold",
           color=TEXT if res == "W" else BG, ha="center", va="center_baseline", alpha=a, zorder=4)
    # scorers
    sa = ep(t, t_sc, 0.4) * dim
    if sa <= 0:
        return
    toks = []
    for i, (name, n) in enumerate(scorers):
        if i:
            toks.append((", ", MUTED, "regular", None))
        toks.append((name, PLAYER_COL.get(name, TEXT), "semibold", name))
        if n > 1:
            toks.append((f" ({n})", TEXT, "regular", name))
    size = 16 if len(scorers) < 3 else 15
    cxp = x + 14
    by = top - 74
    spans = {}
    for s, colr, w, owner in toks:
        wd = text_width(s, size, w)
        c.text(cxp, by, s, size=size, color=colr, weight=w, alpha=sa)
        if owner:
            lo, hi = spans.get(owner, (cxp, cxp))
            spans[owner] = (min(lo, cxp), cxp + wd)
        cxp += wd
    for name, ha in (hl or {}).items():
        if ha > 0 and name in spans:
            lo, hi = spans[name]
            colr = PLAYER_COL.get(name, TEXT)
            c.box(lo - 7, by - 9, hi - lo + 14, 33, r=8, fc=colr, ec=colr, lw=2,
                  alpha=0.22 * ha * dim, zorder=3)
            c.box(lo - 7, by - 9, hi - lo + 14, 33, r=8, fc="none", ec=colr, lw=2.5,
                  alpha=ha * dim, zorder=3)


def draw_route(c, t, cfg):
    title_block(c, "Barcelona 2014/15", "Champions League route · Barcelona score first",
                alpha=ep(t, cfg.get("title_t", PAST), 0.6))

    # name tags (top right)
    xr = 1840
    tags = [("Suárez", SUAREZ), ("Neymar", NEYMAR), ("Messi", MESSI)]
    tag_t = cfg.get("tags_t", [PAST] * 3)[::-1]
    for (name, colr), tt in zip(tags, tag_t):
        w = text_width(name, 21, "semibold") + 58
        a = ep(t, tt, 0.35)
        bump = 1 + 0.35 * np.sin(np.pi * prog(t, tt, 0.5))
        x = xr - w
        c.box(x, 985, w, 46, r=23, fc=PANEL, ec=colr if bump > 1.01 else LINE, lw=2, alpha=a)
        c.circle(x + 24, 1008, 9 * bump, fc=colr, alpha=a, zorder=6)
        c.text(x + 42, 1001, name, size=21, weight="semibold", alpha=a)
        xr = x - 14

    # route line and nodes
    node_t = cfg.get("route_t", [PAST] * 5)
    for i in range(4):
        p = ep(t, node_t[i] + 0.1, 0.35)
        if p > 0:
            x0, x1 = COLX[i] + 16, COLX[i + 1] - 16
            c.line([x0, x0 + (x1 - x0) * p], [NODE_Y, NODE_Y], color=FAINT, lw=3, zorder=2)
    nodes = cfg.get("nodes", {})
    for i in range(5):
        a = ep(t, node_t[i], 0.35)
        if a <= 0:
            continue
        t_cur, t_done = nodes.get(i, (None, None))
        cur = t_cur is not None and t >= t_cur and (t_done is None or t < t_done)
        done = t_done is not None and t >= t_done
        if cur:
            k = ep(t, t_cur, 0.4)
            pulse = 0.5 + 0.5 * np.sin((t - t_cur) * 3.0)
            c.circle(COLX[i], NODE_Y, 20 + 6 * pulse, fc=BARCA, alpha=0.18 * k * a, zorder=3)
            c.circle(COLX[i], NODE_Y, 13, fc=BARCA, ec=BARCA, lw=3, alpha=a, zorder=4)
            lc = TEXT
        elif done:
            c.circle(COLX[i], NODE_Y, 13, fc=BARCA, ec=BARCA, lw=3, alpha=a * 0.85, zorder=4)
            lc = TEXT
        else:
            c.circle(COLX[i], NODE_Y, 13, fc=BG, ec=FAINT, lw=3, alpha=a, zorder=4)
            lc = MUTED
        c.text(COLX[i], 905, NODE_LABELS[i], size=21, weight="semibold", color=lc, ha="center", alpha=a)

    # emphasis for C2f
    home_a = ep(t, cfg.get("home_t", 1e9), 0.6)
    loss_a = ep(t, cfg.get("loss_t", 1e9), 0.6)

    hls = cfg.get("hl", [])
    for key, (tc, ts) in cfg.get("cards", {}).items():
        if key == "F" and cfg.get("final_info"):
            continue
        dim = 1.0
        outline = None
        if home_a > 0:
            if key in HOME:
                outline = (BARCA, home_a, "-")
            elif key in LOSSES and loss_a > 0:
                outline = (OPP, loss_a, "-")
            else:
                dim = 1 - 0.55 * max(home_a - (loss_a if key in LOSSES else 0), 0)
        if cfg.get("arc_t") is not None and key == "MD2":
            outline = (OPP, ep(t, cfg["arc_t"] + 0.8, 0.4), "-")
        hl = {}
        for hk, name, h0, h1 in hls:
            if hk == key:
                hl[name] = ep(t, h0, 0.35) * (1 - ep(t, h1, 0.5))
        draw_card(c, key, t, tc, ts, dim=dim, outline=outline, hl=hl)

    # group table
    tt = cfg.get("table_t")
    if tt:
        y = CARD_TOP - 6 * (CARD_H + CARD_GAP) - 26
        x = COLX[0] - CARD_W / 2 + 16
        a1, a2 = ep(t, tt[0], 0.4), ep(t, tt[1], 0.4)
        c.tokens(x, y, [("1st   ", MUTED, "regular"), ("Barcelona", BARCA, "semibold"),
                        ("   15 pts", TEXT, "semibold")], size=19, alpha=a1)
        c.tokens(x, y - 34, [("2nd   ", MUTED, "regular"), ("PSG", OPP, "semibold"),
                             ("   13 pts", TEXT, "semibold")], size=19, alpha=a2)

    # aggregates
    for col, ta in cfg.get("agg", {}).items():
        a = ep(t, ta, 0.4)
        y = CARD_TOP - 2 * (CARD_H + CARD_GAP) - 28
        c.text(COLX[col], y, AGG[col], size=23, weight="bold", ha="center", alpha=a)

    # QF to MD2 link
    if cfg.get("arc_t") is not None:
        p = ep(t, cfg["arc_t"], 0.8)
        if p > 0:
            mx, mtop = card_xy("MD2")
            pts = bezier((COLX[2] - 40, 560), (700, 330), (mx + CARD_W + 10, mtop - CARD_H / 2))
            n = max(2, int(len(pts) * p))
            c.line(pts[:n, 0], pts[:n, 1], color=OPP, lw=2.5, ls=(0, (6, 5)), zorder=6)
            if p >= 0.98:
                # arrow head
                d = pts[-1] - pts[-4]
                d = d / np.linalg.norm(d)
                nrm = np.array([-d[1], d[0]])
                tip = pts[-1]
                tri = np.array([tip, tip - 18 * d + 9 * nrm, tip - 18 * d - 9 * nrm])
                from matplotlib.patches import Polygon
                c.track(c.ax.add_patch(Polygon(tri, closed=True, fc=OPP, ec="none", zorder=6)))
            la = ep(t, cfg["arc_t"] + 0.6, 0.5)
            c.text(720, 425, "Lost 2-3 to PSG in Paris, MD2", size=18, color=MUTED, ha="center", alpha=la)

    # Messi knockout counter
    mc = cfg.get("messi")
    if mc:
        a = ep(t, mc[0][0], 0.4)
        val, t_last = mc[0][1], mc[0][0]
        for tv, v in mc:
            if t >= tv:
                val, t_last = v, tv
        if a > 0:
            bx, by, bw, bh = 1310, 250, 360, 150
            c.box(bx, by, bw, bh, r=14, fc=PANEL, ec=LINE, lw=1.5, alpha=a)
            c.text(bx + 24, by + bh - 40, "Messi, knockout goals", size=19, color=MUTED, alpha=a)
            s = 1 + 0.4 * np.sin(np.pi * prog(t, t_last, 0.5)) if t_last != mc[0][0] else 1
            c.text(bx + 24, by + 26, str(val), size=60 * s, weight="bold", color=MESSI, alpha=a)

    # final info card (C2e)
    fi = cfg.get("final_info")
    if fi:
        t0, t1, t2, t3 = fi
        a = ep(t, t0, 0.45)
        x = COLX[4] - CARD_W / 2
        top = CARD_TOP - (1 - a) * 18
        h = 170
        c.box(x, top - h, CARD_W, h, r=12, fc=PANEL, ec=BARCA, lw=2, alpha=a)
        c.text(x + 18, top - 36, "Final", size=17, color=MUTED, alpha=a)
        c.text(x + 18, top - 74, "6 June 2015", size=22, weight="semibold", alpha=ep(t, t1, 0.4))
        c.text(x + 18, top - 110, "Olympiastadion, Berlin", size=19, alpha=ep(t, t2, 0.4))
        c.tokens(x + 18, top - 148, [("Juventus", OPP, "semibold"), (" v ", MUTED, "regular"),
                                     ("Barcelona", BARCA, "semibold")], size=20, alpha=ep(t, t3, 0.4))

    # totals (C2f)
    tot = cfg.get("totals")
    if tot:
        items = [("13", "played"), ("11", "won"), ("2", "lost"), ("31", "scored"), ("11", "conceded")]
        xs = [600, 860, 1120, 1380, 1640]
        for (num, lab), x, tv in zip(items, xs, tot):
            a = ep(t, tv, 0.4)
            rise = (1 - a) * 14
            c.text(x, 300 - rise, num, size=62, weight="bold", ha="center", alpha=a)
            c.text(x, 258 - rise, lab, size=20, color=MUTED, ha="center", alpha=a)
        if home_a > 0:
            c.tokens(860, 160, [("Home games: ", MUTED, "regular"), ("won 6 of 6", TEXT, "semibold")],
                     size=22, alpha=home_a, ha="center")
        if loss_a > 0:
            c.tokens(1460, 160, [("Both defeats: ", MUTED, "regular"),
                                 ("away, 2-3 and 2-3", TEXT, "semibold")],
                     size=22, alpha=loss_a, ha="center")


# ------------------------------------------------------------------ clip configs
def all_past(keys):
    return {k: (PAST, PAST) for k in keys}


def cfg_c2():
    # L10 to L13 (0:43). Route draws in, then 'Messi. Neymar. Luis Suárez.'
    return {"title_t": 0.0, "route_t": [0.3, 0.6, 0.9, 1.2, 1.5], "tags_t": [2.0, 2.7, 3.5]}


def cfg_c2a():
    # L14 to L22 (1:02). Card at each line, scorers on the scorer mention.
    cards = {"MD1": (3.3, 8.0), "MD2": (10.3, 13.0), "MD3": (19.3, 21.0),
             "MD4": (22.3, 24.0), "MD5": (25.3, 26.8), "MD6": (29.3, 31.5)}
    return {"nodes": {0: (0.3, 38.0)}, "cards": cards, "table_t": (35.0, 37.3)}


def cfg_c2b():
    # L27 to L32 (1:58)
    cards = all_past(GROUP_KEYS)
    cards.update({"R1": (3.3, 6.4), "R2": (15.3, 17.6)})
    return {"nodes": {0: (PAST, PAST), 1: (0.3, 26.0)}, "cards": cards, "table_t": (PAST, PAST),
            "agg": {1: 20.3}, "messi": [(21.2, 0)]}


def cfg_c2c():
    # L33 to L37 (2:25)
    cards = all_past(GROUP_KEYS + ["R1", "R2"])
    cards.update({"Q1": (4.3, 6.2), "Q2": (9.0, 10.3)})
    return {"nodes": {0: (PAST, PAST), 1: (PAST, PAST), 2: (0.3, 20.0)}, "cards": cards,
            "table_t": (PAST, PAST), "agg": {1: PAST, 2: 11.2}, "messi": [(PAST, 0)],
            "arc_t": 13.3}


def cfg_c2d():
    # L39 to L44 (2:50)
    cards = all_past(GROUP_KEYS + ["R1", "R2", "Q1", "Q2"])
    cards.update({"S1": (2.3, 3.6), "S2": (9.3, 10.8)})
    hl = [("S1", "Neymar", 12.4, 16.5), ("S2", "Neymar", 12.4, 16.5), ("S1", "Messi", 20.4, 99)]
    return {"nodes": {0: (PAST, PAST), 1: (PAST, PAST), 2: (PAST, PAST), 3: (0.3, 25.0)},
            "cards": cards, "table_t": (PAST, PAST), "agg": {1: PAST, 2: PAST, 3: 17.3},
            "messi": [(PAST, 0), (4.4, 2)], "hl": hl}


def cfg_c2e():
    # L49 (3:36): 'The final. The sixth of June, twenty fifteen. The Olympiastadion in Berlin.
    # Juventus against Barcelona.'
    cards = all_past(GROUP_KEYS + ["R1", "R2", "Q1", "Q2", "S1", "S2"])
    return {"nodes": {0: (PAST, PAST), 1: (PAST, PAST), 2: (PAST, PAST), 3: (PAST, PAST), 4: (0.3, None)},
            "cards": cards, "table_t": (PAST, PAST), "agg": {1: PAST, 2: PAST, 3: PAST},
            "messi": [(PAST, 2)], "final_info": (0.4, 1.4, 2.9, 4.4)}


def cfg_c2f():
    # L63 to L66 (4:48). Totals on L64, home games on L66, the two defeats on 'Three-two in Paris'.
    cards = all_past(list(MATCHES))
    return {"nodes": {i: (PAST, PAST) for i in range(5)}, "cards": cards, "table_t": (PAST, PAST),
            "agg": {1: PAST, 2: PAST, 3: PAST}, "totals": [3.0, 4.0, 5.0, 7.0, 8.2],
            "home_t": 14.3, "loss_t": 19.0}


def make(name, dur, cfg_fn):
    def factory():
        c = Clip(name, dur)
        cfg = cfg_fn()
        return c, (lambda t: draw_route(c, t, cfg)), None
    return factory


CLIPS = {
    "C2": make("C2_route_intro", 21.0, cfg_c2),
    "C2a": make("C2a_route_group_stage", 46.0, cfg_c2a),
    "C2b": make("C2b_route_r16", 29.0, cfg_c2b),
    "C2c": make("C2c_route_qf", 22.0, cfg_c2c),
    "C2d": make("C2d_route_sf", 27.0, cfg_c2d),
    "C2e": make("C2e_route_final", 8.0, cfg_c2e),
    "C2f": make("C2f_route_full", 26.0, cfg_c2f),
}

if __name__ == "__main__":
    for key in sys.argv[1:] or CLIPS:
        clip, draw, zoom = CLIPS[key]()
        print("rendered", clip.render(draw, zoom=zoom))
