"""A goal from the final, replayed on the board from StatsBomb events (passes, carries, shots, saves, the defender
beaten), framed on the move. Each named step lands on the narration word given in `anchors`.
"""
from kit import D, MUTED, ACCENT, INK, Pitch, arrow, defs, dot, place_tags, tag, fade_in

FLIP = lambda p: [120 - p[0], 80 - p[1]]


def goal_scene(sc, key, attack, anchors, t_show, t_hide, score_html, frame=(150, 200, 1800, 900)):
    """key: goal label in D['goals'] ("4'", "55'", "68'", "90+7'"); attack: the scoring team (drawn attacking right).
    anchors: {step index: local time}. Steps between anchors are spaced evenly. Returns the scene's group id."""
    seq = D["goals"][key]
    g = sc.uid("goal")

    # every point in the attacking team's frame (events by the other team are mirrored)
    def pt(p, team):
        return list(p) if team == attack else FLIP(p)

    steps = []
    for st in seq:
        s = dict(st)
        for k in ("from", "to", "at"):
            if k in s:
                s[k] = pt(s[k], st["team"])
        steps.append(s)
    shot = [s for s in steps if s["kind"] == "shot"][-1]

    # framing: fit every point (and the goal mouth) into the frame, at most 20 px a yard
    xs = [p[0] for s in steps for k in ("from", "to", "at") if k in s for p in [s[k]]] + [120]
    ys = [p[1] for s in steps for k in ("from", "to", "at") if k in s for p in [s[k]]] + [36, 44]
    fx0, fy0, fx1, fy1 = frame
    scale = min(20, (fx1 - fx0) / max(25, max(xs) - min(xs) + 10), (fy1 - fy0) / max(20, max(ys) - min(ys) + 10))
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    P = Pitch((fx0 + fx1) / 2 - cx * scale, (fy0 + fy1) / 2 - cy * scale, scale)

    # timing: anchored steps at their words, the rest spread evenly between neighbours
    n = len(steps)
    times = [None] * n
    for i, t in anchors.items():
        times[i] = t
    known = [i for i in range(n) if times[i] is not None]
    for a, b in zip(known, known[1:]):
        for i in range(a + 1, b):
            times[i] = round(times[a] + (times[b] - times[a]) * (i - a) / (b - a), 3)
    for i in range(known[0]):
        times[i] = round(times[known[0]] - 0.6 * (known[0] - i), 3)
    for i in range(known[-1] + 1, n):
        times[i] = round(times[known[-1]] + 0.6 * (i - known[-1]), 3)
    durs = []
    for i, s in enumerate(steps):
        nxt = times[i + 1] if i + 1 < n else times[i] + 0.5
        durs.append(round(max(0.25, min(1.0, (nxt - times[i]) * 0.85)), 3) if s["kind"] in ("pass", "carry", "shot") else 0.0)

    js, arrows, actors, extras = [], [], {}, []
    team_of = {}

    def add_actor(name, loc, t0, team):
        """A player's dot where the events put him; a second dot when he has moved more than 10 yards."""
        last = [k for k in actors if k.split("#")[0] == name]
        if last:
            (px, py), _, _ = actors[last[-1]]
            if ((px - loc[0]) ** 2 + (py - loc[1]) ** 2) ** 0.5 <= 10:
                return
        actors[name if not last else f"{name}#{len(last) + 1}"] = (loc, t0, team)
    for i, s in enumerate(steps):
        t0, d = times[i], durs[i]
        if s["kind"] in ("pass", "carry", "shot"):
            x1, y1 = P.P(*s["from"])
            x2, y2 = P.P(*s["to"])
            aid = f"{g}-a{i}"
            arrows.append(arrow(aid, x1, y1, x2, y2, {"pass": "pass", "carry": "run", "shot": "shot"}[s["kind"]], sc.cid))
            js.append(f'tl.fromTo("#{aid}-mp", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: {d}, ease: "power2.inOut" }}, {t0});')
            js.append(f'tl.fromTo("#{aid}-head", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {round(t0 + d - 0.05, 3)});')
            js.append(f'tl.fromTo("#{g}-ball", {{ attr: {{ cx: {x1}, cy: {y1} }} }}, {{ attr: {{ cx: {x2}, cy: {y2} }}, duration: {d}, ease: "power2.inOut", immediateRender: false }}, {t0});')
            add_actor(s["player"], s["from"], t0, s["team"])
            if s.get("to_player"):
                add_actor(s["to_player"], s["to"], round(t0 + d, 3), s["team"])
        elif s["kind"] in ("keeper", "beaten"):
            add_actor(s["player"], s["at"], t0, s["team"])
            if s["kind"] == "keeper":
                kx, ky = P.P(*s["at"])
                extras.append(f'<g id="{g}-save" opacity="0"><circle cx="{kx}" cy="{ky}" r="34" fill="none" stroke="#fff" stroke-width="4" stroke-dasharray="8 8"/>'
                              f'<text x="{kx}" y="{ky + 62}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="#fff">SAVED</text></g>')
                js.append(fade_in(f"#{g}-save", t0, 0.2, blur=False))
                js.append(f'tl.to("#{g}-save", {{ opacity: 0, duration: 0.3 }}, {round(t0 + 1.6, 3)});')
                sc.sfx(t0, "click2", 0.6)
            else:
                bx, by = P.P(*s["at"])
                extras.append(f'<g id="{g}-beat" opacity="0"><path d="M {bx - 18} {by - 18} L {bx + 18} {by + 18} M {bx + 18} {by - 18} L {bx - 18} {by + 18}" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round"/></g>')
                js.append(fade_in(f"#{g}-beat", t0, 0.2, blur=False))
        team_of[s["player"]] = s["team"]
    shot_end = times[n - 1] + durs[n - 1]

    # opponents (and unnamed teammates) at the moment of the scoring shot: StatsBomb freeze frame
    others = []
    named = {k.split("#")[0] for k in actors}
    for f in shot.get("freeze", []):
        if f["name"] in named:
            continue
        team = attack if f["teammate"] else ("Juventus" if attack == "Barcelona" else "Barcelona")
        others.append((P.P(*pt(f["loc"], attack)), team))
    mine = []
    for k, (name, (loc, t0, team)) in enumerate(actors.items()):
        x, y = P.P(*loc)
        mine.append((k, name, x, y, t0, team))
    spots = place_tags([(k, x, y, name.split("#")[0]) for k, name, x, y, _, _ in mine],
                       [(x, y, 30) for _, _, x, y, _, _ in mine] + [((x, y)[0], (x, y)[1], 20) for (x, y), _ in others],
                       frame=(60, 190, 1860, 920))
    dots, tags = [], []
    for j, ((x, y), team) in enumerate(others):
        pid = f"{g}-o{j}"
        dots.append(dot(pid, x, y, "A" if team == "Barcelona" else "B", prefix=sc.cid))
        js.append(f'tl.fromTo("#{pid}", {{ opacity: 0 }}, {{ opacity: 0.9, duration: 0.4 }}, {round(times[0] + 0.2 + j * 0.04, 3)});')
    for k, name, x, y, t0, team in mine:
        pid = f"{g}-p{k}"
        if k == 0:  # the player who starts the move is on the board as soon as the scene opens
            t0 = min(t0, round(t_show + 0.6, 3))
        side = "A" if team == "Barcelona" else "B"
        dots.append(dot(pid, x, y, side, key=True, prefix=sc.cid))
        tags.append(tag(f"{pid}-tag", x, y, *spots[k], name.split("#")[0], side))
        js.append(f'tl.fromTo("#{pid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {round(t0 - 0.3, 3)});')
        js.append(f'tl.fromTo("#{pid}-ring", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {round(t0 - 0.25, 3)});')
        js.append(f'tl.fromTo("#{pid}-tag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {round(t0 - 0.2, 3)});')
        js.append(f'tl.to("#{pid}-ring", {{ opacity: 0.35, duration: 0.4 }}, {round(t0 + 1.4, 3)});')
        sc.sfx(t0 - 0.2, "click1", 0.35)

    bx, by = P.P(*steps[0].get("from", steps[0].get("at")))
    gx, gy = P.P(117, 40)
    sc.add(f"""
    <div id="{g}" style="position:absolute;inset:0;opacity:0">
      <svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">
        {defs(sc.cid)}
        <rect width="1920" height="1080" fill="#07080a"/>
        <g id="{g}-cam">
          {P.svg()}
          {''.join(arrows)}
          {''.join(dots)}
          {''.join(extras)}
          {''.join(tags)}
          <circle id="{g}-ball" cx="{bx}" cy="{by}" r="9" fill="#fff" filter="url(#{sc.cid}-glowW)"/>
        </g>
      </svg>
      <div class="recon">Reconstruction · positions illustrative</div>
      <div class="src" style="left:98px;top:124px">Data: StatsBomb open data</div>
      <div id="{g}-score" class="oswald" style="position:absolute;right:96px;top:56px;font-size:46px;background:rgba(7,8,10,.85);padding:6px 18px;border-radius:6px;opacity:0">{score_html}</div>
    </div>""",
           f'tl.fromTo("#{g}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {t_show});',
           f'tl.to("#{g}", {{ opacity: 0, duration: 0.15 }}, {t_hide});',
           f'tl.fromTo("#{g}-cam", {{ scale: 1 }}, {{ scale: 1.08, svgOrigin: "{gx} {gy}", duration: {round(t_hide - t_show, 3)}, ease: "power1.inOut" }}, {t_show});',
           *js,
           f'tl.fromTo("#{g}-score", {{ opacity: 0, scale: 1.3, filter: "blur(8px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }}, {round(shot_end + 0.05, 3)});')
    sc.sfx(shot_end, "hit1" if key in ("4'", "68'") else "hit2", 0.9)
    return g, shot_end
