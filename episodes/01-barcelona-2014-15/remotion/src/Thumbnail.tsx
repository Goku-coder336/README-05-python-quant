// YouTube thumbnail (1280x720). Text chosen in Step 6: "8 GOALS. THEN 2."
import React from "react";
import { AbsoluteFill } from "remotion";
import { BG, FONT, GOAL_BLOCK, MESSI, MUTED, TEXT } from "./theme";

const Blocks: React.FC<{ total: number; messi: number; y: number }> = ({ total, messi, y }) => (
  <>
    {Array.from({ length: total }).map((_, i) => (
      <rect key={i} x={70 + i * 46} y={y} width={38} height={38} rx={6} fill={i < messi ? MESSI : GOAL_BLOCK} />
    ))}
  </>
);

export const Thumbnail: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: BG }}>
    <svg width={1280} height={720} viewBox="0 0 1280 720" style={{ fontFamily: FONT }}>
      <text x={70} y={86} fontSize={30} fontWeight={600} fill={MUTED} letterSpacing={3}>RUN OF THE CHAMPIONS</text>
      <text x={64} y={290} fontSize={196} fontWeight={700} fill={TEXT} letterSpacing={-4}>
        <tspan fill={MESSI}>8</tspan> GOALS.
      </text>
      <text x={64} y={480} fontSize={196} fontWeight={700} fill={TEXT} letterSpacing={-4}>
        THEN <tspan fill={MESSI}>2</tspan>.
      </text>
      <Blocks total={15} messi={8} y={548} />
      <Blocks total={16} messi={2} y={600} />
      <text x={1210} y={680} fontSize={32} fontWeight={600} fill={TEXT} textAnchor="end">
        Messi · Barcelona 2014/15
      </text>
    </svg>
  </AbsoluteFill>
);
