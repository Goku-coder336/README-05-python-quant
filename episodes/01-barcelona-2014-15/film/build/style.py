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


# ---------------------------------------------------------------- Pip, the film's character
# An original tactics-board magnet: a red glowing disc (like Barcelona's player dots) with eyes, brows, a mouth,
# thin arms and legs, and a magnifying glass. Local origin (0, 0) is between the feet; the body centre is at
# (0, -112), radius 58. Parts are separate groups so they can be offset in time (head leads, arms follow).
def pip_svg(pid, prefix, glass=True):
    ink = "#0b0c0f"
    limb = "#d5dae2"  # light limbs so Pip reads on the dark board
    leg = lambda side, x: (f'<g id="{pid}-leg{side}"><line x1="{x * 0.6}" y1="-62" x2="{x}" y2="-6" stroke="{limb}" stroke-width="10" stroke-linecap="round"/>'
                           f'<ellipse cx="{x + (6 if x > 0 else -6)}" cy="-4" rx="16" ry="8" fill="{limb}"/></g>')
    arm = lambda side, x: (f'<g id="{pid}-arm{side}"><line x1="{x}" y1="-118" x2="{x + (40 if x > 0 else -40)}" y2="-78" stroke="{limb}" stroke-width="9" stroke-linecap="round"/>'
                           f'<circle cx="{x + (42 if x > 0 else -42)}" cy="-76" r="10" fill="#fff"/>'
                           + (f'<g id="{pid}-glass"><line x1="{x + 46}" y1="-80" x2="{x + 66}" y2="-108" stroke="#9aa1ad" stroke-width="7" stroke-linecap="round"/>'
                              f'<circle cx="{x + 78}" cy="-124" r="22" fill="rgba(255,255,255,.12)" stroke="#d9dde3" stroke-width="6"/></g>' if (glass and x > 0) else "")
                           + '</g>')
    eyes = {
        "normal": f'<ellipse cx="-21" cy="-124" rx="15" ry="19" fill="#fff"/><ellipse cx="21" cy="-124" rx="15" ry="19" fill="#fff"/>'
                  f'<g id="{pid}-pupils"><circle cx="-19" cy="-121" r="7.5" fill="{ink}"/><circle cx="23" cy="-121" r="7.5" fill="{ink}"/></g>',
        "wide": f'<ellipse cx="-22" cy="-126" rx="19" ry="24" fill="#fff"/><ellipse cx="22" cy="-126" rx="19" ry="24" fill="#fff"/>'
                f'<circle cx="-22" cy="-126" r="5" fill="{ink}"/><circle cx="22" cy="-126" r="5" fill="{ink}"/>',
        "happy": f'<path d="M -34 -120 Q -21 -138 -8 -120" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M 8 -120 Q 21 -138 34 -120" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>',
        "closed": f'<line x1="-34" y1="-122" x2="-8" y2="-122" stroke="#fff" stroke-width="6" stroke-linecap="round"/>'
                  f'<line x1="8" y1="-122" x2="34" y2="-122" stroke="#fff" stroke-width="6" stroke-linecap="round"/>',
    }
    mouths = {
        "smile": '<path d="M -14 -92 Q 0 -80 14 -92" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
        "o": '<ellipse cx="0" cy="-88" rx="8" ry="10" fill="#0b0c0f" stroke="#fff" stroke-width="4"/>',
        "flat": '<line x1="-11" y1="-89" x2="11" y2="-89" stroke="#fff" stroke-width="5" stroke-linecap="round"/>',
        "grin": '<path d="M -18 -94 Q 0 -70 18 -94 Z" fill="#0b0c0f" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
    }
    brows = (f'<g id="{pid}-brows"><line id="{pid}-browL" x1="-34" y1="-152" x2="-10" y2="-149" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>'
             f'<line id="{pid}-browR" x1="10" y1="-149" x2="34" y2="-152" stroke="{ink}" stroke-width="6" stroke-linecap="round"/></g>')
    eye_g = "".join(f'<g id="{pid}-eyes-{k}" opacity="{1 if k == "normal" else 0}">{v}</g>' for k, v in eyes.items())
    mouth_g = "".join(f'<g id="{pid}-mouth-{k}" opacity="{1 if k == "smile" else 0}">{v}</g>' for k, v in mouths.items())
    return (f'<g id="{pid}">'
            f'<ellipse id="{pid}-shadow" cx="0" cy="2" rx="52" ry="10" fill="rgba(0,0,0,.55)"/>'
            f'{leg("L", -22)}{leg("R", 22)}'
            f'<g id="{pid}-body">'
            f'<circle cx="0" cy="-104" r="58" fill="#9e1020"/>'                      # magnet base (thickness)
            f'<circle cx="0" cy="-112" r="58" fill="{TEAM_A}" filter="url(#{prefix}-glowA)"/>'
            f'<path d="M -38 -146 Q -20 -164 6 -166" fill="none" stroke="rgba(255,255,255,.45)" stroke-width="7" stroke-linecap="round"/>'
            f'<g id="{pid}-face">{eye_g}{brows}{mouth_g}</g>'
            f'</g>'
            f'{arm("L", -50)}{arm("R", 50)}'
            f'</g>')


