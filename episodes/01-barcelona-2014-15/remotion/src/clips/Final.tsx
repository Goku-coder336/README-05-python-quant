// C3 (final xG timeline), C4 (final shot map), C5 (Rakitić goal reconstruction).
// Data: StatsBomb open data, exported and checked against CLAUDE.md by code/export_remotion_data.py.
// Times are seconds from the start of the script line the clip sits on.
import React from "react";
import { ev, keys, lin, pulse } from "../anim";
import { Box, Credit, Stage, Title, Tok, Txt, useT } from "../components/ui";
import data from "../data/final.json";
import { BARCA, BG, FAINT, LINE, MUTED, OPP, PANEL, TEXT } from "../theme";

type Shot = { team: string; name: string; m: number; x: number; y: number; xg: number; goal: boolean; label: string };
const SHOTS = data.shots as Shot[];
const TEAM_COL: Record<string, string> = { Barcelona: BARCA, Juventus: OPP };
const TOT = data.totals as Record<string, number>;

// ======================================================================= C3
// L52 to L57 (3:50). Goals pop on L52 to L54 as each is said; totals on L57.
const PX0 = 190;
const PX1 = 1500;
const MMAX = 98;
const X = (m: number) => PX0 + ((PX1 - PX0) * m) / MMAX;
const Y = (g: number) => 890 - 256 * g;
const CLOCK: [number, number][] = [[0, 0], [2.4, 54.4], [5.4, 68.0], [9.8, 96.75], [10.4, MMAX - 0.5]];
const T_STATS = 11.3;
const T_END: Record<string, number> = { Barcelona: 22.6, Juventus: 25.8 };

const series = (team: string) => {
  const pts: [number, number][] = [[0, 0]];
  let cum = 0;
  SHOTS.filter((s) => s.team === team).forEach((s) => {
    pts.push([s.m, cum]);
    cum += s.xg;
    pts.push([s.m, cum]);
  });
  pts.push([MMAX - 0.5, cum]);
  return { pts, tot: cum, n: SHOTS.filter((s) => s.team === team).length };
};
const SERIES = { Barcelona: series("Barcelona"), Juventus: series("Juventus") };
const cumAt = (team: "Barcelona" | "Juventus", m: number) => {
  let v = 0;
  SERIES[team].pts.forEach(([pm, g]) => {
    if (pm <= m) v = g;
  });
  return v;
};

