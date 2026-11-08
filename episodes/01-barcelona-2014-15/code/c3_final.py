"""C3 (final xG timeline), C4 (final shot map), C5 (Rakitić goal reconstruction).

StatsBomb open data, 2015 Champions League final (match 18242), via statsbombpy.
check_figures() compares the data with CLAUDE.md and stops the render if anything differs.
Clip times are seconds from the start of the script line the clip is placed on.
"""
import os
import sys
import warnings

import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

from common import (Clip, ep, prog, interp_keys, title_block, text_width, W, H, BG, PANEL, LINE,
                    FAINT, MUTED, TEXT, BARCA, OPP, CREDIT)

warnings.filterwarnings("ignore")

MATCH_ID = 18242  # Juventus 1-3 Barcelona, 6 June 2015 (competition 16, season 26)
CACHE = os.path.join(os.path.dirname(__file__), "data_cache", f"events_{MATCH_ID}.pkl")

# Figures recorded in CLAUDE.md
EXPECTED = {
    ("Barcelona", "shots"): 17, ("Barcelona", "xg"): 2.27,
    ("Juventus", "shots"): 15, ("Juventus", "xg"): 1.38,
    ("Barcelona", "passes"): 600, ("Juventus", "passes"): 377,
    ("Barcelona", "pressures"): 122, ("Juventus", "pressures"): 144,
}

SHORT = {
    "Ivan Rakitić": "Rakitić", "Álvaro Borja Morata Martín": "Morata",
    "Luis Alberto Suárez Díaz": "Suárez", "Neymar da Silva Santos Junior": "Neymar",
    "Lionel Andrés Messi Cuccittini": "Messi", "Andrés Iniesta Luján": "Iniesta",
    "Jordi Alba Ramos": "Jordi Alba", "Gianluigi Buffon": "Buffon",
}


def load_events():
    if os.path.exists(CACHE):
        return pd.read_pickle(CACHE)
    from statsbombpy import sb
    ev = sb.events(match_id=MATCH_ID)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    ev.to_pickle(CACHE)
    return ev


def check_figures(ev, verbose=True):
    shots = ev[ev.type == "Shot"]
    got = {}
    for team in ("Barcelona", "Juventus"):
        got[(team, "shots")] = int((shots.team == team).sum())
        got[(team, "xg")] = round(float(shots[shots.team == team].shot_statsbomb_xg.sum()), 2)
        got[(team, "passes")] = int(((ev.type == "Pass") & (ev.team == team)).sum())
        got[(team, "pressures")] = int(((ev.type == "Pressure") & (ev.team == team)).sum())
    bad = {k: (EXPECTED[k], got[k]) for k in EXPECTED if abs(EXPECTED[k] - got[k]) > 1e-9}
    if verbose:
        for k in EXPECTED:
            print(f"  {k[0]:9s} {k[1]:9s} CLAUDE.md {EXPECTED[k]:>7}  StatsBomb {got[k]:>7}")
    if bad:
        raise SystemExit(f"StatsBomb figures differ from CLAUDE.md: {bad}. Not rendering.")
    return got


def shot_table(ev):
    s = ev[ev.type == "Shot"].copy()
    s["m"] = s.minute + s.second / 60.0
    s = s.sort_values("m")
    s["name"] = s.player.map(lambda p: SHORT.get(p, p.split()[0]))
    s["x"] = s.location.map(lambda l: l[0])
    s["y"] = s.location.map(lambda l: l[1])
    return s


def minute_label(m):
    mi = int(m) + 1
    return f"90+{mi - 90}'" if mi > 90 else f"{mi}'"


