"""The nine chapters of the film. Each is one HyperFrames sub-composition; times come from the measured voice.
Every figure comes from data/film_data.json (StatsBomb, checked against CLAUDE.md) or the verified run (UEFA).
"""
from kit import (ACCENT, BLOCK, D, INK, MUTED, TEAM_A, TEAM_B, TEAM_B_EDGE, Piles, Pitch, Scene, big_text, board, card,
                 chapter_label, fade_in, fade_out, result_card, route, defs, dot)
from goals import goal_scene

RUN = D["run"]
GREY = "#6b7380"


def run(label_round, label):
    return next(m for m in RUN if m["round"] == label_round and m["label"] == label)


def rc(sc, m, x, y, t, w=600):
    return result_card(sc, x, y, m["label"], m["opp"], m["venue"], m["res"], m["score"], m["scorers"], t, w)


def blocks_row(sc, key, total, red, x0, y, t_drop, red_times, bs=56, gap=13, outline=None, static=False):
    ids = []
    for i in range(total):
        bid = f"{sc.cid}-{key}{i}"
        ids.append(bid)
        if static:  # on screen from the first frame (the film's opening frame is its poster)
            sc.add(f'<div id="{bid}" style="position:absolute;left:{x0 + i * (bs + gap)}px;top:{y}px;width:{bs}px;height:{bs}px;border-radius:9px;background:{BLOCK}"></div>')
            continue
        sc.add(f'<div id="{bid}" style="position:absolute;left:{x0 + i * (bs + gap)}px;top:{y}px;width:{bs}px;height:{bs}px;border-radius:9px;background:{BLOCK};opacity:0"></div>',
               f'tl.fromTo("#{bid}", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "bounce.out" }}, {round(t_drop + i * 0.045, 3)});')
    for i, tr in zip(range(red), red_times):
        sc.js.append(f'tl.to("#{ids[i]}", {{ backgroundColor: "{TEAM_A}", boxShadow: "0 0 22px {TEAM_A}", duration: 0.15 }}, {round(tr, 3)});')
        sc.sfx(tr, "click2", 0.35)
    for i, t in (outline or []):
        sc.js.append(f'tl.to("#{ids[i]}", {{ backgroundColor: "rgba(225,29,46,.18)", boxShadow: "inset 0 0 0 4px {ACCENT}", duration: 0.15 }}, {round(t, 3)});')
    if not static:
        sc.sfx(t_drop, "pop", 0.4)
    return ids


def number(sc, x, y, a, b, t, hit=False, size=84):
    i = sc.uid("num")
    sc.add(f'<div id="{i}" class="oswald" style="position:absolute;left:{x}px;top:{y}px;font-size:{size}px;line-height:1;opacity:0">'
           f'<span style="color:{ACCENT}">{a}</span><span style="color:{MUTED};font-size:{int(size * .62)}px"> / {b}</span></div>',
           f'tl.fromTo("#{i}", {{ opacity: 0, scale: 1.3 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power4.out" }}, {round(t, 3)});')
    sc.sfx(t, "hit2" if hit else "pop", 0.85 if hit else 0.5)
    return i


def src(sc, x, y, text, t, sel=None):
    i = sel or sc.uid("src")
    sc.add(f'<div id="{i}" class="src" style="left:{x}px;top:{y}px;opacity:0">{text}</div>', fade_in(f"#{i}", t, 0.3, blur=False))
    return i


def panel(sc, inner, t_in, t_out=None):
    i = sc.uid("pn")
    sc.add(f'<div id="{i}" style="position:absolute;inset:0;opacity:0">{inner}</div>',
           f'tl.fromTo("#{i}", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }}, {round(t_in, 3)});',
           fade_out(f"#{i}", t_out) if t_out else None)
    return i


# ======================================================================= c0: the case
def c0():
    sc = Scene(0, "open")
    board(sc)
    X0 = 140
    t1 = sc.W("0.1", "eight")
    blocks_row(sc, "g", 15, 8, X0, 230, sc.T("0.1") + 0.2, [t1 + 0.12 * i for i in range(8)], static=True)
    sc.add(f'<div id="{sc.cid}-gl" class="oswald" style="position:absolute;left:{X0}px;top:160px;font-size:40px;color:{MUTED};letter-spacing:.06em">GROUP STAGE</div>')
    number(sc, 1290, 212, 8, 15, t1 + 1.1)
    t2 = sc.W("0.2", "two")
    blocks_row(sc, "k", 16, 2, X0, 470, sc.T("0.2") + 0.3, [t2, t2 + 0.25])
    sc.add(f'<div id="{sc.cid}-kl" class="oswald" style="position:absolute;left:{X0}px;top:400px;font-size:40px;color:{MUTED};letter-spacing:.06em;opacity:0">KNOCKOUTS</div>',
           fade_in(f"#{sc.cid}-kl", sc.T("0.2") + 0.1, 0.3))
    number(sc, 1290, 452, 2, 16, t2 + 0.35, hit=True)
    src(sc, X0, 580, "Barcelona's Champions League goals, 2014/15 · Source: UEFA", sc.T("0.1") + 1.0)
    # the title card opens out of Pip's magnifying glass
    t_iris = sc.W("0.3", "go") + 0.25
    sc.add(f"""<div id="{sc.cid}-title" style="position:absolute;inset:0;background:#07080a;clip-path:circle(0px at 1040px 700px)">
      <div style="position:absolute;left:0;right:0;top:250px;text-align:center">
        <div class="oswald" style="font-size:150px;line-height:1;letter-spacing:.02em">RUN OF THE CHAMPIONS</div>
        <div id="{sc.cid}-rule" style="width:560px;height:6px;margin:34px auto 28px;background:{ACCENT};border-radius:3px;box-shadow:0 0 18px {TEAM_A}"></div>
        <div class="oswald" style="font-size:72px;color:{ACCENT};letter-spacing:.06em">BARCELONA 2014/15</div>
        <div style="font:600 38px Inter;color:{INK};margin-top:26px;letter-spacing:.02em">The case of the moving goals</div>
      </div></div>""",
           f'tl.fromTo("#{sc.cid}-title", {{ clipPath: "circle(0px at 1040px 700px)" }}, {{ clipPath: "circle(2300px at 1040px 700px)", duration: 0.7, ease: "power3.in" }}, {round(t_iris, 3)});',
           f'tl.fromTo("#{sc.cid}-rule", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, {round(t_iris + 0.6, 3)});')
    sc.sfx(t_iris, "whoosh1", 0.9)
    p = sc.pip(1600, 930, 1.7, -1)
    sc.js += [f'Pip.look("{p}", 6, -7, {sc.T("0.1") + 0.3});', f'Pip.arm("{p}", "R", -100, {sc.W("0.1", "Messi")});',
              f'Pip.mood("{p}", "happy", "smile", {t1 + 1.0});', f'Pip.arm("{p}", "R", 0, {sc.T("0.2")});',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("0.2") + 0.1});', f'Pip.walk("{p}", 1250, {sc.T("0.2") + 0.4}, 1.8);',
              f'Pip.look("{p}", 7, -8, {sc.T("0.2") + 0.5});', f'Pip.blink("{p}", {t2 - 0.4});',
              f'Pip.mood("{p}", "wide", "o", {t2 + 0.35});', f'Pip.brows("{p}", -16, 16, {t2 + 0.4});',
              f'Pip.arm("{p}", "L", 50, {t2 + 0.45});', f'Pip.arm("{p}", "R", -50, {t2 + 0.5});',
              f'Pip.arm("{p}", "L", 0, {sc.T("0.3")});', f'Pip.mood("{p}", "normal", "flat", {sc.T("0.3")});', f'Pip.brows("{p}", 10, -10, {sc.T("0.3")});',
              f'Pip.arm("{p}", "R", -125, {sc.W("0.3", "where")});', f'Pip.look("{p}", -6, -6, {sc.W("0.3", "where")});',
              f'Pip.move("{p}", 1650, 930, {t_iris + 0.8}, 0.6);', f'Pip.arm("{p}", "R", 0, {t_iris + 0.8});', f'Pip.brows("{p}", 0, 0, {t_iris + 0.8});',
              f'Pip.mood("{p}", "happy", "grin", {sc.T("0.4")});', f'Pip.arm("{p}", "R", -150, {sc.T("0.4") + 0.2});',
              f'Pip.arm("{p}", "R", -110, {sc.T("0.4") + 0.6});', f'Pip.arm("{p}", "R", -150, {sc.T("0.4") + 1.0});', f'Pip.arm("{p}", "R", 0, {sc.T("0.4") + 1.6});']
    return sc


