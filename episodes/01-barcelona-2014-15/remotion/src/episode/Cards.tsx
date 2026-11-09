// Text cards and the two chart slots for the full episode. Times are seconds since the card's
// sequence started; Episode.tsx passes them in from the real voiceover timings.
// Facts only from CLAUDE.md (verified run, key findings) and the checked StatsBomb export.
import React from "react";
import { ev } from "../anim";
import { Box, Credit, Stage, Title, Tok, Txt, useT } from "../components/ui";
import data from "../data/final.json";
import { BARCA, FAINT, GOAL_BLOCK, MESSI, MUTED, NEYMAR, OPP, TEXT } from "../theme";

// ------------------------------------------------------------------ text cards
/** L06: series title. */
export const SeriesCard: React.FC = () => {
  const t = useT();
  return (
    <Stage>
      <Txt x={160} y={500} size={120} weight={700} opacity={ev(t, 0.1, 0.6)} dy={(1 - ev(t, 0.1, 0.6)) * 20}>
        Run of the Champions
      </Txt>
      <rect x={164} y={548} width={420 * ev(t, 0.5, 0.8)} height={6} rx={3} fill={BARCA} />
      <Txt x={164} y={640} size={60} weight={600} color={MUTED} opacity={ev(t, 0.9, 0.6)}>Barcelona 2014/15</Txt>
    </Stage>
  );
};

/** L07 to L09: Luis Enrique, then the quote on 'transitional year'. */
export const EnriqueCard: React.FC<{ quoteAt: number }> = ({ quoteAt }) => {
  const t = useT();
  return (
    <Stage>
      <Txt x={160} y={420} size={84} weight={700} opacity={ev(t, 0.1, 0.5)}>Luis Enrique.</Txt>
      <Txt x={160} y={520} size={84} weight={700} color={MUTED} opacity={ev(t, 0.9, 0.5)}>First season.</Txt>
      <g opacity={ev(t, quoteAt, 0.6)}>
        <rect x={160} y={600} width={8} height={120} rx={4} fill={BARCA} />
        <Txt x={200} y={690} size={88} weight={600} dy={(1 - ev(t, quoteAt, 0.6)) * 16}>“A transitional year”</Txt>
      </g>
    </Stage>
  );
};

/** L61 to L62: Iniesta, then Xavi. */
export const AwardsCard: React.FC<{ xaviAt: number }> = ({ xaviAt }) => {
  const t = useT();
  return (
    <Stage>
      <Txt x={160} y={440} size={44} color={MUTED} opacity={ev(t, 0.1, 0.5)}>Man of the Match</Txt>
      <Txt x={160} y={530} size={92} weight={700} opacity={ev(t, 0.2, 0.5)}>Andrés Iniesta</Txt>
      <Txt x={160} y={680} size={44} color={MUTED} opacity={ev(t, xaviAt, 0.5)}>Xavi</Txt>
      <Txt x={160} y={770} size={92} weight={700} opacity={ev(t, xaviAt + 0.1, 0.5)}>
        <Tok color={MESSI}>767th</Tok>
        <Tok> and final appearance</Tok>
      </Txt>
    </Stage>
  );
};

/** L75 to L77: the quote returns, then 2015 Barcelona, 2025 PSG, 2026 PSG. */
export const BookendCard: React.FC<{ quoteAt: number; y2015: number; y2025: number; y2026: number }> = ({
  quoteAt, y2015, y2025, y2026,
}) => {
  const t = useT();
  const items: [string, string, number][] = [["2015", "Barcelona", y2015], ["2025", "PSG", y2025], ["2026", "PSG", y2026]];
  return (
    <Stage>
      <g opacity={ev(t, quoteAt, 0.6)}>
        <rect x={160} y={300} width={8} height={120} rx={4} fill={BARCA} />
        <Txt x={200} y={390} size={88} weight={600}>“A transitional year”</Txt>
      </g>
      {items.map(([yr, club, at], i) => (
        <g key={yr} opacity={ev(t, at, 0.5)}>
          <Txt x={160 + i * 520} y={640} size={110} weight={700} color={i === 0 ? MESSI : TEXT}>{yr}</Txt>
          <Txt x={164 + i * 520} y={700} size={40} color={MUTED}>{club}</Txt>
        </g>
      ))}
      <Txt x={160} y={800} size={34} color={MUTED} opacity={ev(t, y2015, 0.5)}>Luis Enrique, Champions League winner</Txt>
    </Stage>
  );
};

