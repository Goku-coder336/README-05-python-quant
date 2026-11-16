/* Shared cast for "movie logic" meme skits: muted teal film set, rubbery line-drawn guys,
 * props (bomb, wire cutters, megaphone), explosion, captions, camera.
 * Every function draws from its arguments only, so a frame is a pure function of time.
 */
(function () {
  const PAL = {
    bg: "#6e968b", bgDark: "#5e8479", set: "#6b5545", setDark: "#4e3d32", window: "#3d4f52", truss: "rgba(25,30,30,0.55)",
    skin: "#83998f", skinShade: "#6d8379", soot: "#3c403e", line: "#141414", white: "#f4f4ee", mouth: "#2a0f12",
    tongue: "#b9474f", red: "#a3262a", redLight: "#c94a3f", cap: "#2c3e50", wireRed: "#c0392b", wireBlue: "#2e6fb7",
    led: "#ff3b30", metal: "#c9cfd1", sweat: "#cfe9ff",
  };
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const easeOut = (k) => 1 - Math.pow(1 - k, 3);
  const easeBack = (k) => { const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
  const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  function ink(ctx, w = 6) { ctx.lineWidth = w; ctx.strokeStyle = PAL.line; ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.stroke(); }
  function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }

  // ---------- camera ----------
  function applyCamera(ctx, cam) {
    ctx.translate(540 + (cam.shakeX || 0), 960 + (cam.shakeY || 0));
    ctx.scale(cam.z, cam.z);
    ctx.translate(-cam.cx, -cam.cy);
  }

  // ---------- set: flat teal + blurred studio shapes ----------
  function drawSet(ctx, t) {
    ctx.fillStyle = PAL.bg; ctx.fillRect(-1500, -1000, 4500, 4500);
    ctx.save();
    ctx.filter = "blur(12px)";
    // wooden flat (a fake house front) on the left
    ctx.fillStyle = PAL.set; ctx.beginPath(); ctx.moveTo(-200, 1520); ctx.lineTo(-200, 720); ctx.lineTo(120, 560); ctx.lineTo(330, 700); ctx.lineTo(330, 1520); ctx.fill();
    ctx.fillStyle = PAL.setDark; ctx.fillRect(330, 700, 40, 820);
    ctx.fillStyle = PAL.window; ctx.fillRect(60, 820, 150, 130); ctx.fillRect(-120, 1050, 120, 160);
    ctx.fillStyle = "rgba(255,255,255,0.15)"; ctx.fillRect(130, 820, 8, 130); ctx.fillRect(60, 880, 150, 8);
    // light stand + softbox on the right
    ctx.fillStyle = "#2a3330"; ctx.fillRect(1180, 820, 14, 700);
    ctx.fillStyle = "#e9efe6"; ctx.beginPath(); ctx.moveTo(1100, 700); ctx.lineTo(1290, 700); ctx.lineTo(1260, 860); ctx.lineTo(1130, 860); ctx.fill();
    // crates
    ctx.fillStyle = "#7a6650"; ctx.fillRect(-60, 1360, 200, 150); ctx.fillRect(1240, 1300, 180, 210);
    ctx.restore();
    // sketchy truss lines like a hand-drawn background
    ctx.save(); ctx.strokeStyle = PAL.truss; ctx.lineWidth = 3; ctx.filter = "blur(1.5px)";
    for (let k = 0; k < 3; k++) {
      ctx.beginPath(); ctx.moveTo(250, 760 + k * 60);
      ctx.bezierCurveTo(500, 600 + k * 50, 750, 820 - k * 40, 1300, 640 + k * 70); ctx.stroke();
    }
    ctx.restore();
  }

  function shadow(ctx, x, y, w) {
    ctx.save(); ctx.fillStyle = "rgba(20,40,35,0.22)"; ctx.beginPath(); ctx.ellipse(x, y, w, w * 0.16, 0, 0, 7); ctx.fill(); ctx.restore();
  }

  // ---------- the guy ----------
  // g: {x, floor, s, facing ±1, crouch 0..1, lean, front:[x,y], back:[x,y] (hand targets, local, facing right),
  //     mouth 0..1, lids 0..1, brows, lookX, lookY, headDy, headTilt, hair: "tuft"|"cap"|"afro", soot 0..1, smile}
  function drawGuy(ctx, g) {
    const c = clamp(g.crouch || 0), skin = g.soot > 0.5 ? PAL.soot : PAL.skin;
    ctx.save(); ctx.translate(g.x, g.floor); ctx.scale((g.s || 1) * (g.facing || 1), g.s || 1);
    const hip = [-10 * c, -330 + 120 * c];
    const neck = [hip[0] + 35 * c + 30 * (g.lean || 0), hip[1] - 290 + 30 * c];
    const at = (k) => [lerp(neck[0], hip[0], k), lerp(neck[1], hip[1], k)];
    const sh = at(0.12);
    // feet
    for (const [fx, rot] of [[-75, -0.15], [80, 0.1]]) {
      ctx.beginPath(); ctx.ellipse(fx, -14, 52, 18, rot, 0, 7); ctx.fillStyle = skin; ctx.fill(); ink(ctx, 5);
    }
    // legs
    ctx.beginPath(); ctx.moveTo(hip[0] - 22, hip[1]); ctx.quadraticCurveTo(-40 + 10 * c, hip[1] / 2 + 20 * c, -70, -26); ink(ctx, 8);
    ctx.beginPath(); ctx.moveTo(hip[0] + 22, hip[1]); ctx.quadraticCurveTo(70 + 110 * c, hip[1] / 2 - 40 * c, 75, -26); ink(ctx, 8);
    // arm helper
    const arm = (to, bend) => {
      ctx.beginPath(); ctx.moveTo(sh[0], sh[1] + 10);
      const mx = (sh[0] + to[0]) / 2, my = (sh[1] + to[1]) / 2;
      ctx.quadraticCurveTo(mx - 30 * bend, my + 50 * bend, to[0], to[1]); ink(ctx, 8);
      ctx.beginPath(); ctx.ellipse(to[0], to[1], 15, 12, 0.4, 0, 7); ctx.fillStyle = PAL.line; ctx.fill();
      ctx.beginPath(); ctx.moveTo(to[0] + 4, to[1] - 6); ctx.lineTo(to[0] + 18, to[1] - 18); ink(ctx, 7);
    };
    arm(g.back || [-40, hip[1] + 10], 1);
    // torso (bean)
    const ang = Math.atan2(neck[0] - hip[0], -(neck[1] - hip[1]));
    ctx.save(); ctx.translate((hip[0] + neck[0]) / 2, (hip[1] + neck[1]) / 2 + 10); ctx.rotate(ang);
    ctx.beginPath(); ctx.moveTo(0, -150);
    ctx.bezierCurveTo(60, -150, 75, -40, 70, 40); ctx.bezierCurveTo(68, 140, 30, 175, -5, 175);
    ctx.bezierCurveTo(-50, 175, -78, 130, -70, 40); ctx.bezierCurveTo(-64, -40, -60, -150, 0, -150);
    ctx.fillStyle = skin; ctx.fill(); ink(ctx, 6);
    ctx.beginPath(); ctx.moveTo(-20, 60); ctx.quadraticCurveTo(-30, 110, -10, 140); ctx.lineWidth = 3; ctx.strokeStyle = "rgba(0,0,0,0.35)"; ctx.stroke();
    ctx.restore();
    // head
    const hx = neck[0] + 30, hy = neck[1] - 95 + (g.headDy || 0);
    ctx.beginPath(); ctx.moveTo(neck[0], neck[1] + 10); ctx.lineTo(hx - 5, hy + 60); ink(ctx, 9);
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(g.headTilt || 0);
    if (g.hair === "afro") {
      for (let k = 0; k < 16; k++) { const a = Math.PI * (0.75 + k * 0.1); ctx.beginPath(); ctx.arc(Math.cos(a) * 95 - 10, Math.sin(a) * 100 - 25, 46, 0, 7); ctx.fillStyle = "#1b1b1b"; ctx.fill(); }
    }
    ctx.beginPath(); ctx.ellipse(0, 0, 78, 94, 0, 0, 7); ctx.fillStyle = skin; ctx.fill(); ink(ctx, 6);
    // ear
    ctx.beginPath(); ctx.ellipse(-62, 8, 16, 24, 0, 0, 7); ctx.fillStyle = skin; ctx.fill(); ink(ctx, 5);
    // eyes
    const lx = clamp(g.lookX ?? 1, -1, 1), ly = g.lookY || 0, lids = clamp(g.lids || 0);
    for (const [ex, ey] of [[8, -22], [50, -26]]) {
      ctx.save(); ctx.beginPath(); ctx.ellipse(ex, ey, 18, 22, 0, 0, 7); ctx.fillStyle = PAL.white; ctx.fill(); ink(ctx, 4); ctx.clip();
      ctx.beginPath(); ctx.arc(ex + lx * 6, ey + 2 + ly * 6, 6.5, 0, 7); ctx.fillStyle = PAL.line; ctx.fill();
      if (lids > 0) { ctx.fillStyle = skin; ctx.fillRect(ex - 20, ey - 24, 40, 44 * lids); ctx.beginPath(); ctx.moveTo(ex - 20, ey - 22 + 44 * lids); ctx.lineTo(ex + 20, ey - 22 + 44 * lids); ink(ctx, 4); }
      ctx.restore();
    }
    // brows [inner lift, outer lift] per eye, positive = up
    const B = { flat: [0, 0], angry: [-12, 8], worried: [12, -6], shock: [16, 16], skeptic: [0, 0], deadpan: [-3, -3] }[g.brows || "flat"];
    for (const [ex, side] of [[8, -1], [50, 1]]) {
      let inner = B[0], outer = B[1];
      if (g.brows === "skeptic") { inner = side > 0 ? 18 : -6; outer = side > 0 ? 22 : -2; }
      const xi = ex - side * 14, xo = ex + side * 16;
      ctx.beginPath(); ctx.moveTo(xo, -58 - outer); ctx.lineTo(xi, -58 - inner); ink(ctx, 7);
    }
    // nose
    ctx.beginPath(); ctx.ellipse(70, 10, 32, 22, 0.25, 0, 7); ctx.fillStyle = skin; ctx.fill(); ink(ctx, 5);
    // mouth
    const m = clamp(g.mouth || 0), mx = 30, my = 50;
    if (m < 0.08) {
      ctx.beginPath();
      if (g.smile === "frown") { ctx.moveTo(mx - 24, my + 6); ctx.quadraticCurveTo(mx, my - 8, mx + 24, my + 6); }
      else if (g.smile === "smirk") { ctx.moveTo(mx - 22, my + 2); ctx.quadraticCurveTo(mx + 6, my + 6, mx + 26, my - 8); }
      else if (g.smile === "o") { ctx.ellipse(mx, my, 9, 12, 0, 0, 7); }
      else { ctx.moveTo(mx - 22, my); ctx.lineTo(mx + 22, my); }
      ink(ctx, 5);
    } else {
      ctx.save(); ctx.beginPath(); ctx.ellipse(mx, my + 6 * m, 24 + 8 * m, 6 + 24 * m, 0.05, 0, 7);
      ctx.fillStyle = PAL.mouth; ctx.fill(); ctx.clip();
      ctx.fillStyle = PAL.white; ctx.fillRect(mx - 40, my - 30 + 6 * m, 80, 30 - 14 * m + 8);
      ctx.beginPath(); ctx.ellipse(mx + 4, my + 30 * m + 8, 20, 10, 0, 0, 7); ctx.fillStyle = PAL.tongue; ctx.fill();
      ctx.restore();
      ctx.beginPath(); ctx.ellipse(mx, my + 6 * m, 24 + 8 * m, 6 + 24 * m, 0.05, 0, 7); ink(ctx, 5);
    }
    // hair / hat
    if (g.hair === "tuft") {
      for (let k = 0; k < 5; k++) { ctx.beginPath(); ctx.moveTo(-30 + k * 16, -86); ctx.quadraticCurveTo(-36 + k * 18, -120, -20 + k * 20, -128 + (k % 2) * 10); ink(ctx, 5); }
    } else if (g.hair === "cap") {
      ctx.beginPath(); ctx.moveTo(-78, -30); ctx.bezierCurveTo(-80, -120, 70, -130, 76, -40); ctx.closePath();
      ctx.fillStyle = PAL.cap; ctx.fill(); ink(ctx, 5);
      ctx.beginPath(); ctx.ellipse(-92, -36, 42, 12, -0.15, 0, 7); ctx.fillStyle = PAL.cap; ctx.fill(); ink(ctx, 5);
    } else if (g.hair === "afro") {
      ctx.save(); ctx.strokeStyle = "#555"; ctx.lineWidth = 3;
      for (let k = 0; k < 10; k++) { ctx.beginPath(); ctx.arc(-60 + hash(k) * 120, -110 + hash(k + 3) * 40, 10, 0, 5); ctx.stroke(); }
      ctx.restore();
    }
    ctx.restore();
    // front arm last, so it overlaps the body
    arm(g.front || [40, hip[1] + 10], g.frontBend ?? 1);
    ctx.restore();
    // hand position in world coords (for props)
    const f = (g.facing || 1) * (g.s || 1), s = g.s || 1;
    const fr = g.front || [40, hip[1] + 10];
    return { hand: [g.x + fr[0] * f, g.floor + fr[1] * s], head: [g.x + hx * f, g.floor + hy * s], mouth: [g.x + (hx + mx) * f, g.floor + (hy + my) * s] };
  }

  // ---------- props ----------
  function drawBomb(ctx, x, y, o) {
    ctx.save(); ctx.translate(x, y);
    for (let k = 0; k < 3; k++) {
      rr(ctx, -120, -40 - k * 40, 240, 40, 16); ctx.fillStyle = k % 2 ? PAL.red : PAL.redLight; ctx.fill(); ink(ctx, 5);
    }
    for (const bx of [-70, 60]) { ctx.fillStyle = "#222"; ctx.fillRect(bx, -122, 22, 124); }
    // timer box
    rr(ctx, -90, -215, 180, 90, 14); ctx.fillStyle = "#151515"; ctx.fill(); ink(ctx, 5);
    rr(ctx, -74, -202, 148, 64, 8); ctx.fillStyle = "#2a0606"; ctx.fill();
    if (o.lit !== false) {
      ctx.font = '900 54px "JetBrains Mono", "DejaVu Sans Mono", monospace'; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.shadowColor = PAL.led; ctx.shadowBlur = 18; ctx.fillStyle = PAL.led; ctx.fillText(o.digits, 0, -168); ctx.shadowBlur = 0;
    }
    // wires: red (left) and blue (right); red can be cut
    ctx.lineWidth = 9; ctx.lineCap = "round";
    ctx.strokeStyle = PAL.wireBlue; ctx.beginPath(); ctx.moveTo(70, -130); ctx.bezierCurveTo(170, -150, 170, -60, 115, -60); ctx.stroke();
    ctx.strokeStyle = PAL.wireRed;
    if (!o.cut) { ctx.beginPath(); ctx.moveTo(-70, -130); ctx.bezierCurveTo(-170, -150, -170, -60, -115, -60); ctx.stroke(); }
    else {
      ctx.beginPath(); ctx.moveTo(-70, -130); ctx.bezierCurveTo(-120, -142, -140, -128, -148, -112); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-115, -60); ctx.bezierCurveTo(-150, -62, -158, -72, -156, -88); ctx.stroke();
    }
    ctx.restore();
  }

  function drawCutters(ctx, x, y, ang, open) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    for (const s of [-1, 1]) {
      ctx.save(); ctx.rotate(s * (0.08 + 0.25 * open));
      rr(ctx, -70, -9, 70, 18, 9); ctx.fillStyle = PAL.red; ctx.fill(); ink(ctx, 4);
      ctx.beginPath(); ctx.moveTo(0, -6); ctx.lineTo(55, s * -2); ctx.lineTo(0, 6); ctx.closePath(); ctx.fillStyle = PAL.metal; ctx.fill(); ink(ctx, 4);
      ctx.restore();
    }
    ctx.beginPath(); ctx.arc(0, 0, 6, 0, 7); ctx.fillStyle = "#333"; ctx.fill();
    ctx.restore();
  }

  function drawMegaphone(ctx, x, y, ang) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
    ctx.beginPath(); ctx.moveTo(-10, -18); ctx.lineTo(120, -52); ctx.lineTo(120, 52); ctx.lineTo(-10, 18); ctx.closePath();
    ctx.fillStyle = PAL.red; ctx.fill(); ink(ctx, 5);
    ctx.beginPath(); ctx.ellipse(120, 0, 14, 52, 0, 0, 7); ctx.fillStyle = "#6e1416"; ctx.fill(); ink(ctx, 5);
    rr(ctx, 20, 14, 18, 40, 6); ctx.fillStyle = "#2b2b2b"; ctx.fill(); ink(ctx, 4);
    ctx.restore();
  }

  // dt = seconds since the blast
  function drawExplosion(ctx, x, y, dt) {
    if (dt < 0 || dt > 1.8) return;
    ctx.save(); ctx.translate(x, y);
    const k = easeOut(clamp(dt / 0.35));
    if (dt < 0.6) {
      ctx.globalAlpha = 1 - seg(dt, 0.35, 0.6);
      for (const [r, col] of [[430, "#ff8a1f"], [300, "#ffd23f"], [150, "#fff6c9"]]) {
        ctx.beginPath();
        for (let i = 0; i <= 24; i++) { const a = (i / 24) * Math.PI * 2, rr2 = r * k * (i % 2 ? 0.62 : 1); ctx.lineTo(Math.cos(a) * rr2, Math.sin(a) * rr2 * 0.85 - 80 * k); }
        ctx.fillStyle = col; ctx.fill(); ink(ctx, 6);
      }
    }
    ctx.globalAlpha = 1 - seg(dt, 0.9, 1.8);
    for (let i = 0; i < 14; i++) {
      const a = hash(i) * Math.PI * 2, d = (120 + hash(i + 5) * 260) * easeOut(clamp(dt / 1.2));
      const r = (70 + hash(i + 9) * 70) * (0.6 + 0.6 * clamp(dt / 0.8));
      ctx.beginPath(); ctx.arc(Math.cos(a) * d, Math.sin(a) * d * 0.6 - 120 - dt * 90, r, 0, 7);
      ctx.fillStyle = i % 3 ? "#7d827f" : "#5f6461"; ctx.fill();
    }
    ctx.restore();
  }

  // ---------- captions (screen space) ----------
  function drawCaption(ctx, text, alpha, y = 1300, x = 510, maxW = 780) {
    if (!text || alpha <= 0) return;
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.font = '800 60px Inter, "Helvetica Neue", Arial, sans-serif'; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const words = text.split(" "), lines = []; let cur = "";
    for (const w of words) { const tl = cur ? cur + " " + w : w; if (ctx.measureText(tl).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tl; }
    lines.push(cur);
    lines.forEach((l, i) => {
      const yy = y + (i - (lines.length - 1) / 2) * 72;
      ctx.shadowColor = "rgba(0,0,0,0.45)"; ctx.shadowBlur = 14; ctx.shadowOffsetY = 3;
      ctx.fillStyle = "#ffffff"; ctx.fillText(l, x, yy);
    });
    ctx.restore();
  }

  window.MemeCast = { PAL, clamp, lerp, seg, easeOut, easeBack, hash, applyCamera, drawSet, shadow, drawGuy,
    drawBomb, drawCutters, drawMegaphone, drawExplosion, drawCaption };
})();
