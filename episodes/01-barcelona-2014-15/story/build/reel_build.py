"""Write index.html for the 60-second reel (HyperFrames root composition)."""
import json
caps = json.load(open("assets/audio/reel/captions.json"))
STAGES = [  # start, end, title, detail, label
    (5.8, 13.2, "GROUP STAGE", "Messi: 8 of Barcelona's 15 group goals · hat-trick at APOEL, 4-0", "Illustration of the scorer, not a replay of the goal · Results: UEFA"),
    (13.2, 19.4, "ROUND OF 16", "Man City 1-2 Barcelona · Suárez 2 · aggregate 3-1", "Illustration of the scorer, not a replay of the goal · Results: UEFA"),
    (19.4, 25.8, "QUARTER-FINAL", "PSG 1-3 Barcelona · Barcelona 2-0 PSG · aggregate 5-1", "Illustration of the scorer, not a replay of the goal · Results: UEFA"),
    (25.8, 32.0, "SEMI-FINAL", "Barcelona 3-0 Bayern · Messi 2, Neymar · aggregate 5-3", "Illustration of the scorer, not a replay of the goal · Results: UEFA"),
    (32.0, 50.5, "FINAL · BERLIN · 6 JUNE 2015", "Juventus 1-3 Barcelona", "Reconstruction: positions from StatsBomb open data, movement from CMU motion capture"),
]
SCORES = [(32.0, "JUV 0-0 BAR"), (34.35, "JUV 0-1 BAR · Rakitić 4'"), (37.0, "JUV 1-1 BAR · Morata 55'"), (41.75, "JUV 1-2 BAR · Suárez 68'"), (47.95, "JUV 1-3 BAR · Neymar 90+7'")]
els, js = [], []
for i, (a, b, t, d, l) in enumerate(STAGES):
    els.append(f'<div id="st{i}" class="stage clip" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="2"><div class="st-t">{t}</div><div class="st-d">{d}</div><div class="st-l">{l}</div></div>')
    js.append(f'tl.fromTo("#st{i}", {{ x: -60, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {a + 0.05});')
for i, (a, s) in enumerate(SCORES):
    b = SCORES[i + 1][0] if i + 1 < len(SCORES) else 50.5
    els.append(f'<div id="sc{i}" class="score clip" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="3">{s}</div>')
    if i: js.append(f'tl.fromTo("#sc{i}", {{ scale: 1.35, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.3, ease: "power4.out" }}, {a});')
for i, (a, b, s) in enumerate(caps):
    els.append(f'<div id="cp{i}" class="cap clip" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="4"><span>{s}</span></div>')