# ======================================================================= C3
def c3():
    """L52 to L57 (3:50). Goals pop on L52 to L54, totals on L57. 32 s."""
    ev = load_events()
    check_figures(ev, verbose=False)
    s = shot_table(ev)
    c = Clip("C3_final_xg_timeline", 32.0)
    PX0, PX1, PY0, PY1 = 190, 1500, 190, 830
    MMAX, XGMAX = 98.0, 2.5
    X = lambda m: PX0 + (PX1 - PX0) * m / MMAX
    Y = lambda g: PY0 + (PY1 - PY0) * g / XGMAX

    series = {}
    for team in ("Barcelona", "Juventus"):
        st = s[s.team == team]
        ms, gs = [0.0], [0.0]
        cum = 0.0
        for m, g in zip(st.m, st.shot_statsbomb_xg):
            ms += [m, m]
            gs += [cum, cum + g]
            cum += g
        ms.append(MMAX - 0.5)
        gs.append(cum)
        series[team] = (np.array(ms), np.array(gs), cum, len(st))
    goals = []
    for _, r in s[s.shot_outcome == "Goal"].iterrows():
        ms, gs, _, _ = series[r.team]
        cum_after = gs[np.searchsorted(ms, r.m, side="right") - 1]
        goals.append((r.team, r.m, cum_after, f"{r['name']} {minute_label(r.m)}"))

    # match clock: Morata 55' on 'equalised', Suárez on 'Suárez', Neymar on 'Neymar'
    clock = [(0.0, 0.0), (2.4, 54.4), (5.4, 68.0), (9.8, 96.75), (10.4, MMAX - 0.5)]
    T_STATS = 11.3
    T_END = {"Barcelona": 22.6, "Juventus": 25.8}
    col = {"Barcelona": BARCA, "Juventus": OPP}

    # static layer
    c.static = True
    for g in (0.5, 1.0, 1.5, 2.0, 2.5):
        c.line([PX0, PX1], [Y(g)] * 2, color=LINE, lw=1.2, zorder=1)
        c.text(PX0 - 18, Y(g), f"{g:.1f}", size=17, color=MUTED, ha="right", va="center")
    c.line([PX0, PX1], [PY0, PY0], color=FAINT, lw=2, zorder=1)
    for m in (0, 15, 30, 45, 60, 75, 90):
        c.text(X(m), PY0 - 36, f"{m}'", size=17, color=MUTED, ha="center")
    c.line([X(45)] * 2, [PY0, PY1], color=FAINT, lw=1.5, ls=(0, (4, 4)), zorder=1)
    c.text(X(45) + 8, PY1 - 22, "Half-time", size=15, color=MUTED)
    c.text(PX0 - 18, PY1 + 30, "xG", size=17, color=MUTED, ha="right")
    title_block(c, "Juventus 1-3 Barcelona",
                "Champions League final, Berlin, 6 June 2015 · cumulative expected goals (xG)")
    c.credit()
    c.static = False

    def draw(t):
        M = interp_keys(t, clock)
        for team in ("Juventus", "Barcelona"):
            ms, gs, tot, n = series[team]
            k = np.searchsorted(ms, M, side="right")
            xs = list(ms[:k]) + [M]
            ys = list(gs[:k]) + [gs[k - 1]]
            c.line([X(v) for v in xs], [Y(v) for v in ys], color=col[team], lw=4, zorder=4)
            hx, hy = X(M), Y(ys[-1])
            # head label: team name, then the totals on L57
            ea = ep(t, T_END[team], 0.5)
            c.text(hx + 20, hy + 6, team, size=22, weight="semibold", color=TEXT, va="baseline")
            c.circle(hx, hy, 7, fc=col[team], zorder=6)
            if ea > 0:
                c.tokens(hx + 20, hy - 30, [(f"{tot:.2f}", TEXT, "bold"), (" xG", MUTED, "regular"),
                                            (f"  ·  {n}", TEXT, "bold"), (" shots", MUTED, "regular")],
                         size=22 * (1 + 0.2 * (1 - ea)), alpha=ea)
        for team, gm, gy, lab in goals:
            if M < gm:
                continue
            tg = interp_keys(gm, [(m, tt) for tt, m in clock])  # when the clock reached it
            a = ep(t, tg, 0.35)
            r = 13 * (1 + 0.6 * np.sin(np.pi * prog(t, tg, 0.45)))
            c.circle(X(gm), Y(gy), r, fc=col[team], ec=TEXT, lw=2.5, alpha=a, zorder=7)
            if team == "Barcelona" and gm < 10:
                c.text(X(gm) + 4, Y(gy) + 30, lab, size=19, weight="semibold", ha="left", alpha=a)
            elif team == "Barcelona":
                c.text(X(gm) - 14, Y(gy) + 26, lab, size=19, weight="semibold", ha="right", alpha=a)
            else:
                c.text(X(gm) - 16, Y(gy) + 24, lab, size=19, weight="semibold", ha="right", alpha=a)
        a = ep(t, T_STATS, 0.5)
        c.box(1490, 970, 350, 52, r=26, fc=PANEL, ec=LINE, lw=1.5, alpha=a)
        c.text(1665, 989, "According to StatsBomb", size=20, weight="semibold", ha="center", alpha=a)

    return c, draw, None


