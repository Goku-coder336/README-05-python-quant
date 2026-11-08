// C2 route chart family: C2 (intro), C2a (group), C2b (R16), C2c (QF), C2d (SF),
// C2e (final node), C2f (full run with totals). Verified run in CLAUDE.md only.
// Times are seconds from the start of the script line the clip sits on.
import { measureText } from "@remotion/layout-utils";
import React from "react";
import { ev, pulse } from "../anim";
import { Box, Stage, Title, Tok, Txt, useT } from "../components/ui";
import { AGG, GROUP_KEYS, HOME, LOSSES, MATCHES, Match } from "../data/run";
import { BARCA, BG, FAINT, FONT, LINE, MESSI, MUTED, NEYMAR, OPP, PANEL, PLAYER_COL, SUAREZ, TEXT } from "../theme";

const PAST = -10;
const COLX = [256, 608, 960, 1312, 1664];
const NODE_Y = 210;
const NODE_LABELS = ["Group F", "Round of 16", "Quarter-final", "Semi-final", "Final"];
const CW = 344;
const CH = 92;
const GAP = 10;
const TOP = 260;

const cardXY = (m: Match) => ({ x: COLX[m.col] - CW / 2, top: TOP + m.slot * (CH + GAP) });
const byKey = (k: string) => MATCHES.find((m) => m.key === k)!;
const width = (text: string, size: number, weight: number) =>
  measureText({ text, fontFamily: FONT, fontSize: size, fontWeight: String(weight) }).width;

export type RouteCfg = {
  titleT?: number;
  routeT?: number[]; // when each node appears
  tagsT?: number[]; // Messi, Neymar, Suárez name tags
  nodes?: Record<number, [number, number | null]>; // node -> [current from, done from]
  cards?: Record<string, [number, number]>; // key -> [card in, scorers in]
  tableT?: [number, number];
  agg?: Record<number, number>;
  messi?: [number, number][]; // [time, value] for the Messi knockout counter
  arcT?: number; // QF to MD2 link
  finalInfo?: [number, number, number, number];
  totals?: number[];
  homeT?: number;
  lossT?: number;
  hl?: [string, string, number, number][]; // card, scorer, from, until
};

// ------------------------------------------------------------------ pieces
const Card: React.FC<{
  m: Match; t: number; tc: number; ts: number; dim: number;
  outline?: [string, number]; hl: Record<string, number>;
}> = ({ m, t, tc, ts, dim, outline, hl }) => {
  const a = ev(t, tc, 0.5) * dim;
  if (a <= 0.001) return null;
  const { x, top: top0 } = cardXY(m);
  const top = top0 + (1 - ev(t, tc, 0.5)) * 22;
  const sa = ev(t, ts, 0.4) * dim;
  const size = m.scorers.length < 3 ? 22 : 21;
  // scorer runs with their x positions (for highlight boxes)
  const runs: { text: string; color: string; weight: number; owner?: string }[] = [];
  m.scorers.forEach(([name, n], i) => {
    if (i) runs.push({ text: ", ", color: MUTED, weight: 400 });
    runs.push({ text: name, color: PLAYER_COL[name] ?? TEXT, weight: 600, owner: name });
    if (n > 1) runs.push({ text: ` (${n})`, color: TEXT, weight: 400, owner: name });
  });
  let cx = x + 16;
  const spans: Record<string, [number, number]> = {};
  runs.forEach((r) => {
    const w = width(r.text, size, r.weight);
    if (r.owner) {
      const s = spans[r.owner];
      spans[r.owner] = s ? [s[0], cx + w] : [cx, cx + w];
    }
    cx += w;
  });
  const chipW = 88;
  return (
    <g>
      <Box x={x} y={top} w={CW} h={CH} r={12} fill={PANEL} stroke={LINE} sw={1.5} opacity={a} />
      {outline && outline[1] > 0 ? (
        <Box x={x - 3} y={top - 3} w={CW + 6} h={CH + 6} r={14} stroke={outline[0]} sw={3.5} opacity={outline[1] * dim} />
      ) : null}
      <Txt x={x + 16} y={top + 34} size={25} opacity={a}>
        <Tok color={MUTED}>{m.label}</Tok>
        <Tok>{"   "}</Tok>
        <Tok weight={600}>{m.opp}</Tok>
      </Txt>
      <Txt x={x + CW - 16} y={top + 74} size={22} color={MUTED} anchor="end" opacity={a}>{m.venue}</Txt>
      <Box x={x + CW - 14 - chipW} y={top + 14} w={chipW} h={34} r={8} fill={m.res === "W" ? BARCA : OPP} opacity={a} />
      <Txt x={x + CW - 14 - chipW / 2} y={top + 39} size={25} weight={700} anchor="middle" color={m.res === "W" ? TEXT : BG} opacity={a}>
        {`${m.res} ${m.score}`}
      </Txt>
      {Object.entries(hl).map(([name, h]) => {
        const sp = spans[name];
        if (!sp || h <= 0) return null;
        const col = PLAYER_COL[name] ?? TEXT;
        return (
          <g key={name}>
            <Box x={sp[0] - 7} y={top + 52} w={sp[1] - sp[0] + 14} h={33} r={8} fill={col} opacity={0.22 * h * dim} />
            <Box x={sp[0] - 7} y={top + 52} w={sp[1] - sp[0] + 14} h={33} r={8} stroke={col} sw={2.5} opacity={h * dim} />
          </g>
        );
      })}
      <Txt x={x + 16} y={top + 75} size={size} opacity={sa}>
        {runs.map((r, i) => (
          <Tok key={i} color={r.color} weight={r.weight}>{r.text}</Tok>
        ))}
      </Txt>
    </g>
  );
};

