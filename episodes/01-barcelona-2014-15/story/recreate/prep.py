"""Clean measured poses into tracks: one team per track (majority vote), gaps filled, jitter smoothed, the ball
interpolated. Writes a small JS file the animation reads."""
import json, sys
from collections import Counter, defaultdict
import numpy as np

src, dst, var = sys.argv[1], sys.argv[2], sys.argv[3]
D = json.load(open(src))
F = D["frames"]; n = len(F)
tracks = defaultdict(lambda: {"team": Counter(), "K": np.full((n, 17, 2), np.nan), "C": np.zeros((n, 17)), "area": np.zeros(n)})
for i, fr in enumerate(F):
    for p in fr["people"]:
        t = tracks[p["id"]]
        if p["team"]: t["team"][p["team"]] += 1
        K = np.array(p["kp"]); C = np.array(p["conf"])
        K[C < 0.25] = np.nan
        t["K"][i] = K; t["C"][i] = C
        b = p["box"]; t["area"][i] = (b[2] - b[0]) * (b[3] - b[1])
def fill_smooth(a, w=5):
    out = a.copy()
    idx = np.arange(len(a))
    ok = ~np.isnan(a)
    if ok.sum() < 2: return out
    first, last = idx[ok][0], idx[ok][-1]
    out[first:last + 1] = np.interp(idx[first:last + 1], idx[ok], a[ok])
    k = np.ones(w) / w
    seg = out[first:last + 1]
    pad = np.pad(seg, (w // 2, w // 2), mode="edge")
    out[first:last + 1] = np.convolve(pad, k, mode="valid")
    return out
res = []
for tid, t in tracks.items():
    present = ~np.all(np.isnan(t["K"][:, :, 0]), axis=1)
    if present.sum() < 8: continue
    team = t["team"].most_common(1)[0][0] if t["team"] else "REF"
    K = t["K"].copy()
    for j in range(17):
        for c in range(2): K[:, j, c] = fill_smooth(K[:, j, c])
    span = np.where(present)[0]
    res.append({"id": int(tid), "team": team, "from": int(span[0]), "to": int(span[-1]), "size": float(np.nanmean(t["area"][present])),
                "K": [None if np.isnan(K[i, 0, 0]) else np.round(np.nan_to_num(K[i], nan=0.0), 1).tolist() for i in range(n)],
                "C": np.round(t["C"], 2).tolist()})
# ball: keep detections that sit at someone's feet, or continue a smooth path from the last kept one
# (a shot in flight); everything else is a false hit (heads, socks). Then fill short gaps.
def feet(i):
    out = []
    for r in res:
        K = r["K"][i]
        if K: out += [K[15], K[16]]
    return out
kept = [None] * n; last = None
for i, fr in enumerate(F):
    bb = fr["ball"]
    if not bb or bb[2] > 80: continue
    near = any(abs(bb[0] - f[0]) < 230 and -260 < bb[1] - f[1] < 90 for f in feet(i))
    cont = last is not None and np.hypot(bb[0] - last[1][0], bb[1] - last[1][1]) < 70 * (i - last[0]) and i - last[0] <= 4
    if near or cont:
        kept[i] = bb; last = (i, bb)
ball = [None] * n
ki = [i for i in range(n) if kept[i]]
for i in range(n):
    if kept[i]: ball[i] = kept[i]; continue
    prev = [k for k in ki if k < i]; nxt = [k for k in ki if k > i]
    if prev and nxt and nxt[0] - prev[-1] <= 8:
        u = (i - prev[-1]) / (nxt[0] - prev[-1]); ball[i] = [kept[prev[-1]][q] * (1 - u) + kept[nxt[0]][q] * u for q in range(3)]
# a ball's size changes slowly: smooth the radius hard
rs = [b[2] for b in ball if b]
med = float(np.median(rs)) if rs else 40
for i in range(n):
    if ball[i]: ball[i] = [round(ball[i][0], 1), round(ball[i][1], 1), round(0.7 * med + 0.3 * ball[i][2], 1)]
print("ball kept in", len(ki), "frames, shown in", sum(b is not None for b in ball))
for r in res: print(r["id"], r["team"], r["from"], r["to"], int(r["size"]))
open(dst, "w").write(f"window.{var} = " + json.dumps({"w": D["w"], "h": D["h"], "fps": D["fps"], "n": n, "tracks": res, "ball": ball}, separators=(",", ":")) + ";\n")
