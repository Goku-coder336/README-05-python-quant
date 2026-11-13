# Reel 01: French is easy ("-eau")

Status: **rendered (v2)**. Files: `renders/01-french-eau-v2-music.mp4`, `renders/01-french-eau-v2-nomusic.mp4`.

- Series tag: `WORD SONG #01` · 1080x1920 · 30 fps · 39.2 s
- Teacher: Barnaby (Option A), voice ElevenLabs **George**. Duet: Barnaby and Odette, sung by the ElevenLabs music model.
- Music: one ElevenLabs song (French café pop, accordion, pizzicato, upright bass, 105 BPM), seed 11.
- Exact timings live in `timeline.json`, built from the real line lengths and the sung word timestamps.

## v2 changes (owner feedback)

- New music: a real song instead of the generated beat.
- After the words, the teacher reads the whole sentence in English, phrase by phrase.
- The French sentence is sung as a song, like the reference, and the duet lip-syncs to it.

## Running order

| Time (s) | Scene | On screen | Audio |
|---|---|---|---|
| 0.0 – 1.5 | Hook | FRENCH IS EASY | George: "French is easy." |
| 1.5 – 16.9 | Lesson | cue → answer: water → EAU, high → HAUT, EAU · HAUT · OH ("Same."), hat → CHAPEAU, bird → OISEAU, boat → BATEAU, cake → GÂTEAU, castle → CHÂTEAU, knife → COUTEAU | George says each English word, then the French word |
| 16.9 – 18.0 | Turn | NOW TRY THIS | "Now try this." |
| 18.0 – 24.2 | English sentence | IN ENGLISH: The fine bird in a hat, / on the boat, / cuts the castle's cake with a knife… / and falls in the water. | George reads it, deadpan |
| 24.2 – 26.3 | Count-in | NOW IN FRENCH · 1, 2, 3… (pointer raised like a conductor) | song lead-in bar |
| 26.3 – 37.2 | Sung payoff | Le bel oiseau au chapeau, / sur le bateau, / coupe le gâteau du château au couteau… / et tombe à l'eau ! (translation under each) | the duet sings; splash on "l'eau" |
| 37.2 – 39.2 | Button | EASY. · Follow for Lesson 2 | George: "Easy." |

## Accuracy check

- Meanings: eau = water, haut = high, chapeau = hat, oiseau = bird, bateau = boat, gâteau = cake, château = castle, couteau = knife.
- Sound: all end in the same "oh" sound (the "h" in "haut" is silent).
- Grammar: "le bel oiseau" (bel before a vowel), "au chapeau" (with the hat), "couper … au couteau" (to cut with a knife), "tomber à l'eau" (to fall in the water).
- Every spoken French word and the full sung lyric were checked with ElevenLabs speech-to-text.

## Rebuild

```
python3 vo.py && python3 timeline.py && python3 music.py && python3 timeline.py && python3 audio.py && python3 build.py
npx hyperframes check --json && npx hyperframes render -q delivery -o renders/01-french-eau-v2-music.mp4
```
