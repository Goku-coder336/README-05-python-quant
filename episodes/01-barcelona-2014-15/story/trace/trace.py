"""Trace players from a match clip into flat illustration: a plain background, white pitch lines, and each
player as a flat, posterised cut-out with a dark outline. Nothing from the footage survives except the shapes of
the players, the ball and the pitch markings.

Two passes. Pass 1 finds the ball and the players in every frame and builds a smooth camera path that follows the
play. Pass 2 crops a vertical window around that path (zoomed in for wide broadcast shots), upscales it, and
traces it.

Usage: python trace.py input.mp4 output.mp4 --crop x,y,w,h [--zoom 2] [--start S --end E] [--bg #1f8e86]
"""
import argparse, os, subprocess
import numpy as np
import cv2
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--bg", default="#1f8e86")
ap.add_argument("--crop", default="", help="x,y,w,h of the match picture inside the recording")
ap.add_argument("--zoom", type=float, default=1.0, help="1 = window as tall as the picture; 2 = half as tall")
ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=0)
ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--colours", type=int, default=4)
ap.add_argument("--horizontal", action="store_true", help="16:9 output instead of 9:16")
a = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))
model = YOLO(os.path.join(HERE, "yolov8s-seg.pt"))
bg = np.array([int(a.bg[i:i + 2], 16) for i in (5, 3, 1)], np.uint8)  # BGR
OW, OH = (1920, 1080) if a.horizontal else (1080, 1920)

cap = cv2.VideoCapture(a.src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
step = max(1, round(fps / a.fps))
crop = [int(v) for v in a.crop.split(",")] if a.crop else [0, 0, int(cap.get(3)), int(cap.get(4))]
CW, CH = crop[2], crop[3]
f0, f1 = int(a.start * fps), int(a.end * fps) if a.end else 10 ** 9


def frames():
    cap = cv2.VideoCapture(a.src)
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok or i > f1: return
        if i >= f0 and (i - f0) % step == 0:
            yield fr[crop[1]:crop[1] + crop[3], crop[0]:crop[0] + crop[2]]
        i += 1


def grass_mask(fr):
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, (30, 40, 30), (90, 255, 255))


