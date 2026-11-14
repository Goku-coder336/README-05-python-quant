/* Building blocks for motion-capture scenes: kickers, runners, carriers, idlers, a keeper's dive and a trophy lift.
   Every builder returns a function of scene time t that gives world joint positions (yards, z up). */
(function () {
  const MO = window.MO;
  const ang = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]);
  const ease = (u) => { u = Math.max(0, Math.min(1, u)); return u * u * (3 - 2 * u); };
  const L = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, (a[2] || 0) + ((b[2] || 0) - (a[2] || 0)) * u];
  const RUN = { clip: "09_01", a: 0, b: 22, speed: 4.76 };
  const KICKS = { shot: { clip: "10_06", frame: 102 }, pass: { clip: "10_02", frame: 87 }, shot2: { clip: "11_01", frame: 101 } };

  // a kick, placed so the kicking toe meets the ball at tKick, facing the target
  function kicker(kind, tKick, at, target) {
    const k = KICKS[kind], P0 = MO.frame(k.clip, k.frame), toe = MO.J(P0, "RightToeBase_end"), fa = MO.facing(P0), phi = ang(at, target);
    return (t) => MO.place(MO.frame(k.clip, k.frame + (t - tKick) * 30), toe, [at[0] - 0.18 * Math.cos(phi), at[1] - 0.18 * Math.sin(phi)], phi, fa);
  }
  // where a kicker's hips are at time t (to hand over to the next builder)
  const hipsAt = (f, t) => { const h = MO.J(f(t), "Hips"); return [h[0], h[1]]; };

  // run along a polyline of points [[x,y],...] between t0 and t1, at constant speed
  function runner(pts, t0, t1, opt) {
    opt = opt || {};
    const seg = [];
    let total = 0;
    for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); seg.push(d); total += d; }
    const v = total / (t1 - t0), rate = v / RUN.speed;
    const at = (t) => {
      let s = Math.max(0, Math.min(total, (t - t0) * v));
      for (let i = 0; i < seg.length; i++) { if (s <= seg[i] || i === seg.length - 1) { const u = seg[i] ? Math.min(1, s / seg[i]) : 0; return [L(pts[i], pts[i + 1], u), ang(pts[i], pts[i + 1])]; } s -= seg[i]; }
    };
    const f = (t) => {
      const [p, phi] = at(t);
      const P = MO.loopFrame(RUN.clip, RUN.a, RUN.b, (t - t0) * 30 * rate + (opt.phase || 0));
      return MO.place(P, [0, 0], p, phi);
    };
    f.pos = (t) => at(t)[0];
    f.dir = (t) => at(t)[1];
    return f;
  }
  // stand and watch: the quiet start of capture 10_01, facing a point (or a function of t)
  function idle(at, face, off) {
    const P0 = MO.frame("10_01", 8), fa = MO.facing(P0);
    return (t) => MO.place(MO.frame("10_01", 8 + (((t * 30 + (off || 0)) % 100) + 100) % 100), P0[0], at, ang(at, typeof face === "function" ? face(t) : face), fa);
  }
  // play builders one after another: [[until t, builder], ...]
  const chain = (...parts) => (t) => { for (const [t1, f] of parts) if (t < t1) return f(t); return parts[parts.length - 1][1](t); };

  // rotate joints about an axis through point c (Rodrigues)
  function rotAbout(P, c, axis, a) {
    const [kx, ky, kz] = axis, co = Math.cos(a), si = Math.sin(a);
    return P.map((p) => {
      const v = [p[0] - c[0], p[1] - c[1], p[2] - c[2]];
      const kv = kx * v[0] + ky * v[1] + kz * v[2];
      const cr = [ky * v[2] - kz * v[1], kz * v[0] - kx * v[2], kx * v[1] - ky * v[0]];
      return [c[0] + v[0] * co + cr[0] * si + kx * kv * (1 - co), c[1] + v[1] * co + cr[1] * si + ky * kv * (1 - co), c[2] + v[2] * co + cr[2] * si + kz * kv * (1 - co)];
    });
  }
  // arms reaching (used for the dive and the trophy lift): hands go along direction d from the shoulders
  function reach(P, d, spread) {
    const Q = P.map((p) => p.slice());
    for (const [s, sgn] of [["Left", -1], ["Right", 1]]) {
      const sh = MO.J(Q, s + "Arm"), l = MO.J(Q, "LeftArm"), r = MO.J(Q, "RightArm");
      const side = [(r[0] - l[0]) * sgn * (spread || 0), (r[1] - l[1]) * sgn * (spread || 0), 0];
      const dir = [d[0] + side[0], d[1] + side[1], d[2] + side[2]], n = Math.hypot(...dir);
      const u = dir.map((x) => x / n);
      Q[MO.JI[s + "ForeArm"]] = [sh[0] + u[0] * 0.3, sh[1] + u[1] * 0.3, sh[2] + u[2] * 0.3];
      Q[MO.JI[s + "Hand"]] = [sh[0] + u[0] * 0.58, sh[1] + u[1] * 0.58, sh[2] + u[2] * 0.58];
    }
    return Q;
  }
  // a keeper: ready, then a dive towards side point `to` between t0 and t0 + 0.55
  function diver(at, face, to, t0) {
    const base = idle(at, face, 30);
    return (t) => {
      const u = ease((t - t0) / 0.55);
      if (u <= 0) return base(t);
      let P = base(t0);
      const h = MO.J(P, "Hips");
      const dx = to[0] - at[0], dy = to[1] - at[1], dl = Math.hypot(dx, dy) || 1;
      const side = [dx / dl, dy / dl, 0];
      P = reach(P, [side[0] * 0.55, side[1] * 0.55, 0.85], 0.15);
      const axis = [-side[1], side[0], 0]; // horizontal, across the dive
      P = rotAbout(P, [h[0], h[1], 0.05], axis, 1.25 * u);
      const lift = Math.sin(Math.min(1, u) * Math.PI) * 0.35 + 0;
      const move = Math.min(dl, 1.6) * u;
      const fall = u >= 1 ? Math.min(0.6, (t - t0 - 0.55) * 1.5) : 0;
      return P.map((p) => [p[0] + side[0] * move, p[1] + side[1] * move, Math.max(0, p[2] + lift - fall * 0.2)]);
    };
  }
  // the cup, raised over the head by the player at `at`
  function lifter(at, face, t0) {
    const base = idle(at, face, 5);
    return (t) => {
      const u = ease((t - t0) / 0.8);
      const P = base(t);
      return u <= 0 ? P : reach(P, [0, 0, 1], 0.12 * u);
    };
  }

  // a ball path from keyframes [[t, [x,y,z]], ...]: linear between keys, with an optional arc on a segment ([t,p,arc])
  function ballPath(keys) {
    return (t) => {
      if (t <= keys[0][0]) return keys[0][1].concat([0]).slice(0, 3);
      for (let i = 1; i < keys.length; i++) {
        if (t <= keys[i][0]) {
          const [ta, pa] = keys[i - 1], [tb, pb, arc] = keys[i];
          const u = (t - ta) / (tb - ta);
          const p = L(pa, pb, u);
          if (arc) p[2] += Math.sin(u * Math.PI) * arc;
          return p;
        }
      }
      const p = keys[keys.length - 1][1];
      return [p[0], p[1], p[2] || 0];
    };
  }
  // a ball at a runner's feet, half a yard ahead, bouncing a little
  function carried(run, t0, t1) {
    return (t) => {
      const p = run.pos(Math.max(t0, Math.min(t1, t))), a = run.dir(t);
      return [p[0] + Math.cos(a) * 0.55, p[1] + Math.sin(a) * 0.55, Math.abs(Math.sin(t * 9)) * 0.06];
    };
  }

  window.K3 = { kicker, runner, idle, chain, diver, lifter, ballPath, carried, hipsAt, ang, ease, L };
})();
