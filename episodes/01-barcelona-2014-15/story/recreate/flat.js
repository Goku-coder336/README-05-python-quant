/* "Matchday Flat": players redrawn from measured poses (17 body points per player per frame). Nothing from the
   reference footage is drawn: every shape here is ours, placed on the measured joints.
   Look: flat fills, one shadow tone, a dark outline round the whole silhouette, faceless heads, kit colours. */
(function () {
  const KITS = {
    BAR:  { shirt: "#a3123a", stripe: "#1d3c8f", shorts: "#1d3c8f", socks: "#1d3c8f", boots: "#111" },
    BARA: { shirt: "#d6f53a", stripe: null, shorts: "#d6f53a", socks: "#d6f53a", boots: "#ff5a3c", trim: "#1d3c8f" },
    PSG:  { shirt: "#1b2440", stripe: null, shorts: "#1b2440", socks: "#1b2440", boots: "#ff7a2f", trim: "#c8102e" },
    JUV:  { shirt: "#f4f4f2", stripe: "#151515", shorts: "#151515", socks: "#151515", boots: "#111" },
    BAY:  { shirt: "#eceef0", stripe: null, shorts: "#eceef0", socks: "#eceef0", boots: "#111", trim: "#c8102e" },
    REF:  { shirt: "#2b8fc4", stripe: null, shorts: "#161a22", socks: "#161a22", boots: "#111" },
  };
  const OUT = "#14181b";
  const sh = (hex, k) => { const n = parseInt(hex.slice(1), 16), c = (v) => Math.max(0, Math.min(255, Math.round(v * k)));
    return "#" + ((1 << 24) + (c((n >> 16) & 255) << 16) + (c((n >> 8) & 255) << 8) + c(n & 255)).toString(16).slice(1); };
  const L = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const f1 = (v) => v.toFixed(1);
  function cap(a, b, r1, r2) {
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 0.01, nx = -dy / l, ny = dx / l;
    return `M ${f1(a[0] + nx * r1)} ${f1(a[1] + ny * r1)} L ${f1(b[0] + nx * r2)} ${f1(b[1] + ny * r2)} A ${f1(r2)} ${f1(r2)} 0 0 0 ${f1(b[0] - nx * r2)} ${f1(b[1] - ny * r2)} ` +
           `L ${f1(a[0] - nx * r1)} ${f1(a[1] - ny * r1)} A ${f1(r1)} ${f1(r1)} 0 0 0 ${f1(a[0] + nx * r1)} ${f1(a[1] + ny * r1)} Z`;
  }
  const poly = (ps) => "M " + ps.map((p) => f1(p[0]) + " " + f1(p[1])).join(" L ") + " Z";
  let UID = 0;

  // K: 17 points [x, y], C: their confidence (low = hidden behind the body, drawn in the shadow tone)
  function player(K, C, T, opt) {
    opt = opt || {};
    // a point never seen in this track comes back as 0,0: borrow its partner on the other side, or its parent joint
    const PART = { 1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5, 7: 5, 8: 6, 9: 7, 10: 8, 11: 12, 12: 11, 13: 11, 14: 12, 15: 13, 16: 14 };
    K = K.map((p) => p.slice());
    for (let pass = 0; pass < 3; pass++) for (let i = 0; i < 17; i++) if (!K[i][0] && !K[i][1] && PART[i] != null) K[i] = K[PART[i]].slice();
    if (!K[0][0] && !K[0][1]) K[0] = [K[5][0] * 0.5 + K[6][0] * 0.5, Math.min(K[5][1], K[6][1]) - 40];
    const kit = KITS[T.kit] || KITS.BAR, skin = T.skin || "#c99572", hair = T.hairCol || "#1a120c", id = "f" + (UID++);
    const mS = L(K[5], K[6], 0.5), mH = L(K[11], K[12], 0.5);
    const s = Math.max(20, Math.hypot(mS[0] - mH[0], mS[1] - mH[1]));   // torso length sets every width
    const B = T.build || 1;
    const shapes = []; // [depthKey, svgPath, fill]
    const side = (i) => (C[i] < 0.5 ? 0.8 : 1);                         // hidden limb: shadow tone
    const facing = (K[0][0] - mS[0]) || (K[15][0] - K[13][0]) || 1;      // which way the front points on screen
    const dir = facing >= 0 ? 1 : -1;
    const backView = C[0] < 0.35 && (C[3] > 0.3 || C[4] > 0.3);

    for (const [h, k, a, t] of [[11, 13, 15, "L"], [12, 14, 16, "R"]]) {
      const tone = side(k), kn = K[k], an = K[a], hip = K[h];
      const toe = [an[0] + dir * s * 0.32, an[1] + s * 0.06];
      shapes.push([tone, cap(hip, kn, 0.2 * s * B, 0.14 * s * B), sh(skin, tone)]);
      shapes.push([tone, cap(L(kn, an, 0.18), an, 0.13 * s * B, 0.085 * s * B), sh(kit.socks, tone)]);
      shapes.push([tone, cap(an, toe, 0.085 * s, 0.07 * s), sh(kit.boots, tone)]);
      shapes.push([tone, cap(hip, L(hip, kn, 0.45), 0.19 * s * B, 0.17 * s * B), sh(kit.shorts, tone)]);
    }
    for (const [sh_, el, wr] of [[5, 7, 9], [6, 8, 10]]) {
      const tone = side(el);
      shapes.push([tone, cap(K[sh_], K[el], 0.12 * s * B, 0.1 * s * B), sh(skin, tone)]);
      shapes.push([tone, cap(K[el], K[wr], 0.1 * s * B, 0.08 * s * B), sh(skin, tone)]);
      shapes.push([tone, cap(K[sh_], L(K[sh_], K[el], 0.45), 0.155 * s * B, 0.13 * s * B), sh(kit.shirt, tone)]);
    }
    // sort: shadow-tone limbs behind, lit limbs in front
    const back = shapes.filter((x) => x[0] < 1), front = shapes.filter((x) => x[0] >= 1);
    // torso: shoulders out to the sleeves, hips out to the shorts
    const across = [K[6][0] - K[5][0], K[6][1] - K[5][1]], al = Math.hypot(...across) || 1, ax = [across[0] / al, across[1] / al];
    const wS = Math.max(al / 2, 0.3 * s) * B + 0.06 * s, wH = 0.22 * s * B;
    const torso = poly([[mS[0] - ax[0] * wS, mS[1] - ax[1] * wS - 0.04 * s], [mS[0] + ax[0] * wS, mS[1] + ax[1] * wS - 0.04 * s],
                        [mH[0] + ax[0] * wH, mH[1] + ax[1] * wH + 0.06 * s], [mH[0] - ax[0] * wH, mH[1] - ax[1] * wH + 0.06 * s]]);
    const pelvis = cap([mH[0] - ax[0] * wH * 0.6, mH[1] - ax[1] * wH * 0.6], [mH[0] + ax[0] * wH * 0.6, mH[1] + ax[1] * wH * 0.6], 0.16 * s, 0.16 * s);
    // head: centred between the ears and nose, sized from the torso
    const hp = [0, 3, 4, 1, 2].filter((i) => C[i] > 0.3).map((i) => K[i]);
    const hc = hp.length ? [hp.reduce((u, p) => u + p[0], 0) / hp.length, hp.reduce((u, p) => u + p[1], 0) / hp.length] : [mS[0], mS[1] - 0.45 * s];
    const hr = 0.3 * s;
    const neck = cap(mS, L(mS, hc, 0.7), 0.1 * s, 0.09 * s);

    const all = (fillOn) => {
      const p = (d, fill) => fillOn ? `<path d="${d}" fill="${fill}"/>` : `<path d="${d}" fill="${OUT}" stroke="${OUT}" stroke-width="${f1(0.05 * s)}" stroke-linejoin="round"/>`;
      let o = back.map((x) => p(x[1], x[2])).join("");
      o += p(neck, sh(skin, 0.88)) + p(pelvis, kit.shorts) + p(torso, kit.shirt);
      if (fillOn && kit.stripe) {
        let st = "";
        for (let k = -2; k <= 2; k++) {
          const o1 = [mS[0] + ax[0] * k * wS * 0.42, mS[1] + ax[1] * k * wS * 0.42 - 0.05 * s], o2 = [mH[0] + ax[0] * k * wH * 0.42, mH[1] + ax[1] * k * wH * 0.42 + 0.06 * s];
          st += `<line x1="${f1(o1[0])}" y1="${f1(o1[1])}" x2="${f1(o2[0])}" y2="${f1(o2[1])}" stroke="${kit.stripe}" stroke-width="${f1(T.kit === "JUV" ? 0.08 * s : 0.12 * s)}"/>`;
        }
        o += `<clipPath id="${id}c"><path d="${torso}"/></clipPath><g clip-path="url(#${id}c)">${st}</g>`;
      }
      if (fillOn) {
        // one shadow tone down the far side of the shirt
        o += `<clipPath id="${id}s"><path d="${torso}"/></clipPath><path clip-path="url(#${id}s)" d="${poly([[mS[0] - dir * 0.05 * s, mS[1] - s], [mS[0] - dir * 2 * s, mS[1] - s], [mH[0] - dir * 2 * s, mH[1] + s], [mH[0] - dir * 0.15 * s, mH[1] + s]])}" fill="rgba(0,0,0,.16)"/>`;
        if (kit.trim) o += `<path d="${cap(L(mS, hc, 0.05), L(mS, hc, 0.12), 0.11 * s, 0.11 * s)}" fill="${kit.trim}"/>`;
        if (backView && T.num) o += `<text x="${f1(L(mS, mH, 0.45)[0])}" y="${f1(L(mS, mH, 0.45)[1])}" text-anchor="middle" dominant-baseline="middle" font-family="Oswald" font-weight="700" font-size="${f1(0.42 * s)}" fill="${T.kit === "BARA" ? "#1d3c8f" : "#ffffff"}">${T.num}</text>`;
      }
      o += front.map((x) => p(x[1], x[2])).join("");
      // head: hair cap on the back of the head, a flat face with one cheek shadow, no features
      const hx = hc[0], hy = hc[1];
      if (fillOn) {
        o += `<circle cx="${f1(hx)}" cy="${f1(hy)}" r="${f1(hr)}" fill="${skin}"/>`;
        o += `<clipPath id="${id}h"><circle cx="${f1(hx)}" cy="${f1(hy)}" r="${f1(hr)}"/></clipPath><g clip-path="url(#${id}h)">` +
             `<rect x="${f1(hx - dir * hr * 0.15 - (dir > 0 ? hr * 2 : 0))}" y="${f1(hy - hr)}" width="${f1(hr * 2)}" height="${f1(hr * 2)}" fill="rgba(0,0,0,.14)"/>` +
             (backView ? `<circle cx="${f1(hx)}" cy="${f1(hy - hr * 0.05)}" r="${f1(hr * 1.02)}" fill="${hair}"/>`
                       : `<ellipse cx="${f1(hx - dir * hr * 0.35)}" cy="${f1(hy - hr * 0.55)}" rx="${f1(hr * 1.05)}" ry="${f1(hr * 0.75)}" fill="${hair}"/>`) +
             (T.hair === "curly" ? `<circle cx="${f1(hx - dir * hr * 0.2)}" cy="${f1(hy - hr * 0.7)}" r="${f1(hr * 0.9)}" fill="${hair}"/>` : "") +
             (T.beard && !backView ? `<ellipse cx="${f1(hx + dir * hr * 0.25)}" cy="${f1(hy + hr * 0.6)}" rx="${f1(hr * 0.75)}" ry="${f1(hr * 0.45)}" fill="${hair}" opacity=".75"/>` : "") +
             `</g>`;
        if (T.hair === "curly") o += `<circle cx="${f1(hx - dir * hr * 0.25)}" cy="${f1(hy - hr * 0.75)}" r="${f1(hr * 0.75)}" fill="${hair}"/><circle cx="${f1(hx - dir * hr * 0.85)}" cy="${f1(hy - hr * 0.3)}" r="${f1(hr * 0.6)}" fill="${hair}"/>`;
      } else {
        o += `<circle cx="${f1(hx)}" cy="${f1(hy)}" r="${f1(hr + 0.025 * s)}" fill="${OUT}"/>`;
        if (T.hair === "curly") o += `<circle cx="${f1(hx - dir * hr * 0.25)}" cy="${f1(hy - hr * 0.75)}" r="${f1(hr * 0.75 + 0.025 * s)}" fill="${OUT}"/><circle cx="${f1(hx - dir * hr * 0.85)}" cy="${f1(hy - hr * 0.3)}" r="${f1(hr * 0.6 + 0.025 * s)}" fill="${OUT}"/>`;
      }
      return o;
    };
    // ground shadow: a dark brush stroke under the feet
    const gy = Math.max(K[15][1], K[16][1]) + 0.08 * s, gx = (K[15][0] + K[16][0]) / 2;
    const shadow = `<ellipse cx="${f1(gx)}" cy="${f1(gy)}" rx="${f1(0.75 * s)}" ry="${f1(0.11 * s)}" fill="rgba(5,30,32,.35)"/>`;
    return { svg: shadow + `<g>${all(false)}</g><g>${all(true)}</g>`, foot: gy, head: [hc[0], hc[1] - hr] };
  }

  function ball(x, y, r) {
    return `<circle cx="${f1(x)}" cy="${f1(y)}" r="${f1(r)}" fill="#fff" stroke="${OUT}" stroke-width="${f1(r * 0.16)}"/>` +
           `<path d="M ${f1(x)} ${f1(y - r * 0.38)} l ${f1(r * 0.36)} ${f1(r * 0.26)} l ${f1(-r * 0.14)} ${f1(r * 0.42)} h ${f1(-r * 0.44)} l ${f1(-r * 0.14)} ${f1(-r * 0.42)} Z" fill="${OUT}"/>`;
  }
  window.FLAT = { player, ball, KITS };
})();
