"""Write index.html for the vertical 60-second reel "Road to the Treble" (1080x1920, HyperFrames).
Traced clips (from the user's own recordings) between kinetic text cards; the cup at the end is drawn.
Run from this folder: python build.py
"""
import json, math, random

random.seed(7)
caps = json.load(open("../assets/audio/reel/short_captions.json"))
# the last line reads better split at the full stop
caps = [c for c in caps if c[0] < 46.5] + [[46.7, 49.7, "Champions of Europe. The treble, again."],
                                            [49.7, 51.7, "Messi, Suárez and Neymar:"], [51.7, 54.9, "twenty-seven of Barcelona's thirty-one goals."]]

V = [  # id, file, start, duration, media start
    ("v0", "sf_messi_close.mp4", 0.0, 1.43, 0),
    ("v1", "r16_slow.mp4", 17.6, 2.5, 0),
    ("v2", "qf_suarez.mp4", 20.2, 6.2, 0),
    ("v3", "sf_messi_close.mp4", 27.6, 3.3, 0),
    ("v4", "final_celebration.mp4", 41.0, 0.79, 0),
]
CHIPS = [(15.8, 20.2, "ROUND OF 16"), (20.2, 27.6, "QUARTER-FINAL"), (27.6, 33.0, "SEMI-FINAL"), (8.6, 15.8, "GROUP STAGE"), (33.0, 46.0, "THE FINAL · BERLIN")]
TRACED = [(0.0, 1.43), (17.6, 20.1), (20.2, 26.4), (27.6, 30.9), (41.0, 41.79)]

els, js = [], []
def clip(i, start, dur, html, cls="card", track=3):
    els.append(f'<div id="{i}" class="{cls} clip" data-start="{start}" data-duration="{round(dur, 2)}" data-track-index="{track}">{html}</div>')
def slam(sel, t, d=0.28, s=1.6):
    js.append(f'tl.fromTo("{sel}", {{ scale: {s}, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: {d}, ease: "power4.out" }}, {t});')
def rise(sel, t, d=0.4):
    js.append(f'tl.fromTo("{sel}", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: {d}, ease: "power3.out" }}, {t});')
def shake(t):
    js.append(f'tl.fromTo("#cards", {{ x: -14 }}, {{ x: 0, duration: 0.25, ease: "elastic.out(1,0.3)" }}, {t});')
def flash(t):
    js.append(f'tl.fromTo("#flash", {{ opacity: 0.55 }}, {{ opacity: 0, duration: 0.35, immediateRender: false }}, {t});')

# ---------------------------------------------------------------- videos
for i, f, s, d, ms in V:
    els.append(f'<video id="{i}" class="vid clip" src="assets/clips/{f}" data-start="{s}" data-duration="{d}" data-media-start="{ms}" data-track-index="1" muted playsinline></video>')
    js.append(f'tl.fromTo("#{i}", {{ scale: 1.08 }}, {{ scale: 1, duration: {min(d, 1.2)}, ease: "power2.out" }}, {s});')
for k, (s, e) in enumerate(TRACED):
    clip(f"tr{k}", s, e - s, "Traced from match footage", "traced", 6)

# ---------------------------------------------------------------- the hook
clip("h0", 0.0, 1.43, '<div class="mega y">MSN</div><div class="lbl">Barcelona 2014/15</div>', "card over")
slam("#h0 .mega", 0.05)
clip("h1", 1.43, 1.57, '<div id="h1a" class="mega y">27 GOALS</div><div id="h1b" class="big">3 FORWARDS</div><div id="h1c" class="big r">1 TREBLE</div>')
slam("#h1a", 1.45); slam("#h1b", 1.85); slam("#h1c", 2.25); flash(1.43); shake(2.25)

# ---------------------------------------------------------------- the trio
clip("i0", 3.0, 5.6, '<div class="top">ROAD TO THE TREBLE</div><div class="sub">BARCELONA · CHAMPIONS LEAGUE 2014/15</div>'
     '<div class="names"><div id="n1" class="name">MESSI</div><div id="n2" class="name">SUÁREZ</div><div id="n3" class="name">NEYMAR</div></div>')
