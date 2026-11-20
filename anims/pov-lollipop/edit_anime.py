"""Edit the anime 'Amma asks me to help' reel. usage: edit_anime.py <killin.wav> <aeroplane.wav> <caps_dir> <out_dir>"""
import subprocess, sys
R1, R2, CAPS, OUT = sys.argv[1:5]
D = "assets/pov-lollipop/anime"; A = "assets/pov-lollipop/audio"
HOOK = 3.92  # "gotta put 'em in the dirt" region in the Killin' 'em recording (4 beats = 2.3 s)
# (kind, source, start, dur, extra)
SHOTS = [
    ("pic", f"{D}/s1_cooking.png", 0.0, 2.6, "push"),
    ("vid", f"{D}/clip_strut.mp4", 2.6, 2.3, ""),
    ("pic", f"{D}/s3_sink.jpg", 4.9, 2.7, "push"),
    ("vid", f"{D}/clip_strut.mp4", 7.6, 2.3, "hflip"),
    ("pic", f"{D}/s5_clothes.jpg", 9.9, 2.6, "push"),
    ("vid", f"{D}/clip_strut.mp4", 12.5, 2.3, "zoom"),
    ("pic", f"{D}/s7_stare.jpg", 14.8, 2.2, "stare"),
    ("black", None, 17.0, 0.45, ""),
    ("pic", f"{D}/s8_godmode.jpg", 17.45, 2.15, "god"),
    ("aero", f"{D}/clip_aeroplane.mp4", 19.6, 7.5, ""),
]
TOTAL = 27.1
args, f = [], []
for i, (k, src, st, d, ex) in enumerate(SHOTS):
    if k == "pic":
        args += ["-loop", "1", "-framerate", "30", "-t", f"{d}", "-i", src]
        n = int(d * 30)
        if ex == "push": z = f"1.0+0.08*on/{n}"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
        elif ex == "stare": z = f"1.0+0.35*pow(on/{n},1.5)"; x = f"iw/2-(iw/zoom/2)+if(gt(on,{n-15}),sin(on*2)*14,0)"; y = "ih*0.35-(ih/zoom*0.35)"
        else: z = "1.08+0.03*sin(on*0.9)"; x = "iw/2-(iw/zoom/2)+sin(on*3.1)*10"; y = "ih/2-(ih/zoom/2)+cos(on*2.7)*10"
        post = ",eq=brightness='0.06*sin(t*40)':eval=frame" if ex == "god" else ""
        f.append(f"[{i}:v]scale=2160:3840,zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1080x1920:fps=30{post},trim=duration={d},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s{i}]")
    elif k == "black":
        args += ["-f", "lavfi", "-t", f"{d}", "-i", "color=c=black:s=1080x1920:r=30"]
        f.append(f"[{i}:v]drawbox=x=0:y=930:w='iw*min(1,t/0.25)':h=8:color=white:t=fill,setsar=1,format=yuv420p[s{i}]")
    elif k == "vid":
        args += ["-i", src]
        extra = {"hflip": "hflip,", "zoom": "crop=iw/1.25:ih/1.25:iw*0.1:ih*0.12,", "": ""}[ex]
        f.append(f"[{i}:v]trim=0.1:{0.1+d},setpts=PTS-STARTPTS,{extra}scale=1080:1920,fps=30,setsar=1,format=yuv420p[s{i}]")
    else:  # aeroplane: forward, back, forward to fill the time
        args += ["-i", src]
        f.append(f"[{i}:v]trim=0.1:3.9,setpts=PTS-STARTPTS,scale=1080:1920,fps=30,split[a1][a2];[a2]reverse[ar];"
                 f"[a1][ar]concat=n=2:v=1:a=0,loop=loop=1:size=228,trim=duration={d},setpts=PTS-STARTPTS,"
                 f"fade=t=out:st={d-0.6}:d=0.6,setsar=1,format=yuv420p[s{i}]")
n = len(SHOTS)
cat = "".join(f"[s{i}]" for i in range(n))
f.append(f"{cat}concat=n={n}:v=1:a=0[base]")
# white flash at every cut
flash = "+".join(f"between(t,{s[2]},{s[2]+0.08})" for s in SHOTS[1:] if s[0] != "black")
f.append(f"[base]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.55:t=fill:enable='{flash}'[vb]")
# caption overlays
caps = [("title", 0, TOTAL), ("a1", 0.2, 2.6), ("a2", 5.0, 7.6), ("a3", 10.0, 12.5), ("a4", 14.9, 17.0), ("god", 17.45, 19.6), ("aero", 19.6, TOTAL)]
prev = "vb"; ci = n
for j, (c, a, b) in enumerate(caps):
    args += ["-i", f"{CAPS}/{c}.png"]
    f.append(f"[{prev}][{ci}:v]overlay=0:0:enable='between(t,{a},{b})'[o{j}]"); prev = f"o{j}"; ci += 1
f.append(f"[{prev}]null[vout]")
# audio
aud = []
def add(path, at, gain=1.0, trim=None):
    global ci
    args.extend(["-i", path]); t = f"atrim={trim[0]}:{trim[0]+trim[1]},asetpts=PTS-STARTPTS," if trim else ""
    ms = int(at * 1000); aud.append(f"[{ci}:a]{t}aresample=48000,aformat=channel_layouts=stereo,volume={gain},adelay={ms}|{ms}[x{ci}]"); ci += 1
add(f"{A}/sizzle.mp3", 0.0, 0.35); add(f"{A}/v1.mp3", 0.25, 1.6)
for st in (2.6, 7.6, 12.5): add(R1, st, 0.9, (HOOK, 2.3))
add(f"{A}/clatter.mp3", 4.95, 0.5); add(f"{A}/v2.mp3", 5.1, 1.6)
add(f"{A}/v3.mp3", 10.05, 1.6)
add(f"{A}/v4.mp3", 15.0, 1.8)
add(f"{A}/slash.mp3", 17.0, 0.9); add(f"{A}/powerup.mp3", 17.4, 0.9); add(f"{A}/thunder.mp3", 17.5, 0.7)
add(R2, 19.6, 0.9, (0.23, 7.5))
f.append("".join(f"[x{k}]" for k in range(n + len(caps), ci)) + f"amix=inputs={ci-n-len(caps)}:normalize=0,afade=t=out:st={TOTAL-0.8}:d=0.8,"
         f"alimiter=limit=0.9,apad=whole_dur={TOTAL},atrim=duration={TOTAL}[aout]")
fc = ";".join(f + aud) if False else ";".join(f[:-1] + aud + [f[-1]])
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264",
                "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL),
                "-movflags", "+faststart", f"{OUT}/anime-with-songs.mp4"], check=True)
print("ok")
