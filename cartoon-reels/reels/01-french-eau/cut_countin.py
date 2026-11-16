"""Make v5: the v4 + drawings reel with the "NOW IN FRENCH 1, 2, 3" count-in cut out.

The cut is two bars of the song (8 beats at about 117 BPM, measured from the instrumental stem),
from just after Barnaby finishes the English sentence (25.4 s) to the chorus drop (29.5 s),
so the music stays on the beat and the reel jumps straight from the English line into the singing.
Audio gets a 20 ms crossfade at the join so there is no click.

python3 cut_countin.py
"""
import subprocess

A, B = 25.4, 29.5          # frame-exact at 30 fps (frames 762 and 885)
SRC = "renders/01-french-eau-v4-drawings-music.mp4"
MIXES = {"music": "assets/audio/v4/mix-music.wav", "nomusic": "assets/audio/v4/mix-nomusic.wav"}

for name, wav in MIXES.items():
    out = f"renders/01-french-eau-v5-{name}.mp4"
    fc = (f"[0:v]trim=0:{A},setpts=PTS-STARTPTS[v0];[0:v]trim=start={B},setpts=PTS-STARTPTS[v1];"
          f"[v0][v1]concat=n=2:v=1:a=0[v];"
          f"[1:a]atrim=0:{A + 0.01},asetpts=PTS-STARTPTS[a0];[1:a]atrim=start={B - 0.01},asetpts=PTS-STARTPTS[a1];"
          f"[a0][a1]acrossfade=d=0.02:c1=tri:c2=tri[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC, "-i", wav, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    print("wrote", out)