rise("#i0 .top", 3.05); rise("#i0 .sub", 3.3)
for k, t in enumerate([5.75, 6.55, 7.35]):
    slam(f"#n{k + 1}", t); shake(t)

# ---------------------------------------------------------------- group stage
balls = "".join(f'<div id="gb{k}" class="ball{" red" if k < 8 else ""}"></div>' for k in range(15))
clip("g0", 8.6, 7.2, f'<div class="grid">{balls}</div><div class="count"><span id="gc" class="y">8</span><span class="of">/15</span></div>'
     '<div class="cap2">Messi\'s share of Barcelona\'s group goals · UEFA</div><div id="g3" class="banner">HAT-TRICK v APOEL · 4-0 AWAY</div>')
for k in range(15):
    js.append(f'tl.fromTo("#gb{k}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.18, ease: "back.out(3)" }}, {round(8.75 + k * 0.05, 2)});')
for k in range(8):
    js.append(f'tl.fromTo("#gb{k}", {{ backgroundColor: "rgba(255,255,255,0.18)" }}, {{ backgroundColor: "#ff3b55", boxShadow: "0 0 30px #ff3b55", duration: 0.12, immediateRender: false }}, {round(10.0 + k * 0.17, 2)});')
slam("#g0 .count", 11.4); shake(11.4); rise("#g0 .cap2", 11.7); slam("#g3", 13.1, s=1.3)

# ---------------------------------------------------------------- round of 16
clip("r0", 15.8, 1.8, '<div class="score"><div class="team">MAN CITY</div><div class="num">1-2</div><div class="team">BARÇA</div></div>'
     '<div id="r0b" class="big y">SUÁREZ ×2</div><div class="sub">away leg · aggregate 3-1</div><div class="src">Results: UEFA</div>')
slam("#r0 .score", 15.85); slam("#r0b", 16.5); shake(16.5)
clip("r1", 17.6, 2.5, '<div id="r1a" class="pill">SUÁREZ</div>', "card over")
slam("#r1a", 17.7)

# ---------------------------------------------------------------- quarter-final
clip("q0", 20.2, 6.2, '<div id="q0a" class="pill">SUÁREZ v DAVID LUIZ</div><div id="q0b" class="pill y2">SUÁREZ ×2 IN PARIS</div>', "card over")
slam("#q0a", 20.35); slam("#q0b", 23.6); js.append('tl.to("#q0a", { opacity: 0, duration: 0.2 }, 23.4);')
clip("q1", 26.4, 1.2, '<div class="big y">NEYMAR ×3</div><div class="sub">AGGREGATE 5-1</div><div class="src">Results: UEFA</div>')
slam("#q1 .big", 26.42); flash(26.4)

# ---------------------------------------------------------------- semi-final
clip("s0", 27.6, 3.3, '<div id="s0a" class="pill">MESSI v BAYERN</div>', "card over")
slam("#s0a", 27.75)
clip("s1", 30.9, 2.1, '<div class="score"><div class="team">BARÇA</div><div class="num">3-0</div><div class="team">BAYERN</div></div>'
     '<div id="s1b" class="big y">MESSI ×2</div><div class="sub">AGGREGATE 5-3</div><div class="src">Results: UEFA</div>')
slam("#s1 .score", 30.92); slam("#s1b", 31.4); flash(30.9); shake(31.4)

# ---------------------------------------------------------------- the final
clip("f0", 33.0, 3.0, '<div class="top">THE FINAL</div><div class="sub">BERLIN · 6 JUNE 2015</div><div id="f0a" class="mega y">4\'</div><div id="f0b" class="big">RAKITIĆ</div><div id="f0c" class="scoreline">JUV 0-1 BARÇA</div><div class="src">Results: UEFA</div>')
rise("#f0 .top", 33.05); rise("#f0 .sub", 33.25); slam("#f0a", 34.6); slam("#f0b", 34.85); slam("#f0c", 35.15, s=1.3); flash(34.6); shake(34.85)
clip("f1", 36.0, 5.0, '<div id="f1a" class="mega y">68\'</div><div id="f1b" class="big">MESSI RUNS</div><div id="f1c" class="big">BUFFON SAVES</div><div id="f1d" class="big r">SUÁREZ SCORES</div>'
     '<div id="f1e" class="scoreline">JUV 1-2 BARÇA</div><div class="lbl2">Morata had equalised on 55\'</div><div class="src">Results: UEFA</div>')
