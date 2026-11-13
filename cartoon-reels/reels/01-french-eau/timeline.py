"""Builds the reel's timing from the real voice line lengths.

Run: python3 timeline.py
Reads assets/vo/*.mp3, writes trimmed mono WAVs to assets/vo/trim/, mouth-flap
keys from each line's loudness, and timeline.json (every event in seconds).
"""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
VO = HERE / "assets" / "vo"
TRIM = VO / "trim"
SR = 44100
BPM = 105
BEAT = 60 / BPM
BAR = 4 * BEAT

# lesson items: (english cue line, french answer line, english label, french word on screen, gesture)
WORDS = [
    ("t-water", "t-eau", "water", "EAU", "fade"),
    ("t-high", "t-haut", "high", "HAUT", "point"),
    ("SAME",),
    ("t-hat", "t-chapeau", "hat", "CHAPEAU", "tap"),
    ("t-bird", "t-oiseau", "bird", "OISEAU", "hop"),
    ("t-boat", "t-bateau", "boat", "BATEAU", "tilt"),
    ("t-cake", "t-gateau", "cake", "GÂTEAU", "hop"),
    ("t-castle", "t-chateau", "castle", "CHÂTEAU", "point"),
    ("t-knife", "t-couteau", "knife", "COUTEAU", "bighop"),
]

PAYOFF = [  # (bar, lines that play, french on screen, english under it)
    (0, ["t-p1"], "Le bel oiseau<br>au chapeau,", "The fine bird in a hat,"),
    (1, ["p-p2"], "sur le bateau,", "on the boat,"),
    (2, ["t-p3", "p-p3"], "coupe le gâteau<br>du château<br>au couteau…", "cuts the castle's cake with a knife…"),
    (3, ["t-p4", "p-p4"], "et tombe<br>à l'eau.", "and falls in the water."),
]


def load(lid):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(VO / f"{lid}.mp3"), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def trim(x, db=-38, pad=0.03):
    env = np.abs(x)
    thr = 10 ** (db / 20) * max(env.max(), 1e-6)
    idx = np.where(env > thr)[0]
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def flaps(x, fps=15, db=-26):
    """Open/closed mouth keys at 15 a second from the line's loudness."""
    hop = SR // fps
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    thr = 10 ** (db / 20) * max(rms.max(), 1e-6)
    keys, state = [], False
    for i, r in enumerate(rms):
        # alternate open/closed while loud, so the mouth flaps instead of hanging open
        want = bool(r > thr) and (i % 2 == 0)
        if want != state:
            keys.append([round(i / fps, 3), int(want)])
            state = want
    if state:
        keys.append([round(n / fps, 3), 0])
    return keys


def main():
    TRIM.mkdir(parents=True, exist_ok=True)
    lines = json.loads((VO / "lines.json").read_text())
    info = {}
    for lid in lines:
        x = trim(load(lid))
        (TRIM / f"{lid}.f32").write_bytes(x.astype(np.float32).tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                        "-i", str(TRIM / f"{lid}.f32"), str(TRIM / f"{lid}.wav")], check=True)
        (TRIM / f"{lid}.f32").unlink()
        info[lid] = {"dur": round(len(x) / SR, 3), "flaps": flaps(x)}

    ev = {"bpm": BPM, "beat": round(BEAT, 4), "bar": round(BAR, 4), "voice": [], "items": []}

    def say(lid, t, who):
        ev["voice"].append({"id": lid, "t": round(t, 3), "dur": info[lid]["dur"], "who": who,
                            "flaps": info[lid]["flaps"]})
        return t + info[lid]["dur"]

    # hook
    t = 0.0
    end = say("t-hook", 0.15, "t")
    ev["hook"] = {"start": 0.0, "end": round(end + 0.35, 3)}
    t = end + 0.35

    for w in WORDS:
        if w[0] == "SAME":
            start = t
            v = start + 0.55  # a beat of silence before the deadpan
            end = say("t-same", v, "t")
            ev["items"].append({"kind": "same", "start": round(start, 3), "say": round(v, 3), "end": round(end + 0.55, 3)})
            t = end + 0.55
            continue
        cue, ans, label, word, gesture = w
        start = t
        a = say(cue, start, "t") + 0.32  # half a beat to guess
        end = say(ans, a, "t")
        ev["items"].append({"kind": "word", "start": round(start, 3), "answer": round(a, 3), "end": round(end + 0.55, 3),
                            "cue": label, "word": word, "gesture": gesture})
        t = end + 0.55

    ts = t
    end = say("t-try", ts, "t")
    ev["try"] = {"start": round(ts, 3), "end": round(end + 0.15, 3)}

    # the payoff starts on the next whole beat after the turn
    p = np.ceil((end + 0.15) / BEAT) * BEAT
    ev["payoff"] = {"start": round(float(p), 3), "end": round(float(p + 4 * BAR), 3), "lines": []}
    for bar, ids, fr, en in PAYOFF:
        bt = p + bar * BAR
        for lid in ids:
            who = "t" if lid.startswith("t-") else "p"
            say(lid, bt + 0.04, who)
        ev["payoff"]["lines"].append({"bar": bar, "start": round(float(bt), 3), "fr": fr, "en": en})
    # the laugh: "l'eau" lands near the end of the last phrase
    last = max(info[l]["dur"] for l in PAYOFF[-1][1])
    ev["payoff"]["splash"] = round(float(p + 3 * BAR + 0.04 + last - 0.2), 3)

    b = float(p + 4 * BAR)
    end = say("t-easy", b + 0.15, "t")
    ev["button"] = {"start": round(b, 3), "end": round(max(end + 0.6, b + 1.5), 3)}
    ev["total"] = ev["button"]["end"]

    (HERE / "timeline.json").write_text(json.dumps(ev, indent=1, ensure_ascii=False))
    print(f"hook 0 - {ev['hook']['end']}, lesson to {ts:.2f}, payoff {p:.2f} - {p + 4 * BAR:.2f}, total {ev['total']:.2f} s")
    for it in ev["items"]:
        print(f"  {it['kind']:4} {it['start']:6.2f} - {it['end']:6.2f}  {it.get('word', 'SAME')}")


if __name__ == "__main__":
    main()
