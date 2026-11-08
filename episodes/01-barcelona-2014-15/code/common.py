"""Shared look and render pipeline for the Episode 1 clips.

Every clip draws on a 1920x1080 canvas in pixel coordinates (origin bottom left),
renders frames with matplotlib and pipes them to ffmpeg (H.264, 30 fps).
"""
import os
import subprocess

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib.textpath import text_to_path
from PIL import Image

# ---------------------------------------------------------------- look
W, H, FPS, DPI = 1920, 1080, 30, 100
PT = DPI / 72.0  # pixels per point

BG = "#1a1a19"
PANEL = "#242422"      # card fill
LINE = "#3a3936"       # card edges, grid
FAINT = "#57554f"      # inactive elements
MUTED = "#9a978f"      # secondary text
TEXT = "#f2f0ea"       # primary text

BARCA = "#e0476a"      # Barcelona, in every clip
OPP = "#a9b4be"        # opponents, in every clip
MESSI = "#f2b84b"
NEYMAR = "#3cc6b0"
SUAREZ = "#9c8cf5"
OTHER = TEXT           # other Barcelona scorers (Piqué, Sandro, Rakitić)
GOAL_BLOCK = "#4a4945" # a Barcelona goal not scored by the highlighted player

PLAYER_COL = {"Messi": MESSI, "Neymar": NEYMAR, "Suárez": SUAREZ}

FONT = "Inter"
CREDIT = "Data: StatsBomb open data"

CLIPS_DIR = os.path.join(os.path.dirname(__file__), "..", "clips")


# ---------------------------------------------------------------- timing
def prog(t, start, dur=0.5):
    """Linear 0..1 progress of an event starting at `start` lasting `dur`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return float(np.clip((t - start) / dur, 0.0, 1.0))


def ease(x):
    """Ease-out cubic."""
    return 1 - (1 - x) ** 3


def ep(t, start, dur=0.5):
    return ease(prog(t, start, dur))


def interp_keys(t, keys):
    """Piecewise-linear interpolation through (time, value) keyframes."""
    ts = [k[0] for k in keys]
    vs = [k[1] for k in keys]
    return float(np.interp(t, ts, vs))


# ---------------------------------------------------------------- text helpers
def fprop(size, weight="regular"):
    return fm.FontProperties(family=FONT, weight=weight, size=size)


def text_width(s, size, weight="regular"):
    w, _, _ = text_to_path.get_text_width_height_descent(s, fprop(size, weight), ismath=False)
    return w * PT


class Clip:
    """One clip: a figure with a pixel-coordinate axes and a dynamic artist layer."""

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=BG)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.set_facecolor(BG)
        self.ax.axis("off")
        self.dyn = []
        self.static = True  # artists created while True are permanent

    # -- artist bookkeeping
    def _track(self, a):
        if not self.static:
            self.dyn.append(a)
        return a

    def begin_frame(self):
        for a in self.dyn:
            a.remove()
        self.dyn = []
        self.static = False

    def track(self, a):
        return self._track(a)

    # -- primitives (pixel coordinates)
    def text(self, x, y, s, size=20, color=TEXT, weight="regular", ha="left", va="baseline",
             alpha=1.0, ax=None, zorder=5, **kw):
        ax = ax or self.ax
        if alpha <= 0:
            return None
        a = ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, family=FONT,
                    ha=ha, va=va, alpha=alpha, zorder=zorder, **kw)
        return self._track(a)

    def tokens(self, x, y, toks, size=20, alpha=1.0, ha="left", va="baseline", zorder=5):
        """Draw a run of (text, colour, weight) tokens on one line. Returns end x."""
        widths = [text_width(s, size, w) for s, _, w in toks]
        total = sum(widths)
        if ha == "center":
            x -= total / 2
        elif ha == "right":
            x -= total
        cx = x
        for (s, c, w), wd in zip(toks, widths):
            self.text(cx, y, s, size=size, color=c, weight=w, alpha=alpha, va=va, zorder=zorder)
            cx += wd
        return cx

    def box(self, x, y, w, h, r=12, fc=PANEL, ec="none", lw=0, alpha=1.0, zorder=2, ax=None):
        ax = ax or self.ax
        if alpha <= 0:
            return None
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                           fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=zorder)
        ax.add_patch(p)
        return self._track(p)

    def circle(self, x, y, r, fc=TEXT, ec="none", lw=0, alpha=1.0, zorder=4):
        if alpha <= 0:
            return None
        c = Circle((x, y), r, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=zorder)
        self.ax.add_patch(c)
        return self._track(c)

    def line(self, xs, ys, color=TEXT, lw=2, alpha=1.0, zorder=3, ax=None, **kw):
        ax = ax or self.ax
        if alpha <= 0:
            return None
        (l,) = ax.plot(xs, ys, color=color, lw=lw, alpha=alpha, zorder=zorder,
                       solid_capstyle="round", **kw)
        return self._track(l)

    def credit(self, alpha=1.0):
        self.text(W - 48, 36, CREDIT, size=15, color=MUTED, ha="right", alpha=alpha, zorder=20)

    # -- render
    def render(self, draw, zoom=None, out=None, frames=None):
        """Call draw(t) for every frame and encode with ffmpeg.

        zoom: optional function t -> scale (>= 1) applied around the centre.
        frames: optional list of times; renders PNG stills instead of video (for checks).
        """
        if frames is not None:
            imgs = []
            for t in frames:
                self.begin_frame()
                draw(t)
                imgs.append(self._grab(zoom(t) if zoom else 1.0))
            return imgs
        os.makedirs(CLIPS_DIR, exist_ok=True)
        out = out or os.path.join(CLIPS_DIR, f"{self.name}.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
               "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(round(self.duration * FPS))
        for i in range(n):
            t = i / FPS
            self.begin_frame()
            draw(t)
            proc.stdin.write(self._grab(zoom(t) if zoom else 1.0).tobytes())
        proc.stdin.close()
        proc.wait()
        plt.close(self.fig)
        return out

    def _grab(self, scale=1.0):
        self.fig.canvas.draw()
        arr = np.asarray(self.fig.canvas.buffer_rgba())[:, :, :3]
        if scale > 1.0001:
            img = Image.fromarray(arr)
            cw, ch = W / scale, H / scale
            l, t_ = (W - cw) / 2, (H - ch) / 2
            img = img.resize((W, H), Image.LANCZOS, box=(l, t_, l + cw, t_ + ch))
            arr = np.asarray(img)
        return np.ascontiguousarray(arr)


def title_block(c, title, subtitle=None, alpha=1.0):
    """Top-left title used by every clip."""
    c.text(80, 1000, title, size=30, weight="bold", alpha=alpha)
    if subtitle:
        c.text(80, 958, subtitle, size=19, color=MUTED, alpha=alpha)