slam("#f1a", 36.1); slam("#f1b", 36.75); slam("#f1c", 38.1); slam("#f1d", 39.6); slam("#f1e", 39.95, s=1.3); flash(39.6); shake(39.6)
js.append('tl.fromTo("#f1 .lbl2", { opacity: 0 }, { opacity: 1, duration: 0.3 }, 40.2);')
clip("f2", 41.0, 0.79, '<div class="pill">MESSI · NEYMAR</div>', "card over")
clip("f3", 41.79, 1.21, '<div class="scoreline big2">JUV 1-2 BARÇA</div>')
slam("#f3 .scoreline", 41.8, s=1.2)
clip("f4", 43.0, 3.0, '<div id="f4a" class="mega y">90+7\'</div><div id="f4b" class="big">NEYMAR</div><div id="f4c" class="scoreline">JUV 1-3 BARÇA</div><div class="src">Results: UEFA</div>')
slam("#f4a", 43.05); slam("#f4b", 43.55); slam("#f4c", 44.0, s=1.3); flash(43.55); shake(43.55)

# ---------------------------------------------------------------- the cup
rays = "".join(f'<div class="ray" style="transform:rotate({k * 15}deg)"></div>' for k in range(24))
conf = []
for k in range(110):
    x = random.uniform(0, 1080); w = random.uniform(10, 22); c = ["#ff3b55", "#1d3c8f", "#ffd166", "#ffffff"][k % 4]
    d0 = random.uniform(46.3, 50.0); dur = random.uniform(2.6, 4.8); rot = random.uniform(-540, 540); dx = random.uniform(-90, 90)
    conf.append(f'<div id="cf{k}" class="conf" style="left:{x:.0f}px;width:{w:.0f}px;height:{w * .5:.0f}px;background:{c}"></div>')
    js.append(f'tl.fromTo("#cf{k}", {{ y: -60, x: 0, rotation: 0, opacity: 1 }}, {{ y: 2000, x: {dx:.0f}, rotation: {rot:.0f}, duration: {dur:.2f}, ease: "none" }}, {d0:.2f});')
    js.append(f'tl.fromTo("#cf{k}", {{ y: -60, x: 0, rotation: 0 }}, {{ y: 2000, x: {-dx:.0f}, rotation: {-rot:.0f}, duration: {dur:.2f}, ease: "none", immediateRender: false }}, {d0 + dur + random.uniform(0, 1.5):.2f});')
cup = """<svg id="cupsvg" viewBox="-80 -130 160 170" width="560" height="595"><defs><linearGradient id="sil" x1="0" x2="1">
<stop offset="0" stop-color="#7c858d"/><stop offset=".45" stop-color="#f6f8fa"/><stop offset="1" stop-color="#6f7880"/></linearGradient></defs>
<path d="M -30 -102 Q -74 -104 -72 -64 Q -70 -36 -24 -34" fill="none" stroke="url(#sil)" stroke-width="10"/>
<path d="M 30 -102 Q 74 -104 72 -64 Q 70 -36 24 -34" fill="none" stroke="url(#sil)" stroke-width="10"/>
<path d="M -34 -110 Q -34 -42 -11 -26 L -9 -4 L -26 8 L 26 8 L 9 -4 L 11 -26 Q 34 -42 34 -110 Z" fill="url(#sil)"/>
<rect x="-30" y="8" width="60" height="22" rx="4" fill="url(#sil)"/><rect x="-30" y="16" width="60" height="4" fill="#1d3c8f"/></svg>"""
clip("c0", 46.0, 14.0, f'<div class="rays">{rays}</div>{cup}<div id="c1" class="mega y cupt">CHAMPIONS</div><div id="c2" class="big">OF EUROPE</div>'
     f'<div id="c3" class="treble">LA LIGA · COPA DEL REY · CHAMPIONS LEAGUE</div>'
     f'<div id="c4" class="stat"><div class="n">MSN · 27 OF 31</div><div class="d">Messi 10 · Neymar 10 · Suárez 7</div><div class="s">Champions League goals · Source: UEFA</div></div>'
     f'{"".join(conf)}')