# ======================================================================= c1: a transitional year
def c1():
    sc = Scene(1, "year")
    board(sc)
    chapter_label(sc, 1, "A TRANSITIONAL YEAR")
    card(sc, 96, 170, 780, 110, f'<div style="position:absolute;left:24px;top:14px;font:400 28px Inter;color:{MUTED}">Barcelona coach, 2014/15</div>'
         f'<div class="oswald" style="position:absolute;left:24px;top:46px;font-size:48px">LUIS ENRIQUE · FIRST SEASON</div>', sc.W("1.1", "Luis"))
    q = sc.uid("quote")
    tq = sc.W("1.2", "difficult") - 0.2
    sc.add(f'<div id="{q}" style="position:absolute;left:160px;top:330px;width:1600px;opacity:0;transform-origin:50% 0">'
           f'<div class="oswald" style="font-size:84px;line-height:1.1;text-align:center"><span style="color:{ACCENT}">“</span>A DIFFICULT YEAR, A '
           f'<span style="position:relative;display:inline-block">TRANSITIONAL<span id="{q}-u" style="position:absolute;left:0;right:0;bottom:-6px;height:8px;background:{ACCENT};border-radius:4px;box-shadow:0 0 14px {TEAM_A};transform-origin:0 50%;transform:scaleX(0)"></span></span>'
           f' YEAR<span style="color:{ACCENT}">”</span></div>'
           f'<div id="{q}-src" style="text-align:center;font:400 28px Inter;color:{MUTED};margin-top:22px">Luis Enrique after the final · UEFA.com</div></div>',
           fade_in(f"#{q}", tq, 0.35),
           f'tl.fromTo("#{q}-u", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, {sc.W("1.2b", "phrase")});',
           f'tl.to("#{q}-src", {{ opacity: 0, duration: 0.2 }}, {sc.T("1.3") - 0.3});',
           f'tl.to("#{q}", {{ y: -150, scale: 0.6, opacity: 0.55, duration: 0.6, ease: "power3.inOut" }}, {sc.T("1.3") - 0.2});')
    sc.sfx(tq, "click2", 0.5)
    mags = [("Messi", 620, sc.W("1.3", "Messi")), ("Neymar", 960, sc.W("1.3", "Neymar")), ("Suárez", 1300, sc.W("1.3", "Luis"))]
    for name, x, t in mags:
        i = sc.uid("mag")
        sc.add(f'<div id="{i}" style="position:absolute;left:{x - 70}px;top:470px;width:140px;opacity:0">'
               f'<div style="width:140px;height:140px;border-radius:50%;background:{TEAM_A};box-shadow:0 10px 0 #9e1020, 0 0 40px {TEAM_A}"></div>'
               f'<div style="margin-top:26px;text-align:center;font:700 36px Inter;color:{INK}">{name}</div></div>',
               f'tl.fromTo("#{i}", {{ opacity: 0, y: -80, scale: 1.2 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {round(t, 3)});')
        sc.sfx(t + 0.2, "clack", 0.7)
    # one goal block hops between the three forwards: who will score?
    b = sc.uid("blk")
    t0 = sc.T("1.3b")
    sc.add(f'<div id="{b}" style="position:absolute;left:592px;top:400px;width:56px;height:56px;border-radius:9px;background:{INK};opacity:0"></div>',
           f'tl.fromTo("#{b}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, {t0});',
           f'tl.to("#{b}", {{ keyframes: [{{ x: 170, y: -90 }}, {{ x: 340, y: 0 }}, {{ x: 510, y: -90 }}, {{ x: 680, y: 0 }}, {{ x: 510, y: -90 }}, {{ x: 340, y: 0 }}], duration: 2.6, ease: "none" }}, {t0 + 0.2});',
           fade_out(f"#{b}", sc.T("1.4") + 0.2))
    route(sc, y=830, draw_t=sc.T("1.4") + 0.6)
    p = sc.pip(250, 935, 1.25, 1)
    sc.js += [f'Pip.arm("{p}", "R", -110, {sc.W("1.1", "Luis") - 0.1});', f'Pip.arm("{p}", "R", 0, {sc.W("1.1", "Luis") + 0.8});',
              f'Pip.look("{p}", 6, -6, {tq});', f'Pip.brows("{p}", 12, -6, {tq + 0.4});',
              f'Pip.arm("{p}", "R", -70, {sc.W("1.2b", "phrase")});', f'Pip.arm("{p}", "R", -50, {sc.W("1.2b", "phrase") + 0.25});',
              f'Pip.arm("{p}", "R", -70, {sc.W("1.2b", "phrase") + 0.5});', f'Pip.arm("{p}", "R", 0, {sc.T("1.3")});', f'Pip.brows("{p}", 0, 0, {sc.T("1.3")});',
              f'Pip.mood("{p}", "wide", "o", {sc.W("1.3", "Messi")});', f'Pip.mood("{p}", "happy", "grin", {sc.W("1.3", "Luis") + 0.4});',
              f'Pip.mood("{p}", "normal", "flat", {t0});', f'Pip.brows("{p}", -12, 12, {t0});', f'Pip.look("{p}", 7, -5, {t0 + 0.4});',
              f'Pip.brows("{p}", 0, 0, {sc.T("1.4")});', f'Pip.mood("{p}", "normal", "smile", {sc.T("1.4")});',
              f'Pip.walk("{p}", 330, {sc.E("1.4") - 1.0}, 0.9);']
    return sc


# ======================================================================= c2: Group F
def c2():
    sc = Scene(2, "group")
    board(sc, 0.3)
    chapter_label(sc, 2, "GROUP F · THE MESSI SHOW")
    route(sc, y=150, now=0, t_now=sc.T("2.1"), small=True)
    sc.add(f'<div id="{sc.cid}-teams" style="position:absolute;left:96px;top:226px;font:700 30px Inter;color:{INK};opacity:0">Paris Saint-Germain · Ajax · APOEL</div>',
           fade_in(f"#{sc.cid}-teams", sc.W("2.1", "Paris"), 0.3))
    piles = Piles(sc, ["Messi", "Neymar", "Suárez", "Others"], 1000, 820, gapx=190)
    md = [run("Group F", f"MD{i}") for i in range(1, 7)]
    tcard = [sc.T("2.2") + 0.2, sc.T("2.3") + 0.1, sc.W("2.4", "Three"), sc.W("2.4", "two"), sc.W("2.4", "Four"), sc.W("2.4", "Three", 2)]
    for k, (m, t) in enumerate(zip(md, tcard)):
        rc(sc, m, 96, 280 + k * 94, t)
    piles.add_goal("Others", sc.W("2.2", "Piqué"))
    piles.add_goal("Messi", sc.W("2.3", "Messi"))
    piles.add_goal("Neymar", sc.W("2.3", "Neymar"))
    piles.add_goal("Neymar", tcard[2] + 0.3)
    piles.add_goal("Others", tcard[2] + 0.5)
    piles.add_goal("Suárez", tcard[4] + 0.35)
    piles.add_goal("Neymar", tcard[5] + 0.3)
    piles.add_goal("Suárez", tcard[5] + 0.5)
    counts = [sc.W("2.5", "Once")] + [sc.W("2.5", "twice") + d for d in (0, 0.2)] + [sc.W("2.5", "three") + d for d in (0, 0.15, 0.3)] + [sc.W("2.5", "once", 2)]
    for t in counts:
        piles.add_goal("Messi", t)
    tally = card(sc, 1000, 226, 760, 64, f'<div style="position:absolute;left:20px;top:11px;font:700 30px Inter">W 5 · L 1 · scored 15 · conceded 5</div>', sc.T("2.4b") + 0.2)
    sc.js.append(fade_out(f"#{tally}", sc.T("2.6") - 0.1))
    table = card(sc, 1000, 226, 760, 64, f'<div style="position:absolute;left:20px;top:11px;font:700 30px Inter"><span style="color:{MUTED}">1st</span> Barcelona 15 pts &nbsp; <span style="color:{MUTED}">2nd</span> PSG 13 pts</div>', sc.T("2.6") + 0.1)
    sc.js.append(fade_out(f"#{table}", sc.T("2.8") - 0.1))
    src(sc, 1000, 880, "Group stage goals · Source: UEFA", sc.T("2.7"))
    show = big_text(sc, 1000, 226, f'THE MESSI SHOW<span style="color:{ACCENT}">?</span>', 70, sc.T("2.8") + 0.4, w=760)
    p = sc.pip(1800, 925, 1.05, -1)
    sc.js += [f'Pip.mood("{p}", "closed", "flat", {sc.W("2.3", "lost")});', f'Pip.mood("{p}", "normal", "smile", {sc.W("2.3", "Messi") + 0.3});']
    for k, t in enumerate(counts):
        sc.js.append(f'Pip.arm("{p}", "R", {-60 - 20 * (k % 2)}, {round(t, 3)}, 0.15);')
    sc.js += [f'Pip.arm("{p}", "R", 0, {counts[-1] + 0.5});', f'Pip.mood("{p}", "happy", "grin", {sc.T("2.7")});',
              f'Pip.walk("{p}", 1150, {sc.T("2.7") + 0.5}, 1.2);',
              f'Pip.move("{p}", 1023, 404, {sc.T("2.8")}, 0.5, "power2.out");', f'Pip.arm("{p}", "L", 60, {sc.T("2.8") + 0.5});']
    return sc


