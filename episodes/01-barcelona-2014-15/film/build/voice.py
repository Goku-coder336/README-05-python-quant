"""Record the narration with ElevenLabs (George, eleven_multilingual_v2), one file per script line, then check
each line with ElevenLabs speech-to-text (scribe_v1) and re-record any line it mishears.

The API key is a network secret on this environment: the proxy adds it to requests for api.elevenlabs.io,
so the placeholder header here is replaced on the way out.

Writes assets/audio/vo/<line>.mp3 and data/voice_lines.json (duration and word timings per line).
Usage: python build/voice.py [--only 0.1,0.2] [--force]
"""
import argparse
import json
import os
import re
import ssl
import subprocess
import time
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
FILM = os.path.join(HERE, "..")
VO = os.path.join(FILM, "assets", "audio", "vo")
OUT = os.path.join(FILM, "data", "voice_lines.json")
API = "https://api.elevenlabs.io/v1"
GEORGE = "JBFqnCBsd6RMkjVDRZzb"
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else None
HDR = {"xi-api-key": "set-by-proxy", "User-Agent": "run-of-the-champions-film/1.0"}
SETTINGS = {"stability": 0.55, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": True}


def script_lines():
    md = open(os.path.join(FILM, "SCRIPT.md"), encoding="utf-8").read()
    return [(m.group(1), m.group(2).strip()) for m in re.finditer(r"^\*\*(\d\.\d+[bc]?)\*\* (.+)$", md, re.M)]


def post(url, body, headers, timeout=180):
    req = urllib.request.Request(url, data=body, headers={**HDR, **headers}, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise SystemExit(f"ElevenLabs {e.code}: {msg}")


def tts(text, prev_text, next_text, seed):
    body = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS, "seed": seed}
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    return post(f"{API}/text-to-speech/{GEORGE}?output_format=mp3_44100_128", json.dumps(body).encode(),
                {"Content-Type": "application/json", "Accept": "audio/mpeg"})


def stt(path):
    b = uuid.uuid4().hex
    with open(path, "rb") as f:
        audio = f.read()
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n'.encode(),
             f'--{b}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\neng\r\n'.encode(),
             f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="line.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode(),
             audio, f"\r\n--{b}--\r\n".encode()]
    return json.loads(post(f"{API}/speech-to-text", b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={b}"}))


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


def norm_words(text):
    from num2words import num2words
    text = text.replace("90+7", "90 plus 7")
    text = re.sub(r"(\d+)\.(\d+)", lambda m: f"{num2words(int(m.group(1)))} point {' '.join(num2words(int(c)) for c in m.group(2))}", text)
    text = re.sub(r"(\d+)(st|nd|rd|th)\b", lambda m: num2words(int(m.group(1)), to="ordinal"), text)
    text = re.sub(r"\b(19|20)(\d\d)\b", lambda m: f"{num2words(int(m.group(1) + m.group(2)), to='year')}", text)
    text = re.sub(r"\d+", lambda m: num2words(int(m.group(0))), text)
    text = text.lower().replace("’", "'")
    for joined, split in (("quarterfinal", "quarter final"), ("semifinal", "semi final"), ("zero", "nil")):
        text = text.replace(joined, split)
    text = text.replace("-", " ")
    import unicodedata
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return [w for w in re.sub(r"[^a-z' ]", " ", text).split() if w not in ("and", "a", "the")]


def misheard(script, heard):
    """Words of the script missing from what scribe heard (numbers and accents normalised)."""
    h = set(norm_words(heard))
    return [w for w in norm_words(script) if w not in h and w.strip("'") not in h]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    os.makedirs(VO, exist_ok=True)
    lines = script_lines()
    only = set(a.only.split(",")) if a.only else None
    data = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for i, (lid, text) in enumerate(lines):
        if only and lid not in only:
            continue
        path = os.path.join(VO, f"{lid}.mp3")
        if os.path.exists(path) and lid in data and not a.force and not only:
            continue
        prev_text = lines[i - 1][1] if i else None
        next_text = lines[i + 1][1] if i + 1 < len(lines) else None
        for take in range(3):
            open(path, "wb").write(tts(text, prev_text, next_text, seed=1000 + i * 7 + take))
            res = stt(path)
            heard = res.get("text", "")
            miss = misheard(text, heard)
            if not miss:
                break
            print(f"  {lid} take {take + 1} misheard {miss}: {heard!r}")
        words = [{"w": w["text"], "s": round(w["start"], 3), "e": round(w["end"], 3)} for w in res.get("words", []) if w.get("type") == "word"]
        data[lid] = {"text": text, "heard": heard, "dur": round(duration(path), 3), "words": words, "flag": miss}
        json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)
        print(f"{lid} {data[lid]['dur']:5.2f}s {'CHECK ' + str(miss) if miss else 'ok'}")
    print("total", round(sum(v["dur"] for v in data.values()), 1), "s over", len(data), "lines")


if __name__ == "__main__":
    main()
