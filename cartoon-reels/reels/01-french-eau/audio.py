"""Music, sound effects and the two final mixes, generated with numpy.

Run: python3 audio.py   (after timeline.py)
Writes assets/audio/mix-music.wav and assets/audio/mix-nomusic.wav,
both loudness-normalised to about -15 LUFS.
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).parent
SR = 44100
OUT = HERE / "assets" / "audio"
rng = np.random.default_rng(7)  # seeded: the same mix every run

T = json.loads((HERE / "timeline.json").read_text())
BEAT, BAR = T["beat"], T["bar"]
N = int((T["total"] + 0.5) * SR)


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
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    return e


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------- instruments ---
def kick(big=False):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + (130 if big else 90) * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.22 if big else 0.14)
    return x * (1.0 if big else 0.7)


def clap():
    n = int(0.2 * SR)
    x = bp(rng.standard_normal(n), 900, 3500) * env(n, 0.001, 0.06)
    return x * 0.45


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.06 if open_ else 0.015) * 0.18


def pluck(m, dur=0.35, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = midi(m)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * bright * np.sin(4 * np.pi * f * t) + 0.12 * bright * np.sin(6 * np.pi * f * t))
    return x * env(n, 0.002, 0.12) * 0.22


def bass(m, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * midi(m) * t) + 0.25 * np.sin(4 * np.pi * midi(m) * t)
    e = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03).clip(0, 1)
    return x * e * 0.32


def stab(chord, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(np.sign(np.sin(2 * np.pi * midi(m) * t)) * 0.5 + np.sin(2 * np.pi * midi(m) * 1.003 * t) for m in chord)
    return lp(x, 3200) * env(n, 0.003, 0.12) * 0.07


# F major, two-bar cycle of four chords (half a bar each): F, Dm, Bb, C
CHORDS = [[65, 69, 72], [62, 65, 69], [58, 62, 65], [60, 64, 67]]
ROOTS = [41, 38, 46, 36]


def chord_at(t, start):
    i = int(((t - start) / (BAR / 2))) % 4
    return CHORDS[i], ROOTS[i]


def lesson_music(m, start, end):
    t = start
    k = 0
    while t < end - 1e-6:
        ch, root = chord_at(t, start)
        beat_in_bar = k % 4
        if beat_in_bar in (0, 2):
            put(m, kick(), t)
        if beat_in_bar in (1, 3):
            put(m, clap() * 0.6, t)
        put(m, hat(), t + BEAT / 2)
        if beat_in_bar in (0, 2):
            put(m, bass(root, BEAT * 0.9), t)
        # bouncy pluck arpeggio, eighth notes
        for j, off in enumerate((0, BEAT / 2)):
            put(m, pluck(ch[(k * 2 + j) % 3] + 12, 0.3), t + off)
        t += BEAT
        k += 1


def payoff_music(m, start, splash):
    for k in range(16):
        t = start + k * BEAT
        b = k % 4
        last_bar = k >= 12
        if last_bar and b >= 2:
            continue  # the beat drops out before "l'eau"
        ch, root = chord_at(t, start)
        put(m, kick(big=True), t)
        if b in (1, 3):
            put(m, clap(), t)
        put(m, hat(open_=True), t + BEAT / 2)
        put(m, hat(), t + BEAT / 4)
        put(m, hat(), t + 3 * BEAT / 4)
        put(m, bass(root, BEAT * 0.45), t)
        put(m, bass(root, BEAT * 0.4), t + BEAT / 2)
        put(m, stab([c + 12 for c in ch]), t + BEAT / 2)
        for j in range(4):
            put(m, pluck(ch[(k + j) % 3] + 24, 0.18, bright=1.4) * 0.7, t + j * BEAT / 4)
    # the hit on the laugh, then a last chord ringing out
    put(m, kick(big=True) * 1.2, splash)
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    ring = sum(np.sin(2 * np.pi * midi(c) * tt) for c in [53, 65, 69, 72]) * env(n, 0.005, 0.6) * 0.09
    put(m, ring, splash)


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
    # sweep a band-pass upwards by blending three bands
    lo, mid, hi = bp(x, 300, 900), bp(x, 900, 2500), bp(x, 2500, 7000)
    w = t / d
    y = lo * (1 - w) + mid * np.sin(np.pi * w) + hi * w
    return y * np.sin(np.pi * w) ** 2 * 0.5


def riser(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 200 * 2 ** (3 * t / d)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.08
    noise = hp(rng.standard_normal(n), 2000) * 0.06
    return (tone + noise) * (t / d) ** 2


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


def sting():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * midi(77) * t) + np.sin(2 * np.pi * midi(84) * t)) * env(n, 0.002, 0.18) * 0.12


# -------------------------------------------------------------------- voice ---
def load(lid):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HERE / "assets/vo/trim" / f"{lid}.wav"), "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    voice, sfx, music = buf(), buf(), buf()
    for v in T["voice"]:
        both = sum(1 for w in T["voice"] if abs(w["t"] - v["t"]) < 1e-3)
        put(voice, load(v["id"]), v["t"], 0.75 if both > 1 else 1.0)

    p0, p1 = T["payoff"]["start"], T["payoff"]["end"]
    lesson_music(music, 0.0, T["try"]["start"])
    put(music, riser(p0 - T["try"]["start"]), T["try"]["start"])
    payoff_music(music, p0, T["payoff"]["splash"])
    put(music, sting(), T["button"]["start"] + 0.75)

    # effects
    put(sfx, pop(), 0.0)
    for it in T["items"]:
        if it["kind"] == "word":
            put(sfx, tick(), it["start"])
            put(sfx, pop(), it["answer"])
        else:
            put(sfx, pop() * 0.8, it["start"])
            put(sfx, tick(), it["say"] - 0.05)
    put(sfx, whoosh(0.4), T["try"]["start"] + 0.05)
    put(sfx, whoosh(0.35), p0 - 0.15)
    for ln in T["payoff"]["lines"]:
        put(sfx, pop() * 0.7, ln["start"])
    put(sfx, splash(), T["payoff"]["splash"])
    put(sfx, whoosh(0.3), T["button"]["start"] - 0.12)

    # duck the music under the voice (about -7 dB in the lesson, -3 dB in the payoff)
    active = np.convolve((np.abs(voice) > 0.01).astype(float), np.ones(int(0.05 * SR)), "same") > 0
    duck = np.where(active, 0.45, 1.0)
    pay = (np.arange(N) / SR >= p0) & (np.arange(N) / SR < p1)
    duck[pay & active] = 0.7
    sm = int(0.12 * SR)
    duck = np.convolve(duck, np.ones(sm) / sm, "same")
    music *= duck

    for name, x in (("mix-music", voice + sfx + music * 0.8), ("mix-nomusic", voice + sfx)):
        x = x / max(1e-6, np.abs(x).max()) * 0.9
        raw = OUT / f"{name}.raw.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        str(raw)], input=x.astype(np.float64).tobytes(), check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                        "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "2", str(OUT / f"{name}.wav")],
                       check=True)
        raw.unlink()
    print("wrote", OUT / "mix-music.wav", "and", OUT / "mix-nomusic.wav")


if __name__ == "__main__":
    main()
