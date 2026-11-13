"""Record every voice line with ElevenLabs, one file per line, and measure it.

The API key is injected by the session's network proxy; it is never in this file.
Run: python3 vo.py            (records lines that are missing)
     python3 vo.py --force    (re-records everything)
Writes assets/vo/<id>.mp3 and assets/vo/lines.json (durations in seconds).
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
OUT = Path(__file__).parent / "assets" / "vo"

# Voice names as they appear in the ElevenLabs library.
TEACHER = "George"
PARTNER = "Laura"

DEADPAN = {"stability": 0.75, "similarity_boost": 0.8, "style": 0.05, "use_speaker_boost": True}
ENERGY = {"stability": 0.35, "similarity_boost": 0.8, "style": 0.6, "use_speaker_boost": True}

# id, voice, text, language ("en" or "fr"), settings
LINES = [
    ("t-hook", TEACHER, "French is easy.", "en", DEADPAN),
    ("t-water", TEACHER, "Water.", "en", DEADPAN),
    ("t-eau", TEACHER, "Eau.", "fr", DEADPAN),
    ("t-high", TEACHER, "High.", "en", DEADPAN),
    ("t-haut", TEACHER, "Haut.", "fr", DEADPAN),
    ("t-same", TEACHER, "Same.", "en", DEADPAN),
    ("t-hat", TEACHER, "Hat.", "en", DEADPAN),
    ("t-chapeau", TEACHER, "Chapeau.", "fr", DEADPAN),
    ("t-bird", TEACHER, "Bird.", "en", DEADPAN),
    ("t-oiseau", TEACHER, "Oiseau.", "fr", DEADPAN),
    ("t-boat", TEACHER, "Boat.", "en", DEADPAN),
    ("t-bateau", TEACHER, "Bateau.", "fr", DEADPAN),
    ("t-cake", TEACHER, "Cake.", "en", DEADPAN),
    ("t-gateau", TEACHER, "Gâteau.", "fr", DEADPAN),
    ("t-castle", TEACHER, "Castle.", "en", DEADPAN),
    ("t-chateau", TEACHER, "Château.", "fr", DEADPAN),
    ("t-knife", TEACHER, "Knife.", "en", DEADPAN),
    ("t-couteau", TEACHER, "Couteau.", "fr", DEADPAN),
    ("t-try", TEACHER, "Now try this.", "en", DEADPAN),
    ("t-easy", TEACHER, "Easy.", "en", DEADPAN),
    # payoff chant, one phrase per bar
    ("t-p1", TEACHER, "Le bel oiseau au chapeau !", "fr", ENERGY),
    ("p-p2", PARTNER, "Sur le bateau !", "fr", ENERGY),
    ("t-p3", TEACHER, "Coupe le gâteau du château au couteau !", "fr", ENERGY),
    ("p-p3", PARTNER, "Coupe le gâteau du château au couteau !", "fr", ENERGY),
    ("t-p4", TEACHER, "Et tombe à l'eau !", "fr", ENERGY),
    ("p-p4", PARTNER, "Et tombe à l'eau !", "fr", ENERGY),
]


def call(path, body=None):
    req = urllib.request.Request(API + path, method="POST" if body else "GET")
    req.add_header("xi-api-key", "proxy-injected")  # replaced by the proxy
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def duration(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(f)], capture_output=True, text=True)
    return round(float(out.stdout.strip()), 3)


def main(force):
    OUT.mkdir(parents=True, exist_ok=True)
    voices = {v["name"].split(" ")[0]: v["voice_id"] for v in json.loads(call("/voices"))["voices"]}
    meta = {}
    for lid, voice, text, lang, settings in LINES:
        f = OUT / f"{lid}.mp3"
        if force or not f.exists():
            body = {"text": text, "voice_settings": settings}
            if lang == "fr":
                # turbo v2.5 takes a language code, which forces French pronunciation of single words
                body.update(model_id="eleven_turbo_v2_5", language_code="fr")
            else:
                body.update(model_id="eleven_multilingual_v2")
            f.write_bytes(call(f"/text-to-speech/{voices[voice]}?output_format=mp3_44100_128", body))
        meta[lid] = {"voice": voice, "text": text, "lang": lang, "seconds": duration(f)}
        print(f"{lid:12} {meta[lid]['seconds']:5.2f}s  {text}")
    (OUT / "lines.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main("--force" in sys.argv)
