// Photos from Wikimedia Commons (free licences), with an on-screen credit on every photo.
// Credits and licences: ../../public/photos/CREDITS.md (and photos.ts).
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { ev } from "../anim";
import { Txt, useT } from "../components/ui";
import { PHOTOS, PhotoKey } from "./photos";
import { MUTED, TEXT } from "../theme";

type Rect = [number, number, number, number]; // x, y, w, h as fractions of the photo

/** Place the photo so that `r` (a fraction rect) fills a box of size bw x bh. */
const placement = (key: PhotoKey, r: Rect, bw: number, bh: number) => {
  const p = PHOTOS[key];
  const cw = r[2] * p.w;
  const scale = bw / cw;
  return { width: p.w * scale, height: p.h * scale, left: -r[0] * p.w * scale, top: -r[1] * p.h * scale, bh };
};

const lerpRect = (a: Rect, b: Rect, f: number): Rect => [0, 1, 2, 3].map((i) => a[i] + (b[i] - a[i]) * f) as Rect;

/** The credit line for a photo: photographer, licence, Wikimedia Commons. */
export const creditText = (key: PhotoKey) => `Photo: ${PHOTOS[key].author}, ${PHOTOS[key].licence}, Wikimedia Commons`;

/**
 * A photo in a box, slowly moving from crop `from` to crop `to` over `dur` seconds (Ken Burns).
 * Crops must have the box's aspect ratio (fraction width * photo width / box width ...).
 */
export const PhotoBox: React.FC<{
  photo: PhotoKey; from: Rect; to?: Rect; dur?: number; x?: number; y?: number; w?: number; h?: number;
  fadeIn?: number; radius?: number; dim?: number; credit?: boolean;
}> = ({ photo, from, to, dur = 8, x = 0, y = 0, w = 1920, h = 1080, fadeIn = 0.4, radius = 0, dim = 0, credit = true }) => {
  const t = useT();
  const f = Math.min(1, Math.max(0, t / dur));
  const r = lerpRect(from, to ?? from, f);
  // keep the crop's aspect ratio matched to the box
  const p = PHOTOS[photo];
  const rh = (r[2] * p.w * (h / w)) / p.h;
  const pl = placement(photo, [r[0], r[1], r[2], rh], w, h);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, overflow: "hidden", borderRadius: radius, opacity: ev(t, 0, fadeIn) }}>
      <Img src={staticFile(`photos/${p.file}`)} style={{ position: "absolute", left: pl.left, top: pl.top, width: pl.width, height: pl.height }} />
      {dim > 0 ? <div style={{ position: "absolute", inset: 0, backgroundColor: `rgba(26,26,25,${dim})` }} /> : null}
      {credit ? (
        <div style={{ position: "absolute", right: 14, bottom: 10, fontFamily: "Inter", fontSize: w > 1000 ? 20 : 15, color: "rgba(242,240,234,0.85)", textShadow: "0 1px 3px rgba(0,0,0,0.9)" }}>
          {creditText(photo)}
        </div>
      ) : null}
    </div>
  );
};

/** Full-frame photo with a dark gradient, a caption (what, where, when) and optional headline text. */
export const PhotoCard: React.FC<{
  photo: PhotoKey; from: Rect; to?: Rect; dur?: number; caption: string; children?: React.ReactNode;
}> = ({ photo, from, to, dur, caption, children }) => {
  const t = useT();
  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a19" }}>
      <PhotoBox photo={photo} from={from} to={to} dur={dur} credit={false} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(26,26,25,0) 45%, rgba(26,26,25,0.92) 100%)" }} />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{ position: "absolute", fontFamily: "Inter" }}>
        {children}
        <Txt x={80} y={1040} size={22} color={MUTED} opacity={ev(t, 0.3, 0.5)}>{caption}</Txt>
        <Txt x={1840} y={1040} size={20} color={TEXT} anchor="end" opacity={0.85 * ev(t, 0.3, 0.5)}>{creditText(photo)}</Txt>
      </svg>
    </AbsoluteFill>
  );
};
