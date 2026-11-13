"""Write the three test scenes (title card, pitch scene, data chart) and a root that plays them.

Usage: python build/test_stills.py   (from the film folder)
"""
import json
import os

from style import (ACCENT, BASE_CSS, INK, MUTED, PIP_JS, TEAM_A, TEAM_B_EDGE, Pitch, arrow, defs, dot, pip_svg, place_tags, tag)

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "..")
D = json.load(open(os.path.join(FILM, "data", "film_data.json"), encoding="utf-8"))


def scene(cid, css, body, js):
    return f"""<template>
  <style>
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def caption(cid, text, start, dur):
    return (f'<div id="{cid}-cap" class="cap clip" data-start="{start}" data-duration="{dur}"><span>{text}</span></div>')


# ---------------------------------------------------------------- title card
def title_scene():
    cid = "t-title"
    p = Pitch(180, 20, 13)
    body = f"""
    <svg id="{cid}-bg" width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0;opacity:.32">
      <g id="{cid}-cam">{p.svg()}</g>
    </svg>
    <div id="{cid}-shade" style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%, rgba(7,8,10,.35) 0%, rgba(7,8,10,.92) 75%)"></div>
    <div style="position:absolute;left:0;right:0;top:330px;text-align:center">
      <div class="oswald" style="font-size:150px;line-height:1;letter-spacing:.02em">
        <span id="{cid}-w1" style="display:inline-block;opacity:0">RUN</span>
        <span id="{cid}-w2" style="display:inline-block;opacity:0">OF</span>
        <span id="{cid}-w3" style="display:inline-block;opacity:0">THE</span>
        <span id="{cid}-w4" style="display:inline-block;opacity:0">CHAMPIONS</span>
      </div>
      <div id="{cid}-rule" style="width:560px;height:6px;margin:34px auto 30px;background:{ACCENT};border-radius:3px;box-shadow:0 0 18px {TEAM_A};transform-origin:50% 50%;transform:scaleX(0)"></div>
      <div id="{cid}-sub" class="oswald" style="font-size:72px;color:{ACCENT};letter-spacing:.06em;opacity:0">BARCELONA 2014/15</div>
    </div>
    {caption(cid, "Barcelona still won the Champions League.", 0.3, 7.5)}
