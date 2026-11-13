"""Build the whole film: the nine chapter scenes, the captions, the audio mixes and the root composition.

Usage: python build/build_film.py [--no-audio]
Writes compositions/c*.html, compositions/captions.html, assets/audio/mix_full.wav, assets/audio/mix_nomusic.wav,
data/timeline.json and index.html.
"""
import argparse
import json
import os
import re
import subprocess

import numpy as np

import kit
from chapters import CHAPTERS
from kit import CH_END, CH_START, FILM, FILM_END, LINES, SFX, STARTS, V, BASE_CSS, INK

SR = 48000
AUD = os.path.join(FILM, "assets", "audio")


# ---------------------------------------------------------------- captions
def caption_groups():
    groups = []
    for lid, text in LINES:
        words = text.split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) >= 6 or (len(cur) >= 3 and re.search(r"[.,?!:;]$", w)):
                chunks.append(cur)
                cur = []
        if cur:
            if chunks and len(cur) <= 2:
                chunks[-1] += cur
            else:
                chunks.append(cur)
        ws = V[lid]["words"]
        a, b = (ws[0]["s"], ws[-1]["e"]) if ws else (0, V[lid]["dur"])
        total = len(text)
        pos = 0
        spans = []
        for c in chunks:
            s = " ".join(c)
            i = text.index(s, pos)
            spans.append((i, i + len(s), s))
            pos = i + len(s)
        for k, (i, j, s) in enumerate(spans):
            t0 = STARTS[lid] + a + (b - a) * i / total
            t1 = STARTS[lid] + a + (b - a) * j / total + 0.25
            if k + 1 < len(spans):
                t1 = min(t1, STARTS[lid] + a + (b - a) * spans[k + 1][0] / total)
            groups.append((round(t0 - 0.05, 3), round(max(t1, t0 + 0.8), 3), s))
    # no overlaps
    for k in range(len(groups) - 1):
        if groups[k][1] > groups[k + 1][0]:
            groups[k] = (groups[k][0], groups[k + 1][0], groups[k][2])
    return groups


def captions_html():
    els, js = [], []
    for k, (t0, t1, s) in enumerate(caption_groups()):
        d = round(t1 - t0, 3)
        els.append(f'<div id="cap-{k}" class="clip capg" data-start="{t0}" data-duration="{d}"><span id="cap-{k}-t">{s}</span></div>')
        js.append(f'tl.fromTo("#cap-{k}-t", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.1 }}, {t0});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .capg {{ position: absolute; left: 0; right: 0; bottom: 56px; text-align: center; }}
    .capg span {{ display: inline-block; font: 600 40px Inter, sans-serif; color: {INK}; background: rgba(7,8,10,.72);
                 padding: 8px 24px; border-radius: 8px; max-width: 1560px; line-height: 1.25; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1920" data-height="1080">
{chr(10).join(els)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + j for j in js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- audio
def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1])


def write(path, mono):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ac", "2", path],
                   input=np.clip(mono, -1, 1).astype(np.float32).tobytes(), check=True)


def finish(src, dst, target=-15.0):
    """Gain to the target loudness, then a true-peak limiter at -1.5 dBTP."""
    g = target - lufs(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"volume={g:.2f}dB,alimiter=limit=0.84:level=false",
                    "-ar", str(SR), dst], check=True)