# GSAP helpers for Pip, inlined into each scene that uses him. GSAP tweens a plain state object per Pip, and
# draw() writes exact SVG transforms (each limb rotates about its own joint, in Pip's own coordinates), so every
# frame is a function of timeline time. All moves are placed at absolute times.
PIP_JS = r"""
    const PIPS = {};
    const pipDraw = (id) => {
      const S = PIPS[id], q = (s) => document.querySelector("#" + id + s);
      q("").setAttribute("transform", `translate(${S.x} ${S.y}) scale(${S.s * S.dir} ${S.s})`);
      q("-legL").setAttribute("transform", `rotate(${S.legL} -13 -62)`);
      q("-legR").setAttribute("transform", `rotate(${S.legR} 13 -62)`);
      q("-armL").setAttribute("transform", `rotate(${S.armL} -50 -118)`);
      q("-armR").setAttribute("transform", `rotate(${S.armR} 50 -118)`);
      q("-body").setAttribute("transform", `translate(0 ${S.bodyY}) translate(0 -50) scale(${S.sx} ${S.sy * S.br}) translate(0 50)`);
      q("-pupils").setAttribute("transform", `translate(${S.px} ${S.py})`);
      q("-browL").setAttribute("transform", `translate(0 ${-Math.max(0, S.browL) / 4}) rotate(${S.browL} -22 -150)`);
      q("-browR").setAttribute("transform", `translate(0 ${Math.min(0, S.browR) / 4}) rotate(${S.browR} 22 -150)`);
    };
    const pipTo = (id, vars, dur, t, ease = "power2.out", from = null) => {
      const tw = Object.assign({}, vars, { duration: dur, ease, onUpdate: () => pipDraw(id) });
      if (from) tl.fromTo(PIPS[id], Object.assign({}, from), Object.assign(tw, { immediateRender: false }), t);
      else tl.to(PIPS[id], tw, t);
    };
    const Pip = {
      place(id, x, y, s = 1, dir = 1) {
        PIPS[id] = { x, y, s, dir, legL: 0, legR: 0, armL: 0, armR: 0, bodyY: 0, sx: 1, sy: 1, br: 1, px: 0, py: 0, browL: 0, browR: 0 };
        pipDraw(id);
        tl.set(PIPS[id], { x, y, s, dir, onComplete: () => pipDraw(id) }, 0);
      },
      move(id, x, y, t, dur, ease = "power2.inOut") { pipTo(id, { x, y }, dur, t, ease); },
      face(id, dir, t) { pipTo(id, { dir }, 0.12, t, "power1.inOut"); },
      walk(id, x1, t, dur) {
        pipTo(id, { x: x1 }, dur, t, "power1.inOut");
        const steps = Math.max(2, Math.round(dur / 0.28)), d = dur / steps;
        pipTo(id, { legL: 24, legR: -24 }, d, t, "sine.inOut", { legL: -24, legR: 24 });
        tl.to(PIPS[id], { legL: -24, legR: 24, bodyY: -7, duration: d, repeat: steps - 2, yoyo: true, ease: "sine.inOut", onUpdate: () => pipDraw(id) }, t + d);
        pipTo(id, { legL: 0, legR: 0, bodyY: 0 }, 0.18, t + dur);
      },
      mood(id, eyes, mouth, t) {  // a take: squash, the new face, a settle
        pipTo(id, { sy: 0.9, sx: 1.06 }, 0.08, t);
        ["normal", "wide", "happy", "closed"].forEach(k => tl.set("#" + id + "-eyes-" + k, { opacity: k === eyes ? 1 : 0 }, t + 0.06));
        ["smile", "o", "flat", "grin"].forEach(k => tl.set("#" + id + "-mouth-" + k, { opacity: k === mouth ? 1 : 0 }, t + 0.06));
        pipTo(id, { sy: 1, sx: 1 }, 0.4, t + 0.08, "elastic.out(1, 0.5)");
      },
      brows(id, l, r, t) { pipTo(id, { browL: l, browR: r }, 0.2, t); },
      look(id, dx, dy, t) { pipTo(id, { px: dx, py: dy }, 0.18, t); },
      arm(id, side, angle, t, dur = 0.32) { pipTo(id, side === "R" ? { armR: angle } : { armL: angle }, dur, t, "back.out(1.6)"); },
      jump(id, t, h = 70) {
        const y0 = PIPS[id].y;
        pipTo(id, { sy: 0.86, sx: 1.08 }, 0.1, t);
        pipTo(id, { y: y0 - h * PIPS[id].s, sy: 1.08, sx: 0.95 }, 0.24, t + 0.1, "power2.out");
        pipTo(id, { y: y0, sy: 1, sx: 1 }, 0.22, t + 0.34, "power2.in");
        pipTo(id, { sy: 0.9, sx: 1.06 }, 0.08, t + 0.56);
        pipTo(id, { sy: 1, sx: 1 }, 0.35, t + 0.64, "elastic.out(1, 0.5)");
      },
      blink(id, t) {
        tl.set("#" + id + "-eyes-normal", { opacity: 0 }, t); tl.set("#" + id + "-eyes-closed", { opacity: 1 }, t);
        tl.set("#" + id + "-eyes-closed", { opacity: 0 }, t + 0.12); tl.set("#" + id + "-eyes-normal", { opacity: 1 }, t + 0.12);
      },
      breathe(id, t, dur) {  // idle life: a slow breath, finite repeats, on its own channel
        const n = Math.max(1, Math.floor(dur / 1.6));
        tl.fromTo(PIPS[id], { br: 1 }, { br: 1.025, duration: 0.8, repeat: n * 2 - 1, yoyo: true, ease: "sine.inOut", immediateRender: false, onUpdate: () => pipDraw(id) }, t);
      },
    };
"""