/** L78 to L79 and the tail: next episode. Right half left clear for YouTube's end screen. */
export const EndCard: React.FC = () => {
  const t = useT();
  return (
    <Stage>
      <Txt x={160} y={440} size={44} color={MUTED} opacity={ev(t, 0.1, 0.5)}>Run of the Champions</Txt>
      <Txt x={160} y={560} size={110} weight={700} opacity={ev(t, 0.3, 0.6)}>Next: 2015/16</Txt>
      <rect x={164} y={604} width={300 * ev(t, 0.7, 0.8)} height={6} rx={3} fill={BARCA} />
    </Stage>
  );
};

/** Lower third over C4 (L58 to L59). Kept inside the bottom 220 px the clip leaves clear. */
export const LowerThird: React.FC<{ passesAt: number; pressuresAt: number }> = ({ passesAt, pressuresAt }) => {
  const t = useT();
  const tot = data.totals as Record<string, number>;
  return (
    <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", fontFamily: "Inter" }}>
      <g opacity={ev(t, passesAt, 0.4)}>
        <Box x={80} y={880} w={1240} h={150} r={14} fill="#242422" stroke="#3a3936" sw={1.5} />
        <Txt x={112} y={940} size={40} weight={600}>
          <Tok color={MUTED} weight={400}>Passes   </Tok>
          <Tok color={BARCA}>Barcelona</Tok><Tok>{` ${tot.Barcelona_passes}`}</Tok>
          <Tok color={MUTED} weight={400}>{"  v  "}</Tok>
          <Tok color={OPP}>Juventus</Tok><Tok>{` ${tot.Juventus_passes}`}</Tok>
        </Txt>
      </g>
      <g opacity={ev(t, pressuresAt, 0.4)}>
        <Txt x={112} y={1000} size={40} weight={600}>
          <Tok color={MUTED} weight={400}>Pressures   </Tok>
          <Tok color={OPP}>Juventus</Tok><Tok>{` ${tot.Juventus_pressures}`}</Tok>
          <Tok color={MUTED} weight={400}>{"  v  "}</Tok>
          <Tok color={BARCA}>Barcelona</Tok><Tok>{` ${tot.Barcelona_pressures}`}</Tok>
        </Txt>
      </g>
      <Txt x={1300} y={1000} size={26} color={MUTED} anchor="end" opacity={ev(t, passesAt, 0.4)}>according to StatsBomb</Txt>
    </svg>
  );
};

// ------------------------------------------------------------------ chart slot: L45 to L48
// Top assister and joint top scorers, 2014/15 Champions League (UEFA, as in CLAUDE.md).
export const ScorersChart: React.FC<{ assistAt: number; goalsAt: number }> = ({ assistAt, goalsAt }) => {
  const t = useT();
  const BS = 46;
  const GAP = 9;
  const scorers: [string, string][] = [["Messi", MESSI], ["Neymar", NEYMAR], ["Cristiano Ronaldo", OPP]];
  return (
    <Stage>
      <Title title="Messi in the 2014/15 Champions League" subtitle="Source: UEFA" opacity={ev(t, 0, 0.5)} />
      <Txt x={160} y={300} size={36} weight={600} color={MUTED} opacity={ev(t, assistAt, 0.4)}>Top assister</Txt>
      {Array.from({ length: 6 }).map((_, i) => (
        <Box key={i} x={560 + i * (BS + GAP)} y={262 - (1 - ev(t, assistAt + 0.3 + i * 0.08, 0.4)) * 14} w={BS} h={BS} r={7}
          fill={MESSI} opacity={ev(t, assistAt + 0.3 + i * 0.08, 0.4)} />
      ))}
      <Txt x={560 + 6 * (BS + GAP) + 16} y={302} size={56} weight={700} opacity={ev(t, assistAt + 0.8, 0.4)}>
        <Tok>6</Tok><Tok color={MUTED} weight={400}>  Messi</Tok>
      </Txt>
      <Txt x={160} y={480} size={36} weight={600} color={MUTED} opacity={ev(t, goalsAt, 0.4)}>Joint top scorers</Txt>
      {scorers.map(([name, col], k) => {
        const y = 540 + k * 110;
        const at = goalsAt + 0.3 + k * 0.5;
        return (
          <g key={name} opacity={ev(t, at, 0.4)}>
            <Txt x={520} y={y + 36} size={40} weight={600} anchor="end">{name}</Txt>
            {Array.from({ length: 10 }).map((_, i) => (
              <Box key={i} x={560 + i * (BS + GAP)} y={y} w={BS} h={BS} r={7} fill={col} opacity={ev(t, at + i * 0.05, 0.3)} />
            ))}
            <Txt x={560 + 10 * (BS + GAP) + 16} y={y + 40} size={52} weight={700}>10</Txt>
          </g>
        );
      })}
    </Stage>
  );
};