# ======================================================================= c3: Manchester and Paris
def c3():
    sc = Scene(3, "r16qf")
    board(sc, 0.3)
    chapter_label(sc, 3, "MANCHESTER AND PARIS")
    r = route(sc, y=150, lit=(0,), now=1, t_now=sc.T("3.1"), small=True)
    sc.js += [f'tl.to("#{r}-n2", {{ attr: {{ fill: "{TEAM_A}", stroke: "{ACCENT}" }}, duration: 0.25 }}, {sc.T("3.4")});',
              f'tl.to("#{r}-t2", {{ attr: {{ fill: "{INK}" }}, duration: 0.25 }}, {sc.T("3.4")});']
    sc.sfx(sc.T("3.4"), "pop", 0.6)
    piles = Piles(sc, ["Suárez", "Neymar", "Rakitić", "Messi"], 1000, 820, gapx=190)
    sc.add(f'<div style="position:absolute;left:1560px;top:766px;width:58px;height:58px;border:3px dashed {MUTED};border-radius:9px"></div>')
    rc(sc, run("Round of 16", "Leg 1"), 96, 230, sc.T("3.2"))
    piles.add_goal("Suárez", sc.W("3.2", "Both") + 0.2)
    piles.add_goal("Suárez", sc.W("3.2", "Suárez") + 0.1)
    sc.add(f'<div id="{sc.cid}-sg" style="position:absolute;left:930px;top:870px;width:186px;text-align:center;font:400 28px Inter;color:{MUTED};opacity:0">group: 2</div>',
           fade_in(f"#{sc.cid}-sg", sc.W("3.2b", "matched"), 0.3))
    rc(sc, run("Round of 16", "Leg 2"), 96, 324, sc.T("3.3"))
    piles.add_goal("Rakitić", sc.W("3.3", "Rakitić"))
    big_text(sc, 96, 418, "AGG 3-1", 44, sc.W("3.3", "aggregate") - 0.3, w=400)
    rc(sc, run("Quarter-final", "Leg 1"), 96, 490, sc.W("3.5", "Three"))
    piles.add_goal("Neymar", sc.W("3.5", "Neymar"))
    piles.add_goal("Suárez", sc.W("3.5", "Suárez"))
    piles.add_goal("Suárez", sc.W("3.5", "twice"))
    rc(sc, run("Quarter-final", "Leg 2"), 96, 584, sc.W("3.5", "Two"))
    piles.add_goal("Neymar", sc.W("3.5", "Neymar", 2))
    piles.add_goal("Neymar", sc.W("3.5", "Neymar", 2) + 0.25)
    big_text(sc, 96, 678, "AGG 5-1", 44, sc.E("3.5"), w=400)
    ghost = rc(sc, run("Group F", "MD2"), 96, 760, sc.T("3.5b"))
    x = sc.uid("x")
    sc.add(f'<div id="{x}" style="position:absolute;left:90px;top:800px;width:612px;height:6px;background:{ACCENT};border-radius:3px;transform-origin:0 50%;transform:scaleX(0)"></div>',
           f'tl.fromTo("#{x}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out" }}, {sc.W("3.5b", "twice")});')
    big_text(sc, 1540, 600, "0", 150, sc.W("3.7", "none"), color=ACCENT, w=120, hit=True)
    src(sc, 1000, 920, "Knockout goals · Source: UEFA", sc.T("3.6"))
    p = sc.pip(1800, 925, 1.05, -1)
    sc.js += [f'Pip.look("{p}", -6, -3, {sc.W("3.2", "Both")});', f'Pip.mood("{p}", "wide", "o", {sc.W("3.2", "Suárez")});',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("3.3")});',
              f'Pip.mood("{p}", "normal", "flat", {sc.T("3.4")});', f'Pip.arm("{p}", "L", 40, {sc.T("3.4") + 0.3});', f'Pip.arm("{p}", "R", -40, {sc.T("3.4") + 0.35});',
              f'Pip.arm("{p}", "L", 0, {sc.T("3.4") + 1.2});', f'Pip.arm("{p}", "R", 0, {sc.T("3.4") + 1.25});',
              f'Pip.mood("{p}", "happy", "grin", {sc.W("3.5b", "twice")});',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("3.6")});', f'Pip.arm("{p}", "R", -60, {sc.T("3.6") + 0.2});',
              f'Pip.walk("{p}", 1700, {sc.T("3.7") - 0.8}, 0.7);', f'Pip.arm("{p}", "R", -20, {sc.T("3.7")});',
              f'Pip.blink("{p}", {sc.T("3.7") + 0.6});', f'Pip.blink("{p}", {sc.T("3.7") + 1.4});', f'Pip.mood("{p}", "wide", "flat", {sc.T("3.7") + 1.9});']
    return sc


# ======================================================================= c4: Bayern
def c4():
    sc = Scene(4, "semi")
    board(sc, 0.3)
    chapter_label(sc, 4, "BAYERN · THE ONE NIGHT")
    r = route(sc, y=150, lit=(0, 1, 2), now=3, t_now=sc.T("4.1"), small=True)
    sc.js += [f'tl.to("#{r}-n4", {{ attr: {{ fill: "{TEAM_A}", stroke: "{ACCENT}" }}, duration: 0.25 }}, {sc.W("4.4", "final")});',
              f'tl.to("#{r}-t4", {{ attr: {{ fill: "{INK}" }}, duration: 0.25 }}, {sc.W("4.4", "final")});']
    piles = Piles(sc, ["Suárez", "Neymar", "Rakitić", "Messi"], 1000, 820, gapx=190, start={"Suárez": 4, "Neymar": 3, "Rakitić": 1, "Messi": 0})
    rc(sc, run("Semi-final", "Leg 1"), 96, 230, sc.T("4.2"))
    piles.add_goal("Messi", sc.W("4.2", "twice"))
    piles.add_goal("Messi", sc.W("4.2", "twice") + 0.3)
    piles.add_goal("Neymar", sc.W("4.2", "third"))
    rc(sc, run("Semi-final", "Leg 2"), 96, 324, sc.T("4.3"))
    piles.add_goal("Neymar", sc.W("4.3", "both"))
    piles.add_goal("Neymar", sc.W("4.3", "both") + 0.3)
    big_text(sc, 96, 418, "AGG 5-3", 44, sc.T("4.4"), w=400)
    card(sc, 1300, 470, 470, 90, f'<div style="position:absolute;left:20px;top:10px;font:400 28px Inter;color:{MUTED}">Messi\'s 2 knockout goals:</div>'
         f'<div style="position:absolute;left:20px;top:44px;font:700 30px Inter">both in the semi-final, first leg</div>', sc.T("4.5") + 0.2)
    src(sc, 1000, 920, "Knockout goals · Source: UEFA", sc.T("4.2"))
    p = sc.pip(1800, 925, 1.05, -1)
    sc.js += [f'Pip.mood("{p}", "wide", "o", {sc.W("4.2", "Messi")});', f'Pip.mood("{p}", "happy", "grin", {sc.W("4.2", "twice") + 0.3});',
              f'Pip.arm("{p}", "L", 150, {sc.W("4.2", "twice") + 0.35});', f'Pip.arm("{p}", "R", -150, {sc.W("4.2", "twice") + 0.4});',
              f'Pip.jump("{p}", {sc.W("4.2", "twice") + 0.35});',
              f'Pip.arm("{p}", "L", 0, {sc.T("4.3")});', f'Pip.arm("{p}", "R", 0, {sc.T("4.3")});', f'Pip.mood("{p}", "normal", "o", {sc.T("4.3b")});',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("4.4")});', f'Pip.arm("{p}", "R", -100, {sc.T("4.5")});', f'Pip.arm("{p}", "R", 0, {sc.E("4.5")});']
    return sc


