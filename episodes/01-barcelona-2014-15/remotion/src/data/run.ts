// Verified run, copied from CLAUDE.md. Barcelona's score first. Do not add other stats.

export type Match = {
  key: string;
  col: number; // 0 Group F, 1 R16, 2 QF, 3 SF, 4 Final
  slot: number;
  label: string;
  opp: string;
  venue: string;
  res: "W" | "L";
  score: string;
  scorers: [string, number][];
};

export const MATCHES: Match[] = [
  { key: "MD1", col: 0, slot: 0, label: "MD1", opp: "APOEL", venue: "home", res: "W", score: "1-0", scorers: [["Piqué", 1]] },
  { key: "MD2", col: 0, slot: 1, label: "MD2", opp: "PSG", venue: "away", res: "L", score: "2-3", scorers: [["Messi", 1], ["Neymar", 1]] },
  { key: "MD3", col: 0, slot: 2, label: "MD3", opp: "Ajax", venue: "home", res: "W", score: "3-1", scorers: [["Neymar", 1], ["Messi", 1], ["Sandro", 1]] },
  { key: "MD4", col: 0, slot: 3, label: "MD4", opp: "Ajax", venue: "away", res: "W", score: "2-0", scorers: [["Messi", 2]] },
  { key: "MD5", col: 0, slot: 4, label: "MD5", opp: "APOEL", venue: "away", res: "W", score: "4-0", scorers: [["Messi", 3], ["Suárez", 1]] },
  { key: "MD6", col: 0, slot: 5, label: "MD6", opp: "PSG", venue: "home", res: "W", score: "3-1", scorers: [["Messi", 1], ["Neymar", 1], ["Suárez", 1]] },
  { key: "R1", col: 1, slot: 0, label: "Leg 1", opp: "Man City", venue: "away", res: "W", score: "2-1", scorers: [["Suárez", 2]] },
  { key: "R2", col: 1, slot: 1, label: "Leg 2", opp: "Man City", venue: "home", res: "W", score: "1-0", scorers: [["Rakitić", 1]] },
  { key: "Q1", col: 2, slot: 0, label: "Leg 1", opp: "PSG", venue: "away", res: "W", score: "3-1", scorers: [["Neymar", 1], ["Suárez", 2]] },
  { key: "Q2", col: 2, slot: 1, label: "Leg 2", opp: "PSG", venue: "home", res: "W", score: "2-0", scorers: [["Neymar", 2]] },
  { key: "S1", col: 3, slot: 0, label: "Leg 1", opp: "Bayern", venue: "home", res: "W", score: "3-0", scorers: [["Messi", 2], ["Neymar", 1]] },
  { key: "S2", col: 3, slot: 1, label: "Leg 2", opp: "Bayern", venue: "away", res: "L", score: "2-3", scorers: [["Neymar", 2]] },
  { key: "F", col: 4, slot: 0, label: "Final", opp: "Juventus", venue: "Berlin", res: "W", score: "3-1", scorers: [["Rakitić", 1], ["Suárez", 1], ["Neymar", 1]] },
];

export const AGG: Record<number, string> = { 1: "Agg 3-1", 2: "Agg 5-1", 3: "Agg 5-3" };
export const HOME = ["MD1", "MD3", "MD6", "R2", "Q2", "S1"];
export const LOSSES = ["MD2", "S2"];
export const GROUP_KEYS = ["MD1", "MD2", "MD3", "MD4", "MD5", "MD6"];

// Goal splits (CLAUDE.md key findings)
export const GROUP_TOTAL = 15;
export const GROUP_MESSI = 8;
export const KO_TOTAL = 16;
export const KO_MESSI = 2;
export const KO_AFTER_QF: [string, number][] = [["Suárez", 4], ["Neymar", 3], ["Rakitić", 1], ["Messi", 0]];
export const SPLIT: [string, number, number][] = [["Neymar", 3, 7], ["Suárez", 2, 5], ["Messi", 8, 2]];
