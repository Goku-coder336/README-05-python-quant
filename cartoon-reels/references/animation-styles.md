# Animation styles: what we can use (from Shaan Johari's style cards, @viashaan)

The owner shared a long guide of 5-second motion "style cards". Each card has a look (hex colours, free fonts), how it moves, a "Never" list and a prompt. This file keeps only what helps our two series. The full guide stays with the owner.

## How we use the cards here

- The prompts say "in Remotion". We build in **HyperFrames** instead (same idea: code that renders frames to MP4). Swap "in Remotion" for "in HyperFrames"; everything else in a card still applies.
- 3D cards ("with three.js") work in HyperFrames too: three.js r170 is saved at `cartoon-reels/assets/three.module.min.js` (MIT licence next to it).
- Every card avoids copying channels: never use their characters, logos or scenes. Same rule as `CLAUDE.md` section 3.

## Rules from the guide that match ours (keep using them)

- Frame one is already moving or already readable. Nothing builds from an empty frame.
- Nothing fades in. Things pop, drop, rise out of a mask, draw on or slide.
- About 10% overshoot on springs, and only where it earns it. Not everything bounces.
- Numbers use tabular (fixed-width) digits so they never jitter while counting.
- Hold the last second (or the last 20 frames) completely still.
- One accent colour. No neon glow, particle bursts, sparkles, lens flares or camera shake.
- Keep the bottom fifth calm (Instagram/Shorts caption area).
- Dither or add fine grain to big soft gradients so they don't band in the MP4.

## Cartoon word-song reels: cards that fit

| Card | Where it could go |
|---|---|
| **Paint Comic** (Part 7) | Cheapest way to act out the stitched sentence as 3 held drawings with a black caps label (like our claude-drawing cutaways, but cruder and funnier). |
| **Ink Doodle** (Part 5) | Same: a simple scene with wobbly lines and one red marker X for the punchline. |
| **POV Doodle** (Part 5) | Eyebrow-driven expressions; a good reference for Barnaby's deadpan reactions. |
| **Crayon Science** (Part 7) | "Boil the lines every 3 frames" for a hand-drawn feel on our drawn cutaways. |

Not for these reels: the 3D studio product cards and the Black Friday cards (wrong tone).

## Football reels: cards that fit (strong matches)

| Card | Football use |
|---|---|
| **Live Leaderboard** (Part 7) | League table, top scorers, Golden Boot race: a row overtakes and slides up. |
| **Ranking bars** (Part 3) | Bar chart race of goals or points by season. |
| **Versus** (Part 3) | Player vs player, club vs club, "tale of the tape". |
| **Globe arcs** (Part 3) | Transfers flying in from other countries; away trips in Europe. |
| **Toy Soldiers** (Part 7) | Explaining a rule or formation with two teams of mannequin figures. |
| **Hologram** (Part 5) | Tactical replay: how a goal was built, the route of the ball. |
| **Day counter** (Part 3) | Unbeaten run, days since a trophy. |
| **Milestone trophy** (Part 4) | 100 goals, 500 appearances. |
| **Stat Chart** (Part 2) | Value or goals over time with the moment that changed it. |
| **Social post receipt** (Part 3) | What a player or manager said (invented accounts only, no real logos). |
| **Timeline** (Part 2) | A club's or player's story across seasons. |

Use real names and clubs only where the owner confirms it's fine. No club crests, league logos or broadcaster graphics.

## Tools the guide implies, and what we have

| Tool | Status here |
|---|---|
| Remotion | Not installed: HyperFrames does the same job and is already set up. Remotion is free for individuals and very small companies; larger companies need a paid licence. |
| three.js | Saved locally (r170). |
| Google Fonts used by the cards (Inter, Inter Tight, Montserrat, Barlow Condensed, Anton, Newsreader, IBM Plex, JetBrains Mono, Patrick Hand, Mali, Comic Relief) | Free; load per reel from Google Fonts. |

## Saving a card as a slash command

The guide suggests saving a card's prompt as `.claude/commands/<name>.md` with `$ARGUMENTS` where your words go, then typing `/<name> your words`. Worth doing once a style becomes a series format.