export const C3: React.FC = () => {
  const t = useT();
  const M = keys(t, CLOCK);
  return (
    <Stage>
      <Title title="Juventus 1-3 Barcelona" subtitle="Champions League final, Berlin, 6 June 2015 · cumulative expected goals (xG)" />
      {[0.5, 1, 1.5, 2, 2.5].map((g) => (
        <g key={g}>
          <line x1={PX0} x2={PX1} y1={Y(g)} y2={Y(g)} stroke={LINE} strokeWidth={1.2} />
          <Txt x={PX0 - 18} y={Y(g) + 8} size={24} color={MUTED} anchor="end">{g.toFixed(1)}</Txt>
        </g>
      ))}
      <line x1={PX0} x2={PX1} y1={Y(0)} y2={Y(0)} stroke={FAINT} strokeWidth={2} />
      {[0, 15, 30, 45, 60, 75, 90].map((m) => (
        <Txt key={m} x={X(m)} y={Y(0) + 40} size={24} color={MUTED} anchor="middle">{`${m}'`}</Txt>
      ))}
      <line x1={X(45)} x2={X(45)} y1={Y(0)} y2={Y(2.5)} stroke={FAINT} strokeWidth={1.5} strokeDasharray="4 4" />
      <Txt x={X(45) + 8} y={Y(2.5) + 24} size={21} color={MUTED}>Half-time</Txt>
      <Txt x={PX0 - 18} y={Y(2.5) - 32} size={24} color={MUTED} anchor="end">xG</Txt>

      {(["Juventus", "Barcelona"] as const).map((team) => {
        const s = SERIES[team];
        const pts = s.pts.filter(([m]) => m <= M);
        const last = pts[pts.length - 1];
        const all = [...pts, [M, last[1]]];
        const d = all.map(([m, g], i) => `${i ? "L" : "M"} ${X(m).toFixed(1)} ${Y(g).toFixed(1)}`).join(" ");
        const hx = X(M);
        const hy = Y(last[1]);
        const ea = ev(t, T_END[team], 0.5);
        return (
          <g key={team}>
            <path d={d} fill="none" stroke={TEAM_COL[team]} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round" />
            <circle cx={hx} cy={hy} r={7} fill={TEAM_COL[team]} />
            <Txt x={hx + 20} y={hy - 6} size={31} weight={600}>{team}</Txt>
            <g style={{ scale: String(1 + 0.2 * (1 - ea)), transformBox: "fill-box", transformOrigin: "0% 50%" }}>
              <Txt x={hx + 20} y={hy + 30} size={31} opacity={ea}>
                <Tok weight={700}>{s.tot.toFixed(2)}</Tok>
                <Tok color={MUTED}> xG</Tok>
                <Tok weight={700}>{`  ·  ${s.n}`}</Tok>
                <Tok color={MUTED}> shots</Tok>
              </Txt>
            </g>
          </g>
        );
      })}

      {SHOTS.filter((s) => s.goal).map((s) => {
        if (M < s.m) return null;
        const tg = keys(s.m, CLOCK.map(([tt, m]) => [m, tt]) as [number, number][]);
        const a = ev(t, tg, 0.35);
        const gy = cumAt(s.team as "Barcelona" | "Juventus", s.m);
        const r = 13 * (1 + 0.6 * pulse(t, tg, 0.45));
        const early = s.team === "Barcelona" && s.m < 10;
        const lx = early ? X(s.m) + 4 : s.team === "Barcelona" ? X(s.m) - 14 : X(s.m) - 16;
        const ly = early ? Y(gy) - 30 : s.team === "Barcelona" ? Y(gy) - 26 : Y(gy) - 24;
        return (
          <g key={s.label} opacity={a}>
            <circle cx={X(s.m)} cy={Y(gy)} r={r} fill={TEAM_COL[s.team]} stroke={TEXT} strokeWidth={2.5} />
            <Txt x={lx} y={ly} size={26} weight={600} anchor={early ? "start" : "end"}>{s.label}</Txt>
          </g>
        );
      })}

      <g opacity={ev(t, T_STATS, 0.5)}>
        <Box x={1490} y={58} w={350} h={52} r={26} fill={PANEL} stroke={LINE} sw={1.5} />
        <Txt x={1665} y={93} size={28} weight={600} anchor="middle">According to StatsBomb</Txt>
      </g>
      <Credit />
    </Stage>
  );
};

// ======================================================================= pitch (SVG, StatsBomb 120 x 80)
type Mapper = (x: number, y: number) => [number, number];

const PitchLines: React.FC<{ P: Mapper; full: boolean; s: number }> = ({ P, full, s }) => {
  const seg = (a: [number, number], b: [number, number], k: string) => {
    const [x1, y1] = P(...a);
    const [x2, y2] = P(...b);
    return <line key={k} x1={x1} y1={y1} x2={x2} y2={y2} stroke={FAINT} strokeWidth={2} />;
  };
  const rect = (x0: number, y0: number, x1: number, y1: number, k: string) => [
    seg([x0, y0], [x1, y0], k + "a"), seg([x1, y0], [x1, y1], k + "b"),
    seg([x1, y1], [x0, y1], k + "c"), seg([x0, y1], [x0, y0], k + "d"),
  ];
  const ends = full ? [0, 1] : [1];
  const xmin = full ? 0 : 72;
  const out: React.ReactNode[] = [];
  // touchlines and goal line(s)
  out.push(seg([xmin, 0], [120, 0], "t1"), seg([xmin, 80], [120, 80], "t2"), seg([120, 0], [120, 80], "g2"));
  if (full) out.push(seg([0, 0], [0, 80], "g1"), seg([60, 0], [60, 80], "half"));
  ends.forEach((e) => {
    const f = (x: number) => (e ? x : 120 - x);
    out.push(...rect(f(102), 18, f(120), 62, `pa${e}`), ...rect(f(114), 30, f(120), 50, `sy${e}`));
    const [gx1, gy1] = P(f(120), 36);
    const [gx2, gy2] = P(f(122.4), 44);
    out.push(
      <rect key={`goal${e}`} x={Math.min(gx1, gx2)} y={Math.min(gy1, gy2)} width={Math.abs(gx2 - gx1)} height={Math.abs(gy2 - gy1)}
        fill="none" stroke={FAINT} strokeWidth={2} />,
    );
    const [sx, sy] = P(f(108), 40);
    out.push(<circle key={`spot${e}`} cx={sx} cy={sy} r={3} fill={FAINT} />);
    // penalty arc: part of the r=10 circle around the spot outside the box
    const pts: string[] = [];
    for (let a = -53.13; a <= 53.13; a += 3) {
      const rad = (a * Math.PI) / 180;
      const [ax, ay] = P(f(108 - 10 * Math.cos(rad)), 40 + 10 * Math.sin(rad));
      pts.push(`${ax.toFixed(1)},${ay.toFixed(1)}`);
    }
    out.push(<polyline key={`arc${e}`} points={pts.join(" ")} fill="none" stroke={FAINT} strokeWidth={2} />);
  });
  if (full) {
    const [cx, cy] = P(60, 40);
    out.push(<circle key="cc" cx={cx} cy={cy} r={10 * s} fill="none" stroke={FAINT} strokeWidth={2} />);
    out.push(<circle key="cs" cx={cx} cy={cy} r={3} fill={FAINT} />);
  }
  return <>{out}</>;
};