// ------------------------------------------------------------------ chart slot: L60
// Messi in the final: every pass (StatsBomb), his event count (most of any Barcelona player).
type Pass = { from: number[]; to: number[]; complete: boolean };
const MP = data.messi.passes as Pass[];
const S = 8;
const PX = 80;
const PY = 240;
const P = (x: number, y: number): [number, number] => [PX + x * S, PY + y * S];

export const MessiFinalChart: React.FC<{ passesAt: number }> = ({ passesAt }) => {
  const t = useT();
  const shown = MP.filter((_, i) => t >= passesAt + i * 0.03).length;
  const done = MP.filter((p, i) => p.complete && t >= passesAt + i * 0.03).length;
  return (
    <Stage>
      <Title title="Messi in the final" subtitle="According to StatsBomb · every pass he made" />
      {/* pitch outline, halfway line, boxes (Barcelona attack right) */}
      <rect x={PX} y={PY} width={120 * S} height={80 * S} fill="none" stroke={FAINT} strokeWidth={2} />
      <line x1={PX + 60 * S} x2={PX + 60 * S} y1={PY} y2={PY + 80 * S} stroke={FAINT} strokeWidth={2} />
      <circle cx={PX + 60 * S} cy={PY + 40 * S} r={10 * S} fill="none" stroke={FAINT} strokeWidth={2} />
      <rect x={PX} y={PY + 18 * S} width={18 * S} height={44 * S} fill="none" stroke={FAINT} strokeWidth={2} />
      <rect x={PX + 102 * S} y={PY + 18 * S} width={18 * S} height={44 * S} fill="none" stroke={FAINT} strokeWidth={2} />
      {MP.map((p, i) => {
        const a = ev(t, passesAt + i * 0.03, 0.3);
        if (a <= 0) return null;
        const [x1, y1] = P(p.from[0], p.from[1]);
        const [x2, y2] = P(p.to[0], p.to[1]);
        return (
          <g key={i} opacity={a}>
            <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * a} y2={y1 + (y2 - y1) * a}
              stroke={p.complete ? MESSI : GOAL_BLOCK} strokeWidth={p.complete ? 2.5 : 2} strokeLinecap="round" />
            <circle cx={x2} cy={y2} r={4} fill={p.complete ? MESSI : GOAL_BLOCK} opacity={a} />
          </g>
        );
      })}
      <Txt x={PX + 90 * S} y={PY - 18} size={22} color={MUTED} anchor="middle">{"Barcelona attack   →"}</Txt>
      <Txt x={1160} y={380} size={120} weight={700} opacity={ev(t, 0.2, 0.5)}>{data.messi.events}</Txt>
      <Txt x={1160} y={430} size={30} color={MUTED} opacity={ev(t, 0.2, 0.5)}>actions recorded by StatsBomb,</Txt>
      <Txt x={1160} y={470} size={30} color={MUTED} opacity={ev(t, 0.2, 0.5)}>the most of any Barcelona player</Txt>
      <Txt x={1160} y={640} size={120} weight={700} color={MESSI} opacity={ev(t, passesAt, 0.4)}>{shown}</Txt>
      <Txt x={1160} y={690} size={30} color={MUTED} opacity={ev(t, passesAt, 0.4)}>passes</Txt>
      <g opacity={ev(t, passesAt, 0.4)}>
        <rect x={1160} y={778} width={36} height={4} rx={2} fill={MESSI} />
        <Txt x={1210} y={790} size={28} color={MUTED}>{`completed (${done})`}</Txt>
        <rect x={1160} y={822} width={36} height={4} rx={2} fill={GOAL_BLOCK} />
        <Txt x={1210} y={834} size={28} color={MUTED}>{`not completed (${shown - done})`}</Txt>
      </g>
      <Credit />
    </Stage>
  );
};