const Tags: React.FC<{ t: number; tagsT: number[] }> = ({ t, tagsT }) => {
  const tags: [string, string, number][] = [
    ["Messi", MESSI, tagsT[0]], ["Neymar", NEYMAR, tagsT[1]], ["Suárez", SUAREZ, tagsT[2]],
  ];
  // laid out right to left from x = 1840
  let xr = 1840;
  const placed = [...tags].reverse().map(([name, col, tt]) => {
    const w = width(name, 29, 600) + 58;
    const x = xr - w;
    xr = x - 14;
    return { name, col, tt, x, w };
  });
  return (
    <>
      {placed.map(({ name, col, tt, x, w }) => {
        const a = ev(t, tt, 0.35);
        const p = pulse(t, tt, 0.5);
        return (
          <g key={name} opacity={a}>
            <Box x={x} y={49} w={w} h={46} r={23} fill={PANEL} stroke={p > 0.01 ? col : LINE} sw={2} />
            <circle cx={x + 24} cy={72} r={9 * (1 + 0.35 * p)} fill={col} />
            <Txt x={x + 42} y={82} size={29} weight={600}>{name}</Txt>
          </g>
        );
      })}
    </>
  );
};

// ------------------------------------------------------------------ the chart
export const Route: React.FC<{ cfg: RouteCfg }> = ({ cfg }) => {
  const t = useT();
  const nodeT = cfg.routeT ?? [PAST, PAST, PAST, PAST, PAST];
  const homeA = ev(t, cfg.homeT ?? 1e9, 0.6);
  const lossA = ev(t, cfg.lossT ?? 1e9, 0.6);

  // Messi counter value
  let mval = 0;
  let mlast = PAST;
  (cfg.messi ?? []).forEach(([tv, v]) => {
    if (t >= tv) {
      mval = v;
      mlast = tv;
    }
  });

  // QF -> MD2 arc
  const md2 = cardXY(byKey("MD2"));
  const p0 = [COLX[2] - 40, 520];
  const p1 = [700, 750];
  const p2 = [md2.x + CW + 10, md2.top + CH / 2];
  const arcP = cfg.arcT !== undefined ? ev(t, cfg.arcT, 0.8) : 0;
  const arcPath = `M ${p0[0]} ${p0[1]} Q ${p1[0]} ${p1[1]} ${p2[0]} ${p2[1]}`;

  return (
    <Stage>
      <Title title="Barcelona 2014/15" subtitle="Champions League route · Barcelona score first" opacity={ev(t, cfg.titleT ?? PAST, 0.6)} />
      <Tags t={t} tagsT={cfg.tagsT ?? [PAST, PAST, PAST]} />

      {/* route line and nodes */}
      {[0, 1, 2, 3].map((i) => {
        const p = ev(t, nodeT[i] + 0.1, 0.4);
        const x0 = COLX[i] + 16;
        const x1 = COLX[i + 1] - 16;
        return p > 0 ? <line key={i} x1={x0} y1={NODE_Y} x2={x0 + (x1 - x0) * p} y2={NODE_Y} stroke={FAINT} strokeWidth={3} strokeLinecap="round" /> : null;
      })}
      {[0, 1, 2, 3, 4].map((i) => {
        const a = ev(t, nodeT[i], 0.35);
        if (a <= 0) return null;
        const [tCur, tDone] = cfg.nodes?.[i] ?? [null, null];
        const cur = tCur !== null && t >= tCur && (tDone === null || t < tDone);
        const done = tDone !== null && t >= tDone;
        const k = cur ? ev(t, tCur!, 0.4) : 0;
        const breathe = cur ? 0.5 + 0.5 * Math.sin((t - tCur!) * 3) : 0;
        return (
          <g key={i} opacity={a}>
            {cur ? <circle cx={COLX[i]} cy={NODE_Y} r={20 + 6 * breathe} fill={BARCA} opacity={0.18 * k} /> : null}
            <circle cx={COLX[i]} cy={NODE_Y} r={13} fill={cur || done ? BARCA : BG} stroke={cur || done ? BARCA : FAINT} strokeWidth={3} opacity={done && !cur ? 0.85 : 1} />
            <Txt x={COLX[i]} y={175} size={29} weight={600} anchor="middle" color={cur || done ? TEXT : MUTED}>{NODE_LABELS[i]}</Txt>
          </g>
        );
      })}

      {/* cards */}
      {Object.entries(cfg.cards ?? {}).map(([key, [tc, ts]]) => {
        if (key === "F" && cfg.finalInfo) return null;
        const m = byKey(key);
        let dim = 1;
        let outline: [string, number] | undefined;
        if (homeA > 0) {
          if (HOME.includes(key)) outline = [BARCA, homeA];
          else if (LOSSES.includes(key) && lossA > 0) outline = [OPP, lossA];
          else dim = 1 - 0.55 * Math.max(homeA - (LOSSES.includes(key) ? lossA : 0), 0);
        }
        if (cfg.arcT !== undefined && key === "MD2") outline = [OPP, ev(t, cfg.arcT + 0.8, 0.4)];
        const hl: Record<string, number> = {};
        (cfg.hl ?? []).forEach(([hk, name, h0, h1]) => {
          if (hk === key) hl[name] = ev(t, h0, 0.35) * (1 - ev(t, h1, 0.5));
        });
        return <Card key={key} m={m} t={t} tc={tc} ts={ts} dim={dim} outline={outline} hl={hl} />;
      })}

      {/* group table */}
      {cfg.tableT ? (
        <>
          <Txt x={COLX[0] - CW / 2 + 16} y={898} size={26} opacity={ev(t, cfg.tableT[0], 0.4)}>
            <Tok color={MUTED}>{"1st   "}</Tok><Tok color={BARCA} weight={600}>Barcelona</Tok><Tok weight={600}>{"   15 pts"}</Tok>
          </Txt>
          <Txt x={COLX[0] - CW / 2 + 16} y={932} size={26} opacity={ev(t, cfg.tableT[1], 0.4)}>
            <Tok color={MUTED}>{"2nd   "}</Tok><Tok color={OPP} weight={600}>PSG</Tok><Tok weight={600}>{"   13 pts"}</Tok>
          </Txt>
        </>
      ) : null}

      {/* aggregates */}
      {Object.entries(cfg.agg ?? {}).map(([col, ta]) => (
        <Txt key={col} x={COLX[Number(col)]} y={492} size={32} weight={700} anchor="middle" opacity={ev(t, ta, 0.4)}>
          {AGG[Number(col)]}
        </Txt>
      ))}

      {/* QF to MD2 link */}
      {arcP > 0 ? (
        <g>
          <path d={arcPath} fill="none" stroke={OPP} strokeWidth={2.5} strokeDasharray="6 5" mask="url(#arcmask)" />
          <defs>
            <mask id="arcmask" maskUnits="userSpaceOnUse">
              <path d={arcPath} fill="none" stroke="white" strokeWidth={12} pathLength={1} strokeDasharray={`${arcP} 1`} />
            </mask>
          </defs>
          {arcP > 0.97 ? (
            <polygon
              points={arrowHead(p1, p2)}
              fill={OPP}
            />
          ) : null}
          <Txt x={720} y={655} size={25} color={MUTED} anchor="middle" opacity={ev(t, cfg.arcT! + 0.6, 0.5)}>
            Lost 2-3 to PSG in Paris, MD2
          </Txt>
        </g>
      ) : null}

      {/* Messi knockout counter */}
      {cfg.messi ? (
        <g opacity={ev(t, cfg.messi[0][0], 0.4)}>
          <Box x={1310} y={680} w={360} h={150} r={14} fill={PANEL} stroke={LINE} sw={1.5} />
          <Txt x={1334} y={720} size={26} color={MUTED}>Messi, knockout goals</Txt>
          <g style={{ scale: String(1 + (mlast !== cfg.messi[0][0] ? 0.4 * pulse(t, mlast, 0.5) : 0)), transformBox: "fill-box", transformOrigin: "0% 100%" }}>
            <Txt x={1334} y={804} size={84} weight={700} color={MESSI}>{mval}</Txt>
          </g>
        </g>
      ) : null}

      {/* final info card (C2e) */}
      {cfg.finalInfo ? (() => {
        const [t0, t1, t2, t3] = cfg.finalInfo;
        const a = ev(t, t0, 0.45);
        const x = COLX[4] - CW / 2;
        const top = TOP + (1 - a) * 18;
        return (
          <g>
            <Box x={x} y={top} w={CW} h={170} r={12} fill={PANEL} stroke={BARCA} sw={2} opacity={a} />
            <Txt x={x + 18} y={top + 36} size={24} color={MUTED} opacity={a}>Final</Txt>
            <Txt x={x + 18} y={top + 74} size={31} weight={600} opacity={ev(t, t1, 0.4)}>6 June 2015</Txt>
            <Txt x={x + 18} y={top + 110} size={26} opacity={ev(t, t2, 0.4)}>Olympiastadion, Berlin</Txt>
            <Txt x={x + 18} y={top + 148} size={28} opacity={ev(t, t3, 0.4)}>
              <Tok color={OPP} weight={600}>Juventus</Tok><Tok color={MUTED}> v </Tok><Tok color={BARCA} weight={600}>Barcelona</Tok>
            </Txt>
          </g>
        );
      })() : null}

      {/* totals (C2f) */}
      {cfg.totals ? (
        <>
          {[["13", "played"], ["11", "won"], ["2", "lost"], ["31", "scored"], ["11", "conceded"]].map(([num, lab], i) => {
            const a = ev(t, cfg.totals![i], 0.45);
            const x = 600 + i * 260;
            const rise = (1 - a) * 16;
            return (
              <g key={lab} opacity={a}>
                <Txt x={x} y={780 + rise} size={86} weight={700} anchor="middle">{num}</Txt>
                <Txt x={x} y={822 + rise} size={28} color={MUTED} anchor="middle">{lab}</Txt>
              </g>
            );
          })}
          <Txt x={860} y={920} size={30} anchor="middle" opacity={homeA}>
            <Tok color={MUTED}>Home games: </Tok><Tok weight={600}>won 6 of 6</Tok>
          </Txt>
          <Txt x={1460} y={920} size={30} anchor="middle" opacity={lossA}>
            <Tok color={MUTED}>Both defeats: </Tok><Tok weight={600}>away, 2-3 and 2-3</Tok>
          </Txt>
        </>
      ) : null}
    </Stage>
  );
};

