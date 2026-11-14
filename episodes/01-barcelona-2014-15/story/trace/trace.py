"""Trace players from a match clip into flat illustration, in the style of the reference: a plain background,
white pitch lines, and each player as a flat, posterised cut-out with a dark outline.

Usage: python trace.py input.mp4 output.mp4 [--bg #1f8e86] [--vertical] [--start S --end E]
The input is a clip the user recorded. Nothing from the frame survives except the players, the ball and the lines.
"""
import argparse, os, subprocess, sys
import numpy as np
import cv2
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--bg", default="#1f8e86")
ap.add_argument("--vertical", action="store_true", help="crop to 9:16, following the players")
ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=0)
ap.add_argument("--crop", default="", help="x,y,w,h of the match picture inside the recording")
ap.add_argument("--fps", type=float, default=30, help="output frame rate")
ap.add_argument("--upscale", type=float, default=1.0)
ap.add_argument("--native", action="store_true", help="keep the input's own size")
ap.add_argument("--colours", type=int, default=4, help="flat colours per player")
a = ap.parse_args()

model = YOLO(os.path.join(os.path.dirname(__file__), "yolov8s-seg.pt"))
bg = np.array([int(a.bg[i:i + 2], 16) for i in (5, 3, 1)], np.uint8)  # BGR
cap = cv2.VideoCapture(a.src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
f0, f1 = int(a.start * fps), int(a.end * fps) if a.end else 10 ** 9
step = max(1, round(fps / a.fps))
crop = [int(v) for v in a.crop.split(",")] if a.crop else None
if crop: W, H = crop[2], crop[3]
W, H = int(W * a.upscale), int(H * a.upscale)
OW, OH = (1080, 1920) if a.vertical else (1920, 1080)
tmp = a.dst + ".frames"; os.makedirs(tmp, exist_ok=True)
cx_smooth = None
i = k = 0
while True:
    ok, fr = cap.read()
    if not ok or i > f1: break
    if i < f0 or (i - f0) % step: i += 1; continue
    if crop: fr = fr[crop[1]:crop[1] + crop[3], crop[0]:crop[0] + crop[2]]
    if a.upscale != 1: fr = cv2.resize(fr, (W, H), interpolation=cv2.INTER_CUBIC)
    out = np.empty_like(fr); out[:] = bg
    # pitch lines: bright, low-saturation thin strokes on the grass
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
    grass = cv2.inRange(hsv, (30, 40, 30), (90, 255, 255))
    white = cv2.inRange(hsv, (0, 0, 175), (180, 60, 255))
    near_grass = cv2.dilate(grass, np.ones((9, 9), np.uint8))
    lines = cv2.bitwise_and(white, near_grass)
    lines = cv2.morphologyEx(lines, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    # keep only long strokes (pitch markings), not on-screen text or app icons
    nl, lab_l, st_l, _ = cv2.connectedComponentsWithStats(lines)
    keep = np.zeros(nl, bool)
    for c in range(1, nl):
        w_, h_ = st_l[c, 2], st_l[c, 3]
        keep[c] = max(w_, h_) > 0.12 * max(W, H) and st_l[c, 4] < 0.35 * w_ * h_ + 50
    lines = (keep[lab_l] * 255).astype(np.uint8)
    out[lines > 0] = (255, 255, 255)
    res = model(fr, classes=[0, 32, 41, 75], conf=0.25, verbose=False, retina_masks=True)[0]
    xs = []
    if res.masks is not None:
        for m, c, box in sorted(zip(res.masks.data.cpu().numpy(), res.boxes.cls.cpu().numpy(), res.boxes.xyxy.cpu().numpy()), key=lambda z: int(z[1]) in (41, 75)):
            m = (m > 0.5).astype(np.uint8)
            if m.shape != fr.shape[:2]: m = cv2.resize(m, (W, H), interpolation=cv2.INTER_NEAREST)
            if int(c) in (41, 75):  # the trophy (read as a cup or vase): silver, flat-shaded
                px = fr[m > 0].astype(np.float32)
                if len(px) > 30:
                    g = px.mean(axis=1)
                    q = np.digitize(g, np.percentile(g, [33, 66]))
                    sil = np.array([[150, 155, 160], [200, 205, 210], [245, 247, 250]], np.uint8)
                    out[m > 0] = sil[q]
                    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    cv2.drawContours(out, cnts, -1, (25, 25, 25), 2, cv2.LINE_AA)
                continue
            if int(c) == 32:  # the ball: a clean white disc
                (bx, by), r = cv2.minEnclosingCircle(cv2.findNonZero(m))
                r = min(r, (m.sum() / np.pi) ** 0.5 * 1.05)
                cv2.circle(out, (int(bx), int(by)), max(3, int(r)), (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(out, (int(bx), int(by)), max(3, int(r)), (30, 30, 30), 1, cv2.LINE_AA)
                continue
            px = fr[m > 0].astype(np.float32)
            if len(px) < 30: continue
            n = min(a.colours, len(px))
            _, lab, cen = cv2.kmeans(px, n, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0), 2, cv2.KMEANS_PP_CENTERS)
            cen = np.clip(cen * 1.08, 0, 255).astype(np.uint8)  # a touch brighter, like flat paint
            flat = np.zeros_like(fr); flat[m > 0] = cen[lab.ravel()]
            flat = cv2.medianBlur(flat, 5)
            # wash out small print: sponsor names, crests and numbers do not survive at this scale
            k_ = max(5, (int(0.012 * max(W, H)) // 2) * 2 + 1)
            flat = cv2.medianBlur(flat, k_)
            m2 = cv2.erode(m, np.ones((2, 2), np.uint8))
            cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(out, cnts, -1, (25, 25, 25), 2, cv2.LINE_AA)
            # a soft shadow under the feet
            x0, y0, x1, y1 = box.astype(int)
            cv2.ellipse(out, ((x0 + x1) // 2, y1), (max(4, int((x1 - x0) * 0.32)), max(2, (x1 - x0) // 12)), 0, 0, 360, (int(bg[0] * .7), int(bg[1] * .7), int(bg[2] * .7)), -1, cv2.LINE_AA)
            out[m2 > 0] = flat[m2 > 0]
            xs.append(((x0 + x1) / 2, (x1 - x0) * (y1 - y0)))
    if a.vertical:
        # follow the action: the area-weighted centre of the players, smoothed
        if xs: tx = sum(x * w for x, w in xs) / sum(w for _, w in xs)
        else: tx = W / 2
        cx_smooth = tx if cx_smooth is None else cx_smooth * 0.9 + tx * 0.1
        cw = int(H * 9 / 16); x0 = int(min(max(0, cx_smooth - cw / 2), W - cw))
        out = out[:, x0:x0 + cw]
    if not a.native: out = cv2.resize(out, (OW, OH), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(tmp, f"{k:05d}.png"), out); k += 1; i += 1
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps / step), "-i", os.path.join(tmp, "%05d.png"), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", a.dst], check=True)
subprocess.run(["rm", "-rf", tmp])
print("traced", k, "frames ->", a.dst)