# ======================================================================= c5: Berlin, part one
def c5():
    sc = Scene(5, "berlin1")
    board(sc, 0.3)
    sc.sfx(0.1, "whoosh2", 0.8)
    tb = sc.W("5.1", "Berlin")
    title = panel(sc, f'<div style="position:absolute;left:0;right:0;top:300px;text-align:center">'
                      f'<div class="oswald" style="font-size:120px;letter-spacing:.03em">BERLIN · 6 JUNE 2015</div>'
                      f'<div style="font:600 40px Inter;color:{INK};margin-top:18px">Olympiastadion · <span style="color:{TEAM_B_EDGE}">Juventus</span> v <span style="color:{ACCENT}">Barcelona</span></div>'
                      f'<div style="font:400 28px Inter;color:{MUTED};margin-top:16px">Champions League final · Source: UEFA</div></div>', tb, sc.T("5.1b") + 1.2)
    t_show = sc.T("5.1b") + 1.3
    ga, ge = goal_scene(sc, "4'", "Barcelona",
                        {0: sc.W("5.2", "switched"), 1: sc.W("5.3", "Alba"), 3: sc.W("5.3", "Neymar", 2), 5: sc.W("5.3", "Iniesta", 2), 6: sc.T("5.4")},
                        t_show, sc.T("5.5") - 0.15,
                        f'JUVENTUS <span style="color:{ACCENT}">0-1</span> BARCELONA <span style="font:700 30px Inter;color:{MUTED}">4\'</span>')
    # 5.4b: the four passes glow again in order
    for k, i in enumerate([0, 1, 3, 5]):
        sc.js.append(f'tl.to("#{ga}-a{i}-head", {{ opacity: 0.2, duration: 0.15, yoyo: true, repeat: 1 }}, {round(sc.T("5.4b") + 0.3 * k, 3)});')
    gb, ge2 = goal_scene(sc, "55'", "Juventus",
                         {0: sc.W("5.5", "found"), 1: sc.W("5.6", "Tevez"), 2: sc.W("5.6", "saved"), 3: sc.W("5.6", "Morata")},
                         sc.T("5.5") - 0.1, sc.dur - 0.05,
                         f'JUVENTUS <span style="color:{TEAM_B_EDGE}">1-1</span> BARCELONA <span style="font:700 30px Inter;color:{MUTED}">55\'</span>')
    sc.sfx(sc.T("5.5") - 0.1, "whoosh2", 0.7)
    p = sc.pip(960, 930, 1.4, 1)
    sc.js += [f'Pip.mood("{p}", "wide", "o", {tb + 0.2});', f'Pip.mood("{p}", "happy", "smile", {tb + 1.4});',
              f'Pip.arm("{p}", "L", 80, {sc.T("5.1b") + 0.4});', f'Pip.arm("{p}", "R", -80, {sc.T("5.1b") + 0.45});',
              f'Pip.arm("{p}", "L", 0, {t_show});', f'Pip.arm("{p}", "R", 0, {t_show});',
              f'Pip.walk("{p}", 170, {t_show - 0.4}, 1.4);', f'Pip.move("{p}", 170, 930, {t_show + 1.0}, 0.01);',
              f'Pip.look("{p}", 7, -5, {sc.W("5.2", "switched")});', f'Pip.look("{p}", 8, -8, {sc.T("5.3")});',
              f'Pip.mood("{p}", "happy", "grin", {ge});', f'Pip.arm("{p}", "R", -150, {ge + 0.05});', f'Pip.jump("{p}", {ge + 0.1});',
              f'Pip.arm("{p}", "R", 0, {ge + 1.4});', f'Pip.mood("{p}", "normal", "smile", {sc.T("5.5")});',
              f'Pip.mood("{p}", "closed", "flat", {ge2 - 0.1});', f'Pip.arm("{p}", "L", 130, {ge2 - 0.05});', f'Pip.arm("{p}", "R", -130, {ge2});']
    return sc


