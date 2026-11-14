/* "Road to the Treble": a 60-second reel. One moment per stage, then the cup.
   Final scenes: positions from StatsBomb open data (events and freeze frames), movement from CMU motion capture.
   Earlier rounds: illustrations of who scored (no event data), labelled as illustrations on screen. */
(function () {
  const S = window.Story, MO = window.MO, K = window.K3;
  const { kicker, runner, idle, chain, diver, lifter, ballPath, carried, hipsAt, ang, ease } = K;
  const cam = (o) => new S.Camera(Object.assign({ fov: 1900, cy: 560 }, o));
  const track = (p, off, fov, look) => cam({ ex: p[0] + off[0], ey: p[1] + off[1], ez: off[2], tx: p[0] + (look ? look[0] : 0), ty: p[1] + (look ? look[1] : 0), tz: look ? look[2] : 1.0, fov: fov || 1900 });
  const lerpCam = (a, b, u) => { u = ease(u); const o = {}; for (const k of ["ex", "ey", "ez", "tx", "ty", "tz", "fov"]) o[k] = a[k] + (b[k] - a[k]) * u; return cam(o); };

  // ------------------------------------------------------------------ scene: the trio
  function introScene() {
    const ys = { Neymar: 37.6, Suárez: 40, Messi: 42.4 };
    const actors = Object.entries(ys).map(([n, y], i) => ({ name: n, kit: "BAR", tag: [[0.8, 5.6]], at: runner([[38, y], [55, y]], 0, 5.8, { phase: i * 7 }) }));
    return {
      dur: 5.8, actors, ball: null,
      cam: (t) => { const x = 38 + 17 * (t / 5.8); return cam({ ex: x + 11.5 - t * 0.3, ey: 40, ez: 1.6, tx: x, ty: 40, tz: 1.1, fov: 1700 }); },
    };
  }

  // ------------------------------------------------------------------ an illustrated goal (no event data for these matches)
  function illustration(o) {
    const dir = ang(o.start, o.contact);
    const pre = [o.contact[0] - Math.cos(dir) * 1.7, o.contact[1] - Math.sin(dir) * 1.7];
    const target = [120, o.goalY, 0.75];
    const TK = 2.7;
    const run = runner([o.start, pre], 0.0, 2.05);
    const kick = kicker("shot", TK, o.contact, target);
    const celebAt = hipsAt(kick, TK + 1.0);
    const celeb = runner([celebAt, o.celebrate], TK + 1.0, o.dur);
    const scorer = { name: o.scorer, kit: "BAR", tag: [[0.3, 2.05], [2.1, TK + 0.9], [TK + 1.4, o.dur]], at: chain([2.05, run], [TK + 1.0, kick], [99, celeb]) };
    const carry = carried(run, 0, 2.05);
    const c0 = carry(2.05);
    const ball = (t) => t < 2.05 ? carry(t) : ballPath([[2.05, c0], [TK, [o.contact[0], o.contact[1], 0]], [TK + 0.28, target, 0.3], [TK + 0.42, [121.3, o.goalY, 0.6]], [TK + 0.9, [121.3, o.goalY, 0]]])(t);
    const actors = [scorer, { name: "keeper", kit: "OPPGK", at: diver([118.6, 40], (t) => ball(t), [118.6, o.goalY], TK + 0.06) }];
    o.defenders.forEach((p, i) => actors.push({ name: "d" + i, kit: "OPP", at: idle(p, (t) => ball(t), i * 13) }));
    (o.mates || []).forEach((p, i) => actors.push({ name: "m" + i, kit: "BAR", at: idle(p, (t) => (t < TK + 0.4 ? ball(t) : MO.J(scorer.at(t), "Hips")), i * 21) }));
    const side = o.camSide || 1;
    return {
      dur: o.dur, actors, ball,
      cam: (t, P) => {
        const h = MO.J(P[0], "Hips");
        if (t < 2.05) return track(h, [-7.5, 11 * side, 6.5], 1800, [4, -1.5 * side, 0.4]);
        if (t < TK + 1.3) return cam({ ex: o.contact[0] - 9, ey: o.contact[1] + 4.5 * side, ez: 3.0, tx: (o.contact[0] + 117) / 2 + 2, ty: (o.contact[1] + o.goalY) / 2, tz: 0.8, fov: 1950 });
        return track(h, [-7, 8.5 * side, 4.2], 1850, [0.5, 0, 0.9]);
      },
    };
  }

  // ------------------------------------------------------------------ the final, from StatsBomb events
  const D = () => window.FILM_DATA;
  function frz(shotPlayer, key, skip) {
    const s = D().goals[key].find((x) => x.kind === "shot" && x.player === shotPlayer);
    return s.freeze.filter((f) => !(skip || []).includes(f.name));
  }
  function rakitic() {
    const TP = 1.0, TS = 2.0, DUR = 5.0;
    const pass = kicker("pass", TP, [112, 31], [111.5, 37.6]);
    const shot = kicker("shot", TS, [112, 38], [120, 41.7]);
    const celeb = runner([hipsAt(shot, TS + 1.2), [hipsAt(shot, TS + 1.2)[0] - 3, hipsAt(shot, TS + 1.2)[1] + 7]], TS + 1.2, DUR + 0.5);
    const ball = ballPath([[TP, [112, 31, 0]], [TP + 0.72, [111.5, 37.6, 0]], [TS, [112, 38, 0]], [TS + 0.3, [120, 41.7, 0.9], 0.25], [TS + 0.45, [121.4, 41.9, 0.75]], [TS + 0.9, [121.4, 41.9, 0]]]);
    const actors = [
      { name: "Rakitić", kit: "BAR", tag: [[0.4, 1.6], [1.62, 3.2], [3.6, DUR]], at: chain([TS + 1.2, shot], [99, celeb]) },
      { name: "Iniesta", kit: "BAR", tag: [[0.0, 1.3]], at: chain([TP + 1.4, pass], [99, idle(hipsAt(pass, TP + 1.4), (t) => ball(t), 3)]) },
      { name: "Buffon", kit: "GKJ", at: diver([118, 39], (t) => ball(t), [118.4, 41.6], TS + 0.08) },
    ];
    frz("Rakitić", "4'", ["Buffon", "Iniesta"]).forEach((f, i) => actors.push({ name: f.name, kit: f.teammate ? "BAR" : "JUV", at: idle(f.loc, (t) => ball(t), i * 11) }));
    return {
      dur: DUR, actors, ball,
      cam: (t, P) => {
        if (t < 1.62) return lerpCam({ ex: 104, ey: 55, ez: 8.5, tx: 112, ty: 35.5, tz: 0, fov: 2050 }, { ex: 105.2, ey: 53, ez: 7.5, tx: 112.4, ty: 36.5, tz: 0, fov: 2050 }, t / 1.62);
        if (t < 3.6) return lerpCam({ ex: 104.6, ey: 32.4, ez: 3.4, tx: 115.5, ty: 40.2, tz: 0.6, fov: 2100 }, { ex: 105.6, ey: 32.7, ez: 3.1, tx: 115.5, ty: 40.2, tz: 0.6, fov: 2100 }, (t - 1.62) / 1.98);
        return track(MO.J(P[0], "Hips"), [-6, 7.5, 3.0], 1850, [0.5, 0, 0.9]);
      },
    };
  }
  function suarez() {
    const DUR = 7.0, TSH = 3.0, TSU = 4.4;
    const carry1 = runner([[84, 34], [98, 30], [101.3, 30]], 0, 2.8);
    const mShot = kicker("shot2", TSH, [102, 30], [117, 41.1]);
    const messi = chain([2.8, carry1], [TSH + 1.2, mShot], [99, idle(hipsAt(mShot, TSH + 1.2), [114, 43], 7)]);
    const bz = chain([2.0, idle([97, 29], (t) => carry1.pos(t), 4)], [99, runner([[97, 29], [101, 32]], 2.0, 3.4, { phase: 3 })]);
    const sRun = runner([[101, 39], [112.6, 42.7]], 1.4, 3.95, { phase: 11 });
    const sShot = kicker("shot", TSU, [114, 43], [120, 42.2]);
    const sCel = runner([hipsAt(sShot, TSU + 1.0), [106, 58]], TSU + 1.0, DUR + 0.6);
    const ballC = carried(carry1, 0, 2.8);
    const ball = (t) => t < 2.8 ? ballC(t) : ballPath([[2.8, ballC(2.8)], [TSH, [102, 30, 0]], [TSH + 0.42, [116.9, 40.4, 0.7], 0.2], [TSH + 1.05, [114, 43, 0], 0.5], [TSU, [114, 43, 0]], [TSU + 0.25, [120, 42.2, 0.5]], [TSU + 0.4, [121.3, 42.2, 0.4]], [TSU + 0.9, [121.3, 42.2, 0]]])(t);
    const actors = [
      { name: "Messi", kit: "BAR", tag: [[0.2, 2.6], [2.62, TSH + 0.6]], at: messi },
      { name: "Suárez", kit: "BAR", tag: [[TSH + 0.7, DUR]], at: chain([3.95, sRun], [TSU + 1.0, sShot], [99, sCel]) },
      { name: "Barzagli", kit: "JUV", tag: [[1.2, 2.6]], at: bz },
      { name: "Buffon", kit: "GKJ", tag: [[TSH + 0.1, TSH + 0.9]], at: diver([117, 38], (t) => ball(t), [117.2, 40.8], TSH + 0.05) },
    ];
    frz("Messi", "68'", ["Barzagli", "Buffon", "Suárez"]).forEach((f, i) => actors.push({ name: f.name, kit: f.teammate ? "BAR" : "JUV", at: idle(f.loc, (t) => ball(t), i * 7) }));
    return {
      dur: DUR, actors, ball,
      cam: (t, P) => {
        if (t < 2.62) { const h = MO.J(P[0], "Hips"); return track(h, [-6.5, 12, 6.0], 1850, [4.5, -1.5, 0.4]); }
        if (t < 4.95) return lerpCam({ ex: 96.5, ey: 21.5, ez: 6.0, tx: 113.5, ty: 39, tz: 0.6, fov: 2000 }, { ex: 97.5, ey: 22.5, ez: 5.5, tx: 114, ty: 39.5, tz: 0.6, fov: 2000 }, (t - 2.62) / 2.33);
        return track(MO.J(P[1], "Hips"), [-6, 7.5, 3.0], 1850, [0.5, 0, 0.9]);
      },
    };
  }
  function neymar() {
    const DUR = 6.5, TP1 = 0.6, TP2 = 1.8, TS = 3.6;
    const p1 = kicker("pass", TP1, [90, 31], [97, 47]);
    const nRun = runner([hipsAt(p1, TP1 + 0.45), [105.4, 26.5]], TP1 + 0.45, 2.85, { phase: 4 });
    const nCarry = runner([[105.4, 26.5], [108.3, 30.4]], 2.85, 3.3, { phase: 12 });
    const nShot = kicker("shot", TS, [109, 31], [120, 42]);
    const nCel = runner([hipsAt(nShot, TS + 1.0), [103, 14]], TS + 1.0, DUR + 0.5);
    const p2 = kicker("pass", TP2, [97, 46], [106, 27]);
    const ball = (t) => {
      if (t > 2.85 && t < 3.3) return carried(nCarry, 2.85, 3.3)(t);
      return ballPath([[TP1, [90, 31, 0]], [TP1 + 0.9, [97, 46.5, 0], 0.8], [TP2, [97, 46, 0]], [TP2 + 1.0, [105.9, 27.1, 0], 0.3], [2.85, [105.9, 27.1, 0]], [3.3, carried(nCarry, 2.85, 3.3)(3.3)], [TS, [109, 31, 0]], [TS + 0.26, [120, 42, 0.6]], [TS + 0.4, [121.3, 42, 0.5]], [TS + 0.9, [121.3, 42, 0]]])(t);
    };
    const actors = [
      { name: "Neymar", kit: "BAR", tag: [[0.1, 1.2], [2.0, 4.2], [4.6, DUR]], at: chain([TP1 + 0.45, p1], [2.85, nRun], [3.3, nCarry], [TS + 1.0, nShot], [99, nCel]) },
      { name: "Pedro", kit: "BAR", tag: [[1.0, 2.4]], at: chain([TP2 - 0.9, idle([97.4, 46.6], (t) => ball(t), 2)], [99, p2]) },
      { name: "Buffon", kit: "GKJ", at: diver([115, 37], (t) => ball(t), [116.4, 39.5], TS + 0.04) },
    ];
    frz("Neymar", "90+7'", ["Buffon", "Pedro"]).forEach((f, i) => actors.push({ name: f.name, kit: f.teammate ? "BAR" : "JUV", at: idle(f.loc, (t) => ball(t), i * 9) }));
    return {
      dur: DUR, actors, ball,
      cam: (t, P) => {
        if (t < 2.85) return lerpCam({ ex: 97, ey: 72, ez: 15, tx: 100, ty: 36, tz: 0, fov: 1750 }, { ex: 100, ey: 69, ez: 14, tx: 103.5, ty: 35, tz: 0, fov: 1800 }, t / 2.85);
        if (t < 4.6) return lerpCam({ ex: 102.6, ey: 22.5, ez: 2.8, tx: 117, ty: 40, tz: 0.8, fov: 2000 }, { ex: 103.4, ey: 23, ez: 2.6, tx: 117, ty: 40, tz: 0.8, fov: 2000 }, (t - 2.85) / 1.75);
        return track(MO.J(P[0], "Hips"), [-6.5, -7.5, 3.0], 1850, [0.5, 0, 0.9]);
      },
    };
  }

  // ------------------------------------------------------------------ the cup
  function trophyScene() {
    const DUR = 9.5, C = [60, 40];
    const actors = [{ name: "lifter", kit: "BAR", at: lifter(C, [72, 40], 0.9), cup: true }];
    const ring = [[-1.4, -1.6], [-1.2, 1.7], [-2.6, -3.2], [-2.5, 3.1], [-3.4, -0.3], [-0.6, -3.4], [-0.5, 3.5], [-3.9, 1.9], [-3.8, -2.2]];
    ring.forEach(([dx, dy], i) => {
      const p = [C[0] + dx, C[1] + dy];
      const J0 = MO.frame("13_11", 38), fa = MO.facing(J0);
      actors.push({ name: "p" + i, kit: i === 4 ? "GKB" : "BAR", at: (t) => t < 1.2 + i * 0.07
        ? idle(p, [72, 40], i * 17)(t)
        : MO.place(MO.frame("13_11", 38 + (((t - 1.2 - i * 0.07) * 30 * 1.15) % 46)), MO.J(J0, "Hips"), p, ang(p, [72, 40]), fa) });
    });
    return {
      dur: DUR, actors, ball: null,
      cam: (t) => { const a = -0.25 + 0.5 * ease(t / DUR); return cam({ ex: C[0] + 8.5 * Math.cos(a), ey: C[1] + 8.5 * Math.sin(a), ez: 1.25, tx: C[0] - 1.2, ty: C[1], tz: 1.75, fov: 1650 }); },
    };
  }
  function cupSVG(c, k) {
    const s = k * 0.0105; // the drawing is about 100 units tall = 0.6 yards held above the head
    return `<g transform="translate(${c[0].toFixed(1)} ${c[1].toFixed(1)}) scale(${s.toFixed(3)})">
      <defs><linearGradient id="silver" x1="0" x2="1"><stop offset="0" stop-color="#8e979f"/><stop offset=".45" stop-color="#f4f6f8"/><stop offset="1" stop-color="#7c858d"/></linearGradient></defs>
      <path d="M -26 -96 Q -60 -96 -60 -66 Q -60 -40 -24 -36" fill="none" stroke="url(#silver)" stroke-width="9"/>
      <path d="M 26 -96 Q 60 -96 60 -66 Q 60 -40 24 -36" fill="none" stroke="url(#silver)" stroke-width="9"/>
      <path d="M -30 -100 Q -30 -40 -10 -26 L -8 -6 L -22 4 L 22 4 L 8 -6 L 10 -26 Q 30 -40 30 -100 Z" fill="url(#silver)"/>
      <rect x="-26" y="4" width="52" height="16" rx="3" fill="url(#silver)"/></g>`;
  }
  // confetti: fixed pseudo-random pieces, falling over the cup scene
  const CONF = Array.from({ length: 140 }, (_, i) => { const r = (n) => ((Math.sin(i * 12.9898 + n * 78.233) * 43758.5453) % 1 + 1) % 1; return { x: r(1) * 1920, sp: 160 + r(2) * 260, ph: r(3) * 1400, w: 8 + r(4) * 10, c: ["#a3123a", "#1d3c8f", "#f2c14e", "#ffffff"][i % 4], rot: r(5) * 360 }; });

  // ------------------------------------------------------------------ the reel
  const SCENES = [];
  function build() {
    const add = (t0, sc, meta) => SCENES.push(Object.assign(sc, { t0, t1: t0 + sc.dur }, meta));
    add(0, introScene(), { kind: "intro" });
    add(5.8, illustration({ dur: 7.4, scorer: "Messi", start: [95, 60], contact: [107, 46], goalY: 38.4, celebrate: [104, 64], defenders: [[100, 55], [109, 41], [104, 38], [112, 47]], mates: [[101, 34]], camSide: 1 }), { kind: "illus" });
    add(13.2, illustration({ dur: 6.2, scorer: "Suárez", start: [94, 40], contact: [106, 39], goalY: 43, celebrate: [103, 56], defenders: [[98, 43], [109, 36], [110, 44], [104, 33]], mates: [[100, 50], [101, 28]], camSide: 1 }), { kind: "illus" });
    add(19.4, illustration({ dur: 6.4, scorer: "Neymar", start: [97, 17], contact: [108, 29], goalY: 44, celebrate: [102, 14], defenders: [[101, 21], [110, 33], [112, 39], [106, 38]], mates: [[104, 44]], camSide: -1 }), { kind: "illus" });
    add(25.8, illustration({ dur: 6.2, scorer: "Messi", start: [93, 53], contact: [105, 44], goalY: 37, celebrate: [102, 62], defenders: [[98, 49], [108, 40], [110, 46], [103, 37]], mates: [[100, 31]], camSide: 1 }), { kind: "illus" });
    add(32.0, rakitic(), { kind: "final" });
    add(37.0, suarez(), { kind: "final" });
    add(44.0, neymar(), { kind: "final" });
    add(50.5, trophyScene(), { kind: "cup" });
  }

  function render(t, svg, tags) {
    if (!SCENES.length) build();
    const sc = SCENES.find((s) => t < s.t1) || SCENES[SCENES.length - 1];
    const u = Math.min(t - sc.t0, sc.dur - 0.001);
    const poses = sc.actors.map((a) => a.at(u));
    const C = sc.cam(u, poses);
    const bodies = sc.actors.map((a, i) => Object.assign(MO.body(C, poses[i], a.kit), { a, P: poses[i] }));
    bodies.sort((x, y) => y.depth - x.depth);
    let out = S.pitchSVG(C, { line: "rgba(255,255,255,.6)", fill: "rgba(255,255,255,.03)" });
    const b = sc.ball ? sc.ball(u) : null;
    const bd = b ? (b[0] - C.ex) * C.f[0] + (b[1] - C.ey) * C.f[1] + (b[2] - C.ez) * C.f[2] : 0;
    let drawn = !b;
    for (const x of bodies) {
      if (!drawn && bd > x.depth) { out += MO.ball(C, b); drawn = true; }
      out += x.svg;
      if (x.a.cup && u > 0.9) {
        const l = MO.J(x.P, "LeftHand"), r = MO.J(x.P, "RightHand"), m = [(l[0] + r[0]) / 2, (l[1] + r[1]) / 2, (l[2] + r[2]) / 2 + 0.05];
        const p = C.p(m[0], m[1], m[2]);
        out += cupSVG(p, p[2]);
      }
    }
    if (!drawn) out += MO.ball(C, b);
    if (sc.kind === "cup" && u > 1.0) {
      const tt = u - 1.0;
      out += CONF.map((c) => { const y = ((c.ph + tt * c.sp) % 1300) - 120, x = c.x + Math.sin(tt * 2 + c.ph) * 30; return `<rect x="${x.toFixed(0)}" y="${y.toFixed(0)}" width="${c.w.toFixed(0)}" height="${(c.w * 0.5).toFixed(0)}" fill="${c.c}" transform="rotate(${(c.rot + tt * 200).toFixed(0)} ${x.toFixed(0)} ${y.toFixed(0)})"/>`; }).join("");
    }
    svg.innerHTML = out;
    let h = "";
    for (const x of bodies) {
      const a = x.a;
      if (!a.tag || !a.tag.some(([p, q]) => u >= p && u < q)) continue;
      const p = C.p(x.head[0], x.head[1], x.head[2]);
      if (p[0] < 40 || p[0] > 1880 || p[1] < 60 || p[1] > 1000) continue;
      h += `<div class="tag${a.kit === "JUV" || a.kit === "GKJ" ? " opp" : ""}" style="left:${p[0].toFixed(0)}px;top:${p[1].toFixed(0)}px">${a.name}</div>`;
    }
    tags.innerHTML = h;
    return sc;
  }
  window.REEL = { render, SCENES, build };
})();
