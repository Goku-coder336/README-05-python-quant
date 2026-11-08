// C1a (Messi paradox) and C1b (scorer split). Verified run in CLAUDE.md only.
// Times are seconds from the start of the script line the clip sits on.
import React from "react";
import { ev, lin, mix, pulse } from "../anim";
import { Box, Stage, Title, Tok, Txt, useT } from "../components/ui";
import {
  GROUP_MESSI, GROUP_TOTAL, KO_AFTER_QF, KO_MESSI, KO_TOTAL, SPLIT,
} from "../data/run";
import { FAINT, GOAL_BLOCK, MESSI, MUTED, PLAYER_COL, TEXT } from "../theme";

// ------------------------------------------------------------------ C1a
// L01 to L05 (0:00). Group bar on L01 ('Eight'), knockout bar on L02 ('two of them'),
// slow zoom from L03, Messi blocks dim on 'supplier' (L04).
const ROWS = [
  { label: "Group stage", sub: "15 Barcelona goals", top: 486, total: GROUP_TOTAL, messi: GROUP_MESSI, tb: 0.3, tg: 1.2, tn: 4.2 },
  { label: "Knockouts", sub: "16 Barcelona goals", top: 756, total: KO_TOTAL, messi: KO_MESSI, tb: 7.8, tg: 10.2, tn: 11.0 },
];
const T_DIM = 21.0;

export const C1a: React.FC = () => {
  const t = useT();
  const zoom = 1 + 0.04 * ev(t, 12, 15);
  const dim = 1 - 0.5 * ev(t, T_DIM, 0.8);
  const BS = 54;
  const GAP = 10;
  const X0 = 400;
  return (
    <Stage zoom={zoom}>
      <Title title="Who scored Barcelona's goals?" subtitle="Champions League 2014/15 · one block = one goal" opacity={ev(t, 0, 0.6)} />
      <g opacity={ev(t, 0.2, 0.6)}>
        <Box x={80} y={204} w={26} h={26} r={5} fill={MESSI} />
        <Txt x={118} y={226} size={26}>Messi</Txt>
        <Box x={230} y={204} w={26} h={26} r={5} fill={GOAL_BLOCK} />
        <Txt x={268} y={226} size={26}>Other Barcelona scorers</Txt>
      </g>
      {ROWS.map((r) => {
        const ra = ev(t, r.tb - 0.3, 0.5);
        const na = ev(t, r.tn, 0.45);
        return (
          <g key={r.label}>
            <Txt x={80} y={r.top + 4} size={42} weight={600} opacity={ra}>{r.label}</Txt>
            <Txt x={80} y={r.top + 42} size={25} color={MUTED} opacity={ra}>{r.sub}</Txt>
            {Array.from({ length: r.total }).map((_, i) => {
              const ba = ev(t, r.tb + i * 0.07, 0.4);
              if (ba <= 0) return null;
              const g = i < r.messi ? ev(t, r.tg + i * (r.messi > 2 ? 0.12 : 0.25), 0.35) : 0;
              const fill = i < r.messi ? mix(GOAL_BLOCK, MESSI, g) : GOAL_BLOCK;
              const op = ba * (g > 0 ? 1 - (1 - dim) * g : 1);
              const s = 1 + 0.18 * pulse(t, r.tg + i * (r.messi > 2 ? 0.12 : 0.25), 0.35) * (i < r.messi ? 1 : 0);
              return (
                <rect
                  key={i}
                  x={X0 + i * (BS + GAP)}
                  y={r.top + (1 - ba) * -16}
                  width={BS}
                  height={BS}
                  rx={8}
                  fill={fill}
                  opacity={op}
                  style={{ scale: String(s), transformBox: "fill-box", transformOrigin: "50% 50%" }}
                />
              );
            })}
            {na > 0 ? (
              <g style={{ scale: String(1 + 0.25 * (1 - na)), transformBox: "fill-box", transformOrigin: "100% 100%" }}>
                <Txt x={1840} y={r.top + 40} size={92} weight={700} anchor="end" opacity={na}>
                  <Tok color={MESSI}>{r.messi}</Tok>
                  <Tok>{` of ${r.total}`}</Tok>
                </Txt>
              </g>
            ) : null}
            <Txt x={1840} y={r.top + 84} size={25} color={MUTED} anchor="end" opacity={na}>scored by Messi</Txt>
          </g>
        );
      })}
    </Stage>
  );
};

// ------------------------------------------------------------------ C1b
// Part 1 (0 to 5 s): L38, knockout tally after two rounds.
// Part 2 (from 5 s): L67 to L74, group v knockouts for the three forwards.
const P1_OUT = 4.9;
const P2_IN = 5.25;