# ======================================================================= c6: Berlin, part two
def c6():
    sc = Scene(6, "berlin2")
    board(sc, 0.3)
    sc.sfx(0.1, "whoosh3", 0.8)
    ga, ge = goal_scene(sc, "68'", "Barcelona",
                        {0: sc.W("6.1", "picked"), 1: sc.W("6.2", "past"), 4: sc.W("6.3", "shot"), 5: sc.W("6.3", "Buffon"), 6: sc.W("6.3", "Suárez")},
                        0.1, sc.T("6.4") - 0.15,
                        f'JUVENTUS <span style="color:{ACCENT}">1-2</span> BARCELONA <span style="font:700 30px Inter;color:{MUTED}">68\'</span>')
    gb, ge2 = goal_scene(sc, "90+7'", "Barcelona",
                         {0: sc.W("6.4", "found"), 2: sc.W("6.4", "found", 2), 4: sc.W("6.4", "scored")},
                         sc.T("6.4") - 0.1, sc.T("6.5") - 0.15,
                         f'JUVENTUS <span style="color:{ACCENT}">1-3</span> BARCELONA <span style="font:700 30px Inter;color:{MUTED}">90+7\'</span>')
    sc.sfx(sc.T("6.4") - 0.1, "whoosh3", 0.7)
    pedro = card(sc, 1300, 160, 520, 96, f'<div style="position:absolute;left:20px;top:10px;font:400 28px Inter;color:{MUTED}">Pedro on 95:19</div>'
                 f'<div style="position:absolute;left:20px;top:46px;font:700 32px Inter">his pass to Neymar 96:38</div>', sc.T("6.4b"))
    sc.js.append(fade_out(f"#{pedro}", sc.T("6.5") - 0.3))
    champ = panel(sc, f'<div style="position:absolute;inset:0;background:#07080a"></div>'
                      f'<div class="oswald" style="position:absolute;left:0;right:0;top:250px;text-align:center;font-size:190px;letter-spacing:.04em;color:{INK};text-shadow:0 0 40px {TEAM_A}">CHAMPIONS</div>'
                      f'<div style="position:absolute;left:0;right:0;top:500px;text-align:center;font:600 40px Inter;color:{ACCENT}">Barcelona 2014/15</div>', sc.T("6.5") - 0.1, sc.T("6.6") - 0.2)
    rt = route(sc, y=700, lit=(0, 1, 2, 3, 4), draw_t=sc.T("6.5") + 0.3)
    sc.js.append(fade_out(f"#{rt}-g", sc.T("6.6") - 0.2))
    sc.sfx(sc.T("6.5"), "hit1", 1.0)
    awards = panel(sc, '<div style="position:absolute;inset:0;background:#07080a"></div>', sc.T("6.6") - 0.1)
    card(sc, 160, 260, 760, 200, f'<div style="position:absolute;left:30px;top:24px;font:400 30px Inter;color:{MUTED}">Official man of the match</div>'
         f'<div class="oswald" style="position:absolute;left:30px;top:72px;font-size:80px">ANDRÉS INIESTA</div>'
         f'<div style="position:absolute;left:30px;top:166px;font:400 24px Inter;color:{MUTED}">Source: UEFA</div>'.replace("24px", "28px"), sc.W("6.6", "Iniesta"))
    xv = sc.uid("xavi")
    card(sc, 1000, 260, 760, 200, f'<div style="position:absolute;left:30px;top:24px;font:400 30px Inter;color:{MUTED}">Xavi, his last Barcelona game</div>'
         f'<div class="oswald" style="position:absolute;left:30px;top:72px;font-size:80px">APPEARANCE <span id="{xv}" style="color:{ACCENT}">0</span></div>'
         f'<div style="position:absolute;left:30px;top:166px;font:400 28px Inter;color:{MUTED}">Source: ESPN</div>', sc.W("6.6", "Xavi"))
    sc.js.append(f'tl.fromTo("#{xv}", {{ textContent: 0 }}, {{ textContent: 767, duration: 1.4, ease: "power2.out", snap: {{ textContent: 1 }} }}, {sc.W("6.6", "seven")});')
    sc.sfx(sc.W("6.6", "seven") + 1.4, "pop", 0.7)
    card(sc, 1000, 500, 760, 90, f'<div style="position:absolute;left:30px;top:22px;font:700 36px Inter">78\' · Xavi on for Iniesta</div>', sc.W("6.6b", "Xavi"))
    p = sc.pip(170, 930, 1.25, 1)
    sc.js += [f'Pip.look("{p}", 7, -3, {sc.W("6.1", "picked")});', f'Pip.mood("{p}", "wide", "o", {sc.W("6.2", "past")});',
              f'Pip.walk("{p}", 330, {sc.W("6.2", "carried")}, 1.6);', f'Pip.walk("{p}", 170, {sc.W("6.3", "shot") - 0.2}, 0.9);',
              f'Pip.mood("{p}", "happy", "grin", {ge});', f'Pip.arm("{p}", "R", -150, {ge + 0.05});', f'Pip.arm("{p}", "L", 150, {ge + 0.1});',
              f'Pip.jump("{p}", {ge + 0.1});', f'Pip.arm("{p}", "R", 0, {ge + 1.3});', f'Pip.arm("{p}", "L", 0, {ge + 1.3});',
              f'Pip.mood("{p}", "happy", "grin", {ge2});', f'Pip.jump("{p}", {ge2 + 0.1});',
              f'Pip.arm("{p}", "L", 120, {sc.W("6.4b", "earlier") - 0.6});', f'Pip.look("{p}", -6, 4, {sc.W("6.4b", "earlier") - 0.5});', f'Pip.arm("{p}", "L", 0, {sc.E("6.4b")});',
              f'Pip.move("{p}", 960, 960, {sc.T("6.5") - 0.1}, 0.01);', f'Pip.mood("{p}", "happy", "grin", {sc.T("6.5")});',
              f'Pip.arm("{p}", "R", -150, {sc.T("6.5") + 0.1});', f'Pip.arm("{p}", "L", 150, {sc.T("6.5") + 0.15});',
              f'Pip.jump("{p}", {sc.T("6.5") + 0.2}, 90);', f'Pip.jump("{p}", {sc.T("6.5") + 1.2}, 60);',
              f'Pip.arm("{p}", "R", 0, {sc.T("6.6")});', f'Pip.arm("{p}", "L", 0, {sc.T("6.6")});', f'Pip.mood("{p}", "normal", "smile", {sc.T("6.6")});',
              f'Pip.move("{p}", 960, 930, {sc.T("6.6")}, 0.4);', f'Pip.look("{p}", -6, -6, {sc.W("6.6", "Iniesta")});', f'Pip.look("{p}", 6, -6, {sc.W("6.6", "Xavi")});']
    return sc


