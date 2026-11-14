"""Read CMU motion-capture BVH files (free for any use, CMU Graphics Lab; BVH conversion by B. Hahne) and
write the joint positions the film needs, at 30 fps, in yards, with z up."""
import json
import math
import sys

import numpy as np

KEEP = ["Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase", "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
        "Spine1", "Neck1", "Head", "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand"]


def rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "X":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "Y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def parse(path):
    toks = open(path).read().split()
    i = 0
    joints, stack = [], []
    while toks[i] != "MOTION":
        t = toks[i]
        if t in ("ROOT", "JOINT"):
            joints.append({"name": toks[i + 1], "parent": stack[-1] if stack else -1, "chan": [], "end": None})
            i += 2
        elif t == "End":
            joints.append({"name": joints[stack[-1]]["name"] + "_end", "parent": stack[-1], "chan": [], "end": True})
            i += 2
        elif t == "{":
            stack.append(len(joints) - 1)
            i += 1
        elif t == "}":
            stack.pop()
            i += 1
        elif t == "OFFSET":
            joints[stack[-1]]["off"] = np.array([float(x) for x in toks[i + 1:i + 4]])
            i += 4
        elif t == "CHANNELS":
            n = int(toks[i + 1])
            joints[stack[-1]]["chan"] = toks[i + 2:i + 2 + n]
            i += 2 + n
        else:
            i += 1
    nf = int(toks[i + 2])
    ft = float(toks[i + 5])
    vals = np.array([float(x) for x in toks[i + 6:]]).reshape(nf, -1)
    return joints, vals, ft


def positions(joints, vals):
    nf = len(vals)
    out = np.zeros((nf, len(joints), 3))
    for f in range(nf):
        col = 0
        R = [None] * len(joints)
        P = [None] * len(joints)
        for j, J in enumerate(joints):
            m = np.eye(3)
            t = J.get("off", np.zeros(3)).copy()
            for c in J["chan"]:
                v = vals[f, col]
                col += 1
                if c.endswith("position"):
                    t["XYZ".index(c[0])] = v
                else:
                    m = m @ rot(c[0], v)
            if J["parent"] < 0:
                R[j], P[j] = m, t
            else:
                p = J["parent"]
                P[j] = P[p] + R[p] @ t
                R[j] = R[p] @ m
            out[f, j] = P[j]
    return out


def convert(path, fps=30):
    joints, vals, ft = parse(path)
    step = max(1, round(1 / (fps * ft)))
    vals = vals[::step]
    pos = positions(joints, vals)
    names = [J["name"] for J in joints]
    # height: head end to the lowest toe, standing at the start, is 1.8 m = 1.97 yd
    he = names.index("Head_end")
    h = pos[0, he, 1] - pos[0, :, 1].min()
    k = 1.97 / h
    # BVH: y up. Film: x, y on the ground, z up (y_film = -z_bvh keeps it right-handed)
    sel = KEEP + ["Head_end", "LeftToeBase_end", "RightToeBase_end"]
    idx = [names.index(n) for n in sel]
    P = pos[:, idx, :] * k
    film = np.stack([P[..., 0], -P[..., 2], P[..., 1]], axis=-1)
    film = film[1:]  # frame 0 of these files is the calibration T-pose
    film[..., 2] -= np.percentile(film[:, :, 2].min(axis=1), 5)  # feet on the ground
    return {"joints": sel, "fps": fps, "frames": np.round(film, 3).tolist()}


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    d = convert(src)
    json.dump(d, open(dst, "w"))
    F = np.array(d["frames"])
    hip = F[:, 0, :2]
    print(dst, len(F), "frames", round(len(F) / 30, 2), "s; hips travel", np.round(hip[-1] - hip[0], 2).tolist())
