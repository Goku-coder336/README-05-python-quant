"""The film's timeline and scene kit: line timings from the measured voice, a Scene builder, and the parts every
chapter reuses (board, chapter label, route, result cards, goal blocks and piles, cards, Pip).
"""
import json
import math
import os
import re
import unicodedata

from style import (ACCENT, BASE_CSS, INK, MUTED, PIP_JS, TEAM_A, TEAM_B, TEAM_B_EDGE, Pitch, arrow, defs, dot,
                   pip_svg, place_tags, tag)
from voice import script_lines

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "..")
D = json.load(open(os.path.join(FILM, "data", "film_data.json"), encoding="utf-8"))
V = json.load(open(os.path.join(FILM, "data", "voice_lines.json"), encoding="utf-8"))
LINES = script_lines()
TEXT = dict(LINES)

GAP, CH_GAP, LEAD, START, TAIL = 0.42, 1.2, 0.6, 0.6, 6.0
# extra breath after a line, so its picture lands before the next line starts
EXTRA = {"0.2": 1.0, "0.3": 0.5, "0.4": 0.6, "1.2": 0.4, "2.8": 0.5, "3.7": 1.3, "4.5": 0.4, "5.4": 1.0, "5.4b": 0.5,
         "5.6": 0.8, "6.3": 1.0, "6.4": 0.8, "6.5": 1.0, "7.3": 0.5, "7.9": 0.5, "8.4b": 0.6, "8.7": 0.5}

STARTS, CH_START, CH_END = {}, {}, {}
_t, _prev = START, None
for lid, _ in LINES:
    ch = int(lid[0])
    if _prev is not None and ch != _prev:
        _t += CH_GAP
    if ch != _prev:
        CH_START[ch] = 0.0 if ch == 0 else round(_t - LEAD, 3)
    STARTS[lid] = round(_t, 3)
    _t += V[lid]["dur"] + GAP + EXTRA.get(lid, 0)
    _prev = ch
FILM_END = round(_t + TAIL, 2)
for ch in CH_START:
    CH_END[ch] = CH_START.get(ch + 1, FILM_END)

SFX = []  # (global time, name, gain)
BLOCK = "#2a2f38"