clip("c5", 57.4, 2.6, '<div class="end"><div class="top">RUN OF THE CHAMPIONS</div><div class="sub">NEXT: 2015/16</div></div>', "card", 4)
js.append('tl.fromTo("#cupsvg", { y: 700, scale: 0.6 }, { y: 0, scale: 1, duration: 0.9, ease: "back.out(1.4)" }, 46.05);')
js.append('tl.fromTo("#c0 .rays", { rotation: 0, opacity: 0 }, { rotation: 60, opacity: 1, duration: 14, ease: "none" }, 46.0);')
flash(46.6); slam("#c1", 46.7); slam("#c2", 47.1); shake(46.7); rise("#c3", 48.3)
js.append('tl.to(["#c1", "#c2", "#c3"], { opacity: 0, duration: 0.3 }, 50.8);')
slam("#c4", 51.2, s=1.25); shake(51.2)
js.append('tl.to("#c4", { opacity: 0, duration: 0.4 }, 57.2);')
rise("#c5 .end", 57.4)

# ---------------------------------------------------------------- stage chips and captions
for k, (s, e, t) in enumerate(CHIPS):
    clip(f"ch{k}", s, e - s, t, "chip", 5)
    js.append(f'tl.fromTo("#ch{k}", {{ x: -80, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3, ease: "power3.out" }}, {s + 0.03});')