# ======================================================================= c7: the evidence
def c7():
    sc = Scene(7, "numbers")
    sc.add('<div style="position:absolute;inset:0;background:#07080a"></div>')
    chapter_label(sc, 7, "THE EVIDENCE")
    intro = panel(sc, f'<div style="position:absolute;left:0;right:0;top:420px;text-align:center;font:700 40px Inter;color:{INK}">The final in numbers</div>'
                      f'<div style="position:absolute;left:0;right:0;top:480px;text-align:center;font:400 30px Inter;color:{MUTED}">All figures: StatsBomb open data</div>',
                  sc.T("7.1") + 0.3, sc.T("7.2") - 0.15)

    # P1: xG timeline
    X0, X1, Y0, Y1, MMAX, GMAX = 230, 1500, 800, 290, 98, 2.5
    X = lambda m: round(X0 + (X1 - X0) * m / MMAX, 1)
    Y = lambda g: round(Y0 - (Y0 - Y1) * g / GMAX, 1)
    parts, js = [], []
    for g in (0.5, 1.0, 1.5, 2.0, 2.5):
        parts.append(f'<line x1="{X0}" x2="{X1}" y1="{Y(g)}" y2="{Y(g)}" stroke="rgba(255,255,255,.08)" stroke-width="2"/>'
                     f'<text x="{X0 - 18}" y="{Y(g) + 9}" text-anchor="end" font-family="Inter" font-size="28" fill="{MUTED}">{g:.1f}</text>')
    for m in (0, 15, 30, 45, 60, 75, 90):
        parts.append(f'<text x="{X(m)}" y="{Y0 + 44}" text-anchor="middle" font-family="Inter" font-size="28" fill="{MUTED}">{m}\'</text>')
    parts.append(f'<line x1="{X0}" x2="{X1}" y1="{Y0}" y2="{Y0}" stroke="rgba(255,255,255,.25)" stroke-width="3"/>'
                 f'<text x="{X0 - 18}" y="{Y1 - 34}" text-anchor="end" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">xG</text>'
                 f'<text x="{X1}" y="{Y0 + 84}" text-anchor="end" font-family="Inter" font-size="28" fill="{MUTED}">minute</text>')
    t_draw, d_draw = sc.W("7.2", "measures"), 3.6
    lines = {}
    for team, col in (("Juventus", TEAM_B_EDGE), ("Barcelona", TEAM_A)):
        pts, cum = [(0, 0)], 0.0
        for s in [s for s in D["shots"] if s["team"] == team]:
            pts += [(s["m"], cum), (s["m"], cum + s["xg"])]
            cum += s["xg"]
        pts.append((MMAX - 1, cum))
        lines[team] = (pts, cum)
        d = "M " + " L ".join(f"{X(m)} {Y(g)}" for m, g in pts)
        filt = f' filter="url(#{sc.cid}-glowA)"' if team == "Barcelona" else ""
        lid = sc.uid("xg")
        parts.append(f'<path id="{lid}" d="{d}" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="100"{filt}/>')
        js.append(f'tl.fromTo("#{lid}", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: {d_draw}, ease: "power1.inOut" }}, {t_draw});')
        ex, ey = X(MMAX - 1), Y(cum)
        eid = sc.uid("xgend")
        te = sc.T("7.3") + 0.4 if team == "Barcelona" else sc.W("7.3", "Juventus")
        parts.append(f'<g id="{eid}" opacity="0"><text x="{ex + 24}" y="{ey + 6}" font-family="Oswald" font-weight="700" font-size="62" fill="{col if team == "Barcelona" else INK}">{cum:.2f}</text>'
                     f'<text x="{ex + 24}" y="{ey + 44}" font-family="Inter" font-weight="700" font-size="28" fill="{MUTED}">{team.upper()} · xG</text></g>')
        js.append(f'tl.fromTo("#{eid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {round(te, 3)});')
        sc.sfx(te, "hit2" if team == "Barcelona" else "pop", 0.8)
    for k, s in enumerate([s for s in D["shots"] if s["goal"]]):
        pts, _ = lines[s["team"]]
        gy = max(g for m, g in pts if m <= s["m"] + 1e-6)
        col = TEAM_A if s["team"] == "Barcelona" else TEAM_B_EDGE
        tt = round(t_draw + d_draw * s["m"] / MMAX, 2)
        early = s["m"] < 10
        mid = sc.uid("gm")
        parts.append(f'<g id="{mid}" opacity="0"><circle cx="{X(s["m"])}" cy="{Y(gy)}" r="13" fill="{col}" stroke="#fff" stroke-width="3"/>'
                     f'<text x="{X(s["m"]) + (16 if early else -18)}" y="{Y(gy) - (40 if early else 22)}" text-anchor="{"start" if early else "end"}" font-family="Inter" font-weight="700" font-size="28" fill="{INK}">{s["label"]}</text></g>')
        js.append(f'tl.fromTo("#{mid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25 }}, {tt});')
    p1 = panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:110px;font-size:58px">EXPECTED GOALS (xG)</div>'
                   f'<div style="position:absolute;left:98px;top:182px;font:400 28px Inter;color:{MUTED}">Cumulative xG by minute, Juventus 1-3 Barcelona</div>'
                   f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">{defs(sc.cid)}{"".join(parts)}</svg>'
                   f'<div class="src" style="left:98px;top:880px">Source: StatsBomb open data</div>', sc.T("7.2") - 0.1, sc.T("7.4") - 0.15)
    sc.js.extend(js)

    # P2: shot map
    S, PX, PY = 9, 420, 200
    Pp = Pitch(PX, PY, S)
    shots, js = [], []
    t_a, t_b = sc.T("7.4") + 0.4, sc.E("7.4") + 1.0
    for k, s in enumerate(D["shots"]):
        barca = s["team"] == "Barcelona"
        x, y = Pp.P(s["x"], s["y"]) if barca else Pp.P(120 - s["x"], 80 - s["y"])
        r = round((60 + 1900 * s["xg"]) ** 0.5 * 0.75, 1)
        col = TEAM_A if barca else TEAM_B_EDGE
        sid = sc.uid("sh")
        shots.append(f'<circle id="{sid}" cx="{x}" cy="{y}" r="{r}" fill="{col if s["goal"] else "none"}" fill-opacity="{1 if s["goal"] else 0}" stroke="{"#fff" if s["goal"] else col}" stroke-width="{3 if s["goal"] else 2.5}" opacity="0"/>')
        js.append(f'tl.fromTo("#{sid}", {{ opacity: 0, scale: 0.2, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {round(t_a + (t_b - t_a) * k / len(D["shots"]), 3)});')
    p2 = panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:110px;font-size:58px">EVERY SHOT, SIZED BY xG</div>'
                   f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">{defs(sc.cid + "p")}{Pp.svg()}{"".join(shots)}</svg>'
                   f'<div style="position:absolute;left:{PX}px;top:{PY + 80 * S + 14}px;font:700 28px Inter;color:{TEAM_B_EDGE}">Juventus shooting this way ←</div>'
                   f'<div style="position:absolute;right:{1920 - PX - 120 * S}px;top:{PY + 80 * S + 14}px;font:700 28px Inter;color:{ACCENT}">→ Barcelona shooting this way</div>'
                   f'<div class="src" style="left:98px;top:880px">Filled circle = goal · circle size = xG · Source: StatsBomb open data</div>', sc.T("7.4") - 0.1, sc.T("7.5") - 0.15)
    sc.js.extend(js)

    # P3: passes per 15 minutes
    bins = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-90", "90+"]
    BX0, BW, BG, BY = 260, 52, 70, 790
    hmax = 140
    bars, js = [], []
    for k, lab in enumerate(bins):
        for j, team in enumerate(("Barcelona", "Juventus")):
            v = D["passes_by_15"][team][k]
            h = round(480 * v / hmax, 1)
            x = BX0 + k * (2 * BW + BG) + j * (BW + 6)
            bid = sc.uid("pb")
            col = TEAM_A if team == "Barcelona" else TEAM_B_EDGE
            bars.append(f'<div id="{bid}" style="position:absolute;left:{x}px;top:{BY - h}px;width:{BW}px;height:{h}px;background:{col};border-radius:6px 6px 0 0;transform-origin:50% 100%;transform:scaleY(0)"></div>'
                        f'<div id="{bid}-v" style="position:absolute;left:{x - 10}px;top:{BY - h - 38}px;width:{BW + 20}px;text-align:center;font:700 28px Inter;color:{INK};opacity:0">{v}</div>')
            tb = sc.T("7.5") + 0.3 + k * 0.12
            js.append(f'tl.fromTo("#{bid}", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.4, ease: "power3.out" }}, {round(tb, 3)});')
            js.append(fade_in(f"#{bid}-v", tb + 0.3, 0.2, blur=False))
            half = 0 if k < 3 else 1
            tdim = sc.T("7.5b") if half == 1 else sc.T("7.5c")
            js.append(f'tl.to(["#{bid}", "#{bid}-v"], {{ opacity: 0.25, duration: 0.3 }}, {tdim});')
            if half == 1:
                js.append(f'tl.to(["#{bid}", "#{bid}-v"], {{ opacity: 1, duration: 0.3 }}, {sc.T("7.5c")});')
        bars.append(f'<div style="position:absolute;left:{BX0 + k * (2 * BW + BG) - 10}px;top:{BY + 14}px;width:{2 * BW + 26}px;text-align:center;font:400 28px Inter;color:{MUTED}">{lab}</div>')
    p3 = panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:110px;font-size:58px">PASSES PER 15 MINUTES</div>'
                   f'<div style="position:absolute;left:98px;top:182px;font:700 30px Inter"><span style="color:{ACCENT}">Barcelona 600</span> &nbsp; <span style="color:{TEAM_B_EDGE}">Juventus 377</span></div>'
                   f'<div style="position:absolute;left:96px;top:{BY - 480}px;height:480px;width:1px"></div>{"".join(bars)}'
                   f'<div class="src" style="left:98px;top:880px">Minutes of the final · units: passes · Source: StatsBomb open data</div>', sc.T("7.5") - 0.1, sc.T("7.6") - 0.15)
    sc.js.extend(js)

    # P4: pressing by thirds
    thirds = ["Own third", "Middle third", "Attacking third"]
    rows, js = [], []
    for j, team in enumerate(("Juventus", "Barcelona")):
        vals = D["pressures_by_third"][team]
        col = TEAM_A if team == "Barcelona" else TEAM_B_EDGE
        y = 330 + j * 270
        rows.append(f'<div style="position:absolute;left:96px;top:{y}px;font:700 34px Inter;color:{col}">{team} · {sum(vals)} pressures</div>')
        for k, v in enumerate(vals):
            x = 96 + k * 580
            w = round(500 * v / 70, 1)
            bid = sc.uid("pr")
            rows.append(f'<div id="{bid}" style="position:absolute;left:{x}px;top:{y + 60}px;width:{w}px;height:64px;background:{col};border-radius:0 8px 8px 0;transform-origin:0 50%;transform:scaleX(0)"></div>'
                        f'<div style="position:absolute;left:{x}px;top:{y + 134}px;font:400 28px Inter;color:{MUTED}">{thirds[k]}</div>'
                        f'<div id="{bid}-v" class="oswald" style="position:absolute;left:{x + w + 14}px;top:{y + 62}px;font-size:52px;opacity:0">{v}</div>')
            t = sc.W("7.6", "pressed") + 0.2 + j * 0.5 + k * 0.15
            js.append(f'tl.fromTo("#{bid}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.45, ease: "power3.out" }}, {round(t, 3)});')
            js.append(fade_in(f"#{bid}-v", t + 0.35, 0.2, blur=False))
            if k < 2:
                js.append(f'tl.to(["#{bid}", "#{bid}-v"], {{ opacity: 0.3, duration: 0.3 }}, {sc.T("7.6b") + 0.3});')
    p4 = panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:110px;font-size:58px">WHERE EACH TEAM PRESSED</div>'
                   f'<div style="position:absolute;left:98px;top:182px;font:400 28px Inter;color:{MUTED}">Pressures by third of the pitch, from each team\'s own goal</div>'
                   f'{"".join(rows)}<div class="src" style="left:98px;top:880px">Units: pressures · Source: StatsBomb open data</div>', sc.T("7.6") - 0.1, sc.T("7.7") - 0.15)
    sc.js.extend(js)

    # P5: pass network
    net = D["network"]
    S5, NX, NY = 10, 360, 190
    Pn = Pitch(NX, NY, S5)
    pos = {n["name"]: Pn.P(n["x"], n["y"]) for n in net["nodes"]}
    els, js = [], []
    t_n = sc.T("7.7") + 0.3
    for k, l in enumerate(net["links"]):
        (x1, y1), (x2, y2) = pos[l["a"]], pos[l["b"]]
        hot = {l["a"], l["b"]} == {"Dani Alves", "Rakitić"}
        lid = sc.uid("ln")
        els.append(f'<line id="{lid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACCENT if hot else "rgba(255,255,255,.55)"}" stroke-width="{round(2 + l["n"] / 3.5, 1)}" stroke-linecap="round" opacity="0"{" filter=" + chr(34) + "url(#" + sc.cid + "n-glowA)" + chr(34) if hot else ""}/>')
        js.append(f'tl.fromTo("#{lid}", {{ opacity: 0 }}, {{ opacity: {1 if hot else 0.6}, duration: 0.3 }}, {round(t_n + 0.6 + k * 0.08, 3)});')
        if hot:
            js.append(f'tl.fromTo("#{lid}", {{ attr: {{ "stroke-width": {round(2 + l["n"] / 3.5, 1)} }} }}, {{ attr: {{ "stroke-width": {round(6 + l["n"] / 3.5, 1)} }}, duration: 0.25, yoyo: true, repeat: 3 }}, {sc.W("7.7", "Alves")});')
    for k, n in enumerate(net["nodes"]):
        x, y = pos[n["name"]]
        r = round(10 + n["n"] / 6, 1)
        nid = sc.uid("nd")
        els.append(f'<g id="{nid}" opacity="0"><circle cx="{x}" cy="{y}" r="{r}" fill="{TEAM_A}" filter="url(#{sc.cid}n-glowA)"/>'
                   f'<text x="{x}" y="{y - r - 12}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{INK}">{n["name"]}</text></g>')
        js.append(f'tl.fromTo("#{nid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {round(t_n + k * 0.05, 3)});')
    p5 = panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:96px;font-size:58px">BARCELONA\'S PASSING NETWORK</div>'
                   f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0">{defs(sc.cid + "n")}{Pn.svg()}{"".join(els)}</svg>'
                   f'<div class="src" style="left:98px;top:{NY + 80 * S5 + 12}px">Completed passes up to the first substitution ({net["until"]}), average positions · line width = passes · Source: StatsBomb open data</div>',
               sc.T("7.7") - 0.1, sc.T("7.8") - 0.15)
    sc.js.extend(js)

    # P6 and P7: player comparison bars
    def bars_panel(title, sub, data, hi, unit, t_in, t_out, t_first):
        rows, js = [], []
        vmax = max(data.values())
        for k, (name, v) in enumerate(data.items()):
            y = 260 + k * 96
            w = round(1100 * v / vmax, 1)
            col = TEAM_A if name == hi else "#3a414d"
            bid = sc.uid("cb")
            rows.append(f'<div style="position:absolute;left:96px;top:{y + 8}px;width:300px;font:700 34px Inter;color:{INK}">{name}</div>'
                        f'<div id="{bid}" style="position:absolute;left:400px;top:{y}px;width:{w}px;height:60px;background:{col};border-radius:0 8px 8px 0;transform-origin:0 50%;transform:scaleX(0);{"box-shadow:0 0 22px " + TEAM_A if name == hi else ""}"></div>'
                        f'<div id="{bid}-v" class="oswald" style="position:absolute;left:{400 + w + 16}px;top:{y - 2}px;font-size:56px;opacity:0">{v}</div>')
            t = t_first + k * 0.18
            js.append(f'tl.fromTo("#{bid}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.5, ease: "power3.out" }}, {round(t, 3)});')
            js.append(fade_in(f"#{bid}-v", t + 0.4, 0.2, blur=False))
        panel(sc, f'<div class="oswald" style="position:absolute;left:96px;top:110px;font-size:58px">{title}</div>'
                  f'<div style="position:absolute;left:98px;top:182px;font:400 28px Inter;color:{MUTED}">{sub}</div>'
                  f'{"".join(rows)}<div class="src" style="left:98px;top:880px">Units: {unit} · Source: StatsBomb open data</div>', t_in, t_out)
        sc.js.extend(js)

    bars_panel("MOST INVOLVED BARCELONA PLAYERS", "Every event in the data per player (passes, carries, receipts, duels, pressures and more). 71 of Messi's 290 were passes.",
               D["events_per_player"], "Messi", "events", sc.T("7.8") - 0.1, sc.T("7.9") - 0.15, sc.T("7.8") + 0.4)
    bars_panel("SHOTS CREATED", "Barcelona passes that led directly to a shot", D["shots_created"], "Rakitić", "passes that led to a shot",
               sc.T("7.9") - 0.1, None, sc.T("7.9") + 0.3)
    p = sc.pip(1790, 930, 1.05, -1)
    sc.js += [f'Pip.mood("{p}", "normal", "smile", 0.3);', f'Pip.arm("{p}", "R", -105, {sc.T("7.3") + 0.3});', f'Pip.arm("{p}", "R", 0, {sc.T("7.4")});',
              f'Pip.mood("{p}", "wide", "o", {sc.T("7.4") + 1});', f'Pip.jump("{p}", {sc.T("7.4") + 1.6}, 40);',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("7.5")});', f'Pip.arm("{p}", "R", -120, {sc.T("7.5b")});', f'Pip.arm("{p}", "R", 0, {sc.T("7.6")});',
              f'Pip.mood("{p}", "closed", "flat", {sc.T("7.6") + 0.6});', f'Pip.mood("{p}", "normal", "smile", {sc.T("7.6b")});',
              f'Pip.arm("{p}", "L", 70, {sc.W("7.7", "Alves")});', f'Pip.arm("{p}", "L", 0, {sc.E("7.7")});',
              f'Pip.mood("{p}", "happy", "smile", {sc.T("7.8") + 0.6});', f'Pip.brows("{p}", -14, 4, {sc.W("7.9", "Rakitić")});',
              f'Pip.mood("{p}", "normal", "o", {sc.W("7.9", "Rakitić")});']
    return sc


