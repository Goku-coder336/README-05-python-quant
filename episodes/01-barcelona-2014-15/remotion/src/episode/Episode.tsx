// The full Episode 1 video: voiceover plus every clip, card and chart, placed by shotlist.md.
// Each visual starts at the real start of its script line in the voiceover (src/data/voice.json).
// Clips keep their own reveal timings, stretched so each script line lands where it is spoken.
import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { C1a, C1b } from "../clips/C1";
import { C3, C4, C5 } from "../clips/Final";
import { CFG_C2, CFG_C2A, CFG_C2B, CFG_C2C, CFG_C2D, CFG_C2E, CFG_C2F, Route } from "../clips/Route";
import { ClipClock } from "../components/ui";
import voice from "../data/voice.json";
import { BG, MESSI, NEYMAR, SUAREZ } from "../theme";
import { AwardsPhotoCard, ForwardsScene, MessiPhotoScene, PipPhoto } from "./PhotoScenes";
import {
  BookendCard, EndCard, EnriqueCard, LowerThird, MessiFinalChart, ScorersChart, SeriesCard,
} from "./Cards";

type Line = { line: number; start: number; end: number; est: number; text: string };
const LINES = voice.lines as Line[];
const L = (n: number) => LINES.find((l) => l.line === n)!;
export const END_TAIL = 15; // seconds of end card after the last line, for YouTube end screen elements
export const EPISODE_SECONDS = L(79).end + END_TAIL;

/** When a word is spoken, estimated from its position in the line. */
const wordAt = (n: number, word: string, occurrence = 1) => {
  const l = L(n);
  const words = l.text.split(/\s+/);
  let seen = 0;
  const idx = words.findIndex((w) => w.toLowerCase().startsWith(word.toLowerCase()) && ++seen === occurrence);
  return l.start + ((idx < 0 ? 0 : idx) / words.length) * (l.end - l.start);
};

/**
 * Clock for a clip placed at line `a` covering lines a..b. Each line's real start maps to its
 * scripted start on the clip's timeline (the clips were timed to script.md's estimates).
 * `offset` is the clip time at line a. Past the last line the clip runs at normal speed.
 */
const clipClock = (a: number, b: number, seqStart: number, offset = 0) => {
  const pts: [number, number][] = [];
  for (let n = a; n <= b; n++) pts.push([L(n).start - seqStart, L(n).est - L(a).est + offset]);
  const nextEst = n80(b);
  pts.push([L(b).end - seqStart, nextEst - L(a).est + offset]);
  return (s: number) => {
    if (s <= pts[0][0]) return pts[0][1];
    for (let i = 1; i < pts.length; i++) {
      if (s <= pts[i][0]) {
        const [x0, y0] = pts[i - 1];
        const [x1, y1] = pts[i];
        return y0 + ((s - x0) / (x1 - x0)) * (y1 - y0);
      }
    }
    const [xl, yl] = pts[pts.length - 1];
    return yl + (s - xl);
  };
};
// scripted start of the line after n (the last line gets its estimated length at 150 words a minute)
function n80(n: number) {
  const next = LINES.find((l) => l.line === n + 1);
  return next ? next.est : L(n).est + (L(n).text.split(/\s+/).length / 150) * 60;
}

type Seg = { from: number; node: (seqStart: number) => React.ReactNode };

const clip = (el: React.ReactNode, clock: (s: number) => number) => (
  <ClipClock.Provider value={clock}>{el}</ClipClock.Provider>
);

