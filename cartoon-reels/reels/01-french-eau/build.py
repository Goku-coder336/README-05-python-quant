"""Writes index.html and the scene files in compositions/ from timeline.json.

Run: python3 timeline.py && python3 audio.py && python3 build.py
TEACHER=B or TEACHER=C swaps in another teacher design (see ../../character.md).
"""
import json
import os
from pathlib import Path

from characters import PARTNER_PIVOTS, TEACHER_PIVOTS, TEACHERS, partner

ROOT = Path(__file__).parent
W, H = 1080, 1920
from variant import AUDIO, TIMELINE

T = json.loads(TIMELINE.read_text())
teacher = TEACHERS[os.environ.get("TEACHER", "A")]
TP, PP = TEACHER_PIVOTS, PARTNER_PIVOTS

P0 = T["payoff"]["start"]
P1 = T["payoff"]["end"]
B0 = T["button"]["start"]
TOTAL = round(T["total"], 3)
SONG_WORDS = json.loads((AUDIO / "song.json").read_text())["words"]

FONT = "font-family: 'Montserrat', sans-serif;"
INK = "#1d1d1b"


def r(x):
    return round(x, 3)


# ------------------------------------------------------------- shared acting ---
def flaps_js(prefix, who, offset, until):
    """Mouth open/closed keys from the voice lines of one speaker, in local time."""
    out = []
    for v in T["voice"]:
        if v["who"] != who or not (offset - 1e-6 <= v["t"] < until):
            continue
        for k, state in v["flaps"]:
            t = r(v["t"] - offset + k)
            out.append(f'tl.set("#{prefix}-mouth-o", {{opacity: {state}}}, {t});'
                       f'tl.set("#{prefix}-mouth-c", {{opacity: {1 - state}}}, {t});')
    return "\n    ".join(out)


def blinks_js(prefix, dur, first=1.1, every=(2.3, 2.9, 2.5)):
    pivots = TP if prefix.endswith("-t") else PP
    out, t, i = [], first, 0
    while t < dur - 0.2:
        for eye in ("eye-l", "eye-r"):
            out.append(f'tl.to("#{prefix}-{eye}", {{scaleY: 0.1, svgOrigin: "{pivots[eye]}", duration: 0.05}}, {r(t)});'
                       f'tl.to("#{prefix}-{eye}", {{scaleY: 1, svgOrigin: "{pivots[eye]}", duration: 0.07}}, {r(t + 0.1)});')
        t += every[i % len(every)]
        i += 1
    return "\n    ".join(out)


def breath_js(prefix, origin, dur, period=3.0, amount=0.015):
    n = int(dur / period)
    if n < 1:
        return ""
    return (f'tl.fromTo("#{prefix}-body", {{scaleY: 1}}, {{scaleY: {1 + amount}, svgOrigin: "{origin}", '
            f'duration: {period / 2}, ease: "sine.inOut", yoyo: true, repeat: {2 * n - 1}}}, 0);')


