/* Run of the Champions: story film kit.
   A pitch seen from an angled camera, illustrated players with posable limbs, and the storyteller, Gus.
   Everything is drawn into SVG strings or updated in place from plain numbers, so a GSAP timeline can drive it. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const W = 1920, H = 1080;

  // ------------------------------------------------------------------ camera
  // World units are StatsBomb yards: x 0..120 along the pitch, y 0..80 across, z up.
  function Camera(o) {
    this.set(o);
  }
  Camera.prototype.set = function (o) {
    Object.assign(this, { ex: 60, ey: 130, ez: 60, tx: 60, ty: 40, tz: 0, fov: 1500, cx: W / 2, cy: H / 2 }, this, o);
    const f = norm([this.tx - this.ex, this.ty - this.ey, this.tz - this.ez]);
    const r = norm(cross(f, [0, 0, 1]));
    const u = cross(r, f);
    this.f = f; this.r = r; this.u = u;
    return this;
  };
  Camera.prototype.p = function (x, y, z) {
    const v = [x - this.ex, y - this.ey, (z || 0) - this.ez];
    const zc = dot(v, this.f), xc = dot(v, this.r), yc = dot(v, this.u);
    const k = this.fov / Math.max(zc, 0.5);
    return [this.cx + xc * k, this.cy - yc * k, k];
  };
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function norm(a) { const l = Math.hypot(a[0], a[1], a[2]); return [a[0] / l, a[1] / l, a[2] / l]; }

  // ------------------------------------------------------------------ pitch
  function pitchPaths(cam) {
    const segs = [];
    const line = (pts) => segs.push(pts.map(([x, y, z]) => cam.p(x, y, z || 0)));
    const rect = (x0, y0, x1, y1) => line([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]);
    const arc = (cx, cy, r, a0, a1, n) => {
      const pts = [];
      for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); }
      line(pts);
    };
    rect(0, 0, 120, 80);
    line([[60, 0], [60, 80]]);
    arc(60, 40, 10, 0, Math.PI * 2, 64);
    rect(0, 18, 18, 62); rect(102, 18, 120, 62);
    rect(0, 30, 6, 50); rect(114, 30, 120, 50);
    const da = Math.acos(6 / 10);
    arc(12, 40, 10, -da, da, 20); arc(108, 40, 10, Math.PI - da, Math.PI + da, 20);
    return segs;
  }
  function d(pts) { return pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" "); }
  function goal(cam, end) {
    // posts and bar (8 yards wide, 2.67 high) plus a little net depth
    const x = end ? 120 : 0, b = end ? 122 : -2, h = 2.67;
    const P = (X, Y, Z) => cam.p(X, Y, Z);
    const frame = d([P(x, 36, 0), P(x, 36, h), P(x, 44, h), P(x, 44, 0)]);
    const net = [d([P(x, 36, h), P(b, 36, h * 0.8), P(b, 44, h * 0.8), P(x, 44, h)]),
                 d([P(b, 36, h * 0.8), P(b, 36, 0)]), d([P(b, 44, h * 0.8), P(b, 44, 0)]),
                 d([P(b, 36, 0), P(b, 44, 0)])];
    let mesh = "";
    for (let i = 1; i < 8; i++) mesh += d([P(x, 36 + i, h), P(b, 36 + i, h * 0.8), P(b, 36 + i, 0)]) + " ";
    return `<path d="${net.join(" ")} ${mesh}" fill="none" stroke="rgba(255,255,255,.28)" stroke-width="2"/>` +
           `<path d="${frame}" fill="none" stroke="#fff" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>`;
  }
  function pitchSVG(cam, opt) {
    opt = opt || {};
    const stroke = opt.line || "rgba(255,255,255,.55)";
    const segs = pitchPaths(cam).map(d).join(" ");
    // mown stripes, 12 yards each, drawn as projected quads
    let stripes = "";
    for (let i = 0; i < 10; i += 2) {
      const a = cam.p(i * 12, 0), b = cam.p(i * 12 + 12, 0), c = cam.p(i * 12 + 12, 80), e = cam.p(i * 12, 80);
      stripes += d([a, b, c, e]) + "Z ";
    }
    const surf = d([cam.p(0, 0), cam.p(120, 0), cam.p(120, 80), cam.p(0, 80)]) + "Z";
    return `<path d="${surf}" fill="${opt.fill || "rgba(255,255,255,.035)"}"/>` +
           `<path d="${stripes}" fill="rgba(255,255,255,.035)"/>` +
           `<path d="${segs}" fill="none" stroke="${stroke}" stroke-width="${opt.w || 3}" stroke-linejoin="round"/>` +
           goal(cam, true) + goal(cam, false);
  }

  // ------------------------------------------------------------------ players
  // Kit colours only: no badges, no faces. One stylised skin tone for everyone.
  const KITS = {
    BAR: { shirt: "#a3123a", shirt2: "#1d3c8f", shorts: "#1d3c8f", socks: "#1d3c8f", boots: "#111" },
    JUV: { shirt: "#f4f4f2", shirt2: "#141414", shorts: "#141414", socks: "#141414", boots: "#111" },
    GKB: { shirt: "#c9f227", shirt2: "#c9f227", shorts: "#c9f227", socks: "#c9f227", boots: "#111" },
    GKJ: { shirt: "#ffb020", shirt2: "#ffb020", shorts: "#ffb020", socks: "#ffb020", boots: "#111" },
  };
  const SKIN = "#c4865f", HAIR = "#24170f";

  // angles in degrees from straight down; positive swings towards the way the player faces
  const POSES = {
    stand:   { hip: 50, lean: 2,   tF: 4,  sF: 0,   tB: -4,  sB: 0,   aF: 8,   fF: 18,  aB: -10, fB: 8,   rot: 0 },
    ready:   { hip: 46, lean: 14,  tF: 14, sF: -12, tB: -12, sB: -26, aF: 22,  fF: 60,  aB: -22, fB: 30,  rot: 0 },
    run1:    { hip: 48, lean: 16,  tF: 42, sF: -6,  tB: -30, sB: -78, aF: -38, fF: 30,  aB: 40,  fB: 100, rot: 0 },
    run2:    { hip: 48, lean: 16,  tF: -30, sF: -78, tB: 42, sB: -6, aF: 40,  fF: 100, aB: -38, fB: 30,  rot: 0 },
    dribble: { hip: 46, lean: 20,  tF: 30, sF: 8,   tB: -22, sB: -60, aF: -30, fF: 20,  aB: 46,  fB: 90,  rot: 0 },
    kick:    { hip: 49, lean: -10, tF: 70, sF: 82,  tB: -6,  sB: -4,  aF: -70, fF: -40, aB: 80,  fB: 70,  rot: 0 },
    wind:    { hip: 49, lean: 6,   tF: -40, sF: -100, tB: 6, sB: 0,   aF: 60,  fF: 80,  aB: -60, fB: -20, rot: 0 },
    slide:   { hip: 16, lean: -58, tF: 84, sF: 92,  tB: 40,  sB: -50, aF: -130, fF: -120, aB: 70, fB: 60,  rot: 0 },
    stretch: { hip: 40, lean: -8,  tF: 58, sF: 50,  tB: -20, sB: -30, aF: 40,  fF: 60,  aB: -40, fB: -10, rot: 0 },
    dive:    { hip: 34, lean: 0,   tF: 10, sF: 4,   tB: -12, sB: -20, aF: 175, fF: 178, aB: 160, fB: 170, rot: 78 },
    joy:     { hip: 52, lean: -4,  tF: 6,  sF: 0,   tB: -18, sB: -40, aF: 160, fF: 170, aB: -160, fB: -170, rot: 0 },
  };

  function seg(x, y, len, ang, dir) {
    const a = ang * Math.PI / 180;
    return [x + Math.sin(a) * len * dir, y + Math.cos(a) * len];
  }
  function ln(a, b, c, w) {
    return `<line x1="${a[0].toFixed(1)}" y1="${a[1].toFixed(1)}" x2="${b[0].toFixed(1)}" y2="${b[1].toFixed(1)}" stroke="${c}" stroke-width="${w}" stroke-linecap="round"/>`;
  }
  function shade(hex, k) {
    const n = parseInt(hex.slice(1), 16);
    const r = Math.round(((n >> 16) & 255) * k), g = Math.round(((n >> 8) & 255) * k), b = Math.round((n & 255) * k);
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
  // The figure in its own frame: feet at y=0, about 100 units tall, facing +x when dir = 1.
  function figureInner(pose, kit, dir, num) {
    const P = typeof pose === "string" ? POSES[pose] : pose;
    const K = KITS[kit] || kit;
    const hip = [0, -P.hip];
    const neck = seg(hip[0], hip[1], -34, -P.lean, dir); // up the torso
    const head = seg(neck[0], neck[1], -12, -P.lean, dir);
    const shoulder = seg(hip[0], hip[1], -30, -P.lean, dir);
    const out = [];
    const leg = (t, s, back) => {
      const k1 = seg(hip[0], hip[1], 25, t, dir), f = seg(k1[0], k1[1], 25, t + s, dir);
      const mid = [hip[0] + (k1[0] - hip[0]) * 0.55, hip[1] + (k1[1] - hip[1]) * 0.55];
      const sh = back ? 0.72 : 1;
      out.push(ln(hip, mid, shade(K.shorts, sh), 18));
      out.push(ln(mid, k1, shade(SKIN, sh), 13));
      const sk = [k1[0] + (f[0] - k1[0]) * 0.25, k1[1] + (f[1] - k1[1]) * 0.25];
      out.push(ln(k1, sk, shade(SKIN, sh), 12));
      out.push(ln(sk, f, shade(K.socks, sh), 12));
      const toe = seg(f[0], f[1], 9, t + s + 90, dir);
      out.push(ln(f, toe, shade(K.boots, 1), 9));
    };
    const arm = (u, fo, back) => {
      const e = seg(shoulder[0], shoulder[1], 17, u, dir), h = seg(e[0], e[1], 16, u + fo, dir);
      const sl = [shoulder[0] + (e[0] - shoulder[0]) * 0.6, shoulder[1] + (e[1] - shoulder[1]) * 0.6];
      const sh = back ? 0.72 : 1;
      out.push(ln(shoulder, sl, shade(K.shirt, sh), 12));
      out.push(ln(sl, e, shade(SKIN, sh), 10));
      out.push(ln(e, h, shade(SKIN, sh), 9));
    };
    arm(P.aB, P.fB, true);
    leg(P.tB, P.sB, true);
    // torso: a tapered stroke, with a second-colour stripe for striped kits
    out.push(ln(hip, neck, K.shirt, 28));
    if (K.shirt2 !== K.shirt) {
      const m1 = [hip[0] + (neck[0] - hip[0]) * 0.1, hip[1] + (neck[1] - hip[1]) * 0.1];
      const m2 = [hip[0] + (neck[0] - hip[0]) * 0.9, hip[1] + (neck[1] - hip[1]) * 0.9];
      out.push(ln([m1[0] + 5 * dir, m1[1]], [m2[0] + 5 * dir, m2[1]], K.shirt2, 6));
      out.push(ln([m1[0] - 5 * dir, m1[1]], [m2[0] - 5 * dir, m2[1]], K.shirt2, 6));
    }
    leg(P.tF, P.sF, false);
    arm(P.aF, P.fF, false);
    out.push(`<circle cx="${head[0].toFixed(1)}" cy="${head[1].toFixed(1)}" r="10" fill="${SKIN}"/>`);
    out.push(`<path d="M ${(head[0] - 10).toFixed(1)} ${(head[1] - 1).toFixed(1)} a 10 10 0 0 1 20 0 q -10 -5 -20 0 Z" fill="${HAIR}"/>`);
    if (num) out.push(`<text x="${neck[0].toFixed(1)}" y="${(neck[1] + 20).toFixed(1)}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="12" fill="${K.shirt2}">${num}</text>`);
    const rot = P.rot ? ` rotate(${P.rot * dir} 0 ${-P.hip})` : "";
    return `<g transform="translate(0 0)${rot}">${out.join("")}</g>`;
  }
  // a player standing at pitch point (x, y): scaled for depth, with a soft shadow
  function player(cam, x, y, pose, kit, dir, opt) {
    opt = opt || {};
    const [sx, sy, k] = cam.p(x, y, 0);
    const s = k * 2.0 / 100 * (opt.scale || 1); // 100 figure units = 2 yards
    const lift = opt.lift ? opt.lift * k : 0;
    const shadow = `<ellipse cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" rx="${(26 * s).toFixed(1)}" ry="${(7 * s).toFixed(1)}" fill="rgba(10,0,30,.35)"/>`;
    return shadow + `<g transform="translate(${sx.toFixed(1)} ${(sy - lift).toFixed(1)}) scale(${s.toFixed(3)})">${figureInner(pose, kit, dir, opt.num)}</g>`;
  }
  function ball(cam, x, y, z) {
    const [sx, sy, k] = cam.p(x, y, z || 0.12);
    const [gx, gy] = cam.p(x, y, 0);
    const r = Math.max(4, k * 0.12);
    return `<ellipse cx="${gx.toFixed(1)}" cy="${gy.toFixed(1)}" rx="${(r * 1.1).toFixed(1)}" ry="${(r * 0.35).toFixed(1)}" fill="rgba(10,0,30,.35)"/>` +
           `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${r.toFixed(1)}" fill="#fff" stroke="#111" stroke-width="${(r * 0.18).toFixed(1)}"/>` +
           `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${(r * 0.38).toFixed(1)}" fill="#111"/>`;
  }
  // a name tag above a player
  function nameTag(cam, x, y, name, team, h) {
    const [sx, sy, k] = cam.p(x, y, h || 2.5);
    const w = 22 + name.length * 15.5;
    const col = team === "JUV" ? "#f4f4f2" : "#ff3b55";
    return `<g transform="translate(${sx.toFixed(1)} ${(sy - 16).toFixed(1)})">` +
           `<rect x="${-w / 2}" y="-44" width="${w}" height="42" rx="21" fill="rgba(20,8,60,.85)" stroke="${col}" stroke-width="3"/>` +
           `<text x="0" y="-15" text-anchor="middle" font-family="Inter" font-weight="700" font-size="26" fill="#fff">${name}</text>` +
           `<path d="M -7 -2 L 0 8 L 7 -2 Z" fill="${col}"/></g>`;
  }
  // a dashed path on the ground between two pitch points
  function groundArrow(cam, a, b, col, lift) {
    const n = 24, pts = [];
    for (let i = 0; i <= n; i++) {
      const t = i / n, x = a[0] + (b[0] - a[0]) * t, y = a[1] + (b[1] - a[1]) * t;
      pts.push(cam.p(x, y, (lift || 0) * 4 * t * (1 - t)));
    }
    return `<path d="${d(pts)}" fill="none" stroke="${col}" stroke-width="6" stroke-dasharray="16 12" stroke-linecap="round"/>`;
  }

  // ------------------------------------------------------------------ Gus, the storyteller
  // An old groundsman with a flat cap, a white moustache and a stick of chalk. His own frame: feet at 0, about 520 tall.
  function gus(id, opt) {
    opt = opt || {};
    const coat = "#2f6b4f", coat2 = "#245640", shirt = "#f2ede2", trouser = "#5a4636", cap = "#7a6a55", skin = "#e8b48e";
    return `<g id="${id}">
      <ellipse cx="0" cy="0" rx="120" ry="16" fill="rgba(10,0,30,.35)"/>
      <!-- legs and boots -->
      <g id="${id}-legs">
        <rect x="-58" y="-200" width="46" height="190" rx="18" fill="${trouser}"/>
        <rect x="12" y="-200" width="46" height="190" rx="18" fill="${shade(trouser, 0.86)}"/>
        <path d="M -70 -16 q 0 -26 30 -26 h 26 q 6 0 6 10 v 32 h -62 Z" fill="#2a1d14"/>
        <path d="M 8 -16 q 0 -26 30 -26 h 26 q 6 0 6 10 v 32 h -62 Z" fill="#2a1d14"/>
      </g>
      <!-- arm behind -->
      <g id="${id}-armB" transform="rotate(${opt.armB || 0} 64 -372)">
        <rect x="46" y="-376" width="40" height="150" rx="20" fill="${coat2}"/>
        <circle cx="66" cy="-218" r="21" fill="${skin}"/>
        <rect x="60" y="-202" width="12" height="34" rx="4" fill="#fff"/>
      </g>
      <!-- body: cardigan over a shirt and tie -->
      <path d="M -92 -380 q 0 -40 40 -46 h 104 q 40 6 40 46 v 186 q 0 14 -14 14 h -156 q -14 0 -14 -14 Z" fill="${coat}"/>
      <path d="M -26 -426 h 52 l -12 120 h -28 Z" fill="${shirt}"/>
      <path d="M -7 -416 h 14 l 7 92 l -14 16 l -14 -16 Z" fill="#a3123a"/>
      <circle cx="-42" cy="-300" r="6" fill="#d9c27a"/><circle cx="-42" cy="-262" r="6" fill="#d9c27a"/><circle cx="-42" cy="-224" r="6" fill="#d9c27a"/>
      <rect x="20" y="-300" width="44" height="34" rx="6" fill="${coat2}"/>
      <!-- head -->
      <g id="${id}-head" transform="rotate(${opt.tilt || 0} 0 -440)">
        <rect x="-18" y="-452" width="36" height="34" fill="${shade(skin, 0.9)}"/>
        <ellipse cx="0" cy="-520" rx="70" ry="78" fill="${skin}"/>
        <ellipse cx="-70" cy="-514" rx="12" ry="20" fill="${shade(skin, 0.92)}"/>
        <ellipse cx="70" cy="-514" rx="12" ry="20" fill="${shade(skin, 0.92)}"/>
        <!-- eyes, brows, glasses -->
        <g id="${id}-eyes"><ellipse cx="-25" cy="-528" rx="8" ry="10" fill="#22160f"/><ellipse cx="25" cy="-528" rx="8" ry="10" fill="#22160f"/>
          <circle cx="-22" cy="-532" r="3" fill="#fff"/><circle cx="28" cy="-532" r="3" fill="#fff"/></g>
        <g id="${id}-blink" opacity="0"><path d="M -35 -528 h 20 M 15 -528 h 20" stroke="#22160f" stroke-width="5" stroke-linecap="round"/></g>
        <circle cx="-25" cy="-528" r="21" fill="none" stroke="#3b2c22" stroke-width="5"/>
        <circle cx="25" cy="-528" r="21" fill="none" stroke="#3b2c22" stroke-width="5"/>
        <path d="M -4 -530 h 8" stroke="#3b2c22" stroke-width="5"/>
        <path id="${id}-browL" d="M -44 -560 q 18 -12 36 -2" stroke="#e9e4da" stroke-width="9" fill="none" stroke-linecap="round"/>
        <path id="${id}-browR" d="M 8 -562 q 18 -10 36 2" stroke="#e9e4da" stroke-width="9" fill="none" stroke-linecap="round"/>
        <ellipse cx="0" cy="-498" rx="13" ry="16" fill="${shade(skin, 0.88)}"/>
        <!-- mouth (opens when he talks), then the moustache over it -->
        <ellipse id="${id}-mouth" cx="0" cy="-466" rx="16" ry="${opt.mouth == null ? 3 : opt.mouth}" fill="#5a1f1a"/>
        <path d="M 0 -486 q -22 -6 -46 6 q 10 18 30 12 q 12 -4 16 -10 q 4 6 16 10 q 20 6 30 -12 q -24 -12 -46 -6 Z" fill="#f1ede6"/>
        <!-- flat cap -->
        <path d="M -76 -560 q 4 -62 80 -64 q 66 2 74 58 q -70 -14 -154 6 Z" fill="${cap}"/>
        <path d="M -78 -558 q 60 -20 150 -8 q 40 6 46 18 q -60 -6 -120 2 q -50 4 -76 -12 Z" fill="${shade(cap, 0.82)}"/>
      </g>
      <!-- arm in front, holding chalk -->
      <g id="${id}-armF" transform="rotate(${opt.armF || 0} -66 -372)">
        <rect x="-88" y="-376" width="42" height="150" rx="21" fill="${coat}"/>
        <rect x="-82" y="-246" width="30" height="20" rx="4" fill="${shirt}"/>
        <circle cx="-67" cy="-212" r="22" fill="${skin}"/>
      </g>
    </g>`;
  }

  window.Story = { Camera, pitchSVG, player, ball, nameTag, groundArrow, gus, POSES, KITS, figureInner, W, H };
})();
