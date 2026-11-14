# Hand-off: cartoon reels (and football reels)

Read this first in a new session. Repo `Goku-coder336/README-05-python-quant`, branch **`claude/gifted-cray-jnk1eo`** (everything below is committed there; `main` does not have it).

## Where things are

- `cartoon-reels/CLAUDE.md`: the series rules (format, joke rules, character, layout, voice/music, process). Follow it.
- `cartoon-reels/character.md`: series characters. Teacher **Barnaby** (Option A, approved): curl of hair, round glasses, mustard cardigan, teal bow tie, pointer. Partner **Odette**: black bun, coral top, yellow hoops. Options B (pigeon) and C (robot) exist in `characters.py` but were not chosen.
- `cartoon-reels/jokes-used.md`: log of used jokes; check before pitching.
- `cartoon-reels/reels/01-french-eau/`: reel 01, "French is easy" (eau, haut, chapeau, oiseau, bateau, gâteau, château, couteau). `SCRIPT.md`, `YOUTUBE.md` (title, description, tags) and `renders/` are inside.
- `cartoon-reels/demos/`: claude-drawing demos (cartoon style): `oiseau_drawing.*` (bird in a top hat on a boat) and `oiseau_gateau.py` / `gateau_*` (bird cutting a castle cake). Each has a draw-on GIF and a finished JPG.

## Reel 01 versions (all rendered, in `renders/`)

| Version | What | Length |
|---|---|---|
| v2 | Teacher-only lesson, French café song | 39.0 s |
| v3 | Teacher-only lesson, catchier pop song (whistle hook, 118 BPM) | 36.2 s |
| **v4 (latest, owner liked it)** | Odette asks ("How do you say water in French?"), Barnaby answers; music only teases under the dialogue, builds under the English sentence, drops into the sung chorus | 40.7 s |

All end on "EASY." + "Sing it in the comments" (no "Follow for Lesson 2"). Each has a `-music` and `-nomusic` file (no-music keeps the sung vocals stem).

## How reel 01 is built

From `cartoon-reels/reels/01-french-eau/`, choose the variant with `VARIANT=v2|v3|v4` (see `variant.py`):

```
python3 vo.py            # ElevenLabs voice lines (George = teacher, Laura = Odette); vo_fix.py re-records lines speech-to-text mishears
python3 timeline.py      # timing from real line lengths (+ song word timestamps if present)
python3 music.py         # ElevenLabs music (music_v2_5): song, verified by speech-to-text, plus stems
python3 timeline.py && python3 audio.py && python3 build.py
npx hyperframes check --json
npx hyperframes render -q delivery -o renders/<name>-music.mp4
# no-music: ffmpeg mux the render's video with assets/audio[/vN]/mix-nomusic.wav
```

ElevenLabs key is saved on the cloud environment as a network secret for `api.elevenlabs.io` (header `xi-api-key`); code sends the placeholder `proxy-injected`. Never ask for the key in chat.

## Next steps the owner asked for / is deciding

1. Third demo drawing to finish the set: **"et tombe à l'eau !"** (bird toppling off the boat into the water, splash, hat flying). Same style as `cartoon-reels/demos/oiseau_gateau.py`.
2. Then add the drawings into reel 01 (e.g. as cutaways during the sung chorus, rendered at full 1080x1920 with more frames), likely on top of v4.
3. Owner may still change the music, voices or script of reel 01.
4. Football reels: rules were in `~/football-reels/CLAUDE.md` (temporary, now lost). The owner wants them in a separate GitHub repo they will create; the full brief is in the chat history (ask the owner to paste it again if needed).

## Tools installed in the old session (temporary: reinstall in a new session)

HyperFrames skills (`npx skills add heygen-com/hyperframes -g -y -a claude-code`), Lemo-Opuscar plugin, Bang Motion plugin, YouTube agent plugin, claude-drawing / huashu-art-motion / vox-explainer / vox-director skills, claude-mem, Vercel and addyosmani skills. Python needs `scipy`. Huashu needs Python Playwright pinned to 1.63.0 (`uv run --with playwright==1.63.0`) to match the preinstalled Chromium.