const Part1: React.FC<{ t: number; fade: number }> = ({ t, fade }) => {
  const BS = 72;
  const GAP = 12;
  const X0 = 640;
  const times = [2.0, 2.7, 3.4, 4.1]; // 'Suárez four. Neymar three. Rakitić one. Messi none.'
  return (
    <g opacity={fade}>
      <Title title="Knockout goals after two rounds" subtitle="Round of 16 and quarter-final" opacity={ev(t, 0, 0.5)} />
      <Txt x={1840} y={104} size={48} anchor="end" opacity={ev(t, 1.0, 0.5)}>
        <Tok weight={700}>8</Tok>
        <Tok color={MUTED}> goals</Tok>
      </Txt>
      {KO_AFTER_QF.map(([name, n], k) => {
        const top = 1080 - (700 - k * 140) - BS;
        const tr = times[k];
        const ra = ev(t, tr - 0.2, 0.4);
        const col = PLAYER_COL[name] ?? TEXT;
        return (
          <g key={name}>
            <Txt x={X0 - 40} y={top + 50} size={48} weight={600} anchor="end" opacity={ra}>{name}</Txt>
            {Array.from({ length: n }).map((_, i) => {
              const ba = ev(t, tr + i * 0.09, 0.4);
              return <Box key={i} x={X0 + i * (BS + GAP)} y={top - (1 - ba) * 14} w={BS} h={BS} r={9} fill={col} opacity={ba} />;
            })}
            {n === 0 ? <Box x={X0} y={top} w={BS} h={BS} r={9} stroke={FAINT} sw={2.5} opacity={ra} /> : null}
            <Txt x={X0 + Math.max(n, 1) * (BS + GAP) + 18} y={top + 56} size={62} weight={700} color={n ? col : MESSI} opacity={ra}>
              {n}
            </Txt>
          </g>
        );
      })}
    </g>
  );
};

const FOCUS: Record<string, [number, number]> = { Neymar: [10, 14], Suárez: [14, 17], Messi: [17, 21] };
const T_KO: Record<string, number> = { Neymar: 12.6, Suárez: 15.9, Messi: 19.4 };

const Part2: React.FC<{ t: number; fade: number }> = ({ t, fade }) => {
  const BS = 54;
  const GAP = 10;
  const XL = 960 - 150;
  const XR = 960 + 150;
  const active = Object.entries(FOCUS).find(([, [s, e]]) => t >= s && t < e)?.[0];
  return (
    <g opacity={fade}>
      <Title title="Same three forwards. The goals moved." subtitle="Champions League 2014/15 · one block = one goal" />
      <Txt x={560} y={280} size={36} weight={600} color={MUTED} anchor="middle">Group stage</Txt>
      <Txt x={1360} y={280} size={36} weight={600} color={MUTED} anchor="middle">Knockouts</Txt>
      {SPLIT.map(([name, g, ko], k) => {
        const top = 1080 - (620 - k * 150) - BS;
        let emph = active && active !== name ? 0.35 : 1;
        if (t >= 25.0 && t < 28.8 && name === "Messi") emph = 0.35; // L73 is about Neymar and Suárez
        const col = PLAYER_COL[name];
        const tg = 5.8 + k * 0.6;
        const tk = T_KO[name];
        return (
          <g key={name} opacity={emph}>
            <Txt x={960} y={top + 40} size={44} weight={600} anchor="middle" opacity={ev(t, 5.4, 0.4)}>{name}</Txt>
            {Array.from({ length: g }).map((_, i) => {
              const ba = ev(t, tg + i * 0.06, 0.4);
              return <Box key={`g${i}`} x={XL - (i + 1) * BS - i * GAP} y={top - (1 - ba) * 14} w={BS} h={BS} r={8} fill={col} opacity={ba} />;
            })}
            <Txt x={XL - g * (BS + GAP) - 14} y={top + 44} size={58} weight={700} anchor="end" opacity={ev(t, tg + g * 0.06, 0.3)}>{g}</Txt>
            {Array.from({ length: ko }).map((_, i) => {
              const ba = ev(t, tk + i * 0.08, 0.4);
              return <Box key={`k${i}`} x={XR + i * (BS + GAP)} y={top - (1 - ba) * 14} w={BS} h={BS} r={8} fill={col} opacity={ba} />;
            })}
            <Txt x={XR + ko * (BS + GAP) + 12} y={top + 44} size={58} weight={700} opacity={ev(t, tk + ko * 0.08, 0.3)}>{ko}</Txt>
          </g>
        );
      })}
      <Txt x={520} y={910} size={48} weight={700} anchor="middle" opacity={ev(t, 25.3, 0.5)}>
        <Tok color={PLAYER_COL.Neymar}>Neymar</Tok>
        <Tok> + </Tok>
        <Tok color={PLAYER_COL["Suárez"]}>Suárez</Tok>
        <Tok>: 12 of 16</Tok>
      </Txt>
      <Txt x={520} y={955} size={25} color={MUTED} anchor="middle" opacity={ev(t, 25.3, 0.5)}>knockout goals</Txt>
      <Txt x={1400} y={910} size={48} weight={700} anchor="middle" opacity={ev(t, 28.8, 0.5)}>
        <Tok color={MESSI}>Messi</Tok>
        <Tok>: top assister, 6</Tok>
      </Txt>
      <Txt x={1400} y={955} size={25} color={MUTED} anchor="middle" opacity={ev(t, 28.8, 0.5)}>assists in the competition</Txt>
    </g>
  );
};

export const C1b: React.FC = () => {
  const t = useT();
  return (
    <Stage>
      {t < P2_IN ? <Part1 t={t} fade={1 - lin(t, P1_OUT, 0.35)} /> : null}
      {t >= P2_IN ? <Part2 t={t} fade={ev(t, P2_IN, 0.5)} /> : null}
    </Stage>
  );
};

