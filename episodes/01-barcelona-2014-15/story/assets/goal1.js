/* Test scene: Rakitić's goal, 4 minutes, Juventus 0-1 Barcelona.
   Positions: StatsBomb open data (Iniesta's pass from 112,31; Rakitić's shot from 112,38 to 120,41.7; everyone
   else from the shot's freeze frame). Movement: real motion capture (CMU), so poses are illustrative. */
(function () {
  const S = window.Story, MO = window.MO;
  const T_PASS = 2.0, T_SHOT = 3.0, DUR = 8.0;
  const KICK_SHOT = { clip: "10_06", frame: 102 }, KICK_PASS = { clip: "10_02", frame: 87 };
  const ang = (a, b) => Math.atan2(b[1] - a[1], b[0] - a[0]);
  const ease = (u) => u * u * (3 - 2 * u);
  const L = (a, b, u) => [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, (a[2] || 0) + ((b[2] || 0) - (a[2] || 0)) * u];

  // -------------------------------------------------------------- the ball
  const SHOT_FROM = [112, 38, 0], SHOT_TO = [120, 41.7, 0.9], NET = [121.4, 41.9, 0.75];
  function ballAt(t) {
    if (t < T_PASS) return [112, 31, 0];
    if (t < 2.72) return L([112, 31, 0], [111.5, 37.6, 0], ease((t - T_PASS) / 0.72));
    if (t < T_SHOT) return L([111.5, 37.6, 0], SHOT_FROM, (t - 2.72) / 0.28);
    if (t < 3.3) { const u = (t - T_SHOT) / 0.3; const p = L(SHOT_FROM, SHOT_TO, u); p[2] += Math.sin(u * Math.PI) * 0.25; return p; }
    if (t < 3.45) return L(SHOT_TO, NET, (t - 3.3) / 0.15);
    if (t < 3.9) { const u = (t - 3.45) / 0.45; return [NET[0], NET[1], NET[2] * (1 - u) * (1 - u)]; }
    return [NET[0], NET[1], 0];
  }

  // -------------------------------------------------------------- the players
  // a kick clip, placed so the kicking toe is at the ball at the moment of the kick, facing the target
  function kicker(k, tKick, at, target) {
    const P0 = MO.frame(k.clip, k.frame);
    const toe = MO.J(P0, "RightToeBase_end"), hip = MO.J(P0, "Hips");
    // clip space faces -y: rotate so the clip's own facing (hips to toe, roughly -y) points at the target
    const phi = ang(at, target), fa = MO.facing(P0);
    return (t) => {
      const P = MO.frame(k.clip, k.frame + (t - tKick) * 30);
      return MO.place(P, toe, [at[0] - 0.18 * Math.cos(phi), at[1] - 0.18 * Math.sin(phi)], phi, fa);
    };
  }
  // a run along a straight line from a to b between t0 and t1 (run cycle 09_01, frames 0 to 22)
  function runner(a, b, t0, t1) {
    const d = Math.hypot(b[0] - a[0], b[1] - a[1]), v = d / (t1 - t0), phi = ang(a, b);
    const rate = v / 4.76; // the capture runs at 4.76 yards a second
    return (t) => {
      const u = Math.max(0, Math.min(1, (t - t0) / (t1 - t0)));
      const P = MO.loopFrame("09_01", 0, 22, (t - t0) * 30 * rate);
      return MO.place(P, [0, 0], [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u], phi);
    };
  }
  // standing and watching (the quiet start of capture 10_01), facing a point
  function idle(at, face, off) {
    const P0 = MO.frame("10_01", 8), fa = MO.facing(P0);
    return (t) => MO.place(MO.frame("10_01", 8 + ((t * 30 + (off || 0)) % 100)), P0[0], at, ang(at, typeof face === "function" ? face(t) : face), fa);
  }
  const chain = (...parts) => (t) => { for (const [t1, f] of parts) if (t < t1) return f(t); return parts[parts.length - 1][1](t); };

  // Rakitić: runs on to the pass, shoots, runs away to celebrate and jumps
  const rakKick = kicker(KICK_SHOT, T_SHOT, SHOT_FROM, SHOT_TO);
  const rakEnd = MO.J(rakKick(T_SHOT + 1.25), "Hips");
  const celebrate = [rakEnd[0] - 3.2, rakEnd[1] + 7.5];
  const rakRun = runner(rakEnd, celebrate, T_SHOT + 1.25, 6.5);
  const jumpStart = MO.frame("13_11", 38);
  const rakJump = (t) => MO.place(MO.frame("13_11", 38 + (t - 6.5) * 30), MO.J(jumpStart, "Hips"), celebrate, ang(rakEnd, celebrate), MO.facing(jumpStart));
  const rakitic = chain([T_SHOT + 1.25, rakKick], [6.5, rakRun], [99, rakJump]);

  // Iniesta: the pass, then he follows Rakitić
  const iniKick = kicker(KICK_PASS, T_PASS, [112, 31], [111.5, 37.6]);
  const iniEnd = MO.J(iniKick(T_PASS + 1.6), "Hips");
  const iniesta = chain([T_PASS + 1.6, iniKick], [7.0, runner(iniEnd, [celebrate[0] + 1.6, celebrate[1] - 1.2], T_PASS + 1.6, 7.0)], [99, idle([celebrate[0] + 1.6, celebrate[1] - 1.2], celebrate, 20)]);

  // the keeper steps across late (capture 83_19, a sidestep); everyone else from the freeze frame
  const buffonAt = [118, 39];
  const keeperStep = (t) => MO.place(MO.frame("83_19", 55 + Math.max(0, t - 2.85) * 30 * 1.6), MO.frame("83_19", 55)[0], buffonAt, Math.PI, MO.facing(MO.frame("83_19", 55)));
  const actors = [
    { name: "Rakitić", kit: "BAR", tag: true, at: rakitic },
    { name: "Iniesta", kit: "BAR", tag: true, at: iniesta },
    { name: "Buffon", kit: "GKJ", at: keeperStep },
  ];
  const freeze = { Vidal: [109, 33], Bonucci: [113, 34], Evra: [115, 43], Pogba: [111, 39], Barzagli: [109, 30], Pirlo: [103, 34],
                   Marchisio: [106, 23], Lichtsteiner: [110, 22] };
  let k = 0;
  for (const [n, p] of Object.entries(freeze)) actors.push({ name: n, kit: "JUV", at: idle(p, (t) => ballAt(t), (k++) * 13) });
  const mates = { Suárez: [111, 46], Messi: [105, 34], Neymar: [104, 28] };
  for (const [n, p] of Object.entries(mates)) {
    const goal = [celebrate[0] - 1.4 + k * 0.4, celebrate[1] - 2.4 + (k % 2) * 1.6];
    actors.push({ name: n, kit: "BAR", at: chain([4.2, idle(p, (t) => ballAt(t), (k++) * 17)], [7.4, runner(p, goal, 4.2, 7.4)], [99, idle(goal, celebrate, k * 7)]) });
  }

  // -------------------------------------------------------------- cameras (hard cuts between shots)
  function cameraAt(t, P_rak) {
    if (t < 2.62) {
      const u = ease(t / 2.62);
      return new S.Camera({ ex: 104 + u * 1.2, ey: 55 - u * 2.0, ez: 8.5 - u * 1.0, tx: 112 + u * 0.4, ty: 35.5 + u * 1.0, tz: 0, fov: 2050, cy: 560 });
    }
    if (t < 4.3) {
      const u = ease((t - 2.62) / 1.68);
      return new S.Camera({ ex: 104.6 + u * 1.0, ey: 32.4 + u * 0.3, ez: 3.4 - u * 0.3, tx: 115.5, ty: 40.2, tz: 0.6, fov: 2100, cy: 540 });
    }
    const h = MO.J(P_rak, "Hips");
    const u = ease(Math.min(1, (t - 4.3) / 3.7));
    return new S.Camera({ ex: h[0] - 6.5 + u * 1.2, ey: h[1] + 7.5 - u * 1.2, ez: 3.2, tx: h[0] + 0.6, ty: h[1], tz: 0.9, fov: 1900, cy: 560 });
  }

  // -------------------------------------------------------------- one frame
  function render(t, svg, tags) {
    const poses = actors.map((a) => a.at(t));
    const cam = cameraAt(t, poses[0]);
    const bodies = actors.map((a, i) => Object.assign(MO.body(cam, poses[i], a.kit), { a }));
    bodies.sort((x, y) => y.depth - x.depth);
    const b = ballAt(t), bd = (() => { const v = [b[0] - cam.ex, b[1] - cam.ey, b[2] - cam.ez]; return v[0] * cam.f[0] + v[1] * cam.f[1] + v[2] * cam.f[2]; })();
    let out = S.pitchSVG(cam, { line: "rgba(255,255,255,.6)", fill: "rgba(255,255,255,.03)" });
    let ballDrawn = false;
    for (const x of bodies) {
      if (!ballDrawn && bd > x.depth) { out += MO.ball(cam, b); ballDrawn = true; }
      out += x.svg;
    }
    if (!ballDrawn) out += MO.ball(cam, b);
    svg.innerHTML = out;
    // name tags for the players the narration names, while they are on the ball
    let h = "";
    for (const x of bodies) {
      const a = x.a;
      const show = (a.name === "Iniesta" && t > 0.4 && t < 2.55) || (a.name === "Rakitić" && ((t > 1.2 && t < 2.6) || (t > 2.62 && t < 3.6) || t > 4.6));
      if (!show) continue;
      const p = cam.p(x.head[0], x.head[1], x.head[2]);
      h += `<div class="tag" style="left:${p[0].toFixed(0)}px;top:${p[1].toFixed(0)}px">${a.name}</div>`;
    }
    tags.innerHTML = h;
  }
  window.GOAL1 = { render, DUR, T_SHOT };
})();