"""
    js = f"""
    tl.fromTo("#{cid}-cam", {{ scale: 1 }}, {{ scale: 1.06, svgOrigin: "960 540", duration: 8, ease: "none" }}, 0);
    ["w1","w2","w3","w4"].forEach((w, i) => tl.fromTo("#{cid}-" + w, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }}, 0.4 + i * 0.09));
    tl.fromTo("#{cid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, 0.9);
    tl.fromTo("#{cid}-sub", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 1.2);
"""
    return cid, scene(cid, "", body, js)


# ---------------------------------------------------------------- pitch scene: Rakitić 4'
def pitch_scene():
    cid = "t-pitch"
    # framed on the move: StatsBomb (98, 36) sits at screen (960, 480), 18 px per yard
    p = Pitch(960 - 98 * 18, 480 - 36 * 18, 18)
    seq = D["goals"]["4'"]
    body, js = [], []
    # timing: one step every ~0.75 s, shot at the end (illustrative pace; order and positions from the events)
    t = 1.0
    plan = []
    for st in seq:
        d = 1.1 if st["kind"] == "pass" and abs(st["to"][0] - st["from"][0]) > 20 else 0.6 if st["kind"] != "carry" else 0.5
        plan.append((st, t, d))
        t += d + 0.15
    shot_t = plan[-1][1]
    players = {}
    for st, t0, d in plan:
        players.setdefault(st["player"], (st["from"], t0))
        if st.get("to_player"):
            players.setdefault(st["to_player"], (st["to"], t0 + d))
    arrows, dots = [], []
    for i, (st, t0, d) in enumerate(plan):
        x1, y1 = p.P(*st["from"])
        x2, y2 = p.P(*st["to"])
        kind = {"pass": "pass", "carry": "run", "shot": "shot"}[st["kind"]]
        aid = f"{cid}-a{i}"
        arrows.append(arrow(aid, x1, y1, x2, y2, kind, cid))
        js.append(f'tl.fromTo("#{aid}-mp", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: {d}, ease: "power2.inOut" }}, {t0});')
        js.append(f'tl.fromTo("#{aid}-head", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {t0 + d - 0.05});')
        js.append(f'tl.fromTo("#{cid}-ball", {{ attr: {{ cx: {x1}, cy: {y1} }} }}, {{ attr: {{ cx: {x2}, cy: {y2} }}, duration: {d}, ease: "power2.inOut", immediateRender: false }}, {t0});')
    # opponents at the moment of the shot (StatsBomb freeze frame)
    opp = [(j, *p.P(*f["loc"])) for j, f in enumerate(seq[-1]["freeze"]) if not f["teammate"]]
    mine = [(k, name, *p.P(*loc), t0) for k, (name, (loc, t0)) in enumerate(players.items())]
    spots = place_tags([(k, x, y, name) for k, name, x, y, _ in mine],
                       [(x, y, 30) for _, _, x, y, _ in mine] + [(x, y, 20) for _, x, y in opp], frame=(60, 190, 1860, 930))
    tags = []
    for j, x, y in opp:  # opponents first, so Barcelona's dots sit on top
        pid = f"{cid}-o{j}"
        dots.append(dot(pid, x, y, "B", prefix=cid))
        js.append(f'tl.fromTo("#{pid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {round(shot_t - 1.6 + j * 0.05, 2)});')
    for k, name, x, y, t0 in mine:
        pid = f"{cid}-p{k}"
        dots.append(dot(pid, x, y, "A", key=True, prefix=cid))
        tags.append(tag(f"{pid}-tag", x, y, *spots[k], name))
        js.append(f'tl.fromTo("#{pid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, {t0 - 0.25});')
        js.append(f'tl.fromTo("#{pid}-ring", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {t0 - 0.2});')
        js.append(f'tl.fromTo("#{pid}-tag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {t0 - 0.15});')
        js.append(f'tl.to("#{pid}-ring", {{ opacity: 0.35, duration: 0.4 }}, {t0 + 1.2});')
    bx, by = p.P(*seq[0]["from"])
    body.append(f"""
    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">
      {defs(cid)}
      <g id="{cid}-cam">
        {p.svg()}
        {''.join(arrows)}
        {''.join(dots)}
        {''.join(tags)}
        <circle id="{cid}-ball" cx="{bx}" cy="{by}" r="9" fill="#fff" filter="url(#{cid}-glowW)"/>
      </g>
    </svg>
    <div class="recon">Reconstruction · positions illustrative</div>
    <div class="src" style="left:98px;top:124px">Data: StatsBomb open data</div>
    <div id="{cid}-score" class="oswald" style="position:absolute;right:96px;top:790px;font-size:46px;background:rgba(7,8,10,.8);padding:6px 18px;border-radius:6px;opacity:0">
      JUVENTUS <span style="color:{ACCENT}">0-1</span> BARCELONA <span style="font-family:Inter;font-weight:700;font-size:30px;color:{MUTED}">4'</span>
    </div>
    {caption(cid, "Alba found Neymar. Neymar found Iniesta. Iniesta found Rakitić.", 0.3, 9.4)}
""")
    end_t = shot_t + plan[-1][2]
    gx, gy = p.P(116, 38)
    js.insert(0, f'tl.fromTo("#{cid}-cam", {{ scale: 1 }}, {{ scale: 1.1, svgOrigin: "{gx} {gy}", duration: {round(end_t + 2, 2)}, ease: "power1.inOut" }}, 0);')
    js.append(f'tl.fromTo("#{cid}-score", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, {end_t + 0.1});')
    return cid, scene(cid, "", "\n".join(body), "\n    ".join(js)), end_t


# ---------------------------------------------------------------- data chart: xG timeline
def chart_scene():
    cid = "t-chart"
    X0, X1, Y0, Y1, MMAX, GMAX = 230, 1560, 790, 250, 98, 2.5
    X = lambda m: round(X0 + (X1 - X0) * m / MMAX, 1)
    Y = lambda g: round(Y0 - (Y0 - Y1) * g / GMAX, 1)
    parts, js = [], []
    for g in (0.5, 1.0, 1.5, 2.0, 2.5):
        parts.append(f'<line x1="{X0}" x2="{X1}" y1="{Y(g)}" y2="{Y(g)}" stroke="rgba(255,255,255,.08)" stroke-width="2"/>'
                     f'<text x="{X0 - 18}" y="{Y(g) + 8}" text-anchor="end" font-family="Inter" font-size="28" fill="{MUTED}">{g:.1f}</text>')
    for m in (0, 15, 30, 45, 60, 75, 90):
        parts.append(f'<text x="{X(m)}" y="{Y0 + 44}" text-anchor="middle" font-family="Inter" font-size="28" fill="{MUTED}">{m}\'</text>')
    parts.append(f'<line x1="{X0}" x2="{X1}" y1="{Y0}" y2="{Y0}" stroke="rgba(255,255,255,.25)" stroke-width="3"/>')
    parts.append(f'<text x="{X0 - 18}" y="{Y1 - 34}" text-anchor="end" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">xG</text>')
    parts.append(f'<text x="{X1}" y="{Y0 + 84}" text-anchor="end" font-family="Inter" font-size="28" fill="{MUTED}">minute</text>')
    lines = {}
    for team, col in (("Juventus", TEAM_B_EDGE), ("Barcelona", TEAM_A)):
        pts, cum = [(0, 0)], 0.0
        for s in [s for s in D["shots"] if s["team"] == team]:
            pts += [(s["m"], cum), (s["m"], cum + s["xg"])]
            cum += s["xg"]
        pts.append((MMAX - 1, cum))
        lines[team] = (pts, cum)
        d = "M " + " L ".join(f"{X(m)} {Y(g)}" for m, g in pts)
        filt = f' filter="url(#{cid}-glowA)"' if team == "Barcelona" else ""
        parts.append(f'<path id="{cid}-{team[:3]}" d="{d}" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="100"{filt}/>')
        js.append(f'tl.fromTo("#{cid}-{team[:3]}", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 3.2, ease: "power1.inOut" }}, 1.2);')
        ex, ey = X(MMAX - 1), Y(cum)
        lab = f"{cum:.2f}"
        parts.append(f'<g id="{cid}-{team[:3]}-end" opacity="0"><text x="{ex + 24}" y="{ey + 4}" font-family="Oswald" font-weight="700" font-size="58" fill="{col if team == "Barcelona" else INK}">{lab}</text>'
                     f'<text x="{ex + 24}" y="{ey + 40}" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">{team.upper()} · xG</text></g>')
        js.append(f'tl.fromTo("#{cid}-{team[:3]}-end", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 4.5);')
    for k, s in enumerate([s for s in D["shots"] if s["goal"]]):
        pts, _ = lines[s["team"]]
        gy = max(g for m, g in pts if m <= s["m"] + 1e-6)
        col = TEAM_A if s["team"] == "Barcelona" else TEAM_B_EDGE
        tt = round(1.2 + 3.2 * s["m"] / MMAX, 2)
        anchor = "start" if s["m"] < 10 else "end"
        dx = 18 if s["m"] < 10 else -18
        parts.append(f'<g id="{cid}-g{k}" opacity="0"><circle cx="{X(s["m"])}" cy="{Y(gy)}" r="13" fill="{col}" stroke="#fff" stroke-width="3"/>'
                     f'<text x="{X(s["m"]) + dx}" y="{Y(gy) - 22}" text-anchor="{anchor}" font-family="Inter" font-weight="700" font-size="28" fill="{INK}">{s["label"]}</text></g>')
        js.append(f'tl.fromTo("#{cid}-g{k}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {tt});')
    body = f"""
    <div class="oswald" id="{cid}-title" style="position:absolute;left:96px;top:70px;font-size:64px;letter-spacing:.02em">EXPECTED GOALS IN THE FINAL</div>
    <div class="lbl" style="position:absolute;left:98px;top:152px;font-size:28px;color:{MUTED}">Cumulative xG (expected goals) by minute · Juventus 1-3 Barcelona, Berlin, 6 June 2015</div>
    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">{defs(cid)}{''.join(parts)}</svg>
    <div class="src" style="left:98px;top:858px">Source: StatsBomb open data</div>
    {caption(cid, "Barcelona finished on 2.27. Juventus on 1.38.", 4.4, 5.3)}
"""
    js.insert(0, f'tl.fromTo("#{cid}-title", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 0.2);')
    return cid, scene(cid, "", body, "\n    ".join(js))


def main():
    os.makedirs(os.path.join(FILM, "compositions"), exist_ok=True)
    hosts, start = [], 0.0
    t_cid, t_html = title_scene()
    p_cid, p_html, p_end = pitch_scene()
    c_cid, c_html = chart_scene()
    durs = {t_cid: 8, p_cid: round(p_end + 2.5, 1), c_cid: 10}
    for cid, html in ((t_cid, t_html), (p_cid, p_html), (c_cid, c_html)):
        open(os.path.join(FILM, "compositions", f"{cid}.html"), "w", encoding="utf-8").write(html)
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                     f'data-start="{start}" data-duration="{durs[cid]}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
        print(cid, "at", start, "for", durs[cid])
        start += durs[cid]
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #07080a; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{start}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    open(os.path.join(FILM, "index.html"), "w", encoding="utf-8").write(index)


if __name__ == "__main__":
    main()
