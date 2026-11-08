# Episode 1 clips (Remotion)

The 12 Step 5 clips for Run of the Champions, Episode 1 (Barcelona 2014/15).

- `sh render-clips.sh` renders every clip to `../clips/` (or `sh render-clips.sh C3 C5` for some).
  It first runs `../code/export_remotion_data.py`, which checks the StatsBomb figures against
  CLAUDE.md and stops if anything differs.
- `npx remotion studio` opens the preview.
- `src/data/run.ts`: the verified run (from CLAUDE.md). `src/data/final.json`: StatsBomb data for the final.
- `src/clips/`: C1 (C1a, C1b), Route (C2 to C2f), Final (C3, C4, C5). Timings are seconds from the
  start of the script line each clip sits on (see `../shotlist.md`).