html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/gsap.min.js"></script>
    <script src="data/mocap.js"></script>
    <script src="data/film_data.js"></script>
    <script src="assets/story.js"></script>
    <script src="assets/mo.js"></script>
    <script src="assets/kit3d.js"></script>
    <script src="assets/reel.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #146a66; }}
      #root {{ position: absolute; inset: 0; font-family: Inter, sans-serif; color: #fff; overflow: hidden; }}
      .bg {{ position: absolute; inset: 0; background: radial-gradient(120% 90% at 50% 40%, #1f8e86 0%, #146a66 55%, #0a3a3d 100%); }}
      .tag {{ position: absolute; transform: translate(-50%, -100%); font: 700 28px Inter, sans-serif; padding: 6px 18px; border-radius: 22px; background: rgba(4,32,36,.88); border: 3px solid #ff3b55; white-space: nowrap; }}
      .tag.opp {{ border-color: #f4f4f2; }}
      .stage {{ position: absolute; left: 56px; top: 44px; max-width: 1180px; }}
      .st-t {{ display: inline-block; font: 700 48px Oswald, sans-serif; letter-spacing: .04em; background: #a3123a; padding: 2px 20px; border-radius: 8px; box-shadow: 0 0 24px rgba(163,18,58,.6); }}
      .st-d {{ font: 600 30px Inter, sans-serif; margin-top: 10px; background: rgba(4,32,36,.78); display: inline-block; padding: 4px 14px; border-radius: 8px; }}
      .st-l {{ font: 400 28px Inter, sans-serif; color: rgba(255,255,255,.82); margin-top: 8px; }}
      .score {{ position: absolute; right: 56px; top: 44px; font: 700 46px Oswald, sans-serif; background: rgba(4,32,36,.85); padding: 6px 20px; border-radius: 10px; }}
      .cap {{ position: absolute; left: 0; right: 0; bottom: 48px; text-align: center; }}
      .cap span {{ display: inline-block; font: 600 42px Inter, sans-serif; background: rgba(4,32,36,.8); padding: 8px 26px; border-radius: 10px; }}
      .title {{ position: absolute; left: 0; right: 0; top: 70px; text-align: center; }}
      .big {{ font: 700 132px Oswald, sans-serif; letter-spacing: .03em; line-height: 1; text-shadow: 0 6px 30px rgba(0,0,0,.35); }}
      .sub {{ font: 700 40px Oswald, sans-serif; letter-spacing: .12em; color: #ffd166; margin-top: 14px; }}
      .stat {{ position: absolute; left: 50%; bottom: 150px; transform: translateX(-50%); text-align: center; background: rgba(4,32,36,.85); border: 3px solid #ffd166; border-radius: 14px; padding: 12px 34px; }}
      .stat .n {{ font: 700 64px Oswald, sans-serif; color: #ffd166; }}
      .stat .d {{ font: 600 30px Inter, sans-serif; }}
      .stat .s {{ font: 400 28px Inter, sans-serif; color: rgba(255,255,255,.8); margin-top: 4px; }}
      .flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="1920" data-height="1080">
      <div class="bg"></div>
      <svg id="pitch" width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0"></svg>
      <div id="tags"></div>
      <div id="flash" class="flash"></div>
      <div id="t0" class="title clip" data-start="0.2" data-duration="5.4" data-track-index="5"><div class="big">ROAD TO THE TREBLE</div><div class="sub">BARCELONA · CHAMPIONS LEAGUE 2014/15</div></div>
      <div id="t1" class="title clip" data-start="51.2" data-duration="8.8" data-track-index="5"><div class="big">CHAMPIONS OF EUROPE</div><div class="sub">LA LIGA · COPA DEL REY · CHAMPIONS LEAGUE</div></div>
      <div id="t2" class="stat clip" data-start="54.6" data-duration="5.4" data-track-index="6"><div class="n">MSN · 27 OF 31</div><div class="d">Champions League goals: Messi 10 · Neymar 10 · Suárez 7</div><div class="s">Source: UEFA</div></div>
{chr(10).join('      ' + e for e in els)}
      <audio id="mix" class="clip" src="assets/audio/reel/reel_full.wav" data-start="0" data-duration="60" data-track-index="7" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const svg = document.getElementById("pitch"), tags = document.getElementById("tags");
      const state = {{ t: 0 }};
      const draw = () => REEL.render(state.t, svg, tags);
      const tl = gsap.timeline({{ paused: true }});
      tl.to(state, {{ t: 60, duration: 60, ease: "none", onUpdate: draw }}, 0);
      tl.fromTo("#t0 .big", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0.25);
      tl.fromTo("#t0 .sub", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 0.8);
      tl.to("#t0", {{ opacity: 0, duration: 0.4 }}, 5.1);
      tl.fromTo("#t1 .big", {{ scale: 1.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "power4.out" }}, 51.25);
      tl.fromTo("#t1 .sub", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 52.4);
      tl.fromTo("#t2", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: "power3.out" }}, 54.6);
      for (const g of [8.85, 16.25, 22.45, 28.85, 34.35, 41.75, 47.95, 51.4]) {{
        tl.fromTo("#flash", {{ opacity: 0 }}, {{ opacity: 0.3, duration: 0.05, immediateRender: false }}, g);
        tl.to("#flash", {{ opacity: 0, duration: 0.35 }}, g + 0.05);
      }}
      {chr(10).join('      ' + j for j in js)}
      draw();
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w", encoding="utf-8").write(html)
print("index.html written:", len(els), "timed overlays")
