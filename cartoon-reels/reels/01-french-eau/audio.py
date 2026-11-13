"""Sound effects and the two final mixes.

Run: python3 audio.py   (after music.py and timeline.py)
- mix-music.wav:   voice + effects + the full song (ElevenLabs music, assets/audio/song.mp3)
- mix-nomusic.wav: voice + effects + the song's vocals stem only, so the sung French
                   stays and Instagram music can go underneath
Both are loudness-normalised to about -15 LUFS.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).parent
SR = 44100
OUT = HERE / "assets" / "audio"
rng = np.random.default_rng(7)  # seeded: the same effects every run

T = json.loads((HERE / "timeline.json").read_text())
N = int(T["total"] * SR)


def buf():
    return np.zeros(N, dtype=np.float64)


def put(track, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= N:
        return
    x = x[: N - i]
    track[i:i + len(x)] += gain * x


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


# ------------------------------------------------------------------ effects ---
def pop():
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    f = 500 + 900 * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.03) * 0.5


def tick():
    n = int(0.03 * SR)
    return hp(rng.standard_normal(n), 3000) * env(n, 0.0005, 0.006) * 0.35


def whoosh(d=0.45):
    n = int(d * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    lo, mid, hi = bp(x, 300, 900), bp(x, 900, 2500), bp(x, 2500, 7000)
    w = t / d
    y = lo * (1 - w) + mid * np.sin(np.pi * w) + hi * w
    return y * np.sin(np.pi * w) ** 2 * 0.5


def splash():
    n = int(0.9 * SR)
    x = lp(rng.standard_normal(n), 2500) * env(n, 0.003, 0.25) * 0.6
    for _ in range(9):  # bubbles
        s = int(rng.uniform(0.1, 0.7) * SR)
        m = int(0.06 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(500, 1100) * (1 + 3 * tt / 0.06)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, 0.002, 0.02) * 0.2
        x[s:s + m] += b[: max(0, min(m, n - s))]
    return x


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def fit(x):
    """Song audio cut or padded to the reel length, with a short fade at the end."""
    y = np.zeros(N)
    y[: min(N, len(x))] = x[:N]
    f = int(0.25 * SR)
    y[N - f:] *= np.linspace(1, 0, f)
    return y


def main():
    voice, sfx = buf(), buf()
    for v in T["voice"]:
        put(voice, load(HERE / "assets/vo/trim" / f"{v['id']}.wav"), v["t"])

    put(sfx, pop(), 0.0)
    for it in T["items"]:
        if it["kind"] == "word":
            put(sfx, tick(), it["start"])
            put(sfx, pop(), it["answer"])
        else:
            put(sfx, pop() * 0.8, it["start"])
    put(sfx, whoosh(0.4), T["try"]["start"] + 0.05)
    for e in T["english"]:
        put(sfx, tick() * 0.8, e["start"])
    put(sfx, whoosh(0.35), T["payoff"]["start"] - 0.15)
    put(sfx, splash() * 0.8, T["payoff"]["splash"])
    put(sfx, whoosh(0.3), T["button"]["start"] - 0.12)

    song = fit(load(OUT / "song.mp3"))
    vocals = fit(load(OUT / "stems" / "vocals.mp3"))

    # duck the song under the teacher's voice (about -7 dB); the sung chorus is never ducked
    active = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(0.05 * SR)), "same") > 0
    duck = np.where(active, 0.45, 1.0)
    sm = int(0.15 * SR)
    duck = np.convolve(duck, np.ones(sm) / sm, "same")
    song *= duck

    for name, x in (("mix-music", voice + sfx + song * 0.75), ("mix-nomusic", voice + sfx + vocals * 0.9)):
        x = x / max(1e-6, np.abs(x).max()) * 0.9
        raw = OUT / f"{name}.raw.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", str(raw)],
                       input=x.astype(np.float64).tobytes(), check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
                        "-ar", str(SR), "-ac", "2", str(OUT / f"{name}.wav")], check=True)
        raw.unlink()
    print("wrote", OUT / "mix-music.wav", "and", OUT / "mix-nomusic.wav")


if __name__ == "__main__":
    main()