# ======================================================================= c8: the verdict
def c8():
    sc = Scene(8, "verdict")
    board(sc, 0.3)
    chapter_label(sc, 8, "THE VERDICT")
    stats = [("13", "PLAYED", sc.W("8.1", "Thirteen")), ("11", "WON", sc.W("8.1", "Eleven")), ("2", "LOST", sc.W("8.1", "Two")),
             ("31", "SCORED", sc.W("8.2", "Thirty")), ("11", "CONCEDED", sc.W("8.2", "Eleven"))]
    els, js = [], []
    for k, (n, lab, t) in enumerate(stats):
        i = sc.uid("st")
        x = 140 + k * 340
        els.append(f'<div id="{i}" style="position:absolute;left:{x}px;top:260px;width:300px;opacity:0"><div class="oswald" style="font-size:150px;line-height:1;color:{ACCENT if lab == "WON" else INK}">{n}</div>'
                   f'<div style="font:700 30px Inter;color:{MUTED};letter-spacing:.06em">{lab}</div></div>')
        js.append(f'tl.fromTo("#{i}", {{ opacity: 0, y: 30, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power4.out" }}, {round(t, 3)});')
        sc.sfx(t, "pop", 0.6)
    els.append(f'<div id="{sc.cid}-home" style="position:absolute;left:140px;top:560px;font:700 44px Inter;opacity:0">Home games: <span style="color:{ACCENT}">won 6 of 6</span></div>'
               f'<div id="{sc.cid}-away" style="position:absolute;left:140px;top:640px;font:700 44px Inter;opacity:0">Both defeats: <span style="color:{TEAM_B_EDGE}">2-3 in Paris, 2-3 in Munich</span></div>'
               f'<div class="src" style="left:140px;top:740px">Source: UEFA</div>')
    js += [fade_in(f"#{sc.cid}-home", sc.W("8.2b", "six") - 0.3), fade_in(f"#{sc.cid}-away", sc.W("8.2b", "defeats"))]
    panel(sc, "".join(els), 0.0, sc.T("8.3") - 0.15)
    sc.js.extend(js)
    # the opening blocks return
    rows = panel(sc, f'<div class="oswald" style="position:absolute;left:140px;top:160px;font-size:40px;color:{MUTED}">GROUP STAGE</div>'
                     f'<div class="oswald" style="position:absolute;left:140px;top:400px;font-size:40px;color:{MUTED}">KNOCKOUTS</div>'
                     f'<div class="src" style="left:140px;top:580px">Red: Messi · outlined: Neymar and Suárez · Source: UEFA</div>', sc.T("8.3") - 0.1, sc.T("8.4") - 0.15)
    g_ids = blocks_row(sc, "vg", 15, 8, 140, 230, sc.T("8.3"), [sc.W("8.3", "eight") + 0.06 * i for i in range(8)])
    k_ids = blocks_row(sc, "vk", 16, 2, 140, 470, sc.T("8.3") + 0.3, [sc.W("8.3", "two")] * 2,
                       outline=[(i, sc.W("8.3", "twelve") + 0.05 * (i - 2)) for i in range(2, 14)])
    for i in g_ids + k_ids:
        sc.js.append(f'tl.to("#{i}", {{ opacity: 0, duration: 0.15 }}, {sc.T("8.4") - 0.15});')
    big_text(sc, 1240, 452, f'<span style="color:{ACCENT}">12</span><span style="color:{MUTED};font-size:52px"> / 16</span>', 84, sc.W("8.3", "twelve") + 0.6, w=300)
    sc.js.append(fade_out(f"#{sc.cid}-bt{sc.n}", sc.T("8.4") - 0.15))
    # joint top scorers: three piles of ten
    tp = panel(sc, f'<div class="oswald" style="position:absolute;left:140px;top:160px;font-size:52px">JOINT TOP SCORERS, 2014/15</div>'
                   f'<div class="src" style="left:140px;top:905px">Champions League goals · Source: UEFA</div>', sc.T("8.4") - 0.1, sc.T("8.5") - 0.15)
    piles = Piles(sc, ["Messi", "Neymar", "Cristiano Ronaldo"], 560, 840, gapx=380, bs=40, colours={"Cristiano Ronaldo": "#6b7380"},
                  show=sc.T("8.4") - 0.1, hide=sc.T("8.5") - 0.15)
    for k in range(10):
        for j, n in enumerate(["Messi", "Neymar", "Cristiano Ronaldo"]):
            piles.add_goal(n, sc.W("8.4", "ten") - 0.6 + k * 0.08 + j * 0.03, from_xy=(piles.x[n], 100))
    for el in [f"{piles.i}-{n}" for n in ("messi", "neymar", "cristianoronaldo")]:
        sc.js.append(f'tl.to("[id^={el}]", {{ opacity: 0, duration: 0.15 }}, {sc.T("8.5") - 0.15});')
    big_text(sc, 960, 300, f'2ND <span style="color:{ACCENT}">TREBLE</span>', 170, sc.W("8.5", "treble") - 0.2, anchor="center", w=1600, hit=True)
    tr = sc.cid + f"-bt{sc.n}"
    src(sc, 760, 520, "First European club to win the treble twice · Source: UEFA", sc.W("8.5", "first"))
    sc.js += [fade_out(f"#{tr}", sc.T("8.6") - 0.15), fade_out(f"#{sc.cid}-src{sc.n}", sc.T("8.6") - 0.15)]
    # Luis Enrique's bookend
    q = panel(sc, f'<div class="oswald" style="position:absolute;left:0;right:0;top:170px;text-align:center;font-size:60px;color:{MUTED}">“A TRANSITIONAL YEAR”</div>', sc.T("8.6"), sc.T("8.7") - 0.15)
    yrs = [("2015", "Barcelona", sc.W("8.6", "transitional")), ("2025", "PSG", sc.W("8.6", "twenty", 2) if True else 0), ("2026", "PSG", sc.W("8.6", "twenty", 4))]
    for k, (y, club, t) in enumerate(yrs):
        i = sc.uid("yr")
        sc.add(f'<div id="{i}" style="position:absolute;left:{260 + k * 520}px;top:380px;width:400px;opacity:0"><div class="oswald" style="font-size:150px;line-height:1;color:{ACCENT if k == 0 else INK}">{y}</div>'
               f'<div style="font:700 36px Inter;color:{MUTED}">{club}</div></div>',
               fade_in(f"#{i}", t, 0.3), fade_out(f"#{i}", sc.T("8.7") - 0.15))
        sc.sfx(t, "pop", 0.6)
    src(sc, 260, 640, "Luis Enrique, Champions League winner · Sources: UEFA, RFI, AP", sc.W("8.6", "Ten"))
    sc.js.append(fade_out(f"#{sc.cid}-src{sc.n}", sc.T("8.7") - 0.15))
    # the question
    big_text(sc, 960, 230, f'WAS THIS THE BEST <span style="color:{ACCENT}">FRONT THREE</span><br>THE CHAMPIONS LEAGUE HAS SEEN?', 86, sc.W("8.7", "Was"), anchor="center", w=1700)
    for k, (name, x) in enumerate([("Messi", 620), ("Neymar", 960), ("Suárez", 1300)]):
        i = sc.uid("mag")
        sc.add(f'<div id="{i}" style="position:absolute;left:{x - 60}px;top:500px;width:120px;opacity:0">'
               f'<div style="width:120px;height:120px;border-radius:50%;background:{TEAM_A};box-shadow:0 9px 0 #9e1020, 0 0 36px {TEAM_A}"></div>'
               f'<div style="margin-top:20px;text-align:center;font:700 34px Inter;color:{INK}">{name}</div></div>',
               f'tl.fromTo("#{i}", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "back.out(2)" }}, {round(sc.W("8.7", "front") + k * 0.15, 3)});')
    big_text(sc, 960, 720, "Tell me in the comments", 48, sc.W("8.7", "Tell"), anchor="center", color=ACCENT, w=1400)
    end_t = sc.E("8.7") + 1.2
    panel(sc, f'<div style="position:absolute;inset:0;background:#07080a"></div>'
              f'<div class="oswald" style="position:absolute;left:140px;top:380px;font-size:44px;color:{MUTED};letter-spacing:.08em">RUN OF THE CHAMPIONS</div>'
              f'<div class="oswald" style="position:absolute;left:140px;top:440px;font-size:130px">NEXT: <span style="color:{ACCENT}">2015/16</span></div>', end_t)
    sc.sfx(end_t, "whoosh2", 0.8)
    p = sc.pip(1780, 930, 1.15, -1)
    sc.js += [f'Pip.arm("{p}", "R", -60, {sc.W("8.1", "Thirteen")});', f'Pip.arm("{p}", "R", -80, {sc.W("8.1", "Eleven")});',
              f'Pip.arm("{p}", "R", -60, {sc.W("8.2", "Thirty")});', f'Pip.arm("{p}", "R", 0, {sc.E("8.2")});',
              f'Pip.mood("{p}", "happy", "smile", {sc.T("8.2b") + 0.5});', f'Pip.mood("{p}", "normal", "smile", {sc.T("8.3")});',
              f'Pip.arm("{p}", "L", 70, {sc.W("8.3", "twelve")});', f'Pip.arm("{p}", "L", 0, {sc.E("8.3")});',
              f'Pip.mood("{p}", "closed", "smile", {sc.W("8.4", "ten")});', f'Pip.mood("{p}", "normal", "smile", {sc.E("8.4")});',
              f'Pip.mood("{p}", "wide", "flat", {sc.T("8.4b") + 0.3});', f'Pip.brows("{p}", 14, -6, {sc.T("8.4b") + 0.4});', f'Pip.look("{p}", -2, 2, {sc.T("8.4b") + 0.4});',
              f'Pip.brows("{p}", 0, 0, {sc.T("8.5")});', f'Pip.mood("{p}", "happy", "grin", {sc.W("8.5", "treble")});', f'Pip.jump("{p}", {sc.W("8.5", "treble") + 0.1}, 50);',
              f'Pip.mood("{p}", "normal", "smile", {sc.T("8.6")});', f'Pip.look("{p}", 0, 3, {sc.W("8.6", "Ten")});',
              f'Pip.move("{p}", 1500, 930, {sc.T("8.7") - 0.1}, 0.5);', f'Pip.arm("{p}", "R", -90, {sc.W("8.7", "Tell")});', f'Pip.look("{p}", 0, 4, {sc.W("8.7", "Tell")});',
              f'Pip.mood("{p}", "happy", "grin", {end_t});', f'Pip.arm("{p}", "R", -150, {end_t + 0.3});', f'Pip.arm("{p}", "R", -110, {end_t + 0.7});', f'Pip.arm("{p}", "R", -150, {end_t + 1.1});']
    return sc


CHAPTERS = [c0, c1, c2, c3, c4, c5, c6, c7, c8]
