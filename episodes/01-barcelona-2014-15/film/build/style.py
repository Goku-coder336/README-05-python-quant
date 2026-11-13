"""Shared look for every scene (the brief's visual style), as HTML/SVG snippets.

Ground #07080a; pitch stripes #14171c / #171b21; pitch lines rgba(255,255,255,.2) 3px; top-down.
Team A (Barcelona) #e11d2e with a red glow, accent #ff3b47. Team B (opponents) #4b5260, border #8b93a1.
Ball white with a soft glow, always on top. Arrows dashed 16 on 12 off, 6px, round caps, drawn on:
red for runs (carries), white for passes and shots. Oswald 700 for titles and numbers, Inter for labels.
"""

GROUND = "#07080a"
STRIPE_A = "#14171c"
STRIPE_B = "#171b21"
LINE = "rgba(255,255,255,.2)"
TEAM_A = "#e11d2e"
ACCENT = "#ff3b47"
TEAM_B = "#4b5260"
TEAM_B_EDGE = "#8b93a1"
INK = "#f4f5f7"
MUTED = "#8b93a1"

BASE_CSS = f"""
  #root {{ position: absolute; inset: 0; background: {GROUND}; overflow: hidden; font-family: Inter, sans-serif; color: {INK}; }}
  .oswald {{ font-family: Oswald, sans-serif; font-weight: 700; }}
  .lbl {{ font-family: Inter, sans-serif; }}
  .src {{ position: absolute; font: 400 28px Inter, sans-serif; color: {MUTED}; letter-spacing: .02em; }}
  .recon {{ position: absolute; left: 96px; top: 64px; font: 700 28px Inter, sans-serif; color: {INK};
            background: rgba(7,8,10,.72); border: 2px solid {ACCENT}; border-radius: 6px; padding: 8px 16px; letter-spacing: .04em; }}
  .cap {{ position: absolute; left: 0; right: 0; bottom: 70px; text-align: center; }}
  .cap span {{ display: inline-block; font: 600 40px Inter, sans-serif; color: {INK}; background: rgba(7,8,10,.62);
               padding: 10px 26px; border-radius: 8px; max-width: 1560px; line-height: 1.25; }}
"""

SVG_DEFS = f"""
  <defs>
    <filter id="{{p}}-glowA" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feFlood flood-color="{TEAM_A}" flood-opacity=".85"/><feComposite in2="b" operator="in" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="{{p}}-glowW" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feFlood flood-color="#ffffff" flood-opacity=".8"/><feComposite in2="b" operator="in" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
"""


def defs(prefix):
    return SVG_DEFS.replace("{p}", prefix)


class Pitch:
    """Top-down pitch in StatsBomb coordinates (x 0-120 left to right, y 0-80 top to bottom)."""

    def __init__(self, x0, y0, s):
        self.x0, self.y0, self.s = x0, y0, s

    def P(self, x, y):
        return round(self.x0 + x * self.s, 1), round(self.y0 + y * self.s, 1)

    def svg(self):
        s, (x0, y0) = self.s, (self.x0, self.y0)
        out = []
        for i in range(12):  # stripes across the length
            out.append(f'<rect x="{x0 + i * 10 * s}" y="{y0}" width="{10 * s}" height="{80 * s}" fill="{STRIPE_A if i % 2 == 0 else STRIPE_B}"/>')
        L = f'fill="none" stroke="{LINE}" stroke-width="3"'

        def rect(ax, ay, bx, by):
            (X1, Y1), (X2, Y2) = self.P(ax, ay), self.P(bx, by)
            out.append(f'<rect x="{min(X1, X2)}" y="{min(Y1, Y2)}" width="{abs(X2 - X1)}" height="{abs(Y2 - Y1)}" {L}/>')

        rect(0, 0, 120, 80)
        X, Y1 = self.P(60, 0)
        _, Y2 = self.P(60, 80)
        out.append(f'<line x1="{X}" y1="{Y1}" x2="{X}" y2="{Y2}" stroke="{LINE}" stroke-width="3"/>')
        cx, cy = self.P(60, 40)
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{10 * s}" {L}/><circle cx="{cx}" cy="{cy}" r="4" fill="{LINE}"/>')
        for e in (0, 1):
            f = (lambda v: v) if e else (lambda v: 120 - v)
            rect(f(102), 18, f(120), 62)
            rect(f(114), 30, f(120), 50)
            rect(f(120), 36, f(122.2), 44)
            sx, sy = self.P(f(108), 40)
            out.append(f'<circle cx="{sx}" cy="{sy}" r="4" fill="{LINE}"/>')
            # penalty arc outside the box
            import math
            pts = []
            for a in range(-53, 54, 4):
                r = math.radians(a)
                pts.append("%s,%s" % self.P(f(108 - 10 * math.cos(r)), 40 + 10 * math.sin(r)))
            out.append(f'<polyline points="{" ".join(pts)}" {L}/>')
        return "\n".join(out)


