/* Pencil-storyboard cast for "Blue Saree": Meera, Arjun, the rainy Fort Kochi tea stall.
 * Everything is a pure function of time. Lines "boil" (re-jitter) 12 times a second like a hand-drawn animatic.
 */
(function () {
  const C = {
    paper: "#f4ecdc", pencil: "#3a332d", soft: "rgba(58,51,45,0.45)", hatch: "rgba(58,51,45,0.28)",
    skinM: "#d9a77f", skinA: "#c99470", hair: "#2f2725", saree: "#3b67c4", sareeDark: "#2c4f9a", gold: "#d4a537",
    shirt: "#efe3c6", mundu: "#faf6ec", awning: "#b5683f", wood: "#a57a52", woodDark: "#7f5a3b", sky: "#c9d3d6",
    wall: "#e2d4bb", wallDark: "#cdbb9c", road: "#b8b6ae", puddle: "#9fb0bb", jasmine: "#ffffff", chai: "#b07a45",
    lips: "#b8585a", blush: "rgba(222,120,110,0.35)", bike: "#2b2b2b", rain: "rgba(70,80,95,0.55)",
  };
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const ease = (k) => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2);
  const easeOut = (k) => 1 - Math.pow(1 - k, 3);
  const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  // ---- pencil primitives -------------------------------------------------------------
  let BOIL = 0; // set per frame
  function curve(ctx, pts, closed, smooth) {
    const n = pts.length; ctx.beginPath();
    if (n < 3 || !smooth) { ctx.moveTo(pts[0][0], pts[0][1]); for (const p of pts.slice(1)) ctx.lineTo(p[0], p[1]); if (closed) ctx.closePath(); return; }
    const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    if (closed) {
      let m = mid(pts[n - 1], pts[0]); ctx.moveTo(m[0], m[1]);
      for (let i = 0; i < n; i++) { const p = pts[i], q = pts[(i + 1) % n], mm = mid(p, q); ctx.quadraticCurveTo(p[0], p[1], mm[0], mm[1]); }
      ctx.closePath();
    } else {
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (let i = 1; i < n - 1; i++) { const mm = mid(pts[i], pts[i + 1]); ctx.quadraticCurveTo(pts[i][0], pts[i][1], mm[0], mm[1]); }
      ctx.lineTo(pts[n - 1][0], pts[n - 1][1]);
    }
  }
  const jitter = (pts, amt, seed) => pts.map((p, i) => [p[0] + (hash(seed + i * 7.3 + BOIL * 13.1) - 0.5) * amt, p[1] + (hash(seed + i * 3.7 + BOIL * 9.7 + 50) - 0.5) * amt]);
  // fill + two jittery pencil passes
  function shape(ctx, pts, o = {}) {
    const seed = o.seed || pts.length * 3.1 + pts[0][0] * 0.01;
    if (o.fill) { curve(ctx, jitter(pts, (o.j || 2) * 0.6, seed + 99), o.closed !== false, o.smooth ?? pts.length >= 8); ctx.fillStyle = o.fill; ctx.fill(); }
    if (o.line === false) return;
    ctx.strokeStyle = o.col || C.pencil; ctx.lineCap = "round"; ctx.lineJoin = "round";
    for (let pass = 0; pass < 2; pass++) {
      ctx.lineWidth = (o.w || 2.6) * (pass ? 0.6 : 1); ctx.globalAlpha = pass ? 0.5 : 0.9;
      curve(ctx, jitter(pts, o.j || 2.5, seed + pass * 41), o.closed !== false, o.smooth ?? pts.length >= 8); ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
  const line = (ctx, pts, o = {}) => shape(ctx, pts, { ...o, closed: false });
  function ellipsePts(cx, cy, rx, ry, n = 18, a0 = 0, a1 = Math.PI * 2) {
    const out = []; for (let i = 0; i < n; i++) { const a = a0 + (a1 - a0) * (i / (a1 - a0 >= 6.28 ? n : n - 1)); out.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); } return out;
  }
  function hatch(ctx, clipPts, x0, y0, x1, y1, gap = 10, ang = 0.9) {
    ctx.save(); curve(ctx, clipPts, true); ctx.clip();
    ctx.strokeStyle = C.hatch; ctx.lineWidth = 1.6;
    const dx = Math.cos(ang) * 600, dy = Math.sin(ang) * 600;
    for (let k = x0 - 300; k < x1 + 300; k += gap) { ctx.beginPath(); ctx.moveTo(k, y0); ctx.lineTo(k + dx, y0 + dy); ctx.stroke(); }
    ctx.restore();
  }

  // paper texture (built once, deterministic)
  let PAPER = null;
  function paper(ctx) {
    if (!PAPER) {
      PAPER = document.createElement("canvas"); PAPER.width = 1080; PAPER.height = 1920;
      const p = PAPER.getContext("2d"); p.fillStyle = C.paper; p.fillRect(0, 0, 1080, 1920);
      for (let i = 0; i < 9000; i++) { p.fillStyle = `rgba(90,70,40,${hash(i) * 0.06})`; p.fillRect(hash(i + 1) * 1080, hash(i + 2) * 1920, 2, 2); }
      const g = p.createRadialGradient(540, 960, 500, 540, 960, 1200); g.addColorStop(0, "rgba(0,0,0,0)"); g.addColorStop(1, "rgba(80,60,30,0.18)");
      p.fillStyle = g; p.fillRect(0, 0, 1080, 1920);
    }
    ctx.drawImage(PAPER, 0, 0);
  }

  // ---- full-body figure ----------------------------------------------------------------
  // P: {who:"meera"|"arjun", x, ground, s, facing, run 0..1, phase, lean, arms:{front:[up,low], back:[up,low]},
  //     look 0..1 (eyes toward viewer side), blink, smile, pallu:{lift, amp}, t}
  function figure(ctx, P) {
    const meera = P.who === "meera", s = P.s || 1, f = P.facing || 1, t = P.t || 0, run = P.run || 0;
    const skin = meera ? C.skinM : C.skinA;
    const bob = -Math.abs(Math.sin(P.phase || 0)) * 16 * run;
    ctx.save(); ctx.translate(P.x, P.ground - 300 * s + bob * s); ctx.scale(f * s, s);
    const lean = P.lean || 0;
    const st = [Math.sin(lean) * 230, -Math.cos(lean) * 230];
    const rot = (p) => [p[0] * Math.cos(lean) - p[1] * Math.sin(lean), p[0] * Math.sin(lean) + p[1] * Math.cos(lean)];
    // legs -> feet
    const feet = [0, 1].map((k) => {
      if (run < 0.01) return [k ? 20 : -16, 300 - bob];
      const ph = (P.phase || 0) + k * Math.PI;
      const th = run * (meera ? 0.36 : 0.62) * Math.sin(ph), bend = run * 1.25 * Math.max(0, Math.sin(ph - 1.3));
      const knee = [Math.sin(th) * 150, Math.cos(th) * 150], sh = th - bend;
      return [knee[0] + Math.sin(sh) * 150, knee[1] + Math.cos(sh) * 150];
    });
    const shoulder = (side) => { const p = rot([side * 36, -216]); return p; };
    const limb = (from, up, low, sleeve) => {
      const e = [from[0] + Math.sin(up) * 105, from[1] + Math.cos(up) * 105];
      const h = [e[0] + Math.sin(up + low) * 100, e[1] + Math.cos(up + low) * 100];
      ctx.lineCap = "round";
      ctx.strokeStyle = C.pencil; ctx.lineWidth = 24; curve(ctx, jitter([from, e, h], 2, from[0] + up), false, true); ctx.stroke();
      ctx.strokeStyle = skin; ctx.lineWidth = 18; curve(ctx, [from, e, h], false, true); ctx.stroke();
      if (sleeve) { ctx.strokeStyle = sleeve; ctx.lineWidth = 30; ctx.beginPath(); ctx.moveTo(from[0], from[1]); ctx.lineTo(lerp(from[0], e[0], 0.55), lerp(from[1], e[1], 0.55)); ctx.stroke();
        line(ctx, [[from[0] - 14, from[1]], [lerp(from[0], e[0], 0.55) - 14, lerp(from[1], e[1], 0.55)]], { w: 2 }); }
      if (meera) for (let k = 0; k < 2; k++) shape(ctx, ellipsePts(lerp(e[0], h[0], 0.8 + k * 0.06), lerp(e[1], h[1], 0.8 + k * 0.06), 11, 5, 10), { fill: null, col: C.gold, w: 2.4, j: 1 });
      shape(ctx, ellipsePts(h[0], h[1] + 6, 11, 14, 10), { fill: skin, w: 2.2 });
      return h;
    };
    const runArm = (k) => [-(run * 0.8) * Math.sin((P.phase || 0) + k * Math.PI), 0.25 + run * 1.1];
    const backArm = P.arms?.back || runArm(1), frontArm = P.arms?.front || runArm(0);
    // back arm
    limb(shoulder(-1), backArm[0], backArm[1], meera ? null : C.shirt);
    // pallu (Meera) flowing behind
    if (meera) {
      const pl = P.pallu || {}, n = 9, base = shoulder(-1);
      const dir = lerp(0.12, 1.25, clamp(pl.lift ?? run)); // radians from straight down toward the back
      const left = [], right = [];
      for (let i = 0; i <= n; i++) {
        const k = i / n, a = dir + Math.sin(t * 7 - i * 0.7) * (pl.amp ?? 0.12) * k;
        const px = base[0] - Math.sin(a) * 290 * k - 8, py = base[1] + Math.cos(a) * 290 * k + 10;
        const w = lerp(26, 46, k);
        left.push([px - Math.cos(a) * w, py - Math.sin(a) * w]); right.push([px + Math.cos(a) * w, py + Math.sin(a) * w]);
      }
      shape(ctx, [...left, ...right.reverse()], { fill: C.sareeDark, w: 2.4, seed: 17, smooth: true });
      line(ctx, left.map((p) => [p[0] + 5, p[1]]), { col: C.gold, w: 3, j: 1 });
    }
    // lower garment (saree skirt / mundu)
    const fx = feet.map((p) => p[0]), hemY = Math.max(feet[0][1], feet[1][1]) - 26;
    const skirt = [[-40, -12], [40, -12], [Math.max(...fx) + 42, hemY], [lerp(Math.max(...fx), Math.min(...fx), 0.5), hemY + 8], [Math.min(...fx) - 42, hemY]];
    for (const p of feet) shape(ctx, ellipsePts(p[0] + 10, p[1] - 4, 22, 9, 10), { fill: meera ? C.gold : "#6b4a33", w: 2.2 });
    shape(ctx, skirt, { fill: meera ? C.saree : C.mundu, w: 2.6, seed: 5 });
    line(ctx, [[Math.min(...fx) - 40, hemY - 6], [Math.max(...fx) + 40, hemY - 6]], { col: C.gold, w: 4, j: 1.5 });
    if (meera) for (let k = 0; k < 4; k++) line(ctx, [[-10 + k * 9, -6], [lerp(-10, Math.min(...fx) - 10, 0.5) + k * 22, hemY - 10]], { col: C.soft, w: 1.6 }); // pleats
    else line(ctx, [[30, -8], [Math.max(...fx) + 20, hemY - 8]], { col: C.soft, w: 1.6 });
    // torso
    const tor = [rot([-40, -222]), rot([40, -222]), rot([34, -12]), rot([-34, -12])];
    shape(ctx, tor, { fill: meera ? C.saree : C.shirt, w: 2.6, seed: 3 });
    hatch(ctx, tor, -60, -260, 60, 0, 11);
    if (meera) { line(ctx, [rot([-34, -214]), rot([30, -40])], { col: C.gold, w: 3, j: 1.5 }); }
    else { line(ctx, [rot([-12, -222]), rot([0, -190]), rot([12, -222])], { w: 2.2 }); line(ctx, [rot([0, -190]), rot([0, -20])], { col: C.soft, w: 1.6 }); }
    // front arm
    const hand = limb(shoulder(1), frontArm[0], frontArm[1], meera ? null : C.shirt);
    // neck + head
    const tilt = P.tilt || 0;
    const hc = rot([8, -282]);
    ctx.strokeStyle = skin; ctx.lineWidth = 22; ctx.beginPath(); ctx.moveTo(...rot([0, -222])); ctx.lineTo(hc[0], hc[1] + 30); ctx.stroke();
    ctx.save(); ctx.translate(hc[0], hc[1]); ctx.rotate(tilt + lean * 0.5);
    if (meera) { // braid down the back + jasmine
      const br = []; for (let i = 0; i < 7; i++) br.push([-30 - i * 3 + Math.sin(t * 3 + i * 0.5) * 3 * i * 0.3, 10 + i * 20]);
      br.forEach((p, i) => shape(ctx, ellipsePts(p[0], p[1], 11, 13, 9), { fill: C.hair, w: 1.8, seed: 60 + i }));
      for (let i = 0; i < 6; i++) shape(ctx, ellipsePts(-38 + (i % 2) * 8, -14 + i * 9, 5, 5, 6), { fill: C.jasmine, w: 1.2, j: 1, seed: 80 + i });
    }
    shape(ctx, ellipsePts(0, 0, 34, 42, 20), { fill: skin, w: 2.6, seed: 9 });
    if (meera) {
      shape(ctx, [[-36, 4], [-34, -26], [-14, -44], [14, -44], [32, -26], [26, -10], [6, -30], [-20, -18], [-28, 6]], { fill: C.hair, w: 2.2, seed: 11 });
      shape(ctx, ellipsePts(20, 10, 3, 5, 6), { fill: C.gold, w: 1.4, j: 0.6 }); // jhumka hint
      ctx.fillStyle = "#7a1d1d"; ctx.beginPath(); ctx.arc(14, -18, 2.6, 0, 7); ctx.fill(); // bindi
    } else {
      for (let i = 0; i < 13; i++) { const a = Math.PI * (1.05 + i * 0.075); shape(ctx, ellipsePts(Math.cos(a) * 34 - 2, Math.sin(a) * 40 - 6, 13, 13, 9), { fill: C.hair, w: 1.8, seed: 30 + i }); }
    }
    // face (3/4 to the right in local coords)
    const blink = clamp(P.blink || 0);
    for (const ex of [6, 24]) {
      if (blink > 0.5) line(ctx, [[ex - 5, -2], [ex + 5, -2]], { w: 2.2, j: 0.8 });
      else { ctx.fillStyle = C.pencil; ctx.beginPath(); ctx.ellipse(ex + (P.look || 0) * 2, -3, 3.4, 4.4 * (P.wide || 1), 0, 0, 7); ctx.fill(); }
      line(ctx, [[ex - 6, -13 - (P.brow || 0)], [ex + 6, -15 - (P.brow || 0)]], { w: 2, j: 0.8 });
    }
    line(ctx, [[33, -2], [40, 12], [32, 15]], { w: 2, j: 0.8 });
    if (P.smile === "o") shape(ctx, ellipsePts(22, 24, 4, 5, 8), { fill: "#5a2a2a", w: 1.6, j: 0.6 });
    else line(ctx, [[12, 22], [22, 26 + (P.smile === "big" ? 4 : 1)], [30, 21]], { w: 2.2, col: meera ? C.lips : C.pencil, j: 0.8 });
    if (meera && P.blush) { ctx.fillStyle = C.blush; ctx.beginPath(); ctx.arc(10, 10, 9, 0, 7); ctx.fill(); }
    ctx.restore();
    ctx.restore();
    return { hand };
  }

  // ---- props & set ------------------------------------------------------------------------
  function bicycle(ctx, x, y, s, spin = 0) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    for (const wx of [-95, 95]) {
      shape(ctx, ellipsePts(wx, -70, 70, 70, 22), { w: 3, seed: wx });
      for (let k = 0; k < 8; k++) { const a = spin + k * Math.PI / 8; line(ctx, [[wx + Math.cos(a) * 66, -70 + Math.sin(a) * 66], [wx - Math.cos(a) * 66, -70 - Math.sin(a) * 66]], { w: 1, col: C.soft, j: 0.5 }); }
    }
    line(ctx, [[-95, -70], [-20, -70], [50, -170], [-40, -170], [-95, -70]], { w: 4, col: C.bike });
    line(ctx, [[-20, -70], [-45, -190]], { w: 4, col: C.bike }); line(ctx, [[50, -170], [95, -70]], { w: 4, col: C.bike });
    line(ctx, [[50, -170], [60, -215], [30, -225]], { w: 4, col: C.bike }); line(ctx, [[60, -215], [90, -222]], { w: 4, col: C.bike });
    shape(ctx, [[-70, -196], [-22, -196], [-28, -186], [-66, -186]], { fill: "#5a3e2c", w: 2 });
    ctx.restore();
  }

  function rainStreet(ctx, t, o = {}) {
    // sky + buildings receding to a vanishing point
    ctx.fillStyle = C.sky; ctx.globalAlpha = 0.7; ctx.fillRect(0, 0, 1080, 1100); ctx.globalAlpha = 1;
    const VP = [400, 1060];
    shape(ctx, [[-20, 260], [VP[0] - 40, 900], [VP[0] - 40, VP[1]], [-20, 1560]], { fill: C.wall, w: 2.8, seed: 201 });
    for (let k = 0; k < 4; k++) { // arched windows on the left facades
      const x = 40 + k * 80, top = 420 + k * 120, h = 180 - k * 30, w = 50 - k * 9;
      shape(ctx, [[x, top + h], [x, top + 20], [x + w / 2, top], [x + w, top + 20], [x + w, top + h]], { fill: C.wallDark, w: 2, seed: 210 + k });
      line(ctx, [[x + w / 2, top + 4], [x + w / 2, top + h]], { col: C.soft, w: 1.4 });
    }
    hatch(ctx, [[-20, 260], [VP[0] - 40, 900], [VP[0] - 40, VP[1]], [-20, 1560]], -20, 200, 400, 1600, 16, 1.2);
    shape(ctx, [[VP[0] - 40, 960], [VP[0] + 120, 930], [VP[0] + 120, VP[1]], [VP[0] - 40, VP[1]]], { fill: C.wallDark, w: 2, seed: 230 });
    // road + pavement
    shape(ctx, [[VP[0] - 40, VP[1]], [VP[0] + 120, VP[1]], [1100, 1500], [1100, 1940], [-20, 1940], [-20, 1560]], { fill: C.road, w: 2.4, seed: 240 });
    for (let k = 0; k < 6; k++) line(ctx, [[VP[0] + 30 - k * 4, VP[1] + 20 + k * 120], [VP[0] + 30 - k * 4, VP[1] + 70 + k * 140]], { col: "rgba(255,255,255,0.7)", w: 4 + k * 1.5 });
    // puddles with ripples
    for (const [px, py, rx] of [[260, 1640, 120], [130, 1820, 150], [600, 1760, 110]]) {
      shape(ctx, ellipsePts(px, py, rx, rx * 0.22, 16), { fill: C.puddle, w: 1.8, seed: px });
      for (let r = 0; r < 3; r++) { const ph = (t * 1.2 + hash(px + r)) % 1; ctx.globalAlpha = 1 - ph;
        shape(ctx, ellipsePts(px + (hash(px + r * 3) - 0.5) * rx, py, ph * 40, ph * 9, 12), { w: 1.4, j: 0.6, seed: px + r }); ctx.globalAlpha = 1; }
    }
    teaStall(ctx, t, o);
  }

  function teaStall(ctx, t, o) {
    // back wall + counter
    shape(ctx, [[520, 760], [1100, 700], [1100, 1470], [520, 1470]], { fill: "#d8c7a6", w: 2.6, seed: 300 });
    shape(ctx, [[600, 1140], [1100, 1110], [1100, 1300], [600, 1310]], { fill: C.wood, w: 2.6, seed: 301 });
    for (let k = 1; k < 4; k++) line(ctx, [[600, 1140 + k * 42], [1100, 1110 + k * 46]], { col: C.soft, w: 1.4 });
    // jars + kettle + glasses on the counter
    for (let k = 0; k < 3; k++) shape(ctx, [[640 + k * 70, 1140], [640 + k * 70, 1060], [690 + k * 70, 1060], [690 + k * 70, 1138]], { fill: "rgba(255,255,255,0.5)", w: 2, seed: 310 + k });
    shape(ctx, [[900, 1120], [905, 1050], [985, 1050], [990, 1118]], { fill: "#9a9a96", w: 2.4, seed: 320 });
    line(ctx, [[900, 1070], [868, 1050], [860, 1030]], { w: 3 });
    for (let i = 0; i < 3; i++) { // steam
      const pts = []; for (let j = 0; j < 7; j++) pts.push([940 + i * 14 + Math.sin(t * 4 + j * 0.8 + i) * 9, 1040 - j * 22]);
      ctx.globalAlpha = 0.55; line(ctx, pts, { col: C.soft, w: 2, j: 1 }); ctx.globalAlpha = 1;
    }
    for (let k = 0; k < 2; k++) { shape(ctx, [[1010 + k * 40, 1112], [1006 + k * 40, 1060], [1034 + k * 40, 1060], [1030 + k * 40, 1112]], { fill: C.chai, w: 2, seed: 330 + k }); }
    // posts + tin awning
    line(ctx, [[530, 820], [530, 1480]], { w: 6 }); line(ctx, [[1070, 760], [1070, 1480]], { w: 6 });
    const aw = [[470, 830], [1100, 770], [1100, 690], [560, 740]];
    shape(ctx, aw, { fill: C.awning, w: 3, seed: 340 });
    for (let k = 1; k < 9; k++) line(ctx, [[lerp(470, 1100, k / 9), lerp(830, 770, k / 9)], [lerp(560, 1100, k / 9), lerp(740, 690, k / 9)]], { col: "rgba(60,30,20,0.5)", w: 1.6 });
    // drips off the awning edge
    for (let k = 0; k < 9; k++) {
      const x = 490 + k * 68, y0 = lerp(830, 770, (x - 470) / 630), p = (t * 1.6 + hash(k)) % 1;
      shape(ctx, ellipsePts(x, y0 + p * 620, 3, 7, 8), { fill: C.puddle, w: 1.2, j: 0.5, seed: 350 + k });
    }
  }

  function rain(ctx, t, avoid) {
    ctx.strokeStyle = C.rain; ctx.lineWidth = 2.2; ctx.lineCap = "round";
    for (let i = 0; i < 170; i++) {
      const x0 = hash(i) * 1200 - 60, sp = 1700 + hash(i + 3) * 700;
      const y = ((hash(i + 7) * 2100 + t * sp) % 2100) - 100, x = x0 - y * 0.12;
      if (avoid && avoid(x, y)) continue;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - 7, y + 46); ctx.stroke();
    }
  }

  // ---- close-ups -----------------------------------------------------------------------
  // o: {who, blink, smile, brow, look, wide, t, drip, blush}
  function faceClose(ctx, cx, cy, u, o) {
    const meera = o.who === "meera", skin = meera ? C.skinM : C.skinA, t = o.t || 0;
    ctx.save(); ctx.translate(cx, cy);
    // shoulders + clothing
    shape(ctx, [[-1.6 * u, 2.6 * u], [-1.3 * u, 1.55 * u], [-0.35 * u, 1.25 * u], [0.35 * u, 1.25 * u], [1.3 * u, 1.55 * u], [1.6 * u, 2.6 * u]], { fill: meera ? C.saree : C.shirt, w: 3, seed: 400 });
    if (meera) line(ctx, [[-1.1 * u, 1.6 * u], [0.6 * u, 2.6 * u]], { col: C.gold, w: 6 });
    else { line(ctx, [[-0.35 * u, 1.25 * u], [0, 1.75 * u], [0.35 * u, 1.25 * u]], { w: 3 }); }
    ctx.fillStyle = skin; ctx.fillRect(-0.3 * u, 0.7 * u, 0.6 * u, 0.62 * u);
    line(ctx, [[-0.3 * u, 0.75 * u], [-0.32 * u, 1.3 * u]], { w: 2.6 }); line(ctx, [[0.3 * u, 0.75 * u], [0.32 * u, 1.3 * u]], { w: 2.6 });
    // hair behind
    if (meera) {
      shape(ctx, [[-0.95 * u, 0.6 * u], [-0.95 * u, -0.6 * u], [-0.5 * u, -1.1 * u], [0.5 * u, -1.1 * u], [0.95 * u, -0.6 * u], [0.92 * u, 0.4 * u]], { fill: C.hair, w: 3, seed: 410, smooth: true });
      for (let i = 0; i < 8; i++) shape(ctx, ellipsePts(-0.88 * u - (i % 2) * 0.1 * u, -0.45 * u + i * 0.11 * u, 0.08 * u, 0.08 * u, 8), { fill: C.jasmine, w: 1.8, seed: 420 + i });
    }
    // head + ears
    for (const sx of [-1, 1]) shape(ctx, ellipsePts(sx * 0.8 * u, 0.05 * u, 0.13 * u, 0.2 * u, 12), { fill: skin, w: 2.6, seed: 430 + sx });
    const head = ellipsePts(0, 0, 0.8 * u, 1.0 * u, 26);
    shape(ctx, head, { fill: skin, w: 3, seed: 440 });
    hatch(ctx, head, -0.9 * u, -u, -0.45 * u, u, 12, 1.1);
    // jhumka swinging from the ear
    if (meera) for (const sx of [-1, 1]) {
      const sw = Math.sin(t * 3.2 + (sx > 0 ? 1 : 0)) * 0.25, ex = sx * 0.82 * u, ey = 0.25 * u;
      ctx.save(); ctx.translate(ex, ey); ctx.rotate(sw);
      line(ctx, [[0, 0], [0, 0.12 * u]], { col: C.gold, w: 3 });
      shape(ctx, [[-0.09 * u, 0.22 * u], [0, 0.1 * u], [0.09 * u, 0.22 * u]], { fill: C.gold, w: 2, seed: 450 + sx });
      ctx.restore();
    }
    // hair in front
    if (meera) shape(ctx, [[-0.82 * u, 0.1 * u], [-0.8 * u, -0.55 * u], [-0.35 * u, -0.98 * u], [0.02 * u, -0.92 * u], [0.45 * u, -0.98 * u], [0.82 * u, -0.5 * u], [0.8 * u, 0.0 * u], [0.6 * u, -0.48 * u], [0.04 * u, -0.72 * u], [-0.56 * u, -0.5 * u]], { fill: C.hair, w: 2.6, seed: 460 });
    else for (let i = 0; i < 22; i++) {
      const a = Math.PI * (1.0 + i * 0.048), bounce = Math.sin(t * 5 + i) * 0.02 * u;
      shape(ctx, ellipsePts(Math.cos(a) * 0.82 * u, Math.sin(a) * 0.92 * u - 0.12 * u + bounce, 0.17 * u, 0.17 * u, 10), { fill: C.hair, w: 2, seed: 470 + i });
    }
    // eyes
    const bl = clamp(o.blink || 0), lk = (o.look || 0) * 0.05 * u, wide = o.wide || 1;
    for (const sx of [-1, 1]) {
      const ex = sx * 0.33 * u, ey = -0.05 * u;
      if (bl > 0.5) { line(ctx, [[ex - 0.15 * u, ey], [ex, ey + 0.04 * u], [ex + 0.15 * u, ey]], { w: 3 }); }
      else {
        const eye = [[ex - 0.17 * u, ey], [ex, ey - 0.09 * u * wide], [ex + 0.17 * u, ey], [ex, ey + 0.07 * u * wide]];
        shape(ctx, eye, { fill: "#fbf8f0", w: 2.6, seed: 480 + sx });
        ctx.fillStyle = "#3b2618"; ctx.beginPath(); ctx.arc(ex + lk, ey - 0.005 * u, 0.065 * u * Math.min(wide, 1.1), 0, 7); ctx.fill();
        ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(ex + lk - 0.02 * u, ey - 0.025 * u, 0.018 * u, 0, 7); ctx.fill();
        if (meera) for (let k = 0; k < 3; k++) line(ctx, [[ex + sx * (0.1 + k * 0.03) * u, ey - 0.06 * u], [ex + sx * (0.14 + k * 0.04) * u, ey - 0.12 * u]], { w: 2, j: 0.6 });
      }
      const br = (o.brow || 0) * 0.06 * u;
      line(ctx, [[ex - sx * 0.14 * u, -0.25 * u - br], [ex, -0.3 * u - br * 1.2], [ex + sx * 0.17 * u, -0.26 * u - br * 0.6]], { w: meera ? 3 : 5 });
    }
    // nose, mouth, details
    line(ctx, [[0.02 * u, -0.05 * u], [0.07 * u, 0.25 * u], [-0.04 * u, 0.29 * u]], { w: 2.4 });
    if (meera) {
      ctx.fillStyle = "#7a1d1d"; ctx.beginPath(); ctx.arc(0, -0.22 * u, 0.03 * u, 0, 7); ctx.fill();
      if (o.blush) { ctx.fillStyle = C.blush; for (const sx of [-1, 1]) { ctx.beginPath(); ctx.ellipse(sx * 0.42 * u, 0.25 * u, 0.15 * u, 0.09 * u, 0, 0, 7); ctx.fill(); } }
      shape(ctx, [[-0.2 * u, 0.5 * u], [0, 0.47 * u], [0.22 * u, 0.48 * u], [0.05 * u, 0.6 * u]], { fill: C.lips, w: 2.2, seed: 490 });
    } else {
      if (o.smile === "o") shape(ctx, ellipsePts(0.02 * u, 0.53 * u, 0.07 * u, 0.09 * u, 12), { fill: "#5a2a2a", w: 2.4, seed: 491 });
      else line(ctx, [[-0.18 * u, 0.52 * u], [0.02 * u, 0.55 * u], [0.2 * u, 0.5 * u]], { w: 3 });
      ctx.fillStyle = C.soft; for (let i = 0; i < 70; i++) { const a = 0.35 + hash(i) * 2.4, r = 0.72 + hash(i + 9) * 0.2; ctx.fillRect(Math.cos(a) * r * 0.8 * u, Math.sin(a) * r * u * 0.95, 2, 2); }
    }
    // water drops falling from his curls
    if (o.drip) for (let i = 0; i < 4; i++) {
      const p = (t * 0.9 + i / 4) % 1, x = (-0.6 + i * 0.4) * u, y = -0.6 * u + p * 1.4 * u;
      ctx.globalAlpha = 1 - p; shape(ctx, [[x, y - 0.06 * u], [x + 0.03 * u, y + 0.02 * u], [x, y + 0.04 * u], [x - 0.03 * u, y + 0.02 * u]], { fill: C.puddle, w: 1.6, seed: 500 + i }); ctx.globalAlpha = 1;
    }
    ctx.restore();
  }

  function label(ctx, text, a = 1) {
    ctx.save(); ctx.globalAlpha = a;
    ctx.font = '700 30px Inter, Arial, sans-serif'; ctx.fillStyle = "rgba(58,51,45,0.75)"; ctx.textAlign = "left";
    ctx.fillText(text, 80, 300);
    ctx.font = '600 22px Inter, Arial, sans-serif'; ctx.fillStyle = "rgba(58,51,45,0.5)"; ctx.fillText("BLUE SAREE · STORYBOARD SKETCH", 80, 262);
    ctx.restore();
  }

  window.Sketch = { C, clamp, lerp, seg, ease, easeOut, hash, setBoil: (b) => (BOIL = b), shape, line, ellipsePts, hatch,
    paper, figure, bicycle, rainStreet, rain, faceClose, label };
})();