function arrowHead(ctrl: number[], tip: number[]) {
  const dx = tip[0] - ctrl[0];
  const dy = tip[1] - ctrl[1];
  const n = Math.hypot(dx, dy);
  const d = [dx / n, dy / n];
  const nr = [-d[1], d[0]];
  const b = [tip[0] - 18 * d[0], tip[1] - 18 * d[1]];
  return [tip, [b[0] + 9 * nr[0], b[1] + 9 * nr[1]], [b[0] - 9 * nr[0], b[1] - 9 * nr[1]]]
    .map((p) => p.join(","))
    .join(" ");
}

// ------------------------------------------------------------------ clip configs
const allPast = (keys: string[]) => Object.fromEntries(keys.map((k) => [k, [PAST, PAST] as [number, number]]));

// L10 to L13 (0:43): route draws in, then 'Messi. Neymar. Luis Suárez.'
export const CFG_C2: RouteCfg = { titleT: 0, routeT: [0.3, 0.6, 0.9, 1.2, 1.5], tagsT: [2.0, 2.7, 3.5] };

// L14 to L22 (1:02): a card on each line, scorers on the scorer mention, table on L22.
export const CFG_C2A: RouteCfg = {
  nodes: { 0: [0.3, 38] },
  cards: { MD1: [3.3, 8.0], MD2: [10.3, 13.0], MD3: [19.3, 21.0], MD4: [22.3, 24.0], MD5: [25.3, 26.8], MD6: [29.3, 31.5] },
  tableT: [35.0, 37.3],
};