def mix():
    n = int((FILM_END + 1) * SR)
    vo = np.zeros(n, np.float32)
    active = np.zeros(n, np.float32)
    for lid, _ in LINES:
        a = load(os.path.join(AUD, "vo", f"{lid}.mp3"))
        i = int(STARTS[lid] * SR)
        vo[i:i + len(a)] += a[: n - i]
        active[max(0, i - int(0.15 * SR)): i + len(a) + int(0.2 * SR)] = 1
    # voice to about -16 LUFS on its own
    tmp = os.path.join(AUD, "_vo.wav")
    write(tmp, vo)
    vo *= 10 ** ((-16 - lufs(tmp)) / 20)

    sfx = np.zeros(n, np.float32)
    cache = {}
    for t, name, gain in SFX:
        if name not in cache:
            s = load(os.path.join(AUD, "sfx", f"{name}.mp3"))
            cache[name] = s / (np.max(np.abs(s)) + 1e-9) * 10 ** (-9 / 20)  # each effect peaks at -9 dBFS before its gain
        s = cache[name] * gain
        i = int(max(0, t) * SR) + int(SR / 30)  # one frame after the picture
        sfx[i:i + len(s)] += s[: max(0, n - i)]

    music = np.zeros(n, np.float32)
    A, B = load(os.path.join(AUD, "music_A.mp3")), load(os.path.join(AUD, "music_B.mp3"))
    xf = int(2.0 * SR)
    cut = int(CH_START[5] * SR)
    a_len = min(len(A), cut + xf)
    env_a = np.ones(a_len, np.float32)
    env_a[a_len - xf:] = np.linspace(1, 0, xf)
    music[:a_len] += A[:a_len] * env_a
    b0 = cut - xf // 2
    b_len = min(len(B), n - b0)
    env_b = np.ones(b_len, np.float32)
    env_b[:xf] = np.linspace(0, 1, xf)
    fo = int(3.5 * SR)
    end_i = int(FILM_END * SR) - b0
    if 0 < end_i <= b_len:
        env_b[max(0, end_i - fo):end_i] *= np.linspace(1, 0, min(fo, end_i))
        env_b[end_i:] = 0
    music[b0:b0 + b_len] += B[:b_len] * env_b
    write(tmp, music)
    music *= 10 ** ((-22 - lufs(tmp)) / 20)
    # duck about 45% under the voice, with 0.25 s ramps
    k = int(0.25 * SR)
    ker = np.ones(k, np.float32) / k
    duck = 1 - 0.45 * np.convolve(active, ker, mode="same")
    music *= duck
    os.remove(tmp)

    full, nomusic = vo + sfx + music, vo + sfx
    for name, arr in (("full", full), ("nomusic", nomusic)):
        raw = os.path.join(AUD, f"_{name}.wav")
        write(raw, arr)
        finish(raw, os.path.join(AUD, f"mix_{name}.wav"))
        os.remove(raw)
    print("mixes:", {f: round(lufs(os.path.join(AUD, f"mix_{f}.wav")), 1) for f in ("full", "nomusic")}, "LUFS")


# ---------------------------------------------------------------- root
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-audio", action="store_true")
    a = ap.parse_args()
    comp = os.path.join(FILM, "compositions")
    for f in os.listdir(comp):
        if f.endswith(".html"):
            os.remove(os.path.join(comp, f))
    hosts = []
    for build in CHAPTERS:
        sc = build()
        open(os.path.join(comp, f"{sc.cid}.html"), "w", encoding="utf-8").write(sc.html())
        hosts.append(f'      <div id="{sc.cid}" data-composition-id="{sc.cid}" data-composition-src="compositions/{sc.cid}.html" '
                     f'data-start="{sc.t0}" data-duration="{sc.dur}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:1"></div>')
    open(os.path.join(comp, "captions.html"), "w", encoding="utf-8").write(captions_html())
    hosts.append(f'      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" '
                 f'data-start="0" data-duration="{FILM_END}" data-track-index="2" data-track-kind="captions" data-width="1920" data-height="1080" style="z-index:5"></div>')
    hosts.append(f'      <audio id="mix" class="clip" src="assets/audio/mix_full.wav" data-start="0" data-duration="{FILM_END}" data-track-index="3" data-volume="1"></audio>')
    open(os.path.join(FILM, "index.html"), "w", encoding="utf-8").write(f"""<!doctype html>
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
    <div id="root" data-composition-id="main" data-start="0" data-duration="{FILM_END}" data-width="1920" data-height="1080">
      <div id="ground" style="position:absolute;inset:0;background:#07080a"></div>
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    json.dump({"film_end": FILM_END, "chapters": {k: [CH_START[k], CH_END[k]] for k in CH_START}, "lines": STARTS,
               "sfx": SFX}, open(os.path.join(FILM, "data", "timeline.json"), "w"), indent=1)
    print("film", FILM_END, "s;", len(SFX), "effects;", len(caption_groups()), "caption groups")
    if not a.no_audio:
        mix()


if __name__ == "__main__":
    main()