def dot(pid, x, y, team, r=16, key=False, prefix="s"):
    """A player dot. Team A red with glow; team B grey with a lighter border. A key player gets a glowing ring."""
    if team == "A":
        body = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TEAM_A}" filter="url(#{prefix}-glowA)"/>'
    else:
        body = f'<circle cx="{x}" cy="{y}" r="{r}" fill="{TEAM_B}" stroke="{TEAM_B_EDGE}" stroke-width="3"/>'
    ring = (f'<circle id="{pid}-ring" cx="{x}" cy="{y}" r="{r + 11}" fill="none" stroke="{ACCENT}" stroke-width="4" '
            f'filter="url(#{prefix}-glowA)" opacity="0"/>') if key else ""
    return f'<g id="{pid}" opacity="0">{ring}{body}</g>'


TAG_H = 44


def tag_width(name):
    return 30 + len(name) * 17


def place_tags(items, obstacles, frame=(60, 40, 1860, 940)):
    """items: [(key, x, y, name)]. obstacles: [(x, y, r)] dots. Returns {key: (cx, cy)} tag centres that avoid
    each other, the dots and the frame edges, trying above, below, right, left at growing distances."""
    placed, out = [], {}

    def hits(box):
        x1, y1, x2, y2 = box
        if x1 < frame[0] or y1 < frame[1] or x2 > frame[2] or y2 > frame[3]:
            return True
        for b in placed:
            if not (x2 + 8 < b[0] or x1 - 8 > b[2] or y2 + 6 < b[1] or y1 - 6 > b[3]):
                return True
        for ox, oy, r in obstacles:
            cx, cy = min(max(ox, x1), x2), min(max(oy, y1), y2)
            if (cx - ox) ** 2 + (cy - oy) ** 2 < (r + 4) ** 2:
                return True
        return False

    for key, x, y, name in items:
        w = tag_width(name)
        best = None
        for dist in (34, 60, 90, 125):
            for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0), (1, -1), (-1, -1), (1, 1), (-1, 1)):
                cx = x + dx * (w / 2 + dist - 10)
                cy = y + dy * (TAG_H / 2 + dist - 10)
                box = (cx - w / 2, cy - TAG_H / 2, cx + w / 2, cy + TAG_H / 2)
                if not hits(box):
                    best = (cx, cy, box)
                    break
            if best:
                break
        if not best:
            cx, cy = x, y - 50
            best = (cx, cy, (cx - w / 2, cy - TAG_H / 2, cx + w / 2, cy + TAG_H / 2))
        placed.append(best[2])
        out[key] = (round(best[0], 1), round(best[1], 1))
    return out


def tag(tid, x, y, cx, cy, name, team="A"):
    """A name tag centred at (cx, cy) with a short leader line to the player at (x, y)."""
    import math
    w = tag_width(name)
    edge = ACCENT if team == "A" else TEAM_B_EDGE
    d = math.hypot(cx - x, cy - y) or 1
    sx, sy = round(x + (cx - x) / d * 30, 1), round(y + (cy - y) / d * 30, 1)  # start outside the ring
    return (f'<g id="{tid}" opacity="0"><line x1="{sx}" y1="{sy}" x2="{cx}" y2="{cy}" stroke="{edge}" stroke-width="2" opacity=".7"/>'
            f'<rect x="{cx - w / 2}" y="{cy - TAG_H / 2}" width="{w}" height="{TAG_H}" rx="6" fill="rgba(7,8,10,.9)" stroke="{edge}" stroke-width="2"/>'
            f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-family="Inter" font-weight="700" font-size="28" fill="{INK}">{name}</text></g>')


def arrow(aid, x1, y1, x2, y2, kind="pass", prefix="s"):
    """Dashed arrow (16 on, 12 off, 6px, round caps), drawn on through a solid mask. kind: pass/shot (white) or run (red)."""
    col = ACCENT if kind == "run" else INK
    d = f"M {x1} {y1} L {x2} {y2}"
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2, y2
    a1 = (hx - 22 * math.cos(ang - 0.45), hy - 22 * math.sin(ang - 0.45))
    a2 = (hx - 22 * math.cos(ang + 0.45), hy - 22 * math.sin(ang + 0.45))
    head = f'<polyline id="{aid}-head" points="{a1[0]:.1f},{a1[1]:.1f} {hx},{hy} {a2[0]:.1f},{a2[1]:.1f}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>'
    return (f'<mask id="{aid}-m" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080">'
            f'<path id="{aid}-mp" d="{d}" stroke="#fff" stroke-width="16" fill="none" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="100"/></mask>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-dasharray="16 12" mask="url(#{aid}-m)"/>'
            + head)
