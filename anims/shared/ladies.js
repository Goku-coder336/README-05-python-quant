/* Shared shapes for "Glasgow meets Seville".
 * Every function draws from its arguments only (no hidden state), so any frame can be
 * drawn on its own from the time t. Colours live in PAL so another style can repaint them.
 */
(function () {
  const PAL = {
    skinMorag: "#f7d3bd", cheekMorag: "rgba(230,90,90,0.45)", hairMorag: "#d4622a", hairMoragDark: "#a8461b",
    jumper: "#efe2c4", jumperLine: "#d6c49c", tartanRed: "#b81f2d", tartanGreen: "#1f5a3a", tartanBlue: "#1d3557",
    tartanYellow: "#f2c94c", welly: "#2f6b3a", tights: "#3a3346", bag: "#7a4a2b",
    skinCarmen: "#d8a47b", cheekCarmen: "rgba(214,80,80,0.35)", hairCarmen: "#1c1416", dress: "#d3122d",
    dressDark: "#9c0c20", dot: "#ffffff", comb: "#8a4b1f", combLight: "#b9763c", rose: "#e0102f", leaf: "#2f7d32",
    gold: "#e2b23a", fan: "#1b1b1b", fanRed: "#c8102e", heel: "#b5121b",
    ink: "#2a1d1f", mouth: "#5b1320", tongue: "#e86b7a", white: "#ffffff",
    skyRain: "#76808e", skyMid: "#a8b6c4", skySun: "#86cdf5", cloud: "#5f6873", cloudLight: "#7d8792",
    sun: "#ffd23f", sunRay: "rgba(255,210,63,0.55)", stone: "#b0603f", stoneDark: "#8d4630", window: "#40505f",
    windowLit: "#f4d79a", pavement: "#9a9ca1", slab: "#86888d", kerb: "#6f7176", road: "#4b4f55",
    puddle: "rgba(120,140,165,0.75)", rain: "rgba(215,228,245,0.75)", busRed: "#d4202b",
  };

  // ---------- helpers ----------
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const easeOut = (k) => 1 - Math.pow(1 - k, 3);
  const easeInOut = (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2);
  const easeBack = (k) => { const c = 1.9; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };
  const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };

  function rr(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function circle(ctx, x, y, r, fill, stroke, lw) {
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.lineWidth = lw || 4; ctx.strokeStyle = stroke; ctx.stroke(); }
  }
  function outline(ctx, lw = 5) { ctx.lineWidth = lw; ctx.strokeStyle = PAL.ink; ctx.lineJoin = "round"; ctx.stroke(); }

  // Tartan inside the current path: base colour, wide bands both ways, thin lines.
  function tartan(ctx, x, y, w, h, base, band, line, period = 70) {
    ctx.save(); ctx.clip();
    ctx.fillStyle = base; ctx.fillRect(x, y, w, h);
    ctx.globalAlpha = 0.55; ctx.fillStyle = band;
    for (let k = x - period; k < x + w + period; k += period) ctx.fillRect(k, y, period * 0.36, h);
    for (let k = y - period; k < y + h + period; k += period) ctx.fillRect(x, k, w, period * 0.36);
    ctx.globalAlpha = 0.9; ctx.fillStyle = line;
    for (let k = x - period; k < x + w + period; k += period) ctx.fillRect(k + period * 0.62, y, 3, h);
    for (let k = y - period; k < y + h + period; k += period) ctx.fillRect(x, k + period * 0.62, w, 3);
    ctx.restore();
  }
  function dots(ctx, x, y, w, h, color, step = 46, r = 8) {
    ctx.save(); ctx.clip(); ctx.fillStyle = color;
    let row = 0;
    for (let j = y; j < y + h + step; j += step * 0.7, row++)
      for (let i = x + (row % 2 ? step / 2 : 0); i < x + w + step; i += step) { ctx.beginPath(); ctx.arc(i, j, r, 0, 7); ctx.fill(); }
    ctx.restore();
  }
  function limb(ctx, pts, color, width) {
    ctx.lineCap = "round"; ctx.lineJoin = "round";
    ctx.beginPath(); ctx.moveTo(pts[0], pts[1]);
    for (let i = 2; i < pts.length; i += 2) ctx.lineTo(pts[i], pts[i + 1]);
    ctx.strokeStyle = PAL.ink; ctx.lineWidth = width + 10; ctx.stroke();
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke();
  }

  // ---------- face ----------
  // f: {skin, cheek, mouth 0..1, blink 0..1, lookX -1..1, brow, lip, lashes, smile}
  function face(ctx, cx, cy, r, f) {
    const eyeY = cy - r * 0.04, ex = r * 0.36;
    // cheeks
    circle(ctx, cx - r * 0.55, cy + r * 0.25, r * 0.17, f.cheek);
    circle(ctx, cx + r * 0.55, cy + r * 0.25, r * 0.17, f.cheek);
    // eyes
    const open = 1 - clamp(f.blink || 0);
    const wide = f.brow === "shock" ? 1.25 : 1;
    for (const s of [-1, 1]) {
      const x = cx + s * ex;
      ctx.save();
      ctx.beginPath(); ctx.ellipse(x, eyeY, r * 0.19 * wide, Math.max(1.5, r * 0.23 * open * wide), 0, 0, 7);
      ctx.fillStyle = PAL.white; ctx.fill(); outline(ctx, 4);
      if (open > 0.15) {
        ctx.clip();
        circle(ctx, x + (f.lookX || 0) * r * 0.08, eyeY + r * 0.02, r * 0.11, PAL.ink);
        circle(ctx, x + (f.lookX || 0) * r * 0.08 - r * 0.035, eyeY - r * 0.03, r * 0.035, PAL.white);
      }
      ctx.restore();
      if (f.lashes) {
        ctx.strokeStyle = PAL.ink; ctx.lineWidth = 4; ctx.lineCap = "round";
        for (let k = 0; k < 3; k++) {
          const a = -Math.PI / 2 + s * (0.5 + k * 0.32);
          const bx = x + Math.cos(a) * r * 0.19, by = eyeY + Math.sin(a) * r * 0.23 * open;
          ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx + Math.cos(a) * 14, by + Math.sin(a) * 14); ctx.stroke();
        }
      }
    }
    // brows
    ctx.strokeStyle = f.browColor || PAL.ink; ctx.lineWidth = 9; ctx.lineCap = "round";
    const by = cy - r * 0.38;
    const brows = {
      neutral: [[-0.1, 0], [0.1, 0]],
      happy: [[-0.22, -0.05], [0.22, -0.05]],
      confused: [[-0.35, -0.22], [0.25, 0.1]],
      cold: [[0.25, -0.05], [-0.25, -0.05]],
      shock: [[-0.1, -0.3], [0.1, -0.3]],
      polite: [[0.15, -0.12], [-0.15, -0.12]],
    }[f.brow || "neutral"];
    for (const [i, s] of [[0, -1], [1, 1]]) {
      const [tilt, lift] = brows[i];
      const x = cx + s * ex;
      ctx.save(); ctx.translate(x, by + lift * r); ctx.rotate(tilt * s * -1);
      ctx.beginPath(); ctx.moveTo(-r * 0.17, 4); ctx.quadraticCurveTo(0, -8, r * 0.17, 4); ctx.stroke();
      ctx.restore();
    }
    // nose
    ctx.lineWidth = 4; ctx.strokeStyle = "rgba(60,30,30,0.55)";
    ctx.beginPath(); ctx.moveTo(cx + (f.lookX || 0) * 6 - 6, cy + r * 0.12); ctx.quadraticCurveTo(cx + (f.lookX || 0) * 6 + 8, cy + r * 0.2, cx + (f.lookX || 0) * 6 - 2, cy + r * 0.24); ctx.stroke();
    // mouth
    const my = cy + r * 0.48, m = clamp(f.mouth || 0);
    if (m < 0.06) {
      ctx.lineWidth = 7; ctx.strokeStyle = f.lip || PAL.mouth; ctx.lineCap = "round";
      ctx.beginPath();
      if (f.smile === "wavy") {
        ctx.moveTo(cx - r * 0.2, my);
        for (let k = 1; k <= 4; k++) ctx.lineTo(cx - r * 0.2 + k * r * 0.1, my + (k % 2 ? -6 : 6));
      } else if (f.smile === "o") {
        ctx.arc(cx, my, r * 0.08, 0, 7);
      } else {
        const curve = f.smile === "flat" ? 4 : 20;
        ctx.moveTo(cx - r * 0.22, my - 4); ctx.quadraticCurveTo(cx, my + curve, cx + r * 0.22, my - 4);
      }
      ctx.stroke();
    } else {
      const w = r * (0.2 + 0.1 * m), h = r * (0.06 + 0.3 * m);
      ctx.beginPath(); ctx.ellipse(cx, my + h * 0.3, w, h, 0, 0, 7);
      ctx.fillStyle = PAL.mouth; ctx.fill();
      ctx.save(); ctx.clip(); circle(ctx, cx, my + h * 1.05, w * 0.75, PAL.tongue); ctx.restore();
      ctx.lineWidth = 6; ctx.strokeStyle = f.lip || PAL.ink; ctx.stroke();
    }
  }

  // ---------- Morag: Glaswegian, ginger curls, tartan tam with a pompom ----------
  // p: {mouth, blink, lookX, brow, smile, armUp 0..1, cup 0..1, headDy, tilt, t}
  function drawMorag(ctx, x, y, s, p) {
    const t = p.t || 0;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(p.tilt || 0);
    // wellies + tights
    for (const sx of [-1, 1]) {
      rr(ctx, sx * 48 - 26, -170, 52, 80, 10); ctx.fillStyle = PAL.tights; ctx.fill();
      rr(ctx, sx * 48 - 32, -112, 64, 112, 14); ctx.fillStyle = PAL.welly; ctx.fill(); outline(ctx);
      rr(ctx, sx * 48 - 36, -16, 72, 16, 6); ctx.fillStyle = "#1d3f24"; ctx.fill();
    }
    // handbag arm (her right = screen left)
    limb(ctx, [-112, -520, -150, -430, -138, -350], PAL.jumper, 44);
    ctx.beginPath(); ctx.moveTo(-170, -330); ctx.quadraticCurveTo(-140, -400, -110, -330);
    ctx.lineWidth = 8; ctx.strokeStyle = PAL.ink; ctx.stroke();
    rr(ctx, -200, -335, 120, 90, 16); ctx.fillStyle = PAL.bag; ctx.fill(); outline(ctx);
    circle(ctx, -140, -300, 7, PAL.gold);
    circle(ctx, -138, -352, 22, PAL.skinMorag, PAL.ink, 5);
    // kilt skirt
    ctx.beginPath(); ctx.moveTo(-112, -345); ctx.lineTo(112, -345); ctx.lineTo(150, -150); ctx.lineTo(-150, -150); ctx.closePath();
    tartan(ctx, -160, -350, 320, 210, PAL.tartanRed, PAL.tartanGreen, PAL.tartanYellow, 64);
    ctx.beginPath(); ctx.moveTo(-112, -345); ctx.lineTo(112, -345); ctx.lineTo(150, -150); ctx.lineTo(-150, -150); ctx.closePath(); outline(ctx);
    ctx.strokeStyle = "rgba(0,0,0,0.25)"; ctx.lineWidth = 3;
    for (let k = -3; k <= 3; k++) { ctx.beginPath(); ctx.moveTo(k * 30, -330); ctx.lineTo(k * 42, -155); ctx.stroke(); }
    // jumper
    ctx.beginPath(); ctx.moveTo(-122, -540); ctx.quadraticCurveTo(-140, -420, -116, -335); ctx.lineTo(116, -335);
    ctx.quadraticCurveTo(140, -420, 122, -540); ctx.quadraticCurveTo(0, -585, -122, -540); ctx.closePath();
    ctx.fillStyle = PAL.jumper; ctx.fill(); outline(ctx);
    ctx.strokeStyle = PAL.jumperLine; ctx.lineWidth = 5;
    for (const cx of [-60, 0, 60]) { ctx.beginPath(); for (let k = 0; k < 6; k++) { ctx.moveTo(cx - 12, -500 + k * 28); ctx.lineTo(cx, -486 + k * 28); ctx.lineTo(cx + 12, -500 + k * 28); } ctx.stroke(); }
    // tartan shawl
    ctx.beginPath(); ctx.moveTo(-130, -548); ctx.quadraticCurveTo(0, -585, 130, -548); ctx.lineTo(70, -470); ctx.lineTo(0, -410); ctx.lineTo(-70, -470); ctx.closePath();
    tartan(ctx, -140, -590, 280, 190, PAL.tartanGreen, PAL.tartanBlue, PAL.tartanRed, 50);
    ctx.beginPath(); ctx.moveTo(-130, -548); ctx.quadraticCurveTo(0, -585, 130, -548); ctx.lineTo(70, -470); ctx.lineTo(0, -410); ctx.lineTo(-70, -470); ctx.closePath(); outline(ctx);
    circle(ctx, 0, -505, 14, PAL.gold, PAL.ink, 4);
    // gesturing arm (her left = screen right), optionally holding a cup of tea
    const up = clamp(p.armUp || 0), cup = clamp(p.cup || 0);
    const wig = Math.sin(t * 9) * 14 * up;
    const ex = lerp(150, 200, Math.max(up, cup)), ey = lerp(-430, -470, Math.max(up, cup));
    const hx = lerp(140, cup > 0 ? 190 : 215, Math.max(up, cup)) + wig * 0.4;
    const hy = lerp(-350, cup > 0 ? -490 : -600, Math.max(up, cup)) + wig;
    limb(ctx, [112, -520, ex, ey, hx, hy], PAL.jumper, 44);
    if (cup > 0.01) drawTeacup(ctx, hx + 30, hy - 8, cup, t);
    circle(ctx, hx, hy, 22, PAL.skinMorag, PAL.ink, 5);
    // head
    ctx.save(); ctx.translate(0, p.headDy || 0);
    rr(ctx, -26, -590, 52, 50, 10); ctx.fillStyle = PAL.skinMorag; ctx.fill();
    // back curls
    for (let k = 0; k < 15; k++) {
      const a = Math.PI * (0.92 + k * 0.083);
      circle(ctx, Math.cos(a) * 98, -665 + Math.sin(a) * 92, 32, k % 2 ? PAL.hairMorag : PAL.hairMoragDark, PAL.ink, 4);
    }
    for (const sx of [-1, 1]) for (let k = 0; k < 3; k++) circle(ctx, sx * (100 - k * 4), -640 + k * 40, 30, PAL.hairMorag, PAL.ink, 4);
    circle(ctx, 0, -660, 92, PAL.skinMorag, PAL.ink, 5);
    face(ctx, 0, -655, 92, { skin: PAL.skinMorag, cheek: PAL.cheekMorag, mouth: p.mouth, blink: p.blink, lookX: p.lookX, brow: p.brow, smile: p.smile, browColor: PAL.hairMoragDark });
    // fringe curls
    for (let k = 0; k < 6; k++) circle(ctx, -70 + k * 28, -735 + Math.abs(k - 2.5) * 5, 24, PAL.hairMorag, PAL.ink, 4);
    // tam o' shanter
    ctx.save(); ctx.translate(12, -770); ctx.rotate(-0.16);
    ctx.beginPath(); ctx.ellipse(0, 0, 128, 42, 0, 0, 7);
    tartan(ctx, -130, -45, 260, 90, PAL.tartanGreen, PAL.tartanRed, PAL.tartanYellow, 46);
    ctx.beginPath(); ctx.ellipse(0, 0, 128, 42, 0, 0, 7); outline(ctx);
    rr(ctx, -84, 22, 168, 18, 9); ctx.fillStyle = PAL.tartanBlue; ctx.fill(); outline(ctx, 4);
    const pw = Math.sin(t * 7) * 4 + (p.headDy || 0) * 0.4;
    for (let k = 0; k < 9; k++) { const a = k * 0.7; circle(ctx, 18 + Math.cos(a) * 14, -46 + pw + Math.sin(a) * 12, 16, PAL.busRed); }
    circle(ctx, 18, -46 + pw, 26, null, PAL.ink, 4);
    ctx.restore();
    ctx.restore();
    ctx.restore();
  }

  // ---------- Carmen: Sevillana, flamenco dress, peineta comb, rose, fan ----------
  // p: {mouth, blink, lookX, brow, smile, fan (0..1 flutter), point 0..1, photo 0..1, headDy, tilt, t}
  function drawCarmen(ctx, x, y, s, p) {
    const t = p.t || 0;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(p.tilt || 0);
    // heels
    for (const sx of [-1, 1]) { rr(ctx, sx * 34 - 22, -26, 44, 26, 8); ctx.fillStyle = PAL.heel; ctx.fill(); outline(ctx, 4); }
    // fan arm (behind skirt edge, screen right)
    const fl = Math.sin(t * 22) * 0.25 * clamp(p.fan || 0);
    const fhx = 165, fhy = -470;
    limb(ctx, [96, -525, 150, -420, fhx, fhy], PAL.skinCarmen, 36);
    ctx.save(); ctx.translate(fhx, fhy); ctx.rotate(-1.15 + fl);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.arc(0, 0, 120, -Math.PI * 0.95, -Math.PI * 0.05); ctx.closePath();
    ctx.fillStyle = PAL.fanRed; ctx.fill(); outline(ctx, 4);
    ctx.strokeStyle = PAL.fan; ctx.lineWidth = 3;
    for (let k = 1; k < 10; k++) { const a = -Math.PI * (0.95 - k * 0.09); ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(Math.cos(a) * 118, Math.sin(a) * 118); ctx.stroke(); }
    ctx.beginPath(); ctx.arc(0, 0, 112, -Math.PI * 0.95, -Math.PI * 0.05); ctx.lineWidth = 10; ctx.strokeStyle = PAL.fan; ctx.setLineDash([10, 8]); ctx.stroke(); ctx.setLineDash([]);
    ctx.restore();
    circle(ctx, fhx, fhy, 19, PAL.skinCarmen, PAL.ink, 5);
    // flamenco skirt: three ruffled tiers
    const tiers = [[-360, -230, 72, 120], [-250, -135, 112, 160], [-150, -30, 150, 205]];
    for (let i = tiers.length - 1; i >= 0; i--) {
      const [y0, y1, w0, w1] = tiers[i];
      const path = () => {
        ctx.beginPath(); ctx.moveTo(-w0, y0); ctx.lineTo(w0, y0); ctx.lineTo(w1, y1);
        const n = 8;
        for (let k = 1; k <= n; k++) { const xa = w1 - (2 * w1 * (k - 0.5)) / n, xb = w1 - (2 * w1 * k) / n; ctx.quadraticCurveTo(xa, y1 + 26, xb, y1); }
        ctx.closePath();
      };
      path(); ctx.fillStyle = i % 2 ? PAL.dressDark : PAL.dress; ctx.fill();
      path(); dots(ctx, -w1 - 20, y0, 2 * w1 + 40, y1 - y0 + 30, PAL.dot, 44, 7);
      path(); outline(ctx);
    }
    // bodice
    ctx.beginPath(); ctx.moveTo(-96, -540); ctx.quadraticCurveTo(-110, -460, -70, -360); ctx.lineTo(70, -360);
    ctx.quadraticCurveTo(110, -460, 96, -540); ctx.quadraticCurveTo(0, -565, -96, -540); ctx.closePath();
    ctx.fillStyle = PAL.dress; ctx.fill();
    ctx.beginPath(); ctx.moveTo(-96, -540); ctx.quadraticCurveTo(-110, -460, -70, -360); ctx.lineTo(70, -360);
    ctx.quadraticCurveTo(110, -460, 96, -540); ctx.quadraticCurveTo(0, -565, -96, -540); ctx.closePath();
    dots(ctx, -120, -570, 240, 220, PAL.dot, 44, 7);
    ctx.beginPath(); ctx.moveTo(-96, -540); ctx.quadraticCurveTo(-110, -460, -70, -360); ctx.lineTo(70, -360);
    ctx.quadraticCurveTo(110, -460, 96, -540); ctx.quadraticCurveTo(0, -565, -96, -540); ctx.closePath(); outline(ctx);
    // shoulder ruffle
    ctx.beginPath(); ctx.moveTo(-110, -545);
    for (let k = 0; k < 8; k++) ctx.quadraticCurveTo(-110 + k * 27.5 + 14, -510, -110 + (k + 1) * 27.5, -545);
    ctx.lineTo(110, -560); ctx.lineTo(-110, -560); ctx.closePath(); ctx.fillStyle = PAL.dressDark; ctx.fill(); outline(ctx, 4);
    // gesture arm (screen left, towards Morag): rest / point at the sign / hold a photo
    const pt = clamp(p.point || 0), ph = clamp(p.photo || 0);
    let hx = -130, hy = -360, ex = -135, ey = -440;
    if (pt > 0) { hx = lerp(hx, -230, pt); hy = lerp(hy, -720, pt); ex = lerp(ex, -170, pt); ey = lerp(ey, -560, pt); }
    if (ph > 0) { hx = lerp(hx, -175, ph); hy = lerp(hy, -470, ph); ex = lerp(ex, -160, ph); ey = lerp(ey, -420, ph); }
    limb(ctx, [-96, -525, ex, ey, hx, hy], PAL.skinCarmen, 36);
    if (ph > 0.01) drawAuntPhoto(ctx, hx - 40, hy - 135, easeBack(ph), t);
    circle(ctx, hx, hy, 19, PAL.skinCarmen, PAL.ink, 5);
    if (pt > 0.5) { ctx.save(); ctx.translate(hx, hy); ctx.rotate(-2.0); rr(ctx, 0, -7, 40, 14, 7); ctx.fillStyle = PAL.skinCarmen; ctx.fill(); outline(ctx, 4); ctx.restore(); }
    // head
    ctx.save(); ctx.translate(0, p.headDy || 0);
    // peineta comb behind the head
    ctx.beginPath(); ctx.moveTo(-80, -730);
    ctx.bezierCurveTo(-110, -840, -50, -905, 0, -905); ctx.bezierCurveTo(50, -905, 110, -840, 80, -730); ctx.closePath();
    ctx.fillStyle = PAL.comb; ctx.fill(); outline(ctx);
    ctx.fillStyle = PAL.combLight;
    for (let k = 0; k < 5; k++) { ctx.beginPath(); ctx.ellipse(-48 + k * 24, -830 + Math.abs(k - 2) * 14, 8, 22, 0, 0, 7); ctx.fill(); }
    // bun + neck
    circle(ctx, 0, -752, 48, PAL.hairCarmen, PAL.ink, 4);
    rr(ctx, -24, -595, 48, 50, 10); ctx.fillStyle = PAL.skinCarmen; ctx.fill();
    // hair back
    ctx.beginPath(); ctx.arc(0, -662, 98, Math.PI * 0.85, Math.PI * 2.15); ctx.closePath(); ctx.fillStyle = PAL.hairCarmen; ctx.fill();
    circle(ctx, 0, -662, 86, PAL.skinCarmen, PAL.ink, 5);
    // hair cap with centre parting + kiss curl
    ctx.beginPath(); ctx.arc(0, -662, 92, Math.PI * 1.08, Math.PI * 1.92); ctx.quadraticCurveTo(40, -730, 0, -742); ctx.quadraticCurveTo(-40, -730, -86, -695); ctx.closePath();
    ctx.fillStyle = PAL.hairCarmen; ctx.fill(); outline(ctx, 4);
    ctx.beginPath(); ctx.arc(-36, -700, 14, -0.5, Math.PI * 1.4); ctx.lineWidth = 6; ctx.strokeStyle = PAL.hairCarmen; ctx.stroke();
    face(ctx, 0, -657, 86, { skin: PAL.skinCarmen, cheek: PAL.cheekCarmen, mouth: p.mouth, blink: p.blink, lookX: p.lookX, brow: p.brow, smile: p.smile, lip: "#b0101e", lashes: true });
    circle(ctx, 34, -620, 4, PAL.ink); // beauty mark
    // hoop earrings
    for (const sx of [-1, 1]) circle(ctx, sx * 86, -620, 20, null, PAL.gold, 6);
    // rose by the ear (towards Morag)
    ctx.save(); ctx.translate(-82, -728);
    ctx.fillStyle = PAL.leaf; ctx.beginPath(); ctx.ellipse(-30, 20, 26, 11, 0.6, 0, 7); ctx.fill();
    for (let k = 0; k < 6; k++) { const a = k * 1.05; circle(ctx, Math.cos(a) * 18, Math.sin(a) * 18, 20, PAL.rose, PAL.ink, 3); }
    circle(ctx, 0, 0, 16, "#a50d24", PAL.ink, 3);
    ctx.restore();
    ctx.restore();
    ctx.restore();
  }

  // ---------- props ----------
  function drawTeacup(ctx, x, y, k, t) {
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
    ctx.strokeStyle = "rgba(255,255,255,0.8)"; ctx.lineWidth = 6; ctx.lineCap = "round";
    for (let i = 0; i < 3; i++) {
      ctx.beginPath(); const ox = -20 + i * 20;
      for (let j = 0; j <= 10; j++) { const yy = -40 - j * 8; const xx = ox + Math.sin(t * 5 + j * 0.7 + i) * 7; j ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); }
      ctx.stroke();
    }
    ctx.beginPath(); ctx.moveTo(-45, -40); ctx.lineTo(45, -40); ctx.quadraticCurveTo(42, 18, 0, 18); ctx.quadraticCurveTo(-42, 18, -45, -40); ctx.closePath();
    ctx.fillStyle = "#ffffff"; ctx.fill(); outline(ctx, 5);
    ctx.beginPath(); ctx.arc(52, -16, 15, -1.4, 1.4); ctx.lineWidth = 8; ctx.strokeStyle = PAL.ink; ctx.stroke();
    ctx.fillStyle = PAL.tartanBlue; ctx.fillRect(-36, -26, 72, 8);
    ctx.beginPath(); ctx.ellipse(0, 22, 62, 10, 0, 0, 7); ctx.fillStyle = "#ffffff"; ctx.fill(); outline(ctx, 4);
    ctx.restore();
  }

  // A framed photo of Tía Lola: grey bun, comb, mantilla, big smile.
  function drawAuntPhoto(ctx, x, y, k, t) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.1 + Math.sin(t * 3) * 0.03); ctx.scale(k, k);
    rr(ctx, -95, -115, 190, 230, 14); ctx.fillStyle = PAL.gold; ctx.fill(); outline(ctx, 5);
    rr(ctx, -75, -95, 150, 190, 8); ctx.fillStyle = "#f6e7c8"; ctx.fill(); outline(ctx, 3);
    ctx.save(); rr(ctx, -75, -95, 150, 190, 8); ctx.clip();
    ctx.beginPath(); ctx.moveTo(0, -88); ctx.bezierCurveTo(-60, -88, -70, 40, -75, 100); ctx.lineTo(75, 100); ctx.bezierCurveTo(70, 40, 60, -88, 0, -88);
    ctx.fillStyle = "rgba(20,20,20,0.85)"; ctx.fill(); // black lace mantilla
    rr(ctx, -55, 40, 110, 70, 20); ctx.fillStyle = PAL.fanRed; ctx.fill();
    circle(ctx, 0, -10, 42, PAL.skinCarmen, PAL.ink, 3);
    ctx.beginPath(); ctx.arc(0, -18, 44, Math.PI * 1.05, Math.PI * 1.95); ctx.fillStyle = "#c9c4c6"; ctx.fill();
    for (const s of [-1, 1]) { ctx.beginPath(); ctx.arc(s * 15, -14, 6, Math.PI, 0); ctx.lineWidth = 3; ctx.strokeStyle = PAL.ink; ctx.stroke(); }
    ctx.beginPath(); ctx.arc(0, 4, 16, 0.2, Math.PI - 0.2); ctx.lineWidth = 4; ctx.stroke();
    circle(ctx, -24, 2, 7, PAL.cheekCarmen); circle(ctx, 24, 2, 7, PAL.cheekCarmen);
    ctx.restore();
    ctx.fillStyle = PAL.ink; ctx.font = "800 22px Inter, Arial, sans-serif"; ctx.textAlign = "center";
    ctx.fillText("TÍA LOLA", 0, 108);
    ctx.restore();
  }

  function drawCheese(ctx, x, y, k) {
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
    ctx.beginPath(); ctx.moveTo(-60, 30); ctx.lineTo(60, 30); ctx.lineTo(60, -10); ctx.lineTo(-60, -40); ctx.closePath();
    ctx.fillStyle = "#ffcf3f"; ctx.fill(); outline(ctx, 4);
    for (const [hx, hy, hr] of [[-25, 5, 9], [15, 12, 7], [35, -2, 6], [-5, -15, 5]]) circle(ctx, hx, hy, hr, "#e3a91e");
    ctx.restore();
  }

  function drawQuestion(ctx, x, y, size, rot, alpha, text = "?") {
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.rotate(rot);
    ctx.font = `900 ${size}px Inter, "Arial Black", sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.lineWidth = size * 0.14; ctx.strokeStyle = PAL.ink; ctx.lineJoin = "round"; ctx.strokeText(text, 0, 0);
    ctx.fillStyle = "#ffe14d"; ctx.fillText(text, 0, 0);
    ctx.restore();
  }

  function drawHeart(ctx, x, y, r, color, alpha = 1) {
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y);
    ctx.beginPath(); ctx.moveTo(0, r * 0.9);
    ctx.bezierCurveTo(-r * 1.4, -r * 0.1, -r * 0.6, -r * 1.2, 0, -r * 0.45);
    ctx.bezierCurveTo(r * 0.6, -r * 1.2, r * 1.4, -r * 0.1, 0, r * 0.9);
    ctx.fillStyle = color; ctx.fill(); outline(ctx, 4);
    ctx.restore();
  }

  function drawSaltire(ctx, x, y, w, h) {
    ctx.save(); ctx.translate(x, y);
    ctx.fillStyle = "#005eb8"; ctx.fillRect(0, 0, w, h);
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, w, h); ctx.clip();
    ctx.strokeStyle = "#fff"; ctx.lineWidth = h * 0.2;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(w, h); ctx.moveTo(w, 0); ctx.lineTo(0, h); ctx.stroke();
    ctx.restore();
    ctx.lineWidth = 4; ctx.strokeStyle = PAL.ink; ctx.strokeRect(0, 0, w, h);
    ctx.restore();
  }
  function drawSpainFlag(ctx, x, y, w, h) {
    ctx.save(); ctx.translate(x, y);
    ctx.fillStyle = "#c60b1e"; ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = "#ffc400"; ctx.fillRect(0, h * 0.25, w, h * 0.5);
    ctx.lineWidth = 4; ctx.strokeStyle = PAL.ink; ctx.strokeRect(0, 0, w, h);
    ctx.restore();
  }

  // Confetti burst from (ox, oy) starting at t0, pure function of t.
  function drawConfetti(ctx, ox, oy, t0, t, n = 90) {
    const dt = t - t0; if (dt < 0 || dt > 4) return;
    const cols = [PAL.tartanRed, PAL.tartanGreen, "#005eb8", "#ffc400", "#c60b1e", "#ffffff"];
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + (hash(i) - 0.5) * 2.6, v = 700 + hash(i + 50) * 900;
      const x = ox + Math.cos(a) * v * dt, y = oy + Math.sin(a) * v * dt + 900 * dt * dt;
      if (y > 1900) continue;
      ctx.save(); ctx.translate(x, y); ctx.rotate(dt * (4 + hash(i + 9) * 8));
      ctx.globalAlpha = clamp(1.6 - dt * 0.45);
      ctx.fillStyle = cols[i % cols.length]; ctx.fillRect(-9, -5, 18, 10);
      ctx.restore();
    }
  }

  // ---------- speech bubble ----------
  function wrap(ctx, text, maxW) {
    const words = text.split(" "), out = []; let line = "";
    for (const w of words) { const tryL = line ? line + " " + w : w; if (ctx.measureText(tryL).width > maxW && line) { out.push(line); line = w; } else line = tryL; }
    if (line) out.push(line); return out;
  }
  // b: {x, bottom, w, tailX, tailY, k (pop 0..1), alpha, text, sub, accent}
  function drawBubble(ctx, b) {
    if (b.alpha <= 0 || b.k <= 0) return;
    // shrink the type until the bubble fits above b.bottom without crossing b.minTop
    let size = 52, fMain, fSub, main, sub, lh, sh, h, y;
    for (; size >= 36; size -= 2) {
      fMain = `900 ${size}px Inter, "Arial Black", sans-serif`; fSub = `italic 600 ${Math.round(size * 0.62)}px Inter, Arial, sans-serif`;
      lh = size * 1.15; sh = size * 0.77;
      ctx.font = fMain; main = wrap(ctx, b.text, b.w - 76);
      ctx.font = fSub; sub = b.sub ? wrap(ctx, b.sub, b.w - 76) : [];
      h = 30 + main.length * lh + (sub.length ? 12 + sub.length * sh : 0) + 24;
      y = b.bottom - h;
      if (y >= (b.minTop || 0)) break;
    }
    const cx = b.x + b.w / 2, cy = b.bottom;
    ctx.save(); ctx.globalAlpha = b.alpha;
    ctx.translate(b.tailX, b.tailY); ctx.scale(b.k, b.k); ctx.translate(-b.tailX, -b.tailY);
    // shadow
    rr(ctx, b.x + 8, y + 10, b.w, h, 34); ctx.fillStyle = "rgba(0,0,0,0.22)"; ctx.fill();
    // body + tail
    const tx = clamp(b.tailX, b.x + 60, b.x + b.w - 60);
    rr(ctx, b.x, y, b.w, h, 34); ctx.fillStyle = "#fffdf6"; ctx.fill(); outline(ctx, 6);
    ctx.beginPath(); ctx.moveTo(tx - 34, cy - 3); ctx.lineTo(b.tailX, b.tailY); ctx.lineTo(tx + 26, cy - 3); ctx.closePath();
    ctx.fillStyle = "#fffdf6"; ctx.fill(); outline(ctx, 6);
    ctx.fillRect(tx - 30, cy - 10, 54, 10);
    // accent strip
    rr(ctx, b.x + 18, y + 16, 12, h - 32, 6); ctx.fillStyle = b.accent; ctx.fill();
    ctx.textAlign = "left"; ctx.textBaseline = "alphabetic"; ctx.fillStyle = PAL.ink;
    ctx.font = fMain; main.forEach((l, i) => ctx.fillText(l, b.x + 48, y + 30 + size * 0.9 + i * lh));
    ctx.font = fSub; ctx.fillStyle = "#6b5b5e";
    sub.forEach((l, i) => ctx.fillText(l, b.x + 48, y + 30 + main.length * lh + 12 + sh * 0.8 + i * sh));
    ctx.restore();
    return { y, h, cx };
  }

  // ---------- background: Glasgow bus stop, rain on the left, sun on the right ----------
  function drawBackground(ctx, t, o = {}) {
    const W = 1080, H = 1920;
    const sky = ctx.createLinearGradient(0, 0, W, 0);
    sky.addColorStop(0, PAL.skyRain); sky.addColorStop(0.5, PAL.skyMid); sky.addColorStop(1, PAL.skySun);
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, H);
    // sun with sunglasses
    ctx.save(); ctx.translate(880, 310);
    ctx.rotate(t * 0.35); ctx.fillStyle = PAL.sunRay;
    for (let k = 0; k < 12; k++) { ctx.rotate(Math.PI / 6); ctx.beginPath(); ctx.moveTo(-14, 80); ctx.lineTo(0, 150); ctx.lineTo(14, 80); ctx.fill(); }
    ctx.restore();
    circle(ctx, 880, 310, 74, PAL.sun, PAL.ink, 5);
    ctx.fillStyle = PAL.ink; rr(ctx, 832, 290, 44, 26, 10); ctx.fill(); rr(ctx, 884, 290, 44, 26, 10); ctx.fill(); ctx.fillRect(870, 296, 18, 6);
    ctx.beginPath(); ctx.arc(880, 330, 22, 0.3, Math.PI - 0.3); ctx.lineWidth = 6; ctx.strokeStyle = PAL.ink; ctx.stroke();
    // tenements
    let bx = -20, i = 0;
    while (bx < W + 20) {
      const bw = 190 + hash(i) * 50, top = 840 + hash(i + 3) * 120;
      ctx.fillStyle = i % 2 ? PAL.stone : PAL.stoneDark; ctx.fillRect(bx, top, bw, 1480 - top);
      ctx.fillStyle = PAL.stoneDark; ctx.fillRect(bx - 6, top - 14, bw + 12, 18);
      rr(ctx, bx + bw * 0.6, top - 70, 40, 60, 4); ctx.fill();
      for (let r = 0; top + 40 + r * 120 < 1400; r++) for (let c = 0; c < 3; c++) {
        const lit = hash(i * 31 + r * 7 + c) > 0.68;
        ctx.fillStyle = lit ? PAL.windowLit : PAL.window;
        ctx.fillRect(bx + 22 + c * (bw - 44) / 3, top + 40 + r * 120, (bw - 44) / 3 - 16, 80);
      }
      bx += bw; i++;
    }
    // rain cloud
    const drift = Math.sin(t * 0.8) * 10;
    for (const [cx, cy, r, c] of [[150, 330, 90, PAL.cloud], [270, 280, 120, PAL.cloud], [400, 320, 100, PAL.cloud], [520, 350, 70, PAL.cloud], [210, 360, 80, PAL.cloudLight], [350, 370, 85, PAL.cloudLight]])
      circle(ctx, cx + drift, cy, r, c);
    // pavement + road
    ctx.fillStyle = PAL.pavement; ctx.fillRect(0, 1470, W, 360);
    ctx.strokeStyle = PAL.slab; ctx.lineWidth = 4;
    for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(0, 1540 + k * 80); ctx.lineTo(W, 1540 + k * 80); ctx.stroke(); }
    for (let k = -2; k < 12; k++) { ctx.beginPath(); ctx.moveTo(k * 140 + 70, 1470); ctx.lineTo(k * 140 - 40, 1800); ctx.stroke(); }
    ctx.fillStyle = PAL.kerb; ctx.fillRect(0, 1800, W, 26); ctx.fillStyle = PAL.road; ctx.fillRect(0, 1826, W, 100);
    // puddle with rain ripples
    ctx.save(); ctx.beginPath(); ctx.ellipse(170, 1690, 150, 40, 0, 0, 7); ctx.fillStyle = PAL.puddle; ctx.fill(); ctx.clip();
    ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.lineWidth = 3;
    for (let k = 0; k < 6; k++) { const ph = (t * 1.3 + hash(k)) % 1; ctx.globalAlpha = 1 - ph; ctx.beginPath(); ctx.ellipse(80 + hash(k + 4) * 180, 1680 + hash(k + 8) * 20, ph * 40, ph * 11, 0, 0, 7); ctx.stroke(); }
    ctx.restore();
    // bus stop
    const flash = clamp(o.signFlash || 0);
    ctx.fillStyle = "#3c3f44"; ctx.fillRect(532, 1000, 16, 480);
    if (flash > 0) { ctx.save(); ctx.globalAlpha = flash * 0.6; circle(ctx, 540, 1040, 150, "#fff7b0"); ctx.restore(); }
    rr(ctx, 465, 950, 150, 90, 14); ctx.fillStyle = PAL.busRed; ctx.fill(); outline(ctx, 5);
    ctx.fillStyle = "#fff"; ctx.font = "900 30px Inter, Arial, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText("BUS", 540, 980); ctx.fillText("STOP", 540, 1012);
    rr(ctx, 470, 1052, 140, 48, 8); ctx.fillStyle = flash > 0.3 ? "#fff3a0" : "#fff"; ctx.fill(); outline(ctx, 4);
    ctx.fillStyle = PAL.ink; ctx.font = "900 25px Inter, Arial, sans-serif"; ctx.fillText("GLASGOW", 540, 1077);
    // rain (left half only)
    ctx.strokeStyle = PAL.rain; ctx.lineWidth = 4; ctx.lineCap = "round";
    for (let k = 0; k < 110; k++) {
      const x0 = 40 + hash(k) * 560, span = 1120;
      const yy = 400 + ((hash(k + 0.5) * span + t * 1250) % span);
      const xx = x0 - (yy - 400) * 0.12;
      ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx - 5, yy + 38); ctx.stroke();
    }
    // gloomy wash on the rainy side
    const wash = ctx.createLinearGradient(0, 0, W, 0);
    wash.addColorStop(0, "rgba(40,50,70,0.28)"); wash.addColorStop(0.55, "rgba(40,50,70,0)");
    ctx.fillStyle = wash; ctx.fillRect(0, 0, W, H);
  }

  window.Ladies = { PAL, clamp, lerp, seg, easeOut, easeInOut, easeBack, hash, rr, circle, outline,
    drawMorag, drawCarmen, drawBackground, drawBubble, drawTeacup, drawAuntPhoto, drawCheese,
    drawQuestion, drawHeart, drawSaltire, drawSpainFlag, drawConfetti };
})();