def on_pitch(box, grass):
    """True when the ground under the player's feet is grass (drops stewards, fans and photographers)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    h = max(4, (y1 - y0) // 5)
    ys, ye = max(0, y1 - h // 2), min(grass.shape[0], y1 + h)
    xs, xe = max(0, x0), min(grass.shape[1], x1)
    if ye <= ys or xe <= xs: return False
    return grass[ys:ye, xs:xe].mean() / 255 > 0.25


# ------------------------------------------------------------------ pass 1: where is the play?
focus = []
for fr in frames():
    g = grass_mask(fr)
    r = model(fr, classes=[0, 32], conf=0.2, verbose=False)[0]
    ball, pts = None, []
    for b, c, cf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.cls.cpu().numpy(), r.boxes.conf.cpu().numpy()):
        if int(c) == 32 and (ball is None or cf > ball[2]): ball = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, cf)
        elif int(c) == 0 and (g.mean() < 20 or on_pitch(b, g)): pts.append(((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, (b[2] - b[0]) * (b[3] - b[1])))
    if ball is not None: focus.append((ball[0], ball[1]))
    elif pts:
        w = sum(p[2] for p in pts)
        focus.append((sum(p[0] * p[2] for p in pts) / w, sum(p[1] * p[2] for p in pts) / w))
    else: focus.append(None)
n = len(focus)
# fill gaps, then smooth (a moving average over about 0.8 s keeps the camera calm)
last = (CW / 2, CH / 2)
F = []
for f in focus:
    last = f if f is not None else last
    F.append(last)
F = np.array(F, float)
k = max(1, int(a.fps * 0.8))
pad = np.pad(F, ((k, k), (0, 0)), mode="edge")
F = np.array([pad[i:i + 2 * k + 1].mean(0) for i in range(n)])

# window size in the cropped picture
if a.horizontal:
    wh = CH / a.zoom; ww = min(CW, wh * 16 / 9)
else:
    wh = CH / a.zoom; ww = wh * 9 / 16
    if ww > CW: ww = CW; wh = ww * 16 / 9
ww, wh = int(ww), int(wh)

# ------------------------------------------------------------------ pass 2: trace the window
tmp = a.dst + ".frames"; os.makedirs(tmp, exist_ok=True)
for idx, fr in enumerate(frames()):
    cx, cy = F[idx]
    x0 = int(min(max(0, cx - ww / 2), CW - ww)); y0 = int(min(max(0, cy - wh * 0.55), CH - wh))
    win = cv2.resize(fr[y0:y0 + wh, x0:x0 + ww], (OW, OH), interpolation=cv2.INTER_CUBIC)
    out = np.empty_like(win); out[:] = bg
    grass = grass_mask(win)
    # pitch markings: bright, low-saturation strokes next to grass, long ones only (no on-screen text)
    hsv = cv2.cvtColor(win, cv2.COLOR_BGR2HSV)
    white = cv2.inRange(hsv, (0, 0, 140), (180, 85, 255))
    lines = cv2.bitwise_and(white, cv2.dilate(grass, np.ones((15, 15), np.uint8)))
    lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    nl, lab_l, st_l, _ = cv2.connectedComponentsWithStats(lines)
    keep = np.zeros(nl, bool)
    for c in range(1, nl):
        w_, h_ = st_l[c, 2], st_l[c, 3]
        keep[c] = max(w_, h_) > 0.05 * max(OW, OH) and st_l[c, 4] < 0.4 * w_ * h_ + 80
    lines = (keep[lab_l] * 255).astype(np.uint8)
    lines = cv2.dilate(lines, np.ones((3, 3), np.uint8))
    out[lines > 0] = (255, 255, 255)

    res = model(win, classes=[0, 32, 41, 75], conf=0.25, verbose=False, retina_masks=True)[0]
    if res.masks is not None:
        items = list(zip(res.masks.data.cpu().numpy(), res.boxes.cls.cpu().numpy(), res.boxes.xyxy.cpu().numpy()))
        items.sort(key=lambda z: (int(z[1]) in (41, 75), z[2][3]))  # far players first, trophy last
        for m, c, box in items:
            m = (m > 0.5).astype(np.uint8)
            if m.shape != win.shape[:2]: m = cv2.resize(m, (OW, OH), interpolation=cv2.INTER_NEAREST)
            c = int(c)
            if c == 32:  # the ball
                pts_ = cv2.findNonZero(m)
                if pts_ is None: continue
                (bx, by), r = cv2.minEnclosingCircle(pts_)
                r = min(r, (m.sum() / np.pi) ** 0.5 * 1.05)
                cv2.circle(out, (int(bx), int(by)), max(4, int(r)), (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(out, (int(bx), int(by)), max(4, int(r)), (30, 30, 30), 2, cv2.LINE_AA)
                continue
            if c in (41, 75):  # a trophy read as a cup or vase: flat silver
                px = win[m > 0].astype(np.float32)
                if len(px) > 30:
                    g_ = px.mean(axis=1); q = np.digitize(g_, np.percentile(g_, [33, 66]))
                    out[m > 0] = np.array([[150, 155, 160], [200, 205, 210], [245, 247, 250]], np.uint8)[q]
                continue
            if grass.mean() > 20 and not on_pitch(box, grass): continue  # off the pitch
            px = win[m > 0].astype(np.float32)
            if len(px) < 60: continue
            bx0, by0, bx1, by1 = box.astype(int)
            small = (by1 - by0) < 0.33 * OH
            # smooth the outline: blur the mask and threshold it again
            m = (cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.2 if small else 1.2) > 0.5).astype(np.uint8)
            cv2.ellipse(out, ((bx0 + bx1) // 2, by1), (max(4, int((bx1 - bx0) * 0.32)), max(2, (bx1 - bx0) // 12)), 0, 0, 360,
                        (int(bg[0] * .7), int(bg[1] * .7), int(bg[2] * .7)), -1, cv2.LINE_AA)
            if small:
                # far players: a clean two-tone silhouette, shirt colour above the waist, darker below
                ys, xs = np.nonzero(m)
                cut = by0 + 0.5 * (by1 - by0)
                top = win[ys[ys < cut], xs[ys < cut]].astype(np.float32)
                shirt = np.median(top, axis=0) if len(top) else px.mean(0)
                hsv_ = cv2.cvtColor(np.uint8([[np.clip(shirt, 0, 255)]]), cv2.COLOR_BGR2HSV)[0, 0].astype(int)
                hsv_[1] = min(255, int(hsv_[1] * 1.35)); hsv_[2] = min(255, max(60, int(hsv_[2] * 1.15)))
                shirt = cv2.cvtColor(np.uint8([[hsv_]]), cv2.COLOR_HSV2BGR)[0, 0].astype(int)
                low = (shirt * 0.55).astype(int)
                out[(m > 0) & (np.arange(OH)[:, None] < cut)] = shirt
                out[(m > 0) & (np.arange(OH)[:, None] >= cut)] = low
                cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                cv2.drawContours(out, cnts, -1, (25, 25, 25), 2, cv2.LINE_AA)
                continue
            nclu = min(a.colours, len(px))
            _, lab, cen = cv2.kmeans(px, nclu, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), 2, cv2.KMEANS_PP_CENTERS)
            cen = np.clip(cen * 1.08, 0, 255).astype(np.uint8)
            flat = np.zeros_like(win); flat[m > 0] = cen[lab.ravel()]
            kk = max(5, (int(0.01 * max(OW, OH)) // 2) * 2 + 1)  # washes out sponsor names, crests and numbers
            flat = cv2.medianBlur(flat, kk)
            m2 = cv2.erode(m, np.ones((3, 3), np.uint8))
            out[m2 > 0] = flat[m2 > 0]
            cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(out, cnts, -1, (25, 25, 25), 3, cv2.LINE_AA)
    cv2.imwrite(os.path.join(tmp, f"{idx:05d}.png"), out)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps / step), "-i", os.path.join(tmp, "%05d.png"),
                "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", a.dst], check=True)
subprocess.run(["rm", "-rf", tmp])
print("traced", n, "frames ->", a.dst)
