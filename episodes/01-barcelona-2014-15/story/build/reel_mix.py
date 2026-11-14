"""Mix the reel: narration, music ducked about 45% under the voice, and effects on the picture's events."""
import json, os, re, subprocess
import numpy as np
SR, DUR = 48000, 60.0
import sys
PLAN = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else None
A = "assets/audio/reel"
VO = {"r1": 0.5, "r2": 5.95, "r3": 13.35, "r4": 19.55, "r5": 25.95, "r6": 32.2, "r7": 37.4, "r8": 46.2, "r9": 51.6}
CUTS = [5.8, 13.2, 19.4, 25.8, 32.0, 37.0, 44.0, 50.5]
SHOTS = [8.5, 15.9, 22.1, 28.5, 34.0, 40.0, 41.4, 47.6]          # a boot on the ball
PASSES = [33.0, 44.6, 45.8]
GOALS = [8.85, 16.25, 22.45, 28.85, 34.35, 41.75, 47.95]          # ball in the net
CUPT, OUT = 50.7, "reel"
if PLAN:
    VO, CUTS, SHOTS, PASSES, GOALS, CUPT, OUT = PLAN["vo"], PLAN["cuts"], PLAN["shots"], PLAN.get("passes", []), PLAN["goals"], PLAN["cup"], PLAN["out"]
def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def lufs(x):
    p = "/tmp/_m.wav"; write(p, x)
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", out)[-1])
def write(p, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ac", "2", p], input=np.clip(x, -1, 1).astype(np.float32).tobytes(), check=True)
n = int(DUR * SR)
def place(buf, x, t, g=1.0):
    i = int(t * SR); x = x[: max(0, n - i)]; buf[i:i + len(x)] += x * g
vo, active = np.zeros(n, np.float32), np.zeros(n, np.float32)
lines = json.load(open(f"{A}/lines.json"))
for k, t in VO.items():
    x = load(f"{A}/{k}.mp3"); place(vo, x, t)
    active[int((t - 0.1) * SR): int((t + len(x) / SR + 0.2) * SR)] = 1
vo *= 10 ** ((-16 - lufs(vo)) / 20)
fx = np.zeros(n, np.float32)
norm = lambda x, db: x / (np.abs(x).max() + 1e-9) * 10 ** (db / 20)
wh, kick, net, roar, cup = (norm(load(f), d) for f, d in [(f"{A}/whoosh.mp3", -12), ("assets/audio/kick.mp3", -8), ("assets/audio/net.mp3", -12), (f"{A}/roar.mp3", -14), (f"{A}/cupcrowd.mp3", -12)])
for t in CUTS: place(fx, wh, t - 0.15)
for t in SHOTS: place(fx, kick, t)
for t in PASSES: place(fx, kick, t, 0.45)
for t in GOALS:
    place(fx, net, t); r = roar.copy(); r[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR)); place(fx, r, t + 0.05)
place(fx, cup, CUPT)
mu = load(f"{A}/music.mp3")[:n]; mu = np.pad(mu, (0, n - len(mu)))
mu *= 10 ** ((-20 - lufs(mu)) / 20)
k = int(0.25 * SR); duck = 1 - 0.45 * np.convolve(active, np.ones(k) / k, mode="same")
mu *= duck; mu[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
for name, mix in (("full", vo + fx + mu), ("nomusic", vo + fx)):
    mix = mix * 10 ** ((-15 - lufs(mix)) / 20)
    write(f"{A}/_raw.wav", mix)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/_raw.wav", "-af", "alimiter=limit=0.8:level=false", "-ar", str(SR), f"{A}/{OUT}_{name}.wav"], check=True)
    os.remove(f"{A}/_raw.wav")
# captions: each line split into short groups, timed by character position over the line's length
caps = []
for k, t in VO.items():
    text, d = lines[k]["text"], lines[k]["dur"]
    raw = [p.strip() for p in re.split(r"(?<=[.,:])\s+", text) if p.strip()]
    parts = []
    for p in raw:  # keep groups of at least four words so each stays up long enough to read
        if parts and (len(parts[-1].split()) < 4 or len(p.split()) < 3) and len((parts[-1] + " " + p).split()) <= 9:
            parts[-1] = parts[-1] + " " + p
        else:
            parts.append(p)
    pos = 0
    for p in parts:
        i = text.index(p, pos); j = i + len(p); pos = j
        caps.append([round(t + 0.1 + (d - 0.3) * i / len(text), 2), round(t + 0.1 + (d - 0.3) * j / len(text) + 0.25, 2), p])
for a, b in zip(caps, caps[1:]): a[1] = min(a[1], b[0])
json.dump(caps, open(f"{A}/{OUT}_captions.json", "w"), ensure_ascii=False, indent=0)
print(len(caps), "caption groups")