# ======================================================================= C4
def c4():
    """L58 to L59 (4:20). 12 s. Bottom 220 px left clear for a CapCut lower third."""
    from mplsoccer import Pitch
    ev = load_events()
    check_figures(ev, verbose=False)
    s = shot_table(ev)
    c = Clip("C4_final_shot_map", 12.0)
    pax = c.fig.add_axes([460 / W, 225 / H, 1000 / W, 660 / H])
    pitch = Pitch(pitch_type="statsbomb", pitch_color=BG, line_color=FAINT, linewidth=2,
                  goal_type="box", pad_left=2, pad_right=2, pad_top=2, pad_bottom=2)
    pitch.draw(ax=pax)
    pax.set_facecolor(BG)

    s = s.reset_index(drop=True)
    # Barcelona attack right; Juventus shots rotated to attack left
    s["px"] = np.where(s.team == "Barcelona", s.x, 120 - s.x)
    s["py"] = np.where(s.team == "Barcelona", s.y, 80 - s.y)
    T0, T1 = 0.6, 7.0
    s["tp"] = T0 + (T1 - T0) * np.arange(len(s)) / (len(s) - 1)
    size = lambda g: 60 + 1900 * g
    col = {"Barcelona": BARCA, "Juventus": OPP}

    c.static = True
    title_block(c, "Juventus 1-3 Barcelona: every shot",
                "Champions League final 2015 · circle size shows xG · filled circle = goal")
    c.text(460 + 500 - 260, 905, "Juventus attack", size=16, color=MUTED, ha="center")
    c.text(460 + 500 + 260, 905, "Barcelona attack", size=16, color=MUTED, ha="center")
    c.text(460 + 500 - 380, 905, "←", size=18, color=MUTED, ha="center")
    c.text(460 + 500 + 380, 905, "→", size=18, color=MUTED, ha="center")
    # size key, top right
    kx = 1560
    c.text(kx, 1010, "xG", size=16, color=MUTED)
    for i, g in enumerate((0.05, 0.2, 0.5)):
        x = kx + 30 + i * 90
        pax_s = c.ax.scatter([x + 30], [1016], s=size(g), fc="none", ec=MUTED, lw=1.5, zorder=5)
        c.text(x + 30, 970, f"{g:g}", size=14, color=MUTED, ha="center")
    c.credit()
    c.static = False

    def panel(team, x, ha, t):
        st = s[(s.team == team) & (s.tp <= t)]
        n = len(st)
        xg = st.shot_statsbomb_xg.sum()
        sign = 1 if ha == "left" else -1
        c.circle(x + sign * 10, 820, 10, fc=col[team])
        c.text(x + sign * 32, 811, team, size=26, weight="bold", ha=ha)
        c.text(x, 720, f"{n}", size=60, weight="bold", ha=ha)
        c.text(x, 690, "shots", size=19, color=MUTED, ha=ha)
        c.text(x, 590, f"{xg:.2f}", size=60, weight="bold", ha=ha)
        c.text(x, 560, "xG", size=19, color=MUTED, ha=ha)

    def draw(t):
        panel("Juventus", 80, "left", t)
        panel("Barcelona", 1840, "right", t)
        for _, r in s.iterrows():
            a = ep(t, r.tp, 0.3)
            if a <= 0:
                continue
            pop = 1 + 0.5 * np.sin(np.pi * prog(t, r.tp, 0.35))
            goal = r.shot_outcome == "Goal"
            cc = col[r.team]
            sc = pitch.scatter(r.px, r.py, s=size(r.shot_statsbomb_xg) * pop, ax=pax,
                               fc=cc if goal else (*mcolors.to_rgb(cc), 0.22),
                               ec=TEXT if goal else cc, lw=2.5 if goal else 1.8, alpha=a, zorder=5 if goal else 4)
            c.track(sc)
            if goal:
                lab = f"{r['name']} {minute_label(r.m)}"
                # labels sit in clear space with a leader line to the shot
                lx, ly = {"Neymar": (90, 13), "Rakitić": (90, 40), "Suárez": (90, 67),
                          "Morata": (30, 68)}[r["name"]]
                la = ep(t, r.tp + 0.2, 0.3)
                right = r.team == "Barcelona"
                c.track(pax.plot([lx + (1 if right else -1), r.px], [ly, r.py], color=MUTED, lw=1.2,
                                 alpha=la, zorder=3)[0])
                txt = pax.text(lx, ly, lab, fontsize=18, fontweight="semibold", color=TEXT,
                               family="Inter", ha="right" if right else "left", va="center",
                               alpha=la, zorder=8)
                c.track(txt)

    return c, draw, None