def norm(w):
    w = "".join(c for c in unicodedata.normalize("NFD", w.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


class Scene:
    def __init__(self, ch, name):
        self.ch, self.cid = ch, f"c{ch}-{name}"
        self.t0, self.dur = CH_START[ch], round(CH_END[ch] - CH_START[ch], 3)
        self.body, self.js, self.pips, self.n = [], [], [], 0

    # -- time, local to this scene
    def T(self, lid):
        return round(STARTS[lid] - self.t0, 3)

    def E(self, lid):
        return round(STARTS[lid] + V[lid]["dur"] - self.t0, 3)

    def W(self, lid, word, occ=1):
        """When `word` is spoken in line `lid` (speech-to-text timing; else by its place in the text)."""
        target, seen = norm(word), 0
        for w in V[lid]["words"]:
            if norm(w["w"]).startswith(target) and target:
                seen += 1
                if seen == occ:
                    return round(self.T(lid) + w["s"], 3)
        text, seen, pos = TEXT[lid], 0, -1
        for m in re.finditer(re.escape(word), text, re.I):
            seen += 1
            if seen == occ:
                pos = m.start()
                break
        frac = max(pos, 0) / max(1, len(text))
        words = V[lid]["words"]
        a, b = (words[0]["s"], words[-1]["e"]) if words else (0, V[lid]["dur"])
        return round(self.T(lid) + a + (b - a) * frac, 3)

    def uid(self, k="e"):
        self.n += 1
        return f"{self.cid}-{k}{self.n}"

    def add(self, html, *js):
        self.body.append(html)
        self.js.extend(j for j in js if j)

    def sfx(self, t, name, gain=1.0):
        SFX.append((round(self.t0 + t, 3), name, gain))

    # -- Pip
    def pip(self, x, y, s=1.2, d=1):
        pid = f"{self.cid}-pip{len(self.pips)}"
        self.pips.append(pid)
        self.js.append(f'Pip.place("{pid}", {x}, {y}, {s}, {d});')
        self.js.append(f'Pip.breathe("{pid}", 0, {self.dur});')
        return pid

    def html(self):
        overlay = ""
        if self.pips:
            overlay = (f'<svg class="pipl" width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0;overflow:visible;z-index:20">'
                       f'{defs(self.cid + "x")}{"".join(pip_svg(p, self.cid + "x") for p in self.pips)}</svg>')
        js = "\n    ".join(self.js)
        return f"""<template>
  <style>
{BASE_CSS}
  .card {{ position: absolute; background: rgba(13,15,19,.92); border: 2px solid #2a2f38; border-radius: 10px; }}
  .chip {{ font: 700 30px Oswald, sans-serif; padding: 2px 12px; border-radius: 6px; }}
  </style>
  <div id="root" data-composition-id="{self.cid}" data-width="1920" data-height="1080">
{chr(10).join(self.body)}
    {overlay}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{PIP_JS if self.pips else ""}
    {js}
    window.__timelines["{self.cid}"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- parts
def fade_in(sel, t, dur=0.3, blur=True, y=0):
    a = "filter: \"blur(8px)\", " if blur else ""
    b = "filter: \"blur(0px)\", " if blur else ""
    return (f'tl.fromTo("{sel}", {{ opacity: 0, {a}y: {y} }}, {{ opacity: 1, {b}y: 0, duration: {dur}, ease: "power4.out" }}, {round(t, 3)});')


def fade_out(sel, t, dur=0.2):
    return f'tl.to("{sel}", {{ opacity: 0, filter: "blur(6px)", duration: {dur}, ease: "power2.in" }}, {round(t, 3)});'


def board(sc, opacity=0.4):
    p = Pitch(180, 20, 13)
    sc.add(f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0;opacity:{opacity}">{p.svg()}</svg>'
           '<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%, rgba(7,8,10,.15) 0%, rgba(7,8,10,.86) 80%)"></div>')


def chapter_label(sc, num, title, t_big=0.15, hold=1.8):
    """A big chapter title that lands, then settles small into the top-left corner."""
    i = sc.uid("ch")
    sc.add(f'<div id="{i}" class="oswald" style="position:absolute;left:96px;top:56px;font-size:30px;color:{MUTED};letter-spacing:.08em;opacity:0;transform-origin:0 0">'
           f'<span style="color:{ACCENT}">{num}</span>&nbsp;&nbsp;{title}</div>',
           f'tl.fromTo("#{i}", {{ opacity: 0, scale: 3.2, x: 300, y: 360, filter: "blur(10px)" }}, {{ opacity: 1, scale: 3.2, x: 300, y: 360, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }}, {t_big});',
           f'tl.to("#{i}", {{ scale: 1, x: 0, y: 0, duration: 0.6, ease: "power3.inOut" }}, {t_big + hold});')
    sc.sfx(t_big, "whoosh" + str(1 + num % 3), 0.8)
    return i


ROUTE_X = [330, 650, 970, 1290, 1610]
ROUTE_NAMES = ["Group F", "Round of 16", "Quarter-final", "Semi-final", "Final"]


def route(sc, y=900, lit=(), now=None, t_now=0.4, draw_t=None, small=False):
    """The season as a chalk route with five stops. `lit` stops are red from the start; `now` lights at t_now."""
    i = sc.uid("rt")
    r = 13 if small else 16
    parts = [f'<line id="{i}-ln" x1="{ROUTE_X[0]}" y1="{y}" x2="{ROUTE_X[-1]}" y2="{y}" stroke="rgba(255,255,255,.28)" stroke-width="4" stroke-dasharray="16 12" stroke-linecap="round"/>']
    js = []
    for k, x in enumerate(ROUTE_X):
        on = k in lit
        parts.append(f'<circle id="{i}-n{k}" cx="{x}" cy="{y}" r="{r}" fill="{TEAM_A if on else "#14171c"}" stroke="{ACCENT if on else "rgba(255,255,255,.45)"}" stroke-width="4"/>'
                     f'<text id="{i}-t{k}" x="{x}" y="{y + 52}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{INK if on else MUTED}">{ROUTE_NAMES[k]}</text>')
    if now is not None:
        js.append(f'tl.to("#{i}-n{now}", {{ attr: {{ fill: "{TEAM_A}", stroke: "{ACCENT}" }}, duration: 0.25 }}, {t_now});')
        js.append(f'tl.to("#{i}-t{now}", {{ attr: {{ fill: "{INK}" }}, duration: 0.25 }}, {t_now});')
        js.append(f'tl.fromTo("#{i}-n{now}", {{ attr: {{ r: {r} }} }}, {{ attr: {{ r: {r + 8} }}, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out" }}, {t_now});')
        sc.sfx(t_now, "pop", 0.6)
    if draw_t is not None:
        js.append(f'tl.fromTo("#{i}-g", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {draw_t});')
        for k in range(5):
            js.append(f'tl.fromTo(["#{i}-n{k}", "#{i}-t{k}"], {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {round(draw_t + 0.35 * k, 3)});')
    sc.add(f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0"><g id="{i}-g">{"".join(parts)}</g></svg>', *js)
    return i


def result_card(sc, x, y, label, opp, venue, res, score, scorers, t, w=560):
    i = sc.uid("rc")
    chip_bg = TEAM_A if res == "W" else TEAM_B
    ven = {"H": "home", "A": "away", "N": "Berlin"}[venue]
    sc_txt = ", ".join(n + (f" {c}" if c > 1 else "") for n, c in scorers)
    sc.add(f'<div id="{i}" class="card" style="left:{x}px;top:{y}px;width:{w}px;height:86px;opacity:0">'
           f'<div style="position:absolute;left:18px;top:6px;font:400 28px Inter;color:{MUTED}">{label} · {ven}</div>'
           f'<div style="position:absolute;left:18px;top:42px;font:700 30px Inter;color:{INK}">{opp}</div>'
           f'<div class="chip" style="position:absolute;right:16px;top:8px;background:{chip_bg};color:#fff">{res} {score}</div>'
           f'<div style="position:absolute;right:18px;top:50px;font:400 28px Inter;color:{INK};white-space:nowrap">{sc_txt}</div></div>',
           f'tl.fromTo("#{i}", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "expo.out" }}, {round(t, 3)});')
    sc.sfx(t, "click1", 0.5)
    return i


class Piles:
    """Goal blocks stacked into a pile per player, bottom-up, with a name and a running count."""

    def __init__(self, sc, names, x0, base, gapx=170, bs=46, colours=None, start=None, show=None, hide=None):
        self.sc, self.bs, self.base = sc, bs, base
        self.x = {n: x0 + k * gapx for k, n in enumerate(names)}
        self.count = {n: (start or {}).get(n, 0) for n in names}
        self.start = dict(self.count)
        self.col = colours or {}
        self.i = sc.uid("pl")
        parts = []
        for n, x in self.x.items():
            parts.append(f'<div id="{self.i}-{norm(n)}-name" style="position:absolute;left:{x - 70}px;top:{base + 14}px;width:{bs + 140}px;text-align:center;font:700 28px Inter;color:{INK}">{n}</div>')
            parts.append(f'<div id="{self.i}-{norm(n)}-num" class="oswald" style="position:absolute;left:{x - 70}px;top:{base - 70 - (bs + 6) * max(self.count[n], 0)}px;width:{bs + 140}px;text-align:center;font-size:52px;color:{ACCENT if n == "Messi" else INK}">{self.count[n]}</div>')
            for k in range(self.count[n]):
                parts.append(self._block(n, k, visible=True))
        self.parts = parts
        if show is None:
            sc.add("\n".join(parts))
        else:  # the labels and counts appear with the piles, not before
            sc.add(f'<div id="{self.i}-wrap" style="position:absolute;inset:0;opacity:0">' + "\n".join(parts) + '</div>',
                   fade_in(f"#{self.i}-wrap", show, 0.3, blur=False), fade_out(f"#{self.i}-wrap", hide) if hide else None)

    def _block(self, n, k, visible=False):
        x, y = self.x[n], self.base - (k + 1) * (self.bs + 6)
        col = self.col.get(n, TEAM_A if n in ("Messi", "Neymar", "Suárez") else "#6b7380")
        glow = f"box-shadow:0 0 16px {col};" if col in (TEAM_A,) else ""
        return (f'<div id="{self.i}-{norm(n)}-b{k}" style="position:absolute;left:{x}px;top:{y}px;width:{self.bs}px;height:{self.bs}px;'
                f'border-radius:8px;background:{col};{glow}opacity:{1 if visible else 0}"></div>')

    def add_goal(self, n, t, from_xy=(960, -80)):
        k = self.count[n]
        self.count[n] += 1
        self.sc.add(self._block(n, k),
                    f'tl.fromTo("#{self.i}-{norm(n)}-b{k}", {{ opacity: 0, x: {from_xy[0] - self.x[n]}, y: {from_xy[1] - (self.base - (k + 1) * (self.bs + 6))}, rotation: -25 }}, '
                    f'{{ opacity: 1, x: 0, y: 0, rotation: 0, duration: 0.55, ease: "power3.out" }}, {round(t, 3)});',
                    f'tl.to("#{self.i}-{norm(n)}-num", {{ y: {-(self.bs + 6) * (self.count[n] - self.start[n])}, duration: 0.3, ease: "power2.out" }}, {round(t + 0.35, 3)});',
                    f'tl.set("#{self.i}-{norm(n)}-num", {{ textContent: "{self.count[n]}" }}, {round(t + 0.4, 3)});')
        self.sc.sfx(t + 0.45, "clack", 0.45)

    def num_offset_fix(self):
        """The count label sits above the pile; tweens above move it relative to its starting place."""
        pass


def card(sc, x, y, w, h, inner, t, sel_id=None, style=""):
    i = sel_id or sc.uid("cd")
    sc.add(f'<div id="{i}" class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;opacity:0;{style}">{inner}</div>',
           fade_in(f"#{i}", t, 0.3))
    sc.sfx(t, "click2", 0.45)
    return i


def big_text(sc, x, y, text, size, t, color=INK, anchor="left", w=1700, sel_id=None, hit=False):
    i = sel_id or sc.uid("bt")
    al = {"left": "left", "center": "center", "right": "right"}[anchor]
    left = x if anchor == "left" else x - w / 2 if anchor == "center" else x - w
    sc.add(f'<div id="{i}" class="oswald" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;text-align:{al};font-size:{size}px;line-height:1.05;color:{color};opacity:0">{text}</div>',
           f'tl.fromTo("#{i}", {{ opacity: 0, scale: 1.18, filter: "blur(8px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }}, {round(t, 3)});')
    if hit:
        sc.sfx(t, "hit1" if hit is True else hit, 0.9)
    return i