// ======================================================================= C4
// L58 to L59 (4:20). 12 s. Bottom 240 px left clear for a CapCut lower third.
const S4 = 8;
const PX = 480;
const PY = 205;
const P4: Mapper = (x, y) => [PX + x * S4, PY + y * S4];
const rad = (xg: number) => (Math.sqrt(60 + 1900 * xg) * 1.389) / 2;
const SHOT_T = SHOTS.map((_, i) => 0.6 + (6.4 * i) / (SHOTS.length - 1));
const GOAL_LABEL: Record<string, [number, number]> = { Neymar: [90, 13], "Rakitić": [90, 40], "Suárez": [90, 67], Morata: [30, 68] };

const TeamPanel: React.FC<{ team: string; x: number; anchor: "start" | "end"; t: number }> = ({ team, x, anchor, t }) => {
  const shown = SHOTS.filter((s, i) => s.team === team && SHOT_T[i] <= t);
  const sign = anchor === "start" ? 1 : -1;
  const xg = shown.reduce((a, s) => a + s.xg, 0);
  return (
    <g>
      <circle cx={x + sign * 10} cy={252} r={10} fill={TEAM_COL[team]} />
      <Txt x={x + sign * 32} y={264} size={36} weight={700} anchor={anchor}>{team}</Txt>
      <Txt x={x} y={360} size={84} weight={700} anchor={anchor}>{shown.length}</Txt>
      <Txt x={x} y={396} size={26} color={MUTED} anchor={anchor}>shots</Txt>
      <Txt x={x} y={500} size={84} weight={700} anchor={anchor}>{xg.toFixed(2)}</Txt>
      <Txt x={x} y={536} size={26} color={MUTED} anchor={anchor}>xG</Txt>
    </g>
  );
};

export const C4: React.FC = () => {
  const t = useT();
  // sanity: the panel totals at the end must equal the checked figures
  if (Math.abs(SERIES.Barcelona.tot - TOT.Barcelona_xg) > 0.006 || SERIES.Barcelona.n !== TOT.Barcelona_shots) {
    throw new Error("Shot data does not match the checked totals");
  }
  return (
    <Stage>
      <Title title="Juventus 1-3 Barcelona: every shot" subtitle="Champions League final 2015 · circle size shows xG · filled circle = goal" />
      <Txt x={P4(30, 0)[0]} y={185} size={22} color={MUTED} anchor="middle">{"←   Juventus attack"}</Txt>
      <Txt x={P4(90, 0)[0]} y={185} size={22} color={MUTED} anchor="middle">{"Barcelona attack   →"}</Txt>
      <Txt x={1560} y={76} size={22} color={MUTED}>xG</Txt>
      {[0.05, 0.2, 0.5].map((g, i) => (
        <g key={g}>
          <circle cx={1620 + i * 90} cy={70} r={rad(g)} fill="none" stroke={MUTED} strokeWidth={1.5} />
          <Txt x={1620 + i * 90} y={124} size={20} color={MUTED} anchor="middle">{String(g)}</Txt>
        </g>
      ))}
      <PitchLines P={P4} full s={S4} />
      <TeamPanel team="Juventus" x={80} anchor="start" t={t} />
      <TeamPanel team="Barcelona" x={1840} anchor="end" t={t} />
      {SHOTS.map((s, i) => {
        const a = ev(t, SHOT_T[i], 0.3);
        if (a <= 0) return null;
        const barca = s.team === "Barcelona";
        const [cx, cy] = barca ? P4(s.x, s.y) : P4(120 - s.x, 80 - s.y);
        const pop = 1 + 0.5 * pulse(t, SHOT_T[i], 0.35);
        const col = TEAM_COL[s.team];
        const lab = s.goal ? GOAL_LABEL[s.name] : null;
        const la = ev(t, SHOT_T[i] + 0.2, 0.3);
        return (
          <g key={i}>
            {lab ? (
              <>
                <line x1={P4(lab[0] + (barca ? 1 : -1), lab[1])[0]} y1={P4(0, lab[1])[1]} x2={cx} y2={cy} stroke={MUTED} strokeWidth={1.2} opacity={la} />
                <Txt x={P4(lab[0], lab[1])[0]} y={P4(0, lab[1])[1] + 9} size={25} weight={600} anchor={barca ? "end" : "start"} opacity={la}>
                  {s.label}
                </Txt>
              </>
            ) : null}
            <circle cx={cx} cy={cy} r={rad(s.xg) * pop} fill={col} fillOpacity={s.goal ? 1 : 0.22}
              stroke={s.goal ? TEXT : col} strokeWidth={s.goal ? 2.5 : 1.8} opacity={a} />
          </g>
        );
      })}
      <Credit />
    </Stage>
  );
};