for k, (s, e, t) in enumerate(caps):
    clip(f"cp{k}", s, e - s, f"<span>{t}</span>", "caption", 7)

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #146a66; }}
      #root {{ position: absolute; inset: 0; overflow: hidden; color: #fff; font-family: Inter, sans-serif; }}
      .bg {{ position: absolute; inset: 0; background: radial-gradient(110% 70% at 50% 40%, #1f8e86 0%, #146a66 55%, #0a3a3d 100%); }}
      .streak {{ position: absolute; height: 120px; background: rgba(5,45,48,.35); border-radius: 60px; transform: rotate(-24deg); }}
      .vid {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #cards {{ position: absolute; inset: 0; }}
      .card {{ position: absolute; left: 120px; right: 192px; top: 380px; bottom: 850px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
      .card.over {{ justify-content: flex-start; padding-top: 80px; }}
      .mega {{ font: 700 150px/0.95 Oswald, sans-serif; letter-spacing: .01em; text-shadow: 0 10px 40px rgba(0,0,0,.35); }}
      .big {{ font: 700 84px/1.04 Oswald, sans-serif; text-shadow: 0 8px 30px rgba(0,0,0,.35); }}
      .big2 {{ font-size: 72px !important; }}
      .y {{ color: #ffd166; }} .r {{ color: #ff3b55; }}
      .top {{ font: 700 64px Oswald, sans-serif; letter-spacing: .04em; }}
      .sub {{ font: 700 34px Oswald, sans-serif; letter-spacing: .08em; color: #ffd166; margin-top: 14px; }}
      .lbl {{ font: 600 32px Inter, sans-serif; background: rgba(4,32,36,.75); padding: 6px 18px; border-radius: 10px; margin-top: 18px; }}
      .lbl2 {{ font: 600 30px Inter, sans-serif; color: rgba(255,255,255,.85); margin-top: 12px; }}
      .names {{ margin-top: 40px; }}
      .name {{ font: 700 112px/1.0 Oswald, sans-serif; }}
      #n1 {{ color: #ff3b55; }} #n2 {{ color: #ffd166; }} #n3 {{ color: #ffffff; }}
      .grid {{ display: grid; grid-template-columns: repeat(5, 96px); gap: 22px; }}
      .ball {{ width: 96px; height: 96px; border-radius: 50%; background: rgba(255,255,255,0.18); border: 5px solid rgba(255,255,255,.8); }}
      .count {{ margin-top: 26px; font: 700 150px/1 Oswald, sans-serif; }}
      .count .of {{ font-size: 70px; color: rgba(255,255,255,.85); }}
      .cap2 {{ font: 600 32px Inter, sans-serif; margin-top: 10px; }}
      .banner {{ margin-top: 34px; font: 700 46px Oswald, sans-serif; background: #a3123a; padding: 8px 30px; border-radius: 12px; box-shadow: 0 0 40px rgba(163,18,58,.6); }}
      .score {{ display: flex; align-items: center; gap: 22px; background: rgba(4,32,36,.85); padding: 16px 26px; border-radius: 20px; margin-bottom: 36px; }}
      .score .team {{ font: 700 50px Oswald, sans-serif; }} .score .num {{ font: 700 96px Oswald, sans-serif; color: #ffd166; }}
      .scoreline {{ margin-top: 26px; font: 700 64px Oswald, sans-serif; background: rgba(4,32,36,.85); padding: 10px 34px; border-radius: 16px; }}
      .pill {{ font: 700 54px Oswald, sans-serif; background: rgba(4,32,36,.85); padding: 8px 32px; border-radius: 16px; border: 4px solid #ff3b55; }}
      .pill.y2 {{ border-color: #ffd166; color: #ffd166; }}
      .chip {{ position: absolute; left: 130px; top: 300px; font: 700 44px Oswald, sans-serif; letter-spacing: .05em; background: #a3123a; padding: 4px 22px; border-radius: 10px; box-shadow: 0 0 30px rgba(163,18,58,.6); }}
      .traced {{ position: absolute; left: 130px; top: 370px; font: 600 30px Inter, sans-serif; background: rgba(4,32,36,.75); padding: 6px 16px; border-radius: 10px; }}
      .src {{ position: absolute; left: 0; right: 0; top: 650px; font: 400 28px Inter, sans-serif; color: rgba(255,255,255,.75); }}
      .caption {{ position: absolute; left: 120px; right: 260px; top: 1090px; text-align: center; }}
      .caption span {{ display: inline-block; font: 800 36px/1.18 Inter, sans-serif; background: rgba(4,32,36,.82); padding: 10px 26px; border-radius: 14px; }}
      .rays {{ position: absolute; left: 384px; top: 120px; width: 0; height: 0; }}
      .ray {{ position: absolute; left: -30px; top: -1100px; width: 60px; height: 1100px; background: linear-gradient(to top, rgba(255,209,102,.35), rgba(255,209,102,0)); transform-origin: 30px 1100px; }}
      .cupt {{ font-size: 96px; }}
      #cupsvg {{ margin-top: -40px; width: 300px; height: 320px; filter: drop-shadow(0 0 40px rgba(255,255,255,.35)); }}
      .treble {{ margin-top: 18px; font: 700 25px Oswald, sans-serif; letter-spacing: .06em; color: #ffd166; }}
      .stat {{ position: absolute; left: 0; right: 0; top: 400px; background: rgba(4,32,36,.9); border: 4px solid #ffd166; border-radius: 22px; padding: 20px; }}
      .stat .n {{ font: 700 72px Oswald, sans-serif; color: #ffd166; }} .stat .d {{ font: 700 34px Inter, sans-serif; }} .stat .s {{ font: 400 26px Inter, sans-serif; color: rgba(255,255,255,.8); margin-top: 6px; }}
      .end {{ position: absolute; left: 0; right: 0; top: 420px; }}
      .conf {{ position: absolute; top: 0; }}
      .flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="1080" data-height="1920">
      <div class="bg"></div>
      <div class="streak" style="left:-200px;top:380px;width:900px"></div>
      <div class="streak" style="left:420px;top:1260px;width:900px"></div>
      <div class="streak" style="left:-100px;top:1650px;width:700px"></div>
      <div id="cards">
      {chr(10).join('      ' + e for e in els)}
      </div>
      <div id="flash" class="flash"></div>
      <audio id="mix" class="clip" src="assets/audio/short_full.wav" data-start="0" data-duration="60" data-track-index="9" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {chr(10).join('      ' + j for j in js)}
      tl.set({{}}, {{}}, 60);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(html)
print("index.html:", len(els), "timed elements,", len(js), "tweens")
