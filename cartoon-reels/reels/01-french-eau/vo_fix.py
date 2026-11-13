"""Re-record lines until ElevenLabs speech-to-text hears the intended French.

Run: python3 vo_fix.py t-p4 p-p2 ...   (line ids from vo.py)
For each line it tries both models over a few takes, transcribes each take with
scribe_v1 and keeps the first one whose transcript matches the script.
"""
import json
import subprocess
import sys
import unicodedata
import uuid
import urllib.request

from vo import API, LINES, OUT, call, duration

MODELS = [("eleven_multilingual_v2", None), ("eleven_turbo_v2_5", "fr")]
TAKES = 3


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return "".join(c for c in s if c.isalnum())


def transcribe(path):
    boundary = uuid.uuid4().hex
    parts = [
        f'--{boundary}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n'.encode(),
        f'--{boundary}\r\nContent-Disposition: form-data; name="language_code"\r\n\r\nfra\r\n'.encode(),
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode()
        + path.read_bytes() + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    req = urllib.request.Request(API + "/speech-to-text", data=b"".join(parts), method="POST")
    req.add_header("xi-api-key", "proxy-injected")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read()).get("text", "")


def main(ids):
    voices = {v["name"].split(" ")[0]: v["voice_id"] for v in json.loads(call("/voices"))["voices"]}
    lines = {l[0]: l for l in LINES}
    meta = json.loads((OUT / "lines.json").read_text())
    for lid in ids:
        _, voice, text, lang, settings = lines[lid]
        best = None
        for model, code in MODELS:
            for take in range(TAKES):
                s = dict(settings, stability=min(0.9, settings["stability"] + 0.1 * take))
                body = {"text": text, "voice_settings": s, "model_id": model}
                if code:
                    body["language_code"] = code
                tmp = OUT / f"{lid}.try.mp3"
                tmp.write_bytes(call(f"/text-to-speech/{voices[voice]}?output_format=mp3_44100_128", body))
                heard = transcribe(tmp)
                ok = norm(heard) == norm(text)
                print(f"{lid:10} {model:24} take {take + 1}: heard {heard!r} {'OK' if ok else ''}")
                if ok:
                    best = tmp
                    break
            if best:
                break
        if best:
            best.replace(OUT / f"{lid}.mp3")
            meta[lid]["seconds"] = duration(OUT / f"{lid}.mp3")
            meta[lid]["verified"] = True
        else:
            (OUT / f"{lid}.try.mp3").unlink(missing_ok=True)
            print(f"!! {lid}: no take matched; kept the original")
    (OUT / "lines.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
