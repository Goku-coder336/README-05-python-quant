"""Make the Episode 1 voiceover offline with Kokoro (Apache 2.0) and record when each line starts.

Reads the 79 script lines from ../script.md, speaks each one, joins them with short pauses (longer at
chapter starts), normalises loudness, and writes:
  ../remotion/public/voiceover.wav       the full voiceover
  ../remotion/src/data/voice.json        real start/end of every line, plus the script's estimates
Model files: ~/.cache/kokoro/kokoro-v1.0.onnx and voices-v1.0.bin (from huggingface.co/fastrtc/kokoro-onnx).

Usage: python voiceover.py [--voice bf_emma] [--speed 0.95] [--lines 1-5]
"""
import argparse
import json
import os
import re
import subprocess
import tempfile

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.join(HERE, "..")
MODEL = os.path.expanduser("~/.cache/kokoro/kokoro-v1.0.onnx")
VOICES = os.path.expanduser("~/.cache/kokoro/voices-v1.0.bin")

# Chapter starts (from script.md): a longer pause goes before these lines
CHAPTER_STARTS = {7, 14, 27, 33, 39, 49, 63}
GAP = 0.40       # seconds between lines
CHAPTER_GAP = 1.0
LEAD_IN = 0.5

# Spoken spellings only (the screen keeps the real names). Chosen by checking Kokoro's phonemes:
# Suárez sjˈuːəɹɛz -> swˈɑːɹɛz, APOEL ɐpˈəʊl -> ɐpˈəʊɛl, Xavi zˈavi -> ʃˈavi,
# Neymar nˈeɪmə -> neɪmˈɑː, Rakitić ɹakˈɪtɪk -> ɹˈakɪtɪtʃ.
RESPELL = {"Suárez": "Swahrez", "APOEL": "Apo-el", "Xavi": "Shavi", "Neymar": "Neymaar", "Rakitić": "Rakitich"}


def script_lines():
    md = open(os.path.join(EP, "script.md"), encoding="utf-8").read()
    rows = re.findall(r"\*\*L(\d\d)\*\* `(\d+):(\d\d)`  (.+?)  $", md, re.M)
    return [(int(n), int(m) * 60 + int(s), text.strip()) for n, m, s, text in rows]


def spoken(text):
    for a, b in RESPELL.items():
        text = text.replace(a, b)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="bf_emma")
    ap.add_argument("--speed", type=float, default=0.95)
    ap.add_argument("--lines", default=None, help="e.g. 1-5, for a quick test")
    a = ap.parse_args()

    from kokoro_onnx import Kokoro
    k = Kokoro(MODEL, VOICES)
    rows = script_lines()
    assert len(rows) == 79, len(rows)
    if a.lines:
        lo, hi = map(int, a.lines.split("-"))
        rows = [r for r in rows if lo <= r[0] <= hi]

    sr = 24000
    pieces, timing, t = [np.zeros(int(LEAD_IN * sr), np.float32)], [], LEAD_IN
    for n, est, text in rows:
        if timing:
            gap = CHAPTER_GAP if n in CHAPTER_STARTS else GAP
            pieces.append(np.zeros(int(gap * sr), np.float32))
            t += gap
        audio, sr = k.create(spoken(text), voice=a.voice, speed=a.speed, lang="en-gb")
        audio = np.asarray(audio, np.float32)
        # trim the model's own leading/trailing silence so the timings are tight
        nz = np.where(np.abs(audio) > 0.01)[0]
        if len(nz):
            audio = audio[max(0, nz[0] - int(0.03 * sr)): nz[-1] + int(0.08 * sr)]
        dur = len(audio) / sr
        timing.append({"line": n, "start": round(t, 3), "end": round(t + dur, 3), "est": est, "text": text})
        pieces.append(audio)
        t += dur
        print(f"L{n:02d} {t - dur:7.2f}s  {dur:5.2f}s  {text[:60]}")
    pieces.append(np.zeros(int(1.0 * sr), np.float32))
    full = np.concatenate(pieces)

    out_wav = os.path.join(EP, "remotion", "public", "voiceover.wav")
    os.makedirs(os.path.dirname(out_wav), exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        raw = os.path.join(d, "raw.wav")
        sf.write(raw, full, sr)
        # loudness for YouTube speech: -16 LUFS integrated, peaks under -1.5 dBTP; keep 48 kHz for video
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "1", out_wav], check=True)
    out_json = os.path.join(EP, "remotion", "src", "data", "voice.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"voice": a.voice, "speed": a.speed, "duration": round(len(full) / sr, 3),
                   "lines": timing}, f, ensure_ascii=False, indent=1)
    print(f"total {len(full) / sr:.1f}s -> {out_wav}")


if __name__ == "__main__":
    main()
