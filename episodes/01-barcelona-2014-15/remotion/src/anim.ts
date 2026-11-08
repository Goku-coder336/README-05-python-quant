import { Easing, interpolate } from "remotion";

// All clip timings are written in seconds from the start of the script line the clip sits on.
// t is the current time in seconds (frame / fps).

const OUT = Easing.bezier(0.16, 1, 0.3, 1);

/** Eased 0..1 progress of an event starting at `start` (s) lasting `dur` (s). */
export const ev = (t: number, start: number, dur = 0.5) =>
  interpolate(t, [start, start + dur], [0, 1], {
    easing: OUT,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/** Linear 0..1 progress. */
export const lin = (t: number, start: number, dur = 0.5) =>
  interpolate(t, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

/** A short overshoot pulse (0 -> 1 -> 0) used for pops. */
export const pulse = (t: number, start: number, dur = 0.45) => {
  const p = lin(t, start, dur);
  return Math.sin(Math.PI * p);
};

/** Piecewise-linear interpolation through [time, value] keys. */
export const keys = (t: number, k: [number, number][]) =>
  interpolate(
    t,
    k.map((x) => x[0]),
    k.map((x) => x[1]),
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

/** Mix two hex colours. */
export const mix = (a: string, b: string, f: number) => {
  const pa = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16));
  const pb = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16));
  const c = pa.map((v, i) => Math.round(v + (pb[i] - v) * f));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
};