// ======================================================================= C5
// L50 to L51 (3:42). The ball reaches the net at the end of L50 ('One-nil').
// 'RECONSTRUCTION' and the StatsBomb credit stay on screen for the whole clip.
type Seg = { kind: string; player: string; from: number[]; to: number[]; to_player?: string };
const SEGS = data.rakitic.segments as Seg[];
const FREEZE = data.rakitic.freeze as { name: string; loc: number[]; teammate: boolean }[];
const S5 = 14;
const P5: Mapper = (x, y) => [110 + y * S5, 230 + (120 - x) * S5];

const TIMES: [number, number][] = (() => {
  let tt = 0.35;
  return SEGS.map((sg) => {
    let d = sg.kind === "carry" ? 0.32 : sg.kind === "pass" ? 0.42 : 0.3;
    if (sg.kind === "pass" && Math.hypot(sg.to[0] - sg.from[0], sg.to[1] - sg.from[1]) > 25) d = 0.7;
    const r: [number, number] = [tt, tt + d];
    tt += d;
    return r;
  });
})();
const T_GOAL = TIMES[TIMES.length - 1][1];
const T_FREEZE = T_GOAL + 0.35;

const BUILD_OFF: Record<string, [number, number, "start" | "end"]> = {
  Messi: [19, 8, "start"], "Jordi Alba": [-19, -6, "end"], Neymar: [17, 27, "start"],
  Iniesta: [-17, -17, "end"], "Rakitić": [19, -8, "start"],
};
const FREEZE_OFF: Record<string, [number, number, "start" | "end"]> = {
  Iniesta: [-19, -6, "end"], Buffon: [-19, 7, "end"], "Suárez": [19, 8, "start"],
  "Jordi Alba": [19, 8, "start"], Messi: [19, 6, "start"],
};

const ballAt = (t: number): number[] => {
  for (let i = 0; i < SEGS.length; i++) {
    const [t0, t1] = TIMES[i];
    if (t >= t0 && t < t1) {
      const f = SEGS[i].kind === "shot" ? lin(t, t0, t1 - t0) : ev(t, t0, t1 - t0);
      return [SEGS[i].from[0] + (SEGS[i].to[0] - SEGS[i].from[0]) * f, SEGS[i].from[1] + (SEGS[i].to[1] - SEGS[i].from[1]) * f];
    }
  }
  return t < TIMES[0][0] ? SEGS[0].from : SEGS[SEGS.length - 1].to;
};

