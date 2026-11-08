import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { BG, CREDIT, FONT, H, MUTED, TEXT, W } from "../theme";

/** Current time in seconds. */
export const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};

/** Full-frame SVG stage in pixel coordinates (origin top left). */
export const Stage: React.FC<{ children: React.ReactNode; zoom?: number }> = ({ children, zoom = 1 }) => (
  <AbsoluteFill style={{ backgroundColor: BG }}>
    <svg
      width={W}
      height={H}
      viewBox={`0 0 ${W} ${H}`}
      style={{ fontFamily: FONT, scale: String(zoom), transformOrigin: "50% 50%" }}
    >
      {children}
    </svg>
  </AbsoluteFill>
);

type TxtProps = {
  x: number;
  y: number;
  size?: number;
  weight?: number;
  color?: string;
  anchor?: "start" | "middle" | "end";
  opacity?: number;
  dy?: number;
  children: React.ReactNode;
};

/** SVG text. Use <Tok> children for runs in different colours or weights. */
export const Txt: React.FC<TxtProps> = ({
  x, y, size = 28, weight = 400, color = TEXT, anchor = "start", opacity = 1, dy = 0, children,
}) =>
  opacity <= 0.001 ? null : (
    <text
      x={x}
      y={y + dy}
      fontSize={size}
      fontWeight={weight}
      fill={color}
      textAnchor={anchor}
      opacity={opacity}
    >
      {children}
    </text>
  );

export const Tok: React.FC<{ color?: string; weight?: number; children: React.ReactNode }> = ({
  color = TEXT, weight, children,
}) => (
  <tspan fill={color} fontWeight={weight} style={{ whiteSpace: "pre" }}>
    {children}
  </tspan>
);

/** Title block used by every clip (top left). */
export const Title: React.FC<{ title: string; subtitle?: string; opacity?: number }> = ({
  title, subtitle, opacity = 1,
}) => (
  <>
    <Txt x={80} y={92} size={42} weight={700} opacity={opacity}>{title}</Txt>
    {subtitle ? (
      <Txt x={80} y={136} size={26} color={MUTED} opacity={opacity}>{subtitle}</Txt>
    ) : null}
  </>
);

/** StatsBomb credit, bottom right. */
export const Credit: React.FC = () => (
  <Txt x={W - 48} y={H - 36} size={21} color={MUTED} anchor="end">{CREDIT}</Txt>
);

/** Rounded rectangle (x, y = top left). */
export const Box: React.FC<{
  x: number; y: number; w: number; h: number; r?: number; fill?: string; stroke?: string;
  sw?: number; opacity?: number;
}> = ({ x, y, w, h, r = 12, fill = "none", stroke = "none", sw = 0, opacity = 1 }) =>
  opacity <= 0.001 ? null : (
    <rect x={x} y={y} width={w} height={h} rx={r} fill={fill} stroke={stroke} strokeWidth={sw} opacity={opacity} />
  );