# ======================================================================= C5
def c5():
    """L50 to L51 (3:42). Ball reaches the net at the end of L50 ('One-nil'). 10 s.
    'RECONSTRUCTION' and the StatsBomb credit are on screen for the whole clip."""
    from mplsoccer import VerticalPitch
    ev = load_events()
    check_figures(ev, verbose=False)
    ev = ev.sort_values("index")
    shot = ev[(ev.type == "Shot") & (ev.shot_outcome == "Goal") & (ev.period == 1)].iloc[0]
    assert SHORT[shot.player] == "Rakitić" and shot.minute == 3
    poss = ev[(ev.possession == shot.possession) & (ev["index"] >= 133) & (ev["index"] <= shot["index"])]

    # build the ball path from Messi's carry to the shot, straight from the events
    segs = []  # (kind, player, start xy, end xy)
    for _, r in poss.iterrows():
        if r.type == "Carry" and r["index"] >= 135:
            segs.append(("carry", SHORT[r.player], r.location, r.carry_end_location))
        elif r.type == "Pass" and r["index"] >= 136:
            segs.append(("pass", SHORT[r.player], r.location, r.pass_end_location,
                         SHORT[r.pass_recipient]))
    segs = [sg for sg in segs if not (sg[0] == "carry" and np.allclose(sg[2], sg[3]))]
    # last pass ends where the shot was taken
    last = list(segs[-1])
    last[3] = shot.location
    segs[-1] = tuple(last)
    segs.append(("shot", "Rakitić", shot.location, shot.shot_end_location[:2]))

    # clip timing (seconds): move compressed so the ball hits the net at the end of L50
    dur = {"carry": 0.32, "pass": 0.42, "shot": 0.3}
    times, tt = [], 0.35
    for sg in segs:
        d = dur[sg[0]]
        if sg[0] == "pass" and np.hypot(*(np.array(sg[3]) - np.array(sg[2]))) > 25:
            d = 0.7
        times.append((tt, tt + d))
        tt += d
    T_GOAL = times[-1][1]
    T_FREEZE = T_GOAL + 0.35

    c = Clip("C5_rakitic_goal_reconstruction", 10.0)
    pax = c.fig.add_axes([90 / W, 40 / H, 1150 / W, 880 / H])
    pitch = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color=BG, line_color=FAINT,
                          linewidth=2, goal_type="box", pad_bottom=1, pad_top=3)
    pitch.draw(ax=pax)
    lo, hi = pax.get_ylim()
    pax.set_ylim((72, hi) if hi > lo else (hi, 72))  # attacking third only

    def P(xy):  # statsbomb (x, y) -> axes data coords for the vertical pitch
        return xy[1], xy[0]

    c.static = True
    title_block(c, "Rakitić, 4 minutes: Barcelona lead 1-0", "Champions League final 2015 · Juventus v Barcelona")
    c.box(1480, 975, 360, 58, r=10, fc=PANEL, ec=TEXT, lw=2)
    c.text(1660, 994, "RECONSTRUCTION", size=24, weight="bold", ha="center")
    c.text(1300, 860, "The move", size=24, weight="bold")
    c.text(1300, 150, "Ball path from StatsBomb event data.", size=15, color=MUTED)
    c.text(1300, 124, "Player positions at the moment of the shot", size=15, color=MUTED)
    c.text(1300, 98, "from the StatsBomb freeze frame.", size=15, color=MUTED)
    c.credit()
    c.static = False

    ff = shot.shot_freeze_frame

    def ball_at(t):
        for (t0, t1), sg in zip(times, segs):
            if t0 <= t < t1:
                f = ep(t, t0, t1 - t0) if sg[0] != "shot" else prog(t, t0, t1 - t0)
                a, b = np.array(sg[2], float), np.array(sg[3], float)
                return a + (b - a) * f, sg
        if t < times[0][0]:
            return np.array(segs[0][2], float), segs[0]
        return np.array(segs[-1][3], float), segs[-1]

    def draw(t):
        pre = 1 - ep(t, T_FREEZE, 0.4)  # build-up dots fade as the freeze frame appears
        # completed paths
        for (t0, t1), sg in zip(times, segs):
            if t < t0:
                continue
            f = min(1.0, (t - t0) / (t1 - t0))
            a, b = np.array(sg[2], float), np.array(sg[3], float)
            e = a + (b - a) * f
            (x0, y0), (x1, y1) = P(a), P(e)
            if sg[0] == "carry":
                c.track(pax.plot([x0, x1], [y0, y1], color=TEXT, lw=2, ls=(0, (3, 3)), alpha=0.7, zorder=3)[0])
            elif sg[0] == "pass":
                c.track(pax.plot([x0, x1], [y0, y1], color=TEXT, lw=2.5, alpha=0.75, zorder=3)[0])
            else:
                c.track(pax.plot([x0, x1], [y0, y1], color=BARCA, lw=4, alpha=0.95, zorder=3)[0])
        # build-up players (on the ball at the time)
        seen = {}
        for (t0, t1), sg in zip(times, segs):
            if t >= t0 and sg[1] not in seen:
                seen[sg[1]] = (sg[2], t0)
        for name, (loc, t0) in seen.items():
            a = ep(t, t0 - 0.1, 0.25) * (pre if name != "Rakitić" else 1)
            if a <= 0:
                continue
            x, y = P(loc)
            c.track(pax.scatter([x], [y], s=380, fc=BARCA, ec=TEXT, lw=1.5, alpha=a, zorder=5))
            off = {"Messi": (14, -4), "Jordi Alba": (-14, 4), "Neymar": (12, -18),
                   "Iniesta": (-12, 12), "Rakitić": (14, 4)}.get(name, (14, 4))
            c.track(pax.annotate(name, (x, y), xytext=off, textcoords="offset points", fontsize=17,
                                 fontweight="semibold", color=TEXT, family="Inter", alpha=a, zorder=9,
                                 ha="left" if off[0] > 0 else "right"))
        # freeze frame at the shot
        fa = ep(t, T_FREEZE, 0.5)
        if fa > 0:
            for p in ff:
                x, y = P(p["location"])
                mate = p["teammate"]
                c.track(pax.scatter([x], [y], s=300, fc=BARCA if mate else OPP, ec=BG, lw=1.5,
                                    alpha=fa * (1 if mate else 0.9), zorder=4))
                nm = SHORT.get(p["player"]["name"])
                if nm in ("Iniesta", "Buffon", "Suárez", "Jordi Alba", "Messi"):
                    off = {"Iniesta": (-14, 4), "Buffon": (-14, 0), "Suárez": (14, -4),
                           "Jordi Alba": (14, -4), "Messi": (14, -2)}[nm]
                    c.track(pax.annotate(nm, (x, y), xytext=off, textcoords="offset points", fontsize=15,
                                         color=MUTED if nm != "Buffon" else OPP, family="Inter",
                                         ha="left" if off[0] > 0 else "right", alpha=fa, zorder=9))
        # ball
        b, sg = ball_at(t)
        bx, by = P(b)
        c.track(pax.scatter([bx], [by], s=110, fc=TEXT, ec=BG, lw=1.5, zorder=8))
        # goal flash
        ga = ep(t, T_GOAL, 0.3)
        if ga > 0:
            pop = 1 + 0.4 * np.sin(np.pi * prog(t, T_GOAL, 0.45))
            c.tokens(1300, 500, [("1-0", TEXT, "bold"), ("  Barcelona", MUTED, "regular")], size=48 * pop, alpha=ga)
        # move list
        y = 800
        rows = []  # move list
        for (t0, t1), sg in zip(times, segs):
            if sg[0] == "pass":
                rows.append((t0, [(sg[1], TEXT, "semibold"), ("  to  ", MUTED, "regular"),
                                  (sg[4], TEXT, "semibold")]))
            elif sg[0] == "shot":
                rows.append((t0, [("Rakitić", TEXT, "semibold"), ("  scores, 4'", MUTED, "regular")]))
        for t0, toks in rows:
            a = ep(t, t0, 0.3)
            c.tokens(1300, y, toks, size=22, alpha=a)
            y -= 52

    return c, draw, None


CLIPS = {"C3": c3, "C4": c4, "C5": c5}

if __name__ == "__main__":
    if sys.argv[1:] == ["check"]:
        check_figures(load_events())
        print("All figures match CLAUDE.md.")
        sys.exit()
    for key in sys.argv[1:] or CLIPS:
        clip, draw, zoom = CLIPS[key]()
        print("rendered", clip.render(draw, zoom=zoom))
