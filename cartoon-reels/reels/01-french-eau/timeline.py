"""Builds the reel's timing from the real voice line lengths and the song.

Run: python3 timeline.py   (before and again after music.py)
Reads assets/vo/*.mp3 (trims them into assets/vo/trim/) and, once it exists,
assets/audio/song.json (the sung words' timestamps). Writes timeline.json.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
VO = HERE / "assets" / "vo"
TRIM = VO / "trim"
from variant import AUDIO, TIMELINE

SONG = AUDIO / "song.json"
SR = 44100

SUNG_MS = 13000   # length of the sung chorus
OUTRO_MS = 2000   # instrumental tail under the button

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

ENGLISH = [  # the sentence in English, read by the teacher, one phrase on screen at a time
    ("t-en1", "The fine bird<br>in a hat,"),
    ("t-en2", "on the boat,"),
    ("t-en3", "cuts the castle's cake<br>with a knife…"),
    ("t-en4", "and falls<br>in the water."),
]

LYRICS = [  # sung lines: (first word, french on screen, english under it)
    ("le", "Le bel oiseau<br>au chapeau,", "The fine bird in a hat,"),
    ("sur", "sur le bateau,", "on the boat,"),
    ("coupe", "coupe le gâteau<br>du château<br>au couteau…", "cuts the castle's cake with a knife…"),
    ("et", "et tombe<br>à l'eau !", "and falls in the water!"),
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
        want = bool(r > thr) and (i % 2 == 0)  # alternate while loud, so the mouth flaps
        if want != state:
            keys.append([round(i / fps, 3), int(want)])
            state = want
    if state:
        keys.append([round(n / fps, 3), 0])
    return keys


def sung_flaps(words, start):
    """Mouth keys for singing: open and close about 8 times a second inside each sung word."""
    keys = []
    for w in words:
        a, b = w["start"] - start, w["end"] - start
        t = a
        while t < b - 0.03:
            keys.append([round(t, 3), 1])
            keys.append([round(min(b, t + 0.08), 3), 0])
            t += 0.125
    return keys


def main():
    TRIM.mkdir(parents=True, exist_ok=True)
    lines = json.loads((VO / "lines.json").read_text())
    info = {}
    for lid in lines:
        x = trim(load(lid))
        f32 = TRIM / f"{lid}.f32"
        f32.write_bytes(x.astype(np.float32).tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1",
                        "-i", str(f32), str(TRIM / f"{lid}.wav")], check=True)
        f32.unlink()
        info[lid] = {"dur": round(len(x) / SR, 3), "flaps": flaps(x)}

    ev = {"voice": [], "items": [], "english": []}

    def say(lid, t, who="t"):
        ev["voice"].append({"id": lid, "t": round(t, 3), "dur": info[lid]["dur"], "who": who, "flaps": info[lid]["flaps"]})
        return t + info[lid]["dur"]

    end = say("t-hook", 0.15)
    ev["hook"] = {"start": 0.0, "end": round(end + 0.35, 3)}
    t = end + 0.35

    for w in WORDS:
        if w[0] == "SAME":
            v = t + 0.55  # a beat of silence before the deadpan
            end = say("t-same", v)
            ev["items"].append({"kind": "same", "start": round(t, 3), "say": round(v, 3), "end": round(end + 0.5, 3)})
            t = end + 0.5
            continue
        cue, ans, label, word, gesture = w
        a = say(cue, t) + 0.3  # a moment to guess
        end = say(ans, a)
        ev["items"].append({"kind": "word", "start": round(t, 3), "answer": round(a, 3), "end": round(end + 0.5, 3),
                            "cue": label, "word": word, "gesture": gesture})
        t = end + 0.5

    end = say("t-try", t)
    ev["try"] = {"start": round(t, 3), "end": round(end + 0.25, 3)}
    t = end + 0.25
    for lid, text in ENGLISH:
        end = say(lid, t)
        ev["english"].append({"start": round(t, 3), "end": round(end + 0.2, 3), "text": text})
        t = end + 0.2
    ev["english"][-1]["end"] = round(t + 0.3, 3)

    # the song: an instrumental intro under everything so far, then the sung chorus, then a short tail
    intro = round(t + 0.3, 3)
    ev["song_plan"] = {"intro_ms": int(intro * 1000), "sung_ms": SUNG_MS, "outro_ms": OUTRO_MS}
    p0, p1 = intro, round(intro + SUNG_MS / 1000, 3)
    ev["payoff"] = {"start": p0, "end": p1, "lines": []}

    if SONG.exists():
        song = json.loads(SONG.read_text())
        words = [w for w in song["words"] if p0 - 0.5 <= w["start"] < p1 + 0.5]
        # the song's chorus has a band lead-in: hold the lesson scene as a count-in and cut on the first sung word
        if words:
            p0 = round(max(intro, words[0]["start"] - 0.35), 3)
            ev["payoff"]["start"] = p0
        ev["count_in"] = {"start": intro, "end": p0}
        # each lyric line starts at its first word
        idx = 0
        for first, fr, en in LYRICS:
            while idx < len(words) and not words[idx]["text"].lower().strip(" ,.!?…'").startswith(first):
                idx += 1
            st = words[idx]["start"] if idx < len(words) else None
            ev["payoff"]["lines"].append({"start": st, "fr": fr, "en": en})
            idx += 1
        # fill any line the timestamps missed, evenly between its neighbours
        for i, ln in enumerate(ev["payoff"]["lines"]):
            if ln["start"] is None:
                prev = ev["payoff"]["lines"][i - 1]["start"] if i else p0
                ln["start"] = round(prev + (p1 - p0) / 5, 3)
            ln["start"] = round(max(p0, ln["start"] - 0.08), 3)
        eau = [w for w in words if "eau" in w["text"].lower() and w["start"] > ev["payoff"]["lines"][-1]["start"]]
        ev["payoff"]["splash"] = round(eau[-1]["start"], 3) if eau else round(p1 - 1.2, 3)
        ev["payoff"]["flaps"] = sung_flaps(words, p0)
        # don't let the chorus drag: cut to the button 1.6 s after the splash
        p1 = round(min(p1, ev["payoff"]["splash"] + 1.6), 3)
        ev["payoff"]["end"] = p1
    else:
        for i, (_, fr, en) in enumerate(LYRICS):
            ev["payoff"]["lines"].append({"start": round(p0 + i * (p1 - p0) / 4, 3), "fr": fr, "en": en})
        ev["payoff"]["splash"] = round(p1 - 1.2, 3)
        ev["payoff"]["flaps"] = []
        ev["count_in"] = {"start": intro, "end": p0}

    b = p1
    end = say("t-easy", b + 0.15)
    ev["button"] = {"start": b, "end": round(max(end + 0.6, b + OUTRO_MS / 1000), 3)}
    ev["total"] = ev["button"]["end"]

    TIMELINE.write_text(json.dumps(ev, indent=1, ensure_ascii=False))
    print(f"hook to {ev['hook']['end']}, lesson to {ev['try']['start']}, english {ev['english'][0]['start']}-{intro}, "
          f"sung {p0}-{p1}, total {ev['total']} s  (song timings: {'yes' if SONG.exists() else 'not yet'})")


if __name__ == "__main__":
    main()
