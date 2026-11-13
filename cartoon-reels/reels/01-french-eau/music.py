"""Generates the reel's song with the ElevenLabs music model.

Run: python3 music.py   (after timeline.py has written song_plan)
One composition: an instrumental intro as long as the lesson and the English sentence,
then a sung chorus (the stitched French line, male and female duet), then a short tail.
Writes assets/audio/song.mp3 and assets/audio/song.json (sung word timestamps).
The API key is injected by the session's network proxy.
"""
import email
import json
import subprocess
import sys
import unicodedata
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).parent
from variant import AUDIO as OUT, TIMELINE, V
API = "https://api.elevenlabs.io/v1/music/detailed?output_format=mp3_44100_192"

STYLES = {}
STYLES["v2"] = ["105 BPM", "F major", "playful comedic French café pop", "accordion", "pizzicato strings",
         "upright bass", "brush drums", "glockenspiel accents", "warm, bright and bouncy"]
# v3: more engaging, like the reference: a catchy earworm with a bouncy groove and a big singalong chorus
STYLES["v3"] = ["118 BPM", "G major", "catchy upbeat bubblegum pop", "bouncy bassline", "punchy kick and handclaps",
                "plucky synth and ukulele", "whistled hook", "playful, viral, earworm energy"]
# v4: the v3 song, but the music only teases under the conversation and builds towards the drop
STYLES["v4"] = STYLES["v3"]
STYLE = STYLES[V]

LYRICS = ("Le bel oiseau au chapeau,\n"
          "sur le bateau,\n"
          "coupe le gâteau du château au couteau,\n"
          "et tombe à l'eau !")


def plan(intro_ms, sung_ms, outro_ms, lesson_ms=None):
    no_vocals = ["vocals", "singing", "humming", "choir", "spoken words"]
    chorus = {"text": "[Chorus]\n" + LYRICS, "duration_ms": sung_ms,
              "positive_styles": STYLE + ["vocals start on the very first beat, no instrumental lead-in",
                                          "every lyric word sung clearly, none skipped", "full band drop", "handclaps",
                                          "catchy sing-along chorus", "male and female duet singing together in French",
                                          "clear French diction", "big, joyful energy"],
              "negative_styles": ["English lyrics", "rap", "spoken word"]}
    outro = {"text": "[Outro]", "duration_ms": max(3000, outro_ms),  # the API minimum is 3 s; the mix trims it
             "positive_styles": STYLE + ["short final flourish", "one last cymbal hit", "instrumental only"],
             "negative_styles": ["vocals", "singing"]}
    if lesson_ms and V not in ("v2", "v3"):
        # a quiet tease under the conversation, then a build under the English sentence, then the drop
        tease = {"text": "[Instrumental intro, very quiet]", "duration_ms": lesson_ms,
                 "positive_styles": [STYLE[0], STYLE[1], "barely there, very quiet and minimal",
                                     "soft ticking pizzicato pulse", "a faint plucked hint of the chorus melody now and then",
                                     "no drums", "playful suspense", "instrumental only"],
                 "negative_styles": no_vocals + ["drums", "loud", "busy arrangement", "bass drops"]}
        build = {"text": "[Build-up]", "duration_ms": intro_ms - lesson_ms,
                 "positive_styles": [STYLE[0], STYLE[1], "the chorus hook teased on a whistle and plucked synth",
                                     "building anticipation", "a soft kick enters halfway", "rising snare roll and riser in the last bar",
                                     "something big is about to drop", "instrumental only"],
                 "negative_styles": no_vocals}
        return {"chunks": [tease, build, chorus, outro]}
    return {"chunks": [
        {"text": "[Instrumental intro]", "duration_ms": intro_ms,
         "positive_styles": STYLE + ["light and sparse, leaves room for a speaking voice", "instrumental only",
                                     "gentle build in the last bars"],
         "negative_styles": no_vocals},
        chorus, outro]}


def compose(seed, T):
    body = {"composition_plan": plan(T["intro_ms"], T["sung_ms"], T["outro_ms"], T.get("lesson_ms")), "model_id": "music_v2_5",
            "respect_sections_durations": True, "with_timestamps": True, "seed": seed}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST")
    req.add_header("xi-api-key", "proxy-injected")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=600) as r:
        ctype, raw = r.headers.get("Content-Type"), r.read()
    msg = email.message_from_bytes(b"Content-Type: " + ctype.encode() + b"\r\n\r\n" + raw)
    meta, audio = None, None
    for part in msg.walk():
        if part.is_multipart():
            continue
        data = part.get_payload(decode=True)
        if "json" in (part.get_content_type() or ""):
            meta = json.loads(data)
        elif data and len(data) > 10000:
            audio = data
    return audio, meta


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if c.isalnum() and not unicodedata.combining(c))


def heard_words(path, offset):
    """Transcribe the sung part with scribe; its word timings are the ones we trust."""
    clip = path.with_suffix(".chorus.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(offset), "-i", str(path), str(clip)], check=True)
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in (("model_id", "scribe_v1"), ("language_code", "fra"))]
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="c.mp3"\r\n'
                 f'Content-Type: audio/mpeg\r\n\r\n'.encode() + clip.read_bytes() + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=b"".join(parts), method="POST")
    req.add_header("xi-api-key", "proxy-injected")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    clip.unlink()
    return d.get("text", ""), [{"text": w["text"], "start": round(w["start"] + offset, 3), "end": round(w["end"] + offset, 3)}
                               for w in d.get("words", []) if w.get("type") == "word"]


def split_stems(song, folder):
    """Vocals and instrumental stems (ElevenLabs stem separation), for the no-music mix."""
    import io
    import zipfile
    boundary = uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="stem_variation_id"\r\n\r\ntwo_stems_v1\r\n'.encode()
            + f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="song.mp3"\r\n'
              f'Content-Type: audio/mpeg\r\n\r\n'.encode() + song.read_bytes() + f"\r\n--{boundary}--\r\n".encode())
    req = urllib.request.Request("https://api.elevenlabs.io/v1/music/stem-separation", data=body, method="POST")
    req.add_header("xi-api-key", "proxy-injected")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=900) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    folder.mkdir(parents=True, exist_ok=True)
    for name in z.namelist():
        if name in ("vocals.mp3", "instrumental.mp3"):
            (folder / name).write_bytes(z.read(name))
    print("stems:", sorted(p.name for p in folder.iterdir()))


def main(seeds):
    T = json.loads(TIMELINE.read_text())["song_plan"]
    want = [norm(w) for w in LYRICS.split()]
    want = [w for w in want if w]
    OUT.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        audio, meta = compose(seed, T)
        path = OUT / f"song-{seed}.mp3"
        path.write_bytes(audio)
        text, words = heard_words(path, max(0, T["intro_ms"] / 1000 - 1))
        got = [norm(w["text"]) for w in words]
        # how many lyric words were sung, in order
        i = 0
        for g in got:
            if i < len(want) and g == want[i]:
                i += 1
        score = i / len(want)
        print(f"seed {seed}: {score:.0%} of the lyric heard in order: {text}")
        if score >= 0.95:
            path.replace(OUT / "song.mp3")
            (OUT / "song-response.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
            (OUT / "song.json").write_text(json.dumps({"seed": seed, "heard": text, "words": words}, indent=1, ensure_ascii=False))
            print("kept seed", seed)
            split_stems(OUT / "song.mp3", OUT / "stems")
            return True
    print("!! no take sang the whole lyric")
    return False


if __name__ == "__main__":
    seeds = [int(a) for a in sys.argv[1:]] or [11, 23, 37, 41]
    sys.exit(0 if main(seeds) else 1)
