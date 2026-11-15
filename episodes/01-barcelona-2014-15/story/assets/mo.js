/* Players moved by real motion capture (CMU Graphics Lab Motion Capture Database, free for any use),
   drawn flat: tapered limbs, kit colours, no faces. Needs story.js (Camera) and data/mocap.js (window.MOCAP). */
(function () {
  const M = window.MOCAP, JI = {};
  M.joints.forEach((n, i) => (JI[n] = i));
  const S = window.Story;

  const KITS = {
    BAR: { shirt: "#a3123a", stripe: "#1d3c8f", shorts: "#1d3c8f", socks: "#1d3c8f", boots: "#101010", sleeve: "#a3123a" },
    JUV: { shirt: "#f4f4f2", stripe: "#151515", shorts: "#151515", socks: "#151515", boots: "#101010", sleeve: "#f4f4f2" },
    GKJ: { shirt: "#f2a516", stripe: null, shorts: "#f2a516", socks: "#f2a516", boots: "#101010", sleeve: "#d98e0c" },
    PSG: { shirt: "#1b2440", stripe: null, shorts: "#1b2440", socks: "#1b2440", boots: "#101010", sleeve: "#1b2440", band: "#c8102e" },
    BAY: { shirt: "#eceef0", stripe: null, shorts: "#eceef0", socks: "#eceef0", boots: "#101010", sleeve: "#d9dde1", band: "#c8102e" },
    GKB: { shirt: "#b8e01f", stripe: null, shorts: "#b8e01f", socks: "#b8e01f", boots: "#101010", sleeve: "#a0c616" },
    OPP: { shirt: "#3d4452", stripe: null, shorts: "#262a33", socks: "#3d4452", boots: "#101010", sleeve: "#353b47" },
    OPPGK: { shirt: "#2fbf71", stripe: null, shorts: "#1f8a50", socks: "#2fbf71", boots: "#101010", sleeve: "#29a863" },
  };
  const SKIN0 = "#b97a55", HAIR0 = "#1d130c";

  function shade(hex, k) {
    const n = parseInt(hex.slice(1), 16);
    const c = (v) => Math.min(255, Math.round(v * k));
    return "#" + ((1 << 24) + (c((n >> 16) & 255) << 16) + (c((n >> 8) & 255) << 8) + c(n & 255)).toString(16).slice(1);
  }
  const lerp3 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
  const nrm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];

  // ---------------------------------------------------------------- sampling and placing clips
  function frame(clip, f) {
    const F = M.clips[clip], n = F.length;
    f = Math.max(0, Math.min(n - 1.001, f));
    const i = Math.floor(f), u = f - i, A = F[i], B = F[Math.min(n - 1, i + 1)];
    return A.map((p, j) => lerp3(p, B[j], u));
  }
  // a looping clip (run): frames a..b repeat; the hips' ground travel is removed so the caller moves the player
  function loopFrame(clip, a, b, f) {
    const len = b - a, k = ((f % len) + len) % len;
    const P = frame(clip, a + k), h = P[0];
    return P.map((p) => [p[0] - h[0], p[1] - h[1], p[2]]);
  }
  // clip space faces -y. Turn to face world angle phi, then move so local point `anchor` lands on world point W.
  function place(P, anchor, W, phi, fa) {
    const a = phi - (fa == null ? -Math.PI / 2 : fa), c = Math.cos(a), s = Math.sin(a);
    return P.map((p) => {
      const x = p[0] - anchor[0], y = p[1] - anchor[1];
      return [W[0] + x * c - y * s, W[1] + x * s + y * c, p[2]];
    });
  }
  const J = (P, name) => P[JI[name]];
  // the way a pose faces on the ground (from the shoulders: up x (right - left))
  function facing(P) { const l = J(P, "LeftArm"), r = J(P, "RightArm"); return Math.atan2(r[0] - l[0], -(r[1] - l[1])); }

  // ---------------------------------------------------------------- drawing
  function capsule(a, b, r1, r2) {
    const dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 0.001;
    const nx = -dy / l, ny = dx / l, f = (v) => v.toFixed(1);
    if (l < Math.abs(r1 - r2) + 0.5) { const r = Math.max(r1, r2), c = r1 > r2 ? a : b; return `M ${f(c[0] - r)} ${f(c[1])} a ${f(r)} ${f(r)} 0 1 0 ${f(2 * r)} 0 a ${f(r)} ${f(r)} 0 1 0 ${f(-2 * r)} 0 Z`; }
    return `M ${f(a[0] + nx * r1)} ${f(a[1] + ny * r1)} L ${f(b[0] + nx * r2)} ${f(b[1] + ny * r2)} ` +
           `A ${f(r2)} ${f(r2)} 0 0 0 ${f(b[0] - nx * r2)} ${f(b[1] - ny * r2)} L ${f(a[0] - nx * r1)} ${f(a[1] - ny * r1)} ` +
           `A ${f(r1)} ${f(r1)} 0 0 0 ${f(a[0] + nx * r1)} ${f(a[1] + ny * r1)} Z`;
  }
  let UID = 0;
  // P: world joint positions (yards). Returns { svg, depth } so the scene can sort players.
  // T (optional): one player's look. skin, hair colour, hair style (short, curly, thin, top), beard, build (limb
  // thickness), number and name on the back, captain's armband. No faces: players are told apart by these.
  function body(cam, P, kitName, T) {
    T = T || {};
    const SKIN = T.skin || SKIN0, HAIR = T.hairCol || HAIR0, B = T.build || 1;
    const K = KITS[kitName], id = "b" + (UID++);
    const prims = []; // {d, depth, fill, kind}
    const depthOf = (p) => { const v = sub(p, [cam.ex, cam.ey, cam.ez]); return v[0] * cam.f[0] + v[1] * cam.f[1] + v[2] * cam.f[2]; };
    const pr = (p) => cam.p(p[0], p[1], p[2]);
    const hips = J(P, "Hips"), dHip = depthOf(hips);
    const seg = (a, b, r1, r2, col, kind, bias) => {
      const A = pr(a), B_ = pr(b), m = lerp3(a, b, 0.5), dep = depthOf(m) + (bias || 0), Bk = kind === "torso" ? 1 : B;
      const far = dep > dHip + 0.06;
      prims.push({ d: capsule(A, B_, r1 * A[2] * Bk, r2 * B_[2] * Bk), depth: dep, fill: far ? shade(col, 0.78) : col, kind });
    };
    for (const side of ["Left", "Right"]) {
      const up = J(P, side + "UpLeg"), kn = J(P, side + "Leg"), an = J(P, side + "Foot"), toe = J(P, side + "ToeBase"), tip = J(P, side + "ToeBase_end");
      seg(up, kn, 0.085, 0.062, SKIN);
      seg(kn, lerp3(kn, an, 0.2), 0.062, 0.064, SKIN, null, 0.001);
      seg(lerp3(kn, an, 0.17), an, 0.066, 0.042, K.socks, null, -0.001);
      seg(an, toe, 0.052, 0.046, K.boots, null, -0.002);
      seg(toe, tip, 0.046, 0.038, K.boots, null, -0.002);
      seg(up, lerp3(up, kn, 0.46), 0.112, 0.102, K.shorts, null, -0.004);
      const ar = J(P, side + "Arm"), el = J(P, side + "ForeArm"), ha = J(P, side + "Hand");
      seg(ar, el, 0.052, 0.044, SKIN);
      seg(el, ha, 0.043, 0.034, SKIN);
      seg(ha, ha, 0.04, 0.04, SKIN);
      seg(ar, lerp3(ar, el, 0.42), 0.072, 0.064, K.sleeve, null, -0.004);
      if (K.band) seg(lerp3(ar, el, 0.36), lerp3(ar, el, 0.42), 0.074, 0.066, K.band, null, -0.005);
      if (T.armband && side === "Left") seg(lerp3(ar, el, 0.3), lerp3(ar, el, 0.42), 0.075, 0.068, "#ffd166", null, -0.006);
    }
    const lU = J(P, "LeftUpLeg"), rU = J(P, "RightUpLeg"), sp = J(P, "Spine1"), nk = J(P, "Neck1"), hd = J(P, "Head"), he = J(P, "Head_end");
    const lA = J(P, "LeftArm"), rA = J(P, "RightArm");
    seg(lU, rU, 0.12, 0.12, K.shorts, "torso", 0.01);
    // torso: three fat capsules, with stripes clipped to them
    const torso = [[lerp3(lU, rU, 0.5), sp, 0.155, 0.17], [sp, nk, 0.17, 0.13], [lA, rA, 0.09, 0.09]];
    const tDepth = depthOf(sp);
    const tPaths = torso.map(([a, b, r1, r2]) => { const A = pr(a), Bp = pr(b); return capsule(A, Bp, r1 * A[2] * B, r2 * Bp[2] * B); }).join(" ");
    let stripes = "";
    if (K.stripe) {
      const sh = nrm(sub(rA, lA)), offs = kitName === "JUV" ? [-0.16, -0.08, 0, 0.08, 0.16] : [-0.12, 0, 0.12];
      const w = kitName === "JUV" ? 0.034 : 0.05;
      for (const o of offs) {
        const a = pr(add(add(lerp3(lU, rU, 0.5), mul(sh, o)), [0, 0, -0.08])), b = pr(add(add(nk, mul(sh, o)), [0, 0, 0.08]));
        stripes += `<line x1="${a[0].toFixed(1)}" y1="${a[1].toFixed(1)}" x2="${b[0].toFixed(1)}" y2="${b[1].toFixed(1)}" stroke="${K.stripe}" stroke-width="${(w * a[2]).toFixed(1)}"/>`;
      }
    }
    // a soft shadow on the side of the shirt away from the light (the light comes from +y, +z)
    const fwd = nrm(crs([0, 0, 1], sub(rA, lA)));
    const sideAway = mul(nrm(crs(fwd, [0, 0, 1])), 0.13);
    const s0 = pr(add(lerp3(lU, rU, 0.5), sideAway)), s1 = pr(add(nk, sideAway));
    prims.push({ depth: tDepth, raw:
      `<clipPath id="${id}t"><path d="${tPaths}"/></clipPath><path d="${tPaths}" fill="${K.shirt}"/>` +
      `<g clip-path="url(#${id}t)">${stripes}<line x1="${s0[0].toFixed(1)}" y1="${s0[1].toFixed(1)}" x2="${s1[0].toFixed(1)}" y2="${s1[1].toFixed(1)}" stroke="rgba(0,0,0,.2)" stroke-width="${(0.12 * s0[2]).toFixed(1)}"/></g>` });
    // neck and head: hair over the crown and the back of the head, no face
    seg(nk, hd, 0.055, 0.05, shade(SKIN, 0.9), null, 0.002);
    const hc = lerp3(hd, he, 0.45), H = pr(hc), r = 0.118 * H[2];
    const back = pr(add(add(hc, mul(fwd, -0.03)), [0, 0, 0.03])), face = pr(add(add(hc, mul(fwd, 0.035)), [0, 0, -0.02]));
    const faceVisible = depthOf(add(hc, fwd)) < depthOf(hc);
    const P2 = (v) => pr(add(hc, v)), up = [0, 0, 1], sideV = nrm(sub(rA, lA));
    const c = (q, rr, col, op) => `<circle cx="${q[0].toFixed(1)}" cy="${q[1].toFixed(1)}" r="${rr.toFixed(1)}" fill="${col}"${op ? ` opacity="${op}"` : ""}/>`;
    const style = T.hair || "short";
    let hairBack = "", hairTop = "";
    if (style === "curly") {
      for (const [sx, sz, sf, rr] of [[0, 0.07, -0.02, 0.9], [-0.075, 0.04, -0.03, 0.72], [0.075, 0.04, -0.03, 0.72], [0, 0.03, -0.07, 0.8], [-0.05, 0.08, 0.01, 0.6], [0.05, 0.08, 0.01, 0.6]])
        hairBack += c(P2(add(add(mul(sideV, sx), mul(up, sz)), mul(fwd, sf))), r * rr * 1.05, HAIR);
    } else if (style === "thin") {
      hairBack = c(P2(add(mul(fwd, -0.045), mul(up, -0.015))), r * 0.92, HAIR);
    } else {
      hairBack = c(P2(add(mul(fwd, -0.03), mul(up, 0.03))), r * 1.02, HAIR);
      if (style === "top") hairTop = c(P2(add(mul(fwd, 0.0), mul(up, 0.085))), r * 0.62, HAIR);
    }
    const faceC = P2(add(mul(fwd, 0.035), mul(up, -0.02)));
    let faceSvg = c(faceC, r * 0.93, SKIN);
    if (T.beard && faceVisible) {
      faceSvg += `<clipPath id="${id}f"><circle cx="${faceC[0].toFixed(1)}" cy="${faceC[1].toFixed(1)}" r="${(r * 0.93).toFixed(1)}"/></clipPath>` +
        `<g clip-path="url(#${id}f)">${c(P2(add(mul(fwd, 0.06), mul(up, -0.085))), r * 0.62, HAIR, 0.55)}</g>`;
    }
    const headSvg = faceVisible ? hairBack + faceSvg + hairTop : faceSvg + hairBack + hairTop;
    // the number (and name) on the back, when the back is to the camera
    if (T.num && !faceVisible) {
      const q = pr(lerp3(lerp3(lU, rU, 0.5), nk, 0.55)), qn = pr(lerp3(lerp3(lU, rU, 0.5), nk, 0.86));
      const col = kitName === "BAR" ? "#ffd166" : (kitName === "JUV" || kitName === "BAY" ? "#151515" : "#ffffff");
      prims.push({ depth: tDepth - 0.01, raw: `<text x="${q[0].toFixed(1)}" y="${q[1].toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="Oswald" font-weight="700" font-size="${(0.2 * q[2]).toFixed(1)}" fill="${col}">${T.num}</text>` +
        (T.name ? `<text x="${qn[0].toFixed(1)}" y="${qn[1].toFixed(1)}" text-anchor="middle" dominant-baseline="middle" font-family="Oswald" font-weight="700" font-size="${(0.06 * qn[2]).toFixed(1)}" fill="${col}">${T.name.toUpperCase()}</text>` : "") });
    }
    prims.push({ depth: depthOf(hc) - 0.02, raw: headSvg });
    prims.sort((a, b) => b.depth - a.depth);
    // ground shadow
    const g = pr([hips[0], hips[1], 0]);
    const shadow = `<ellipse cx="${g[0].toFixed(1)}" cy="${g[1].toFixed(1)}" rx="${(0.42 * g[2]).toFixed(1)}" ry="${(0.13 * g[2]).toFixed(1)}" fill="rgba(0,25,28,.32)"/>`;
    const svg = shadow + prims.map((p) => p.raw || `<path d="${p.d}" fill="${p.fill}"/>`).join("");
    return { svg, depth: dHip, head: add(he, [0, 0, 0.35]) };
  }

  function ball(cam, p) {
    const [sx, sy, k] = cam.p(p[0], p[1], p[2] + 0.12), g = cam.p(p[0], p[1], 0), r = Math.max(3, 0.12 * k);
    return `<ellipse cx="${g[0].toFixed(1)}" cy="${g[1].toFixed(1)}" rx="${(r * 1.1).toFixed(1)}" ry="${(r * 0.35).toFixed(1)}" fill="rgba(0,25,28,.35)"/>` +
      `<circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="${r.toFixed(1)}" fill="#fff" stroke="#1a1a1a" stroke-width="${(r * 0.12).toFixed(1)}"/>` +
      `<circle cx="${(sx + r * 0.15).toFixed(1)}" cy="${(sy - r * 0.1).toFixed(1)}" r="${(r * 0.32).toFixed(1)}" fill="#1a1a1a"/>`;
  }

  // scale a pose about the hips' ground point (taller or shorter players)
  function scaleH(P, k) { const h = P[0]; return P.map((p) => [h[0] + (p[0] - h[0]) * k, h[1] + (p[1] - h[1]) * k, p[2] * k]); }
  window.MO = { frame, loopFrame, place, facing, scaleH, body, ball, J, JI, KITS, fps: M.fps };
})();
