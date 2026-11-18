"""Edit the Blue Saree reel: Kling clips -> one 9:16 video cut to Nenchaadiye (0:12.85 onward).
Shots overlap with soft dissolves centred on bar lines; slight slow motion; warm grade; long fade-out ending.
usage: python3 anims/blue-saree/edit_reel.py <song.mp3> <out.mp4>
"""
import subprocess, sys
song, out = sys.argv[1], sys.argv[2]
C = "assets/blue-saree/clips"
BAR, START = 2.9091, 12.85
XF = 0.6  # dissolve length (s)
# (clip, bars on screen, extra filter)
PLAN = [("shot01", 1.5, ""), ("shot02b", 1.5, ""), ("shot03", 1, "crop=540:960:110:300,"), ("shot04", 1, ""),
        ("shot05", 1, ""), ("shot06", 1, ""), ("shot07", 1.5, ""), ("shot09", 1, ""), ("shot10", 1.5, "")]
ENDHOLD = 1.6  # extra slow tail on the final shot for a soft ending
args, f, durs = [], [], []
for i, (name, bars, ex) in enumerate(PLAN):
    d = bars * BAR + (XF if i < len(PLAN) - 1 else ENDHOLD)
    src = min(d / 1.25, 3.6)  # >= 1.25x slow motion
    k = d / src
    args += ["-i", f"{C}/{name}.mp4"]
    f.append(f"[{i}:v]trim=start=0.3:duration={src:.3f},setpts=(PTS-STARTPTS)*{k:.4f},{ex}"
             f"scale=1080:1920:flags=lanczos,setsar=1,fps=30,trim=duration={d:.3f},format=yuv420p[s{i}]")
    durs.append(d)
prev, off = "s0", 0.0
for i in range(1, len(PLAN)):
    off += durs[i - 1] - XF
    f.append(f"[{prev}][s{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
    prev = f"x{i}"
total = off + durs[-1]
f.append(f"[{prev}]eq=saturation=1.08:contrast=1.04,colorbalance=rs=0.03:bs=-0.03,noise=alls=6:allf=t,"
         f"vignette=PI/5,fade=t=in:d=0.8,fade=t=out:st={total-2.6:.2f}:d=2.6:color=0xFFF4E0[v]")
n = len(PLAN)
f.append(f"[{n}:a]atrim=start={START - XF/2}:duration={total:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.6,"
         f"afade=t=out:st={total-3.0:.2f}:d=3.0,loudnorm=I=-14:TP=-1.0[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-i", song, "-filter_complex", ";".join(f), "-map", "[v]",
                "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print(f"total {total:.2f}s")
