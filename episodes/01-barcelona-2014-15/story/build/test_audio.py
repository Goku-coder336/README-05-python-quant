"""Voice and effects for the 8-second test clip (ElevenLabs: George for the voice, sound effects generated)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "film", "build"))
import voice  # reuses the recording helpers (the key is added by the environment's proxy)

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")
lines = {"t1": ("Iniesta found Rakitić.", None, "One-nil."), "t2": ("One-nil.", "Iniesta found Rakitić.", None)}
for k, (text, prev, nxt) in lines.items():
    p = os.path.join(OUT, f"{k}.mp3")
    if not os.path.exists(p):
        open(p, "wb").write(voice.tts(text, prev, nxt, seed=4242))
sfx = {"kick": "a single clean strike of a leather football by a boot, close, outdoor, short thud",
       "net": "a football hitting the back of a goal net, soft rustle and swish of the net, outdoor",
       "crowd": "a big football stadium crowd erupting into a roar and cheering after a goal, wide and distant, no music"}
dur = {"kick": 0.8, "net": 1.2, "crowd": 5.0}
for k, prompt in sfx.items():
    p = os.path.join(OUT, f"{k}.mp3")
    if not os.path.exists(p):
        body = json.dumps({"text": prompt, "duration_seconds": dur[k], "prompt_influence": 0.5}).encode()
        open(p, "wb").write(voice.post(f"{voice.API}/sound-generation?output_format=mp3_44100_128", body, {"Content-Type": "application/json", "Accept": "audio/mpeg"}))
print(sorted(os.listdir(OUT)))
