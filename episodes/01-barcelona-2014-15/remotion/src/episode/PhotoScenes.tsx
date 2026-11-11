// Scenes built around photos. Times are seconds since the scene's sequence started.
import React from "react";
import { AbsoluteFill } from "remotion";
import { ev, pulse } from "../anim";
import { Tok, Txt, useT } from "../components/ui";
import { BARCA, MESSI, MUTED, NEYMAR, SUAREZ, TEXT } from "../theme";
import { PhotoBox, PhotoCard } from "./Photo";
import { PHOTOS, PhotoKey } from "./photos";

/** L03 to L05: Messi, slow push in; 'Finisher.' then 'Supplier.' land on the words. */
export const MessiPhotoScene: React.FC<{ finisherAt: number; supplierAt: number; dur: number }> = ({ finisherAt, supplierAt, dur }) => {
  const t = useT();
  const fa = ev(t, finisherAt, 0.4);
  const sa = ev(t, supplierAt, 0.4);
  return (
    <PhotoCard photo="messi_a" from={[0.214, 0.15, 0.62, 0]} to={[0.274, 0.23, 0.42, 0]} dur={dur} caption={PHOTOS.messi_a.caption}>
      <defs>
        <linearGradient id="rightShade" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="#1a1a19" stopOpacity="0" />
          <stop offset="0.35" stopColor="#1a1a19" stopOpacity="0.85" />
          <stop offset="1" stopColor="#1a1a19" stopOpacity="0.95" />
        </linearGradient>
      </defs>
      <rect x={900} y={0} width={1020} height={1080} fill="url(#rightShade)" opacity={fa} />
      <Txt x={1100} y={560} size={96} weight={700} color={TEXT} opacity={fa * (1 - 0.6 * sa)}>Finisher.</Txt>
      <g style={{ scale: String(1 + 0.15 * pulse(t, supplierAt, 0.5)), transformBox: "fill-box", transformOrigin: "0% 100%" }}>
        <Txt x={1100} y={690} size={96} weight={700} color={MESSI} opacity={sa}>Supplier.</Txt>
      </g>
    </PhotoCard>
  );
};

/** L10 to L11: the three forwards, each photo popping in on its name. */
const FORWARDS: [PhotoKey, string, string, [number, number, number, number]][] = [
  ["messi_a", "Messi", MESSI, [0.283, 0.24, 0.244, 0]],
  ["neymar_b", "Neymar", NEYMAR, [0.38, 0.05, 0.4875, 0]],
  ["suarez_super", "Suárez", SUAREZ, [0.44, 0.22, 0.443, 0]],
];
export const ForwardsScene: React.FC<{ at: [number, number, number] }> = ({ at }) => {
  const t = useT();
  const BW = 500;
  const BH = 620;
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a19" }}>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", fontFamily: "Inter" }}>
        <Txt x={80} y={120} size={52} weight={700} opacity={ev(t, 0, 0.5)}>Three forwards</Txt>
        <Txt x={80} y={170} size={30} color={MUTED} opacity={ev(t, 0.2, 0.5)}>Barcelona 2014/15</Txt>
      </svg>
      {FORWARDS.map(([key, name, col, crop], i) => {
        const a = ev(t, at[i], 0.45);
        const x = 160 + i * (BW + 80);
        const y = 240 + (1 - a) * 30;
        return (
          <div key={key} style={{ position: "absolute", left: x, top: y, width: BW, height: BH + 90, opacity: a }}>
            <div style={{ position: "absolute", inset: 0, height: BH, borderRadius: 18, overflow: "hidden", outline: `4px solid ${col}` }}>
              <PhotoBox photo={key} from={crop} to={[crop[0] + 0.01, crop[1], crop[2] * 0.94, 0]} dur={10} w={BW} h={BH} fadeIn={0.01} />
            </div>
            <svg width={BW} height={90} style={{ position: "absolute", top: BH + 6, left: 0, fontFamily: "Inter" }}>
              <circle cx={14} cy={52} r={11} fill={col} />
              <Txt x={36} y={66} size={48} weight={700}>{name}</Txt>
            </svg>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/** Picture-in-picture over a route chart: a framed photo with the player's name. */
export const PipPhoto: React.FC<{
  photo: PhotoKey; crop: [number, number, number, number]; name: string; color: string;
  x: number; y: number; w: number; h: number; outAt: number;
}> = ({ photo, crop, name, color, x, y, w, h, outAt }) => {
  const t = useT();
  const a = ev(t, 0, 0.4) * (1 - ev(t, outAt, 0.4));
  if (a <= 0.001) return null;
  return (
    <div style={{ position: "absolute", left: x, top: y + (1 - ev(t, 0, 0.4)) * 20, width: w, height: h + 64, opacity: a }}>
      <div style={{ position: "absolute", left: 0, top: 0, width: w, height: h, borderRadius: 16, overflow: "hidden", outline: `3px solid ${color}`, boxShadow: "0 10px 30px rgba(0,0,0,0.5)" }}>
        <PhotoBox photo={photo} from={crop} to={[crop[0] + 0.01, crop[1], crop[2] * 0.95, 0]} dur={6} w={w} h={h} fadeIn={0.01} />
      </div>
      <svg width={w} height={60} style={{ position: "absolute", top: h + 6, left: 0, fontFamily: "Inter" }}>
        <circle cx={12} cy={34} r={9} fill={color} />
        <Txt x={30} y={46} size={34} weight={700}>{name}</Txt>
      </svg>
    </div>
  );
};

/** L61 to L62: Iniesta beside the awards text (photo cropped to his face; it is from August 2015). */
export const AwardsPhotoCard: React.FC<{ xaviAt: number }> = ({ xaviAt }) => {
  const t = useT();
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a19" }}>
      <div style={{ position: "absolute", left: 1180, top: 140, width: 620, height: 760, borderRadius: 18, overflow: "hidden", opacity: ev(t, 0.1, 0.5) }}>
        <PhotoBox photo="iniesta" from={[0.17, 0.47, 0.65, 0]} to={[0.2, 0.47, 0.6, 0]} dur={8} w={620} h={760} fadeIn={0.01} />
      </div>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", fontFamily: "Inter" }}>
        <Txt x={1180} y={940} size={22} color={MUTED} opacity={ev(t, 0.3, 0.5)}>{PHOTOS.iniesta.caption}</Txt>
        <Txt x={160} y={440} size={44} color={MUTED} opacity={ev(t, 0.1, 0.5)}>Man of the Match</Txt>
        <Txt x={160} y={530} size={92} weight={700} opacity={ev(t, 0.2, 0.5)}>Andrés Iniesta</Txt>
        <rect x={164} y={570} width={300 * ev(t, 0.4, 0.8)} height={6} rx={3} fill={BARCA} />
        <Txt x={160} y={700} size={44} color={MUTED} opacity={ev(t, xaviAt, 0.5)}>Xavi</Txt>
        <Txt x={160} y={790} size={80} weight={700} opacity={ev(t, xaviAt + 0.1, 0.5)}>
          <Tok color={MESSI}>767th</Tok>
          <Tok> and final</Tok>
        </Txt>
        <Txt x={160} y={870} size={80} weight={700} opacity={ev(t, xaviAt + 0.1, 0.5)}>appearance</Txt>
      </svg>
    </AbsoluteFill>
  );
};