// Visual timeline, in script order (shotlist.md). `from` is the first line the visual covers.
const SEGS: Seg[] = [
  { from: 1, node: (s) => clip(<C1a />, clipClock(1, 5, s)) },
  // L03 to L05: Messi photo; 'Finisher.' and 'Supplier.' land on the words in L04
  {
    from: 3,
    node: (s) =>
      clip(<MessiPhotoScene finisherAt={wordAt(4, "finisher") - s} supplierAt={wordAt(4, "supplier") - s} dur={L(6).start - s} />, (x) => x),
  },
  { from: 6, node: () => <SeriesCard /> },
  { from: 7, node: (s) => clip(<EnriqueCard quoteAt={wordAt(8, "transitional") - s} />, (x) => x) },
  // L10 to L11: the three forwards, each photo on its name; the route intro follows on L12
  {
    from: 10,
    node: (s) =>
      clip(<ForwardsScene at={[wordAt(10, "Messi.") - s, wordAt(10, "Neymar.") - s, wordAt(10, "Luis") - s]} />, (x) => x),
  },
  { from: 12, node: (s) => clip(<Route cfg={CFG_C2} />, clipClock(10, 13, s)) },
  { from: 14, node: (s) => clip(<Route cfg={CFG_C2A} />, clipClock(14, 22, s)) },
  // L23 to L24: chart slot for group goals by scorer. Stand-in: C1b held on the group-stage half.
  { from: 23, node: () => clip(<C1b />, () => 9.0) },
  // L25: hold the group stage; L26: hard cut to black on 'You would be wrong.'
  { from: 25, node: () => clip(<Route cfg={CFG_C2A} />, () => 46) },
  { from: 26, node: () => <AbsoluteFill style={{ backgroundColor: "#000" }} /> },
  { from: 27, node: (s) => clip(<Route cfg={CFG_C2B} />, clipClock(27, 32, s)) },
  { from: 33, node: (s) => clip(<Route cfg={CFG_C2C} />, clipClock(33, 37, s)) },
  { from: 38, node: (s) => clip(<C1b />, (x) => Math.min(clipClock(38, 38, s)(x), 4.85)) },
  { from: 39, node: (s) => clip(<Route cfg={CFG_C2D} />, clipClock(39, 44, s)) },
  // L45 to L48: chart slot for top scorers and assisters (verified UEFA figures)
  { from: 45, node: (s) => clip(<ScorersChart assistAt={L(46).start - s} goalsAt={L(47).start - s} />, (x) => x) },
  { from: 49, node: (s) => clip(<Route cfg={CFG_C2E} />, clipClock(49, 49, s)) },
  // C5 starts 0.6 s into its own timeline so the ball goes in as L50 ends ('One-nil')
  { from: 50, node: (s) => clip(<C5 />, clipClock(50, 51, s, 0.6)) },
  { from: 52, node: (s) => clip(<C3 />, clipClock(52, 57, s)) },
  {
    from: 58,
    node: (s) => (
      <>
        {clip(<C4 />, clipClock(58, 59, s))}
        {clip(<LowerThird passesAt={L(58).start - s + 0.3} pressuresAt={L(59).start - s + 0.3} />, (x) => x)}
      </>
    ),
  },
  // L60: chart slot for Messi in the final (StatsBomb)
  { from: 60, node: (s) => clip(<MessiFinalChart passesAt={wordAt(60, "Seventy") - s - 1.5} />, (x) => x) },
  { from: 61, node: (s) => clip(<AwardsPhotoCard xaviAt={L(62).start - s} />, (x) => x) },
  { from: 63, node: (s) => clip(<Route cfg={CFG_C2F} />, clipClock(63, 66, s)) },
  // L67 to L74: C1b part two (its own timeline puts L67 at 5 s)
  { from: 67, node: (s) => clip(<C1b />, clipClock(67, 74, s, 5.0)) },
  {
    from: 75,
    node: (s) =>
      clip(
        <BookendCard
          quoteAt={wordAt(75, "A") - s}
          y2015={L(76).start - s}
          y2025={wordAt(77, "twenty", 1) - s}
          y2026={wordAt(77, "twenty", 3) - s}
        />,
        (x) => x,
      ),
  },
  { from: 78, node: () => <EndCard /> },
];

// Photos laid over the route charts, in the space each chart leaves empty: [start s, end s, node]
const OVERLAYS: [number, number, (dur: number) => React.ReactNode][] = [
  // L28 to L29: 'Both goals came from Suárez'
  [wordAt(28, "Both"), L(30).start, (d) => clip(
    <PipPhoto photo="suarez_super" crop={[0.45, 0.24, 0.42, 0]} name="Suárez" color={SUAREZ} x={1300} y={250} w={330} h={400} outAt={d - 0.4} />, (x) => x)],
  // L34 to L36: Neymar's goals against PSG
  [L(34).start, L(37).start, (d) => clip(
    <PipPhoto photo="neymar_b" crop={[0.23, 0.05, 0.778, 0]} name="Neymar" color={NEYMAR} x={1240} y={250} w={560} h={360} outAt={d - 0.4} />, (x) => x)],
  // L40: 'This is where Messi did score. Twice'
  [L(40).start, L(41).start, (d) => clip(
    <PipPhoto photo="messi_a" crop={[0.252, 0.24, 0.306, 0]} name="Messi" color={MESSI} x={1500} y={250} w={330} h={360} outAt={d - 0.4} />, (x) => x)],
];

export const Episode: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {SEGS.map((seg, i) => {
        const start = i === 0 ? 0 : L(seg.from).start;
        const end = i + 1 < SEGS.length ? L(SEGS[i + 1].from).start : durationInFrames / fps;
        const from = Math.round(start * fps);
        const dur = Math.round(end * fps) - from;
        return (
          <Sequence key={seg.from} from={from} durationInFrames={dur} name={`L${String(seg.from).padStart(2, "0")}`}>
            {seg.node(from / fps)}
          </Sequence>
        );
      })}
      {OVERLAYS.map(([a, b, node], i) => {
        const from = Math.round(a * fps);
        const dur = Math.round(b * fps) - from;
        return (
          <Sequence key={`o${i}`} from={from} durationInFrames={dur} name={`photo ${i + 1}`}>
            {node(dur / fps)}
          </Sequence>
        );
      })}
      <Audio src={staticFile("voiceover.wav")} />
    </AbsoluteFill>
  );
};