// L27 to L32 (1:58)
export const CFG_C2B: RouteCfg = {
  nodes: { 0: [PAST, PAST], 1: [0.3, 26] },
  cards: { ...allPast(GROUP_KEYS), R1: [3.3, 6.4], R2: [15.3, 17.6] },
  tableT: [PAST, PAST], agg: { 1: 20.3 }, messi: [[21.2, 0]],
};

// L33 to L37 (2:25)
export const CFG_C2C: RouteCfg = {
  nodes: { 0: [PAST, PAST], 1: [PAST, PAST], 2: [0.3, 20] },
  cards: { ...allPast([...GROUP_KEYS, "R1", "R2"]), Q1: [4.3, 6.2], Q2: [9.0, 10.3] },
  tableT: [PAST, PAST], agg: { 1: PAST, 2: 11.2 }, messi: [[PAST, 0]], arcT: 13.3,
};

// L39 to L44 (2:50)
export const CFG_C2D: RouteCfg = {
  nodes: { 0: [PAST, PAST], 1: [PAST, PAST], 2: [PAST, PAST], 3: [0.3, 25] },
  cards: { ...allPast([...GROUP_KEYS, "R1", "R2", "Q1", "Q2"]), S1: [2.3, 3.6], S2: [9.3, 10.8] },
  tableT: [PAST, PAST], agg: { 1: PAST, 2: PAST, 3: 17.3 }, messi: [[PAST, 0], [4.4, 2]],
  hl: [["S1", "Neymar", 12.4, 16.5], ["S2", "Neymar", 12.4, 16.5], ["S1", "Messi", 20.4, 99]],
};