export const C5: React.FC = () => {
  const t = useT();
  const pre = 1 - ev(t, T_FREEZE, 0.4);
  const fa = ev(t, T_FREEZE, 0.5);
  const seen: Record<string, [number[], number]> = {};
  SEGS.forEach((sg, i) => {
    if (t >= TIMES[i][0] && !seen[sg.player]) seen[sg.player] = [sg.from, TIMES[i][0]];
  });
  const ball = ballAt(t);
  const trail = [0.04, 0.08, 0.12].map((d) => ballAt(Math.max(0, t - d)));
  const ga = ev(t, T_GOAL, 0.3);
  return (
    <Stage>
      <Title title="Rakitić, 4 minutes: Barcelona lead 1-0" subtitle="Champions League final 2015 · Juventus v Barcelona" />
      <Box x={1480} y={47} w={360} h={58} r={10} fill={PANEL} stroke={TEXT} sw={2} />
      <Txt x={1660} y={88} size={33} weight={700} anchor="middle">RECONSTRUCTION</Txt>
      <PitchLines P={P5} full={false} s={S5} />

      {/* ball path so far */}
      {SEGS.map((sg, i) => {
        const [t0, t1] = TIMES[i];
        if (t < t0) return null;
        const f = sg.kind === "shot" ? lin(t, t0, t1 - t0) : ev(t, t0, t1 - t0); // same easing as the ball
        const [x1, y1] = P5(sg.from[0], sg.from[1]);
        const [x2, y2] = P5(sg.from[0] + (sg.to[0] - sg.from[0]) * f, sg.from[1] + (sg.to[1] - sg.from[1]) * f);
        const style = sg.kind === "carry"
          ? { stroke: TEXT, strokeWidth: 2, strokeDasharray: "5 5", opacity: 0.7 }
          : sg.kind === "pass"
            ? { stroke: TEXT, strokeWidth: 2.5, opacity: 0.75 }
            : { stroke: BARCA, strokeWidth: 4.5, opacity: 0.95 };
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} strokeLinecap="round" {...style} />;
      })}

      {/* players on the ball during the move */}
      {Object.entries(seen).map(([name, [loc, t0]]) => {
        const a = ev(t, t0 - 0.1, 0.25) * (name === "Rakitić" ? 1 : pre);
        if (a <= 0.001) return null;
        const [x, y] = P5(loc[0], loc[1]);
        const [dx, dy, anchor] = BUILD_OFF[name] ?? [19, -8, "start"];
        return (
          <g key={name} opacity={a}>
            <circle cx={x} cy={y} r={14} fill={BARCA} stroke={TEXT} strokeWidth={1.5} />
            <Txt x={x + dx} y={y + dy} size={24} weight={600} anchor={anchor}>{name}</Txt>
          </g>
        );
      })}

      {/* positions at the moment of the shot (StatsBomb freeze frame) */}
      {fa > 0
        ? FREEZE.map((p, i) => {
          const [x, y] = P5(p.loc[0], p.loc[1]);
          const off = FREEZE_OFF[p.name];
          return (
            <g key={i} opacity={fa}>
              <circle cx={x} cy={y} r={12} fill={p.teammate ? BARCA : OPP} stroke={BG} strokeWidth={1.5} />
              {off ? (
                <Txt x={x + off[0]} y={y + off[1]} size={21} color={p.name === "Buffon" ? OPP : MUTED} anchor={off[2]}>{p.name}</Txt>
              ) : null}
            </g>
          );
        })
        : null}

      {/* ball with a short trail */}
      {trail.map((b, i) => {
        const [x, y] = P5(b[0], b[1]);
        return <circle key={i} cx={x} cy={y} r={6 - i * 1.3} fill={TEXT} opacity={0.35 - i * 0.1} />;
      })}
      <circle cx={P5(ball[0], ball[1])[0]} cy={P5(ball[0], ball[1])[1]} r={7} fill={TEXT} stroke={BG} strokeWidth={1.5} />

      {/* the move, listed */}
      <Txt x={1300} y={220} size={33} weight={700}>The move</Txt>
      {SEGS.filter((sg) => sg.kind !== "carry").map((sg, j) => {
        const i = SEGS.indexOf(sg);
        const a = ev(t, TIMES[i][0], 0.3);
        return (
          <Txt key={j} x={1300} y={290 + j * 56} size={31} opacity={a}>
            {sg.kind === "pass" ? (
              <>
                <Tok weight={600}>{sg.player}</Tok>
                <Tok color={MUTED}>{"  to  "}</Tok>
                <Tok weight={600}>{sg.to_player}</Tok>
              </>
            ) : (
              <>
                <Tok weight={600}>Rakitić</Tok>
                <Tok color={MUTED}>{"  scores, 4'"}</Tok>
              </>
            )}
          </Txt>
        );
      })}
      <g style={{ scale: String(1 + 0.4 * pulse(t, T_GOAL, 0.45)), transformBox: "fill-box", transformOrigin: "0% 100%" }}>
        <Txt x={1300} y={600} size={67} weight={700} opacity={ga}>
          <Tok>1-0</Tok>
          <Tok color={MUTED} weight={400}>{"  Barcelona"}</Tok>
        </Txt>
      </g>
      <Txt x={1300} y={930} size={21} color={MUTED}>Ball path from StatsBomb event data.</Txt>
      <Txt x={1300} y={956} size={21} color={MUTED}>Player positions at the moment of the shot</Txt>
      <Txt x={1300} y={982} size={21} color={MUTED}>from the StatsBomb freeze frame.</Txt>
      <Credit />
    </Stage>
  );
};
