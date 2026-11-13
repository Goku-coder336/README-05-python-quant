"""Writes index.html and the scene files in compositions/ from one source.

Run: python3 build.py
Stage 1 (now): a 6 s look-development cut for the 3 approval stills.
"""
from pathlib import Path

import os

from characters import PARTNER_PIVOTS, TEACHER_PIVOTS, TEACHERS, partner

# Which teacher design to use (see ../../character.md). Default: A.
teacher = TEACHERS[os.environ.get("TEACHER", "A")]

ROOT = Path(__file__).parent
W, H = 1080, 1920

FONT_CSS = """
  font-family: 'Montserrat', sans-serif;
"""

# ------------------------------------------------------------------ lesson ---
LESSON_DUR = 4.0


def lesson():
    t = teacher("les-t")
    pv = TEACHER_PIVOTS
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #f4ead8; {FONT_CSS} }}
    #les-glow {{ position: absolute; left: 160px; top: 760px; width: 760px; height: 760px; border-radius: 50%; background: #efdcbc; }}
    #les-floor {{ position: absolute; left: 0; right: 0; top: 1470px; bottom: 0; background: #e6d1ad; border-top: 6px solid #1d1d1b; }}
    #les-tag {{ position: absolute; top: 154px; left: 50%; margin-left: -170px; width: 340px; height: 64px; border-radius: 32px;
               background: #1d1d1b; color: #f4ead8; font-weight: 700; font-size: 30px; letter-spacing: 0.08em;
               display: flex; align-items: center; justify-content: center; }}
    .les-label {{ position: absolute; top: 330px; left: 0; right: 0; display: flex; justify-content: center; }}
    .les-label span {{ padding: 10px 26px; border-radius: 26px; font-weight: 800; font-size: 32px; letter-spacing: 0.12em;
                      border: 5px solid #1d1d1b; }}
    .les-word {{ position: absolute; top: 400px; left: 40px; right: 40px; text-align: center; color: #1d1d1b;
                font-weight: 800; line-height: 1.02; }}
    #les-teacher-wrap {{ position: absolute; left: 240px; top: 760px; width: 600px; height: 900px; }}
    #les-teacher-wrap svg {{ width: 100%; height: 100%; }}
    #les-lectern {{ position: absolute; left: 330px; top: 1340px; width: 420px; height: 380px; }}
  </style>
  <div id="root" data-composition-id="lesson" data-width="{W}" data-height="{H}">
    <div id="les-glow"></div>
    <div id="les-floor"></div>
    <div id="les-teacher-wrap">{t}</div>
    <svg id="les-lectern" viewBox="0 0 420 380" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 10 L410 10 L380 60 L40 60 Z" fill="#c98a52" stroke="#1d1d1b" stroke-width="6" stroke-linejoin="round"/>
      <path d="M60 60 L360 60 L330 370 L90 370 Z" fill="#b07a4a" stroke="#1d1d1b" stroke-width="6" stroke-linejoin="round"/>
      <path d="M120 120 L300 120" stroke="#8a5a32" stroke-width="6" stroke-linecap="round"/>
    </svg>
    <div id="les-tag">WORD SONG #01</div>

    <h1 id="les-hook" class="les-word clip" data-start="0" data-duration="2" style="font-size: 120px; top: 360px;">FRENCH<br>IS EASY</h1>

    <div id="les-lab-fr" class="les-label clip" data-start="2" data-duration="2"><span style="background:#3d6fd6;color:#fff;">FRENCH</span></div>
    <h1 id="les-w-chateau" class="les-word clip" data-start="2" data-duration="2" style="font-size: 132px; top: 420px;">CHÂTEAU</h1>
    <div id="les-cue" class="les-word clip" data-start="2" data-duration="2" style="font-size: 44px; top: 590px; color: #8c7652; font-weight: 700;">castle</div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const P = "les-t";
    // hook: confident, small nod, talking
    tl.fromTo("#les-hook", {{ scale: 0.86, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(1.6)" }}, 0);
    tl.set("#" + P + "-mouth-o", {{ opacity: 1 }}, 0.0);
    tl.set("#" + P + "-mouth-c", {{ opacity: 0 }}, 0.0);
    tl.to("#" + P + "-head", {{ rotation: -4, svgOrigin: "{pv['head']}", duration: 0.4, ease: "power2.out" }}, 0.2);
    tl.set("#" + P + "-mouth-o", {{ opacity: 0 }}, 1.6);
    tl.set("#" + P + "-mouth-c", {{ opacity: 1 }}, 1.6);
    // château: right arm and pointer up, one brow raised
    tl.fromTo("#les-w-chateau", {{ scale: 0.7, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }}, 2.0);
    tl.fromTo("#" + P + "-arm-r", {{ rotation: 0 }}, {{ rotation: -150, svgOrigin: "{pv['arm-r']}", duration: 0.35, ease: "back.out(1.8)" }}, 2.0);
    tl.fromTo("#" + P + "-brow-r", {{ y: 0 }}, {{ y: -22, duration: 0.2, ease: "power3.out" }}, 2.2);
    tl.to("#" + P + "-head", {{ rotation: 5, svgOrigin: "{pv['head']}", duration: 0.35, ease: "power2.out" }}, 2.0);
    window.__timelines["lesson"] = tl;
  </script>
</template>
"""


# ------------------------------------------------------------------ payoff ---
PAYOFF_DUR = 2.0


def payoff():
    a = teacher("pay-t")
    b = partner("pay-p")
    tp, pp = TEACHER_PIVOTS, PARTNER_PIVOTS
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #2b1d4f; {FONT_CSS} }}
    #pay-tint {{ position: absolute; inset: 0; background: #7a2e8c; opacity: 0; }}
    #pay-spot {{ position: absolute; left: 40px; top: 1330px; width: 900px; height: 260px; border-radius: 50%; background: #4a3580; }}
    #pay-floor {{ position: absolute; left: 0; right: 0; top: 1440px; bottom: 0; background: #1d1436; border-top: 6px solid #1d1d1b; }}
    #pay-tag {{ position: absolute; top: 154px; left: 50%; margin-left: -170px; width: 340px; height: 64px; border-radius: 32px;
               background: #ffd23f; color: #1d1d1b; font-weight: 700; font-size: 30px; letter-spacing: 0.08em;
               display: flex; align-items: center; justify-content: center; }}
    .pay-line {{ position: absolute; left: 50px; right: 50px; text-align: center; color: #fffdf6; font-weight: 800; line-height: 1.05; }}
    .pay-trans {{ position: absolute; left: 60px; right: 60px; text-align: center; color: #f4d9a8; font-weight: 600; }}
    #pay-t-wrap {{ position: absolute; left: 20px; top: 780px; width: 450px; height: 675px; }}
    #pay-p-wrap {{ position: absolute; left: 560px; top: 780px; width: 412px; height: 675px; }}
    #pay-t-wrap svg, #pay-p-wrap svg {{ width: 100%; height: 100%; }}
    #pay-mic {{ position: absolute; left: 445px; top: 680px; width: 150px; height: 450px; }}
  </style>
  <div id="root" data-composition-id="payoff" data-width="{W}" data-height="{H}">
    <div id="pay-tint"></div>
    <div id="pay-spot"></div>
    <div id="pay-floor"></div>
    <svg id="pay-mic" viewBox="0 0 140 420" xmlns="http://www.w3.org/2000/svg">
      <path d="M70 0 L70 250" stroke="#1d1d1b" stroke-width="8"/>
      <rect x="40" y="250" width="60" height="110" rx="30" fill="#c9ccd6" stroke="#1d1d1b" stroke-width="6"/>
      <path d="M44 290 L96 290 M44 315 L96 315" stroke="#1d1d1b" stroke-width="4"/>
      <rect x="56" y="356" width="28" height="56" rx="10" fill="#3a3f55" stroke="#1d1d1b" stroke-width="6"/>
    </svg>
    <div id="pay-t-wrap">{a}</div>
    <div id="pay-p-wrap">{b}</div>
    <div id="pay-tag">NOW TRY THIS</div>
    <h1 id="pay-l1" class="pay-line clip" data-start="0" data-duration="2" style="font-size: 92px; top: 340px;">Le bel oiseau<br>au chapeau,</h1>
    <div id="pay-l1t" class="pay-trans clip" data-start="0" data-duration="2" style="font-size: 40px; top: 560px;">The fine bird in a hat,</div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#pay-l1", {{ scale: 0.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }}, 0);
    tl.fromTo("#pay-l1t", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2 }}, 0.15);
    // background flips tint on the beat (105 BPM: 0.571 s a beat)
    tl.set("#pay-tint", {{ opacity: 0.55 }}, 0.571);
    tl.set("#pay-tint", {{ opacity: 0 }}, 1.143);
    tl.set("#pay-tint", {{ opacity: 0.55 }}, 1.714);
    // both performing: mouths open, arms out, heads tilted toward the mic
    tl.set(["#pay-t-mouth-o", "#pay-p-mouth-o"], {{ opacity: 1 }}, 0);
    tl.set(["#pay-t-mouth-c", "#pay-p-mouth-c"], {{ opacity: 0 }}, 0);
    tl.fromTo("#pay-t-arm-l", {{ rotation: 0 }}, {{ rotation: 150, svgOrigin: "{tp['arm-l']}", duration: 0.3, ease: "back.out(2)" }}, 0);
    tl.fromTo("#pay-t-arm-r", {{ rotation: 0 }}, {{ rotation: -25, svgOrigin: "{tp['arm-r']}", duration: 0.3, ease: "back.out(2)" }}, 0.05);
    tl.fromTo("#pay-t-head", {{ rotation: 0 }}, {{ rotation: 7, svgOrigin: "{tp['head']}", duration: 0.3 }}, 0);
    tl.fromTo("#pay-p-arm-l", {{ rotation: 0 }}, {{ rotation: 60, svgOrigin: "{pp['arm-l']}", duration: 0.3, ease: "back.out(2)" }}, 0.08);
    tl.fromTo("#pay-p-arm-r", {{ rotation: 0 }}, {{ rotation: -110, svgOrigin: "{pp['arm-r']}", duration: 0.3, ease: "back.out(2)" }}, 0.03);
    tl.fromTo("#pay-p-head", {{ rotation: 0 }}, {{ rotation: -8, svgOrigin: "{pp['head']}", duration: 0.3 }}, 0);
    tl.fromTo("#pay-p-brow-l", {{ y: 0 }}, {{ y: -14, duration: 0.2 }}, 0.1);
    tl.fromTo("#pay-p-brow-r", {{ y: 0 }}, {{ y: -14, duration: 0.2 }}, 0.12);
    window.__timelines["payoff"] = tl;
  </script>
</template>
"""


def index(total):
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
      <div id="lesson" data-composition-id="lesson" data-composition-src="compositions/lesson.html"
           data-start="0" data-duration="{LESSON_DUR}" data-track-index="1" data-track-kind="graphics"
           data-width="{W}" data-height="{H}"></div>
      <div id="payoff" data-composition-id="payoff" data-composition-src="compositions/payoff.html"
           data-start="{LESSON_DUR}" data-duration="{PAYOFF_DUR}" data-track-index="1" data-track-kind="graphics"
           data-width="{W}" data-height="{H}"></div>
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
    (ROOT / "index.html").write_text(index(LESSON_DUR + PAYOFF_DUR))
    print("wrote index.html, compositions/lesson.html, compositions/payoff.html")