// L49 (3:36): 'The final. The sixth of June, twenty fifteen. The Olympiastadion in Berlin. Juventus against Barcelona.'
export const CFG_C2E: RouteCfg = {
  nodes: { 0: [PAST, PAST], 1: [PAST, PAST], 2: [PAST, PAST], 3: [PAST, PAST], 4: [0.3, null] },
  cards: allPast([...GROUP_KEYS, "R1", "R2", "Q1", "Q2", "S1", "S2"]),
  tableT: [PAST, PAST], agg: { 1: PAST, 2: PAST, 3: PAST }, messi: [[PAST, 2]], finalInfo: [0.4, 1.4, 2.9, 4.4],
};

// L63 to L66 (4:48): totals on L64, home games on L66, the two defeats on 'Three-two in Paris'.
export const CFG_C2F: RouteCfg = {
  nodes: { 0: [PAST, PAST], 1: [PAST, PAST], 2: [PAST, PAST], 3: [PAST, PAST], 4: [PAST, PAST] },
  cards: allPast(MATCHES.map((m) => m.key)),
  tableT: [PAST, PAST], agg: { 1: PAST, 2: PAST, 3: PAST }, totals: [3.0, 4.0, 5.0, 7.0, 8.2], homeT: 14.3, lossT: 19.0,
};

