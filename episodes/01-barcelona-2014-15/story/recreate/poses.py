"""Measure poses from a reference clip: for every frame, each player's 17 body points (COCO: nose, eyes, ears,
shoulders, elbows, wrists, hips, knees, ankles), which team's colour he wears, and where the ball is. Only these
numbers are kept; no pixels from the clip are stored or shown.

Usage: python poses.py clip.mp4 out.json --crop x,y,w,h [--start S --end E] --teams "Barcelona:#d9ff3a,PSG:#1b2440"
"""
import argparse, json, os
import numpy as np, cv2
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--crop", default=""); ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=0)
ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--teams", default="", help="name:#hex,... shirt colours used to tell teams apart")
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
pose = YOLO(os.path.join(HERE, "..", "trace", "yolov8m-pose.pt") if os.path.exists(os.path.join(HERE, "..", "trace", "yolov8m-pose.pt")) else "yolov8m-pose.pt")
det = YOLO(os.path.join(HERE, "..", "trace", "yolov8s-seg.pt"))
teams = [(n, np.array([int(h[i:i + 2], 16) for i in (5, 3, 1)], float)) for n, h in (t.split(":") for t in a.teams.split(","))] if a.teams else []

cap = cv2.VideoCapture(a.src)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
step = max(1, round(fps / a.fps))
crop = [int(v) for v in a.crop.split(",")] if a.crop else [0, 0, int(cap.get(3)), int(cap.get(4))]
f0, f1 = int(a.start * fps), int(a.end * fps) if a.end else 10 ** 9
frames, i = [], 0
while True:
    ok, fr = cap.read()
    if not ok or i > f1: break
    if i >= f0 and (i - f0) % step == 0:
        fr = fr[crop[1]:crop[1] + crop[3], crop[0]:crop[0] + crop[2]]
        r = pose.track(fr, persist=True, conf=0.25, verbose=False, tracker="bytetrack.yaml")[0]
        people = []
        if r.keypoints is not None and len(r.boxes):
            ids = r.boxes.id.cpu().numpy().astype(int) if r.boxes.id is not None else np.arange(len(r.boxes))
            for pid, kp, cf, box in zip(ids, r.keypoints.xy.cpu().numpy(), r.keypoints.conf.cpu().numpy(), r.boxes.xyxy.cpu().numpy()):
                team = None
                if teams:  # shirt colour: the middle of the torso between shoulders and hips
                    pts = [kp[k] for k in (5, 6, 11, 12) if cf[k] > 0.3]
                    if len(pts) >= 3:
                        c = np.mean(pts, axis=0).astype(int)
                        patch = fr[max(0, c[1] - 6):c[1] + 6, max(0, c[0] - 6):c[0] + 6].reshape(-1, 3).astype(float)
                        if len(patch):
                            m = np.median(patch, axis=0)
                            team = min(teams, key=lambda t: np.linalg.norm(t[1] - m))[0]
                people.append({"id": int(pid), "team": team, "kp": np.round(kp, 1).tolist(), "conf": np.round(cf, 2).tolist(), "box": np.round(box, 1).tolist()})
        b = det(fr, classes=[32], conf=0.15, verbose=False)[0]
        ball = None
        if len(b.boxes):
            k = int(np.argmax(b.boxes.conf.cpu().numpy())); x0, y0, x1, y1 = b.boxes.xyxy.cpu().numpy()[k]
            ball = [round(float((x0 + x1) / 2), 1), round(float((y0 + y1) / 2), 1), round(float(max(x1 - x0, y1 - y0) / 2), 1)]
        frames.append({"people": people, "ball": ball})
    i += 1
json.dump({"w": crop[2], "h": crop[3], "fps": fps / step, "frames": frames}, open(a.dst, "w"))
print(len(frames), "frames;", "people per frame:", round(np.mean([len(f["people"]) for f in frames]), 1), "; ball seen in", sum(f["ball"] is not None for f in frames))