# ------------------------------------------------------------------ lesson ---
LESSON_CSS = f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #f4ead8; {FONT} }}
    .set-glow {{ position: absolute; left: 160px; top: 760px; width: 760px; height: 760px; border-radius: 50%; background: #efdcbc; }}
    .set-floor {{ position: absolute; left: 0; right: 0; top: 1470px; bottom: 0; background: #e6d1ad; border-top: 6px solid {INK}; }}
    .set-tag {{ position: absolute; top: 154px; left: 50%; margin-left: -170px; width: 340px; height: 64px; border-radius: 32px;
               background: {INK}; color: #f4ead8; font-weight: 700; font-size: 30px; letter-spacing: 0.08em;
               display: flex; align-items: center; justify-content: center; }}
    .label {{ position: absolute; top: 330px; left: 0; right: 0; display: flex; justify-content: center; }}
    .label span {{ padding: 10px 26px; border-radius: 26px; font-weight: 800; font-size: 32px; letter-spacing: 0.12em; border: 5px solid {INK}; }}
    .lab-en span {{ background: #e3cfa9; color: {INK}; }}
    .lab-fr span {{ background: #3d6fd6; color: #fff; }}
    .lab-gag span {{ background: #ffd23f; color: {INK}; }}
    .word {{ position: absolute; left: 40px; right: 40px; text-align: center; color: {INK}; font-weight: 800; line-height: 1.02; }}
    .cue {{ position: absolute; top: 590px; left: 0; right: 0; text-align: center; color: #8c7652; font-weight: 700; font-size: 44px; }}
    .teacher-wrap {{ position: absolute; left: 240px; top: 760px; width: 600px; height: 900px; }}
    .teacher-wrap svg {{ width: 100%; height: 100%; }}
    .lectern {{ position: absolute; left: 330px; top: 1340px; width: 420px; height: 380px; }}
    .pupil-wrap {{ position: absolute; left: 600px; top: 905px; width: 380px; height: 623px; }}
    .pupil-wrap svg {{ width: 100%; height: 100%; }}
"""

DIALOGUE = T.get("dialogue", False)


def set_html(prefix, wrap):
    """The lesson set: the teacher at the lectern, and in dialogue reels Odette beside him asking."""
    if not DIALOGUE:
        return f'<div id="{wrap}" class="teacher-wrap">{teacher(prefix)}</div>\n    {LECTERN}'
    lectern = LECTERN.replace('class="lectern"', 'class="lectern" style="left: 110px;"')
    return (f'<div id="{wrap}" class="teacher-wrap" style="left: 20px;">{teacher(prefix)}</div>\n    {lectern}\n'
            f'    <div id="{prefix[:3]}-pupil-wrap" class="pupil-wrap">{partner(prefix[:3] + "-p")}</div>')


def pupil_js(q, dur):
    """Odette's life in the lesson set: she breathes, blinks and talks."""
    return "\n    ".join([flaps_js(q, "p", 0, dur), blinks_js(q, dur, 1.6, (2.7, 2.2)), breath_js(q, PP["body"], dur, 3.4)])

LECTERN = f"""<svg class="lectern" viewBox="0 0 420 380" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 10 L410 10 L380 60 L40 60 Z" fill="#c98a52" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
      <path d="M60 60 L360 60 L330 370 L90 370 Z" fill="#b07a4a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
      <path d="M120 120 L300 120" stroke="#8a5a32" stroke-width="6" stroke-linecap="round"/>
    </svg>"""


def gesture_js(p, wrap, g, t):
    if g == "point":
        return (f'tl.to("#{p}-arm-r", {{rotation: -150, svgOrigin: "{TP["arm-r"]}", duration: 0.25, ease: "back.out(2)"}}, {r(t - 0.05)});'
                f'tl.to("#{p}-arm-r", {{rotation: 0, svgOrigin: "{TP["arm-r"]}", duration: 0.3, ease: "power2.inOut"}}, {r(t + 0.75)});'
                f'tl.to("#{p}-brow-r", {{y: -20, duration: 0.15}}, {r(t)});tl.to("#{p}-brow-r", {{y: 0, duration: 0.2}}, {r(t + 0.8)});')
    if g == "tap":
        return (f'tl.to("#{p}-arm-r", {{rotation: -168, svgOrigin: "{TP["arm-r"]}", duration: 0.22, ease: "back.out(1.6)"}}, {r(t - 0.05)});'
                f'tl.to("#{p}-head", {{rotation: -3, svgOrigin: "{TP["head"]}", duration: 0.1, yoyo: true, repeat: 1}}, {r(t + 0.15)});'
                f'tl.to("#{p}-arm-r", {{rotation: 0, svgOrigin: "{TP["arm-r"]}", duration: 0.3}}, {r(t + 0.7)});')
    if g in ("hop", "bighop"):
        h = 46 if g == "bighop" else 26
        extra = (f'tl.to("#{p}-brow-l", {{y: -16, duration: 0.12}}, {r(t)});tl.to("#{p}-brow-l", {{y: 0, duration: 0.2}}, {r(t + 0.7)});'
                 if g == "bighop" else "")
        return (f'tl.to("#{wrap}", {{y: -{h}, duration: 0.14, ease: "power2.out"}}, {r(t)});'
                f'tl.to("#{wrap}", {{y: 0, duration: 0.22, ease: "bounce.out"}}, {r(t + 0.14)});' + extra)
    if g == "tilt":
        return (f'tl.to("#{p}-head", {{rotation: 8, svgOrigin: "{TP["head"]}", duration: 0.2, ease: "back.out(2)"}}, {r(t)});'
                f'tl.to("#{p}-head", {{rotation: 0, svgOrigin: "{TP["head"]}", duration: 0.3}}, {r(t + 0.7)});')
    return ""


def lesson():
    p, wrap = "les-t", "les-teacher-wrap"
    dur = P0
    html, js = [], []
    html.append(f'<h1 id="les-hook" class="word clip" data-start="0" data-duration="{r(T["hook"]["end"])}" '
                f'style="font-size: 120px; top: 360px;">FRENCH<br>IS EASY</h1>')
    js.append(f'tl.to("#{p}-head", {{rotation: -4, svgOrigin: "{TP["head"]}", duration: 0.3}}, 0.15);'
              f'tl.to("#{p}-head", {{rotation: 0, svgOrigin: "{TP["head"]}", duration: 0.3}}, {r(T["hook"]["end"] - 0.3)});')
    if DIALOGUE:
        q = "les-p"
        js.append(f'tl.to("#{q}-brow-l", {{y: -18, duration: 0.2}}, 0.4);tl.to("#{q}-brow-l", {{y: 0, duration: 0.2}}, {r(T["hook"]["end"])});')
        js.append(f'tl.to("#{q}-head", {{rotation: -6, svgOrigin: "{PP["head"]}", duration: 0.4}}, {r(T["hook"]["end"])});')
        for it in T["items"]:
            if it["kind"] == "same":
                oh = it["start"] + 0.35  # when she says "Oh!"
                js.append(f'tl.to("#les-pupil-wrap", {{y: -36, duration: 0.14, ease: "power2.out"}}, {r(oh)});'
                          f'tl.to("#les-pupil-wrap", {{y: 0, duration: 0.25, ease: "bounce.out"}}, {r(oh + 0.14)});'
                          f'tl.to(["#{q}-brow-l", "#{q}-brow-r"], {{y: -22, duration: 0.12}}, {r(oh)});'
                          f'tl.to(["#{q}-brow-l", "#{q}-brow-r"], {{y: 0, duration: 0.25}}, {r(it["end"] - 0.2)});')
                continue
            # she gestures towards him with the arm on his side
            js.append(f'tl.to("#{q}-arm-l", {{rotation: 70, svgOrigin: "{PP["arm-l"]}", duration: 0.2, ease: "back.out(2)"}}, {it["start"]});'
                      f'tl.to("#{q}-arm-l", {{rotation: 0, svgOrigin: "{PP["arm-l"]}", duration: 0.25}}, {r(it["answer"])});')
        js.append(pupil_js(q, dur))
    for i, it in enumerate(T["items"]):
        s, e = it["start"], it["end"]
        if it["kind"] == "same":
            html.append(f'<div id="les-gag-lab" class="label lab-gag clip" data-start="{s}" data-duration="{r(e - s)}"><span>SPOT THE DIFFERENCE</span></div>')
            html.append(f'<h1 id="les-gag" class="word clip" data-start="{s}" data-duration="{r(e - s)}" style="font-size: 96px; top: 410px;">EAU<br>HAUT<br>OH</h1>')
            js.append(f'tl.fromTo("#les-gag", {{opacity: 0, y: 20}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}}, {s});')
            js.append(f'tl.to("#{p}-brow-r", {{y: -26, duration: 0.18, ease: "power3.out"}}, {r(it["say"] - 0.2)});'
                      f'tl.to("#{p}-brow-r", {{y: 0, duration: 0.25}}, {r(e - 0.25)});')
            continue
        a = it["answer"]
        first = DIALOGUE and i == 0
        html.append(f'<div id="les-en-{i}" class="label lab-en clip" data-start="{s}" data-duration="{r(a - s)}"><span>{"HOW DO YOU SAY" if first else "ENGLISH"}</span></div>')
        html.append(f'<h1 id="les-cw-{i}" class="word clip" data-start="{s}" data-duration="{r(a - s)}" style="font-size: 110px; top: 420px; color: #8c7652;">{it["cue"]}</h1>')
        html.append(f'<div id="les-fr-{i}" class="label lab-fr clip" data-start="{a}" data-duration="{r(e - a)}"><span>FRENCH</span></div>')
        size = 132 if len(it["word"]) <= 7 else 120
        html.append(f'<h1 id="les-w-{i}" class="word clip" data-start="{a}" data-duration="{r(e - a)}" style="font-size: {size}px; top: 420px;">{it["word"]}</h1>')
        html.append(f'<div id="les-c-{i}" class="cue clip" data-start="{a}" data-duration="{r(e - a)}">{it["cue"]}</div>')
        js.append(f'tl.fromTo("#les-cw-{i}", {{opacity: 0}}, {{opacity: 1, duration: 0.12}}, {s});')
        if it["gesture"] in ("hop", "bighop", "tap"):
            js.append(f'tl.fromTo("#les-w-{i}", {{scale: 0.6, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.32, ease: "back.out(2.4)"}}, {a});')
        else:
            js.append(f'tl.fromTo("#les-w-{i}", {{opacity: 0, filter: "blur(6px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power3.out"}}, {a});')
        js.append(gesture_js(p, wrap, it["gesture"], a))
    ts = T["try"]["start"]
    e0 = T["english"][0]["start"]
    html.append(f'<h1 id="les-try" class="word clip" data-start="{ts}" data-duration="{r(e0 - ts)}" style="font-size: 110px; top: 400px;">NOW<br>TRY THIS</h1>')
    js.append(f'tl.fromTo("#les-try", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power3.out"}}, {ts});')
    js.append(f'tl.to("#{wrap}", {{y: -18, scale: 1.04, transformOrigin: "50% 100%", duration: 0.5, ease: "power2.inOut"}}, {ts});')
    # the whole sentence in English, one phrase at a time
    en_end = T["english"][-1]["end"]
    html.append(f'<div id="les-en-lab" class="label lab-en clip" data-start="{e0}" data-duration="{r(en_end - e0)}"><span>IN ENGLISH</span></div>')
    for j, e in enumerate(T["english"]):
        html.append(f'<h1 id="les-en-{j}-t" class="word clip" data-start="{e["start"]}" data-duration="{r(e["end"] - e["start"])}" style="font-size: 92px; top: 410px;">{e["text"]}</h1>')
        js.append(f'tl.fromTo("#les-en-{j}-t", {{opacity: 0, filter: "blur(6px)"}}, {{opacity: 1, filter: "blur(0px)", duration: 0.15, ease: "power3.out"}}, {e["start"]});')
    js.append(f'tl.to("#{p}-head", {{rotation: 4, svgOrigin: "{TP["head"]}", duration: 0.4}}, {e0});')
    # count-in: the song's lead-in bar; he lifts the pointer like a conductor and drops it on the cut
    ci = T["count_in"]
    if ci["end"] - ci["start"] > 0.3:
        html.append(f'<div id="les-ci-lab" class="label lab-fr clip" data-start="{ci["start"]}" data-duration="{r(ci["end"] - ci["start"])}"><span>NOW IN FRENCH</span></div>')
        html.append(f'<h1 id="les-ci" class="word clip" data-start="{ci["start"]}" data-duration="{r(ci["end"] - ci["start"])}" style="font-size: 130px; top: 420px;">1, 2, 3…</h1>')
        js.append(f'tl.fromTo("#les-ci", {{scale: 0.7, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)"}}, {ci["start"]});')
        js.append(f'tl.to("#{p}-arm-r", {{rotation: -160, svgOrigin: "{TP["arm-r"]}", duration: 0.3, ease: "back.out(1.6)"}}, {ci["start"]});')
        js.append(f'tl.to("#{p}-brow-r", {{y: -24, duration: 0.2}}, {ci["start"]});')
        js.append(f'tl.to("#{p}-head", {{rotation: 0, svgOrigin: "{TP["head"]}", duration: 0.3}}, {ci["start"]});')
        js.append(f'tl.to("#{p}-arm-r", {{rotation: -60, svgOrigin: "{TP["arm-r"]}", duration: 0.15, ease: "power3.in"}}, {r(ci["end"] - 0.17)});')
    js.append(flaps_js(p, "t", 0, dur))
    js.append(blinks_js(p, dur))
    js.append(breath_js(p, TP["body"], dur))
    body = "\n    ".join(html)
    script = "\n    ".join(js)
    return f"""<template>
  <style>{LESSON_CSS}
  </style>
  <div id="root" data-composition-id="lesson" data-width="{W}" data-height="{H}">
    <div class="set-glow"></div>
    <div class="set-floor"></div>
    {set_html(p, wrap)}
    <div class="set-tag">WORD SONG #01</div>
    {body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {script}
    window.__timelines["lesson"] = tl;
  </script>
</template>
"""


# ------------------------------------------------------------------ payoff ---
def payoff():
    dur = r(P1 - P0)
    html, js = [], []
    lines = T["payoff"]["lines"]
    for i, ln in enumerate(lines):
        s = r(ln["start"] - P0)
        e = r((lines[i + 1]["start"] - P0 if i + 1 < len(lines) else dur) - s)
        size = 92 if i != 2 else 84
        html.append(f'<h1 id="pay-l{i}" class="line clip" data-start="{s}" data-duration="{e}" style="font-size: {size}px;">{ln["fr"]}</h1>')
        nlines = ln["fr"].count("<br>") + 1
        ty = 300 + round(nlines * size * 1.05) + 28  # right under the lyric
        html.append(f'<div id="pay-e{i}" class="trans clip" data-start="{s}" data-duration="{e}" style="top: {ty}px;">{ln["en"]}</div>')
        js.append(f'tl.fromTo("#pay-l{i}", {{scale: 0.7, opacity: 0}}, {{scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2.2)"}}, {s});')
        js.append(f'tl.fromTo("#pay-e{i}", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {r(s + 0.12)});')
    splash = r(T["payoff"]["splash"] - P0)
    # the background flips tint and both characters bounce on every sung word, so they move with the song
    sung = [w for w in SONG_WORDS if P0 - 0.05 <= w["start"] < T["payoff"]["splash"] - 0.05]
    last = -1.0
    for k, w in enumerate(sung):
        t = r(max(0, w["start"] - P0))
        js.append(f'tl.set("#pay-tint", {{opacity: {0.55 if k % 2 else 0}}}, {t});')
        if t - last >= 0.3:
            js.append(f'tl.to(["#pay-t-wrap", "#pay-p-wrap"], {{y: -16, duration: 0.12, ease: "power2.out"}}, {t});'
                      f'tl.to(["#pay-t-wrap", "#pay-p-wrap"], {{y: 0, duration: 0.15, ease: "power2.in"}}, {r(t + 0.13)});')
            last = t
    poses = [(150, -25, 60, -110), (40, -140, 120, -40), (125, -125, 115, -115)]
    for i in range(3):
        t = r(lines[i]["start"] - P0)
        tl_, tr_, pl_, pr_ = poses[i]
        js.append(f'tl.to("#pay-t-arm-l", {{rotation: {tl_}, svgOrigin: "{TP["arm-l"]}", duration: 0.2, ease: "back.out(2)"}}, {t});'
                  f'tl.to("#pay-t-arm-r", {{rotation: {tr_}, svgOrigin: "{TP["arm-r"]}", duration: 0.2, ease: "back.out(2)"}}, {r(t + 0.04)});'
                  f'tl.to("#pay-p-arm-l", {{rotation: {pl_}, svgOrigin: "{PP["arm-l"]}", duration: 0.2, ease: "back.out(2)"}}, {r(t + 0.02)});'
                  f'tl.to("#pay-p-arm-r", {{rotation: {pr_}, svgOrigin: "{PP["arm-r"]}", duration: 0.2, ease: "back.out(2)"}}, {r(t + 0.06)});')
    js.append(f'tl.to("#pay-t-head", {{rotation: 7, svgOrigin: "{TP["head"]}", duration: 0.3}}, 0);')
    js.append(f'tl.to("#pay-p-head", {{rotation: -8, svgOrigin: "{PP["head"]}", duration: 0.3}}, 0);')
    js.append('tl.to(["#pay-p-brow-l", "#pay-p-brow-r"], {y: -14, duration: 0.2}, 0.1);')
    # the laugh on "l'eau": both drop as if into the water, the splash bursts up, the screen shakes
    js.append(f'tl.set("#pay-tint", {{opacity: 0}}, {r(splash - 0.05)});')
    js.append(f'tl.to(["#pay-t-wrap", "#pay-p-wrap"], {{y: 140, duration: 0.25, ease: "power3.in"}}, {r(splash - 0.2)});')
    # set() then to(): a fromTo would apply its start state from the first frame
    js.append(f'tl.set("#pay-water", {{scaleY: 0, opacity: 1, transformOrigin: "50% 100%"}}, {r(splash - 0.01)});'
              f'tl.to("#pay-water", {{scaleY: 1, duration: 0.25, ease: "back.out(2)"}}, {splash});')
    js.append(f'tl.set("#pay-flash", {{opacity: 0.8}}, {splash});tl.to("#pay-flash", {{opacity: 0, duration: 0.3}}, {r(splash + 0.02)});')
    js.append(f'tl.set("#pay-shake", {{x: -18}}, {splash});tl.to("#pay-shake", {{x: 0, duration: 0.4, ease: "elastic.out(1, 0.3)"}}, {r(splash + 0.02)});')
    # both sing: mouths follow the sung words
    for who in ("pay-t", "pay-p"):
        for k, st in T["payoff"]["flaps"]:
            if 0 <= k < dur:
                js.append(f'tl.set("#{who}-mouth-o", {{opacity: {st}}}, {k});tl.set("#{who}-mouth-c", {{opacity: {1 - st}}}, {k});')
    js.append(blinks_js("pay-t", dur, 0.9))
    js.append(blinks_js("pay-p", dur, 1.6, (2.7, 2.2)))
    body = "\n    ".join(html)
    script = "\n    ".join(js)
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #2b1d4f; {FONT} }}
    #pay-shake {{ position: absolute; inset: 0; }}
    #pay-tint {{ position: absolute; inset: 0; background: #7a2e8c; opacity: 0; }}
    #pay-spot {{ position: absolute; left: 40px; top: 1330px; width: 900px; height: 260px; border-radius: 50%; background: #4a3580; }}
    #pay-floor {{ position: absolute; left: 0; right: 0; top: 1440px; bottom: 0; background: #1d1436; border-top: 6px solid {INK}; }}
    #pay-tag {{ position: absolute; top: 154px; left: 50%; margin-left: -170px; width: 340px; height: 64px; border-radius: 32px;
               background: #ffd23f; color: {INK}; font-weight: 700; font-size: 30px; letter-spacing: 0.08em;
               display: flex; align-items: center; justify-content: center; }}
    .line {{ position: absolute; top: 300px; left: 50px; right: 50px; text-align: center; color: #fffdf6; font-weight: 800; line-height: 1.05; }}
    .trans {{ position: absolute; top: 620px; left: 60px; right: 60px; text-align: center; color: #f4d9a8; font-weight: 600; font-size: 40px; }}
    #pay-t-wrap {{ position: absolute; left: 20px; top: 780px; width: 450px; height: 675px; }}
    #pay-p-wrap {{ position: absolute; left: 560px; top: 780px; width: 412px; height: 675px; }}
    #pay-t-wrap svg, #pay-p-wrap svg {{ width: 100%; height: 100%; }}
    #pay-mic {{ position: absolute; left: 445px; top: 690px; width: 150px; height: 450px; }}
    #pay-water {{ position: absolute; left: 0; top: 1150px; width: 1080px; height: 420px; opacity: 0; }}
    #pay-flash {{ position: absolute; inset: 0; background: #fffdf6; opacity: 0; }}
  </style>
  <div id="root" data-composition-id="payoff" data-width="{W}" data-height="{H}">
    <div id="pay-shake" data-layout-allow-overflow>
      <div id="pay-tint"></div>
      <div id="pay-spot"></div>
      <div id="pay-floor"></div>
      <svg id="pay-mic" viewBox="0 0 140 420" xmlns="http://www.w3.org/2000/svg">
        <path d="M70 0 L70 250" stroke="{INK}" stroke-width="8"/>
        <rect x="40" y="250" width="60" height="110" rx="30" fill="#c9ccd6" stroke="{INK}" stroke-width="6"/>
        <path d="M44 290 L96 290 M44 315 L96 315" stroke="{INK}" stroke-width="4"/>
        <rect x="56" y="356" width="28" height="56" rx="10" fill="#3a3f55" stroke="{INK}" stroke-width="6"/>
      </svg>
      <div id="pay-t-wrap">{teacher("pay-t")}</div>
      <div id="pay-p-wrap">{partner("pay-p")}</div>
      <svg id="pay-water" viewBox="0 0 1080 420" xmlns="http://www.w3.org/2000/svg" overflow="visible">
        <path d="M0 420 L0 250 Q90 120 150 230 Q200 40 270 210 Q330 90 390 220 Q450 0 540 190 Q630 10 690 220 Q760 70 810 210 Q880 30 930 230 Q1000 110 1080 240 L1080 420 Z" fill="#3fa9e0" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>
        <path d="M0 420 L0 320 Q140 260 270 320 Q400 270 540 320 Q680 270 810 320 Q950 270 1080 320 L1080 420 Z" fill="#2b86c4"/>
        <circle cx="200" cy="80" r="22" fill="#3fa9e0" stroke="{INK}" stroke-width="5"/>
        <circle cx="560" cy="-30" r="26" fill="#3fa9e0" stroke="{INK}" stroke-width="5"/>
        <circle cx="880" cy="60" r="20" fill="#3fa9e0" stroke="{INK}" stroke-width="5"/>
        <circle cx="400" cy="40" r="14" fill="#3fa9e0" stroke="{INK}" stroke-width="5"/>
        <circle cx="720" cy="50" r="16" fill="#3fa9e0" stroke="{INK}" stroke-width="5"/>
      </svg>
      <div id="pay-tag">SING ALONG</div>
      {body}
    </div>
    <div id="pay-flash"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {script}
    window.__timelines["payoff"] = tl;
  </script>
</template>
"""


# ------------------------------------------------------------------ button ---
def button():
    p, wrap = "btn-t", "btn-teacher-wrap"
    dur = r(TOTAL - B0)
    js = [
        'tl.fromTo("#btn-easy", {scale: 0.8, opacity: 0}, {scale: 1, opacity: 1, duration: 0.2, ease: "back.out(2)"}, 0.1);',
        'tl.fromTo("#btn-follow", {y: 20, opacity: 0}, {y: 0, opacity: 1, duration: 0.25, ease: "power3.out"}, 0.45);',
        f'tl.set("#{p}-brow-r", {{y: -26}}, 0);',
        flaps_js(p, "t", B0, TOTAL + 1),
    ]
    if DIALOGUE:
        js.append('tl.set(["#btn-p-brow-l", "#btn-p-brow-r"], {y: -20}, 0);')
        js.append(f'tl.set("#btn-p-head", {{rotation: -6, svgOrigin: "{PP["head"]}"}}, 0);')
    script = "\n    ".join(js)
    return f"""<template>
  <style>{LESSON_CSS}
    #btn-follow {{ position: absolute; top: 620px; left: 50%; margin-left: -290px; width: 580px; height: 76px; border-radius: 38px;
                  background: #3d6fd6; color: #fff; border: 5px solid {INK}; font-weight: 800; font-size: 34px;
                  display: flex; align-items: center; justify-content: center; }}
  </style>
  <div id="root" data-composition-id="button" data-width="{W}" data-height="{H}">
    <div class="set-glow"></div>
    <div class="set-floor"></div>
    {set_html(p, wrap)}
    <div class="set-tag">WORD SONG #01</div>
    <h1 id="btn-easy" class="word clip" data-start="0" data-duration="{dur}" style="font-size: 150px; top: 380px;">EASY.</h1>
    <div id="btn-follow" class="clip" data-start="0" data-duration="{dur}">Sing it in the comments</div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {script}
    window.__timelines["button"] = tl;
  </script>
</template>
"""


def index(mix="mix-music"):
    host = ('<div id="{id}" data-composition-id="{id}" data-composition-src="compositions/{id}.html" '
            'data-start="{s}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" '
            'data-width="%d" data-height="%d"></div>' % (W, H))
    scenes = "\n      ".join([
        host.format(id="lesson", s=0, d=r(P0)),
        host.format(id="payoff", s=r(P0), d=r(P1 - P0)),
        host.format(id="button", s=r(B0), d=r(TOTAL - B0)),
    ])
    return f"""<!doctype html>
<html lang="en-GB">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #f4ead8; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      {scenes}
      <audio id="mix" src="{AUDIO.relative_to(ROOT).as_posix()}/{mix}.wav" data-start="0" data-duration="{TOTAL}" data-track-index="2"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


if __name__ == "__main__":
    (ROOT / "compositions").mkdir(exist_ok=True)
    (ROOT / "compositions/lesson.html").write_text(lesson())
    (ROOT / "compositions/payoff.html").write_text(payoff())
    (ROOT / "compositions/button.html").write_text(button())
    (ROOT / "index.html").write_text(index())
    print(f"wrote scenes: lesson 0-{P0}, payoff {P0}-{P1}, button {B0}-{TOTAL}")
