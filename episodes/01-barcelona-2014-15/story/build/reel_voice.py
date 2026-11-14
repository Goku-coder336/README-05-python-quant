"""Narration for the 60-second reel: ElevenLabs George, each line checked with speech to text."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "film", "build"))
import voice

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio", "reel")
LINES = [
    ("r1", "Three forwards. One season. Messi. Suárez. Neymar."),
    ("r2", "Group stage. Messi scores eight of Barcelona's fifteen goals, three of them in one night in Cyprus."),
    ("r3", "Round of sixteen. In Manchester, Suárez scores twice."),
    ("r4", "Quarter-final. Paris. Suárez twice more, Neymar three times."),
    ("r5", "Semi-final. Bayern. Messi twice, and Neymar in both legs."),
    ("r6", "Berlin. Four minutes in, Rakitić."),
    ("r7", "Messi runs at Juventus. Buffon saves. Suárez scores."),
    ("r8", "And in stoppage time, Neymar."),
    ("r9", "Champions of Europe. The treble, again. Messi, Suárez and Neymar: twenty-seven of Barcelona's thirty-one goals."),
]
def norm(s):
    s = s.lower().replace("quarter-final", "quarterfinal").replace("semi-final", "semifinal")
    for a, b in (("á", "a"), ("ć", "c"), ("é", "e")): s = s.replace(a, b)
    return re.sub(r"[^a-z0-9 ]", " ", s).split()
info = {}
for i, (k, text) in enumerate(LINES):
    p = os.path.join(OUT, f"{k}.mp3")
    prev = LINES[i - 1][1] if i else None
    nxt = LINES[i + 1][1] if i + 1 < len(LINES) else None
    for take in range(3):
        if not os.path.exists(p) or take:
            open(p, "wb").write(voice.tts(text, prev, nxt, seed=900 + i * 11 + take))
        heard = voice.stt(p).get("text", "")
        miss = [w for w in norm(text) if w not in norm(heard)]
        if not miss: break
        print(k, "take", take, "missing", miss, "heard:", heard)
    d = float(os.popen(f"ffprobe -v error -show_entries format=duration -of csv=p=0 {p}").read())
    info[k] = {"text": text, "dur": round(d, 2), "heard": heard}
    print(k, round(d, 2), heard)
json.dump(info, open(os.path.join(OUT, "lines.json"), "w"), indent=1, ensure_ascii=False)
