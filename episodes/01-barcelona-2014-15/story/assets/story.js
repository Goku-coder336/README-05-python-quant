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
  const SKIN = "#b97a55", HAIR = "#1f140d";

  // angles in degrees from straight down; positive swings towards the way the player faces.
  // t = thigh, s = knee bend (added to the thigh for the shin), a = upper arm, f = elbow bend; F = near side, B = far side.
  const POSES = {
    stand:   { lean: 3,   tF: 6,   sF: -6,  tB: -5,  sB: -2,   aF: 10,   fF: 16,  aB: -8,   fB: 14 },
    ready:   { lean: 20,  tF: 24,  sF: -30, tB: -18, sB: -22,  aF: 34,   fF: 40,  aB: -34,  fB: 34 },
    run1:    { lean: 16,  tF: 58,  sF: -40, tB: -26, sB: -88,  aF: -48,  fF: 86,  aB: 52,   fB: 84 },
    run2:    { lean: 16,  tF: -26, sF: -88, tB: 58,  sB: -40,  aF: 52,   fF: 84,  aB: -48,  fB: 86 },
    dribble: { lean: 24,  tF: 44,  sF: -24, tB: -32, sB: -74,  aF: -40,  fF: 64,  aB: 58,   fB: 70 },
    wind:    { lean: 10,  tF: -38, sF: -96, tB: 8,   sB: -6,   aF: 72,   fF: 30,  aB: -64,  fB: 14 },
    kick:    { lean: -16, tF: 96,  sF: -4,  tB: -4,  sB: -10,  aF: -112, fF: 30,  aB: 86,   fB: 22 },
    stretch: { lean: -2,  tF: 74,  sF: 18,  tB: -42, sB: 12,   aF: 52,   fF: 30,  aB: -60,  fB: 10 },
    slide:   { lean: -48, tF: 84,  sF: 6,   tB: 70,  sB: -150, aF: -150, fF: 10,  aB: 70,   fB: 40 },
    dive:    { lean: 0,   tF: 12,  sF: -8,  tB: -14, sB: -22,  aF: 172,  fF: 4,   aB: 158,  fB: 10, rot: 82, air: 26 },
    joy:     { lean: -6,  tF: 22,  sF: -44, tB: -10, sB: -6,   aF: 160,  fF: 12,  aB: -158, fB: -14 },
  };

  function seg(x, y, len, ang, dir) {
    const a = ang * Math.PI / 180;
    return [x + Math.sin(a) * len * dir, y + Math.cos(a) * len];
  }
  const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  function shade(hex, k) {
    const n = parseInt(hex.slice(1), 16);
    const r = Math.min(255, Math.round(((n >> 16) & 255) * k)), g = Math.min(255, Math.round(((n >> 8) & 255) * k)), b = Math.min(255, Math.round((n & 255) * k));
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  }
  // a tapered limb: a capsule from a (radius r1) to b (radius r2)
  function capsule(a, b, r1, r2) {
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 0.001;
    const ux = dx / l, uy = dy / l, nx = -uy, ny = ux;
    const f = (v) => v.toFixed(2);
    return `M ${f(a[0] + nx * r1)} ${f(a[1] + ny * r1)} L ${f(b[0] + nx * r2)} ${f(b[1] + ny * r2)} ` +
           `A ${f(r2)} ${f(r2)} 0 0 0 ${f(b[0] - nx * r2)} ${f(b[1] - ny * r2)} L ${f(a[0] - nx * r1)} ${f(a[1] - ny * r1)} ` +
           `A ${f(r1)} ${f(r1)} 0 0 0 ${f(a[0] + nx * r1)} ${f(a[1] + ny * r1)} Z`;
  }
  let FIG = 0;
  // The figure in its own frame: feet on y = 0, about 104 units tall, facing +x when dir = 1.
  function figureInner(pose, kit, dir, num) {
    const P = typeof pose === "string" ? POSES[pose] : pose;
    const K = KITS[kit] || kit;
    const id = "fg" + (FIG++);
    const hip = [0, -50];
    const tor = (len) => seg(hip[0], hip[1], -len, -P.lean, dir);
    const neck = tor(32), chest = tor(18), shoulder = tor(25), headC = tor(40);
    const out = [], pts = [];
    const fill = (d, c) => out.push(`<path d="${d}" fill="${c}"/>`);
    const soft = (d, c, edge) => out.push(`<path d="${d}" fill="${c}" stroke="${edge || c}" stroke-width="1.6" stroke-linejoin="round"/>`);
    const poly = (ps) => "M " + ps.map(q => q[0].toFixed(2) + " " + q[1].toFixed(2)).join(" L ") + " Z";
    const perp = (a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1; return [-dy / l, dx / l]; };
    const off = (q, n, r) => [q[0] + n[0] * r, q[1] + n[1] * r];
    const leg = (t, s, back) => {
      const knee = seg(hip[0], hip[1], 26, t, dir), ankle = seg(knee[0], knee[1], 25, t + s, dir);
      const toe = seg(ankle[0], ankle[1], 10, t + s + 92, dir), heel = seg(ankle[0], ankle[1], 3, t + s - 90, dir);
      pts.push(ankle, toe, heel);
      const k = back ? 0.74 : 1;
      const calf = lerp(knee, ankle, 0.32), sock = lerp(knee, ankle, 0.16);
      fill(capsule(hip, knee, 7.8, 5.7), shade(SKIN, k));                 // thigh
      fill(capsule(knee, calf, 6.0, 6.4), shade(SKIN, k));                // knee to calf
      fill(capsule(sock, calf, 6.1, 6.6) + capsule(calf, ankle, 6.6, 3.9), shade(K.socks, k)); // sock over the calf
      fill(capsule(heel, toe, 4.6, 3.4), shade(K.boots, back ? 1 : 1.6)); // boot
      { // shorts leg: a loose trapezoid from the waist to mid-thigh
        const w = tor(4), L = lerp(hip, knee, 0.46), n = perp(w, hip), m = perp(hip, knee);
        soft(poly([off(w, n, 8.4), off(L, m, 8.4), off(L, m, -8.4), off(w, n, -8.4)]), shade(K.shorts, k));
      }
    };
    const arm = (u, fo, back) => {
      const elbow = seg(shoulder[0], shoulder[1], 17, u, dir), hand = seg(elbow[0], elbow[1], 16, u + fo, dir);
      pts.push(hand);
      const k = back ? 0.74 : 1;
      fill(capsule(shoulder, elbow, 4.9, 4.1) + capsule(elbow, hand, 4.0, 3.2), shade(SKIN, k));
      out.push(`<circle cx="${hand[0].toFixed(2)}" cy="${hand[1].toFixed(2)}" r="3.8" fill="${shade(SKIN, k)}"/>`);
      soft(capsule(shoulder, lerp(shoulder, elbow, 0.42), 5.2, 4.8), shade(K.shirt, back ? 0.8 : 0.93), shade(K.shirt, back ? 0.62 : 0.8)); // short sleeve
    };
    arm(P.aB, P.fB, true);
    leg(P.tB, P.sB, true);
    // pelvis and torso, with stripes clipped to the shirt
    const tn = perp(shoulder, hip), waist = tor(3), top = tor(27.5);
    const torsoD = poly([off(waist, tn, 9.2), off(chest, tn, 11.2), off(shoulder, tn, 10.6), off(top, tn, 6), off(top, tn, -6), off(shoulder, tn, -10.6), off(chest, tn, -11.2), off(waist, tn, -9.2)]);
    
    soft(poly([off(tor(6), tn, 9.4), off(tor(-5), tn, 9.8), off(tor(-5), tn, -9.8), off(tor(6), tn, -9.4)]), K.shorts); // waistband to hips
    out.push(`<clipPath id="${id}c"><path d="${torsoD}"/></clipPath>`);
    soft(torsoD, K.shirt);
    if (K.shirt2 !== K.shirt) {
      const offs = kit === "JUV" ? [-9, -1.5, 6] : [-6.5, 5];
      const w = kit === "JUV" ? 4.2 : 5.6;
      const a0 = tor(-4), a1 = tor(36);
      const nx = (a1[1] - a0[1]), ny = -(a1[0] - a0[0]), nl = Math.hypot(nx, ny);
      let st = "";
      for (const o of offs) st += `<line x1="${(a0[0] + nx / nl * o).toFixed(2)}" y1="${(a0[1] + ny / nl * o).toFixed(2)}" x2="${(a1[0] + nx / nl * o).toFixed(2)}" y2="${(a1[1] + ny / nl * o).toFixed(2)}" stroke="${K.shirt2}" stroke-width="${w}"/>`;
      out.push(`<g clip-path="url(#${id}c)">${st}</g>`);
    }
    // a soft shadow down the back of the shirt
    const b0 = seg(hip[0], hip[1], 9, -P.lean - 90, dir), b1 = seg(shoulder[0], shoulder[1], 9, -P.lean - 90, dir);
    out.push(`<g clip-path="url(#${id}c)"><line x1="${b0[0].toFixed(2)}" y1="${b0[1].toFixed(2)}" x2="${b1[0].toFixed(2)}" y2="${b1[1].toFixed(2)}" stroke="rgba(0,0,0,.22)" stroke-width="8"/></g>`);
    if (num) out.push(`<text x="${chest[0].toFixed(1)}" y="${(chest[1] + 4).toFixed(1)}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="11" fill="${K.shirt2}">${num}</text>`);
    leg(P.tF, P.sF, false);
    // neck and head: no face, just shape, an ear and hair
    fill(capsule(shoulder, neck, 4.4, 4.0), shade(SKIN, 0.9));
    const ang = (-P.lean) * dir;
    out.push(`<g transform="rotate(${ang.toFixed(1)} ${headC[0].toFixed(2)} ${headC[1].toFixed(2)})">` +
      `<ellipse cx="${headC[0].toFixed(2)}" cy="${headC[1].toFixed(2)}" rx="6.6" ry="7.8" fill="${SKIN}"/>` +
      `<path d="M ${(headC[0] - 6.9 * dir).toFixed(2)} ${(headC[1] + 3).toFixed(2)} C ${(headC[0] - 8.2 * dir).toFixed(2)} ${(headC[1] - 6).toFixed(2)} ${(headC[0] - 4 * dir).toFixed(2)} ${(headC[1] - 9.4).toFixed(2)} ${(headC[0] + 1.5 * dir).toFixed(2)} ${(headC[1] - 8.5).toFixed(2)} C ${(headC[0] + 6.5 * dir).toFixed(2)} ${(headC[1] - 9).toFixed(2)} ${(headC[0] + 7.3 * dir).toFixed(2)} ${(headC[1] - 5).toFixed(2)} ${(headC[0] + 6.6 * dir).toFixed(2)} ${(headC[1] - 2.6).toFixed(2)} C ${(headC[0] + 3 * dir).toFixed(2)} ${(headC[1] - 5.4).toFixed(2)} ${(headC[0] - 2 * dir).toFixed(2)} ${(headC[1] - 4).toFixed(2)} ${(headC[0] - 3.4 * dir).toFixed(2)} ${(headC[1] + 2).toFixed(2)} Z" fill="${HAIR}"/>` +
      `<ellipse cx="${(headC[0] - 2.6 * dir).toFixed(2)}" cy="${(headC[1] + 1.4).toFixed(2)}" rx="1.6" ry="2.3" fill="${shade(SKIN, 0.82)}"/></g>`);
    arm(P.aF, P.fF, false);
    // stand on the ground: the lowest foot touches y = 0 (or hang in the air for a dive)
    let low = -1e9;
    for (const p of pts) low = Math.max(low, p[1]);
    let dy = -low;
    const rot = P.rot ? ` rotate(${P.rot * dir} ${hip[0]} ${hip[1]})` : "";
    if (P.rot) dy = 50 - (P.air || 0) - 12;
    return `<g transform="translate(0 ${dy.toFixed(2)})${rot}">${out.join("")}</g>`;
  }
  // a player standing at pitch point (x, y): scaled for depth, with a soft shadow
  function player(cam, x, y, pose, kit, dir, opt) {
    opt = opt || {};
    const [sx, sy, k] = cam.p(x, y, 0);
    const s = k * 2.0 / 100 * (opt.scale || 1); // 100 figure units = 2 yards
    const lift = opt.lift ? opt.lift * k : 0;
    const shadow = `<ellipse cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" rx="${(24 * s).toFixed(1)}" ry="${(6 * s).toFixed(1)}" fill="rgba(0,20,25,.35)"/>`;
    return shadow + `<g transform="translate(${sx.toFixed(1)} ${(sy - lift).toFixed(1)}) scale(${s.toFixed(3)})">${figureInner(pose, kit, dir, opt.num)}</g>`;
  }
  function ball(cam, x, y, z) {
    const [sx, sy, k] = cam.p(x, y, z || 0.12);
    const [gx, gy] = cam.p(x, y, 0);
    const r = Math.max(4, k * 0.12);
    return `<ellipse cx="${gx.toFixed(1)}" cy="${gy.toFixed(1)}" rx="${(r * 1.1).toFixed(1)}" ry="${(r * 0.35).toFixed(1)}" fill="rgba(0,20,25,.35)"/>` +
           `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${r.toFixed(1)}" fill="#fff" stroke="#111" stroke-width="${(r * 0.18).toFixed(1)}"/>` +
           `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${(r * 0.38).toFixed(1)}" fill="#111"/>`;
  }
  // a name tag above a player
  function nameTag(cam, x, y, name, team, h) {
    const [sx, sy, k] = cam.p(x, y, h || 2.5);
    const w = 22 + name.length * 15.5;
    const col = team === "JUV" ? "#f4f4f2" : "#ff3b55";
    return `<g transform="translate(${sx.toFixed(1)} ${(sy - 16).toFixed(1)})">` +
           `<rect x="${-w / 2}" y="-44" width="${w}" height="42" rx="21" fill="rgba(4,32,36,.88)" stroke="${col}" stroke-width="3"/>` +
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
      <ellipse cx="0" cy="0" rx="120" ry="16" fill="rgba(0,20,25,.35)"/>
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
