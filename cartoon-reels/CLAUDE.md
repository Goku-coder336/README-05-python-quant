# Cartoon Word-Song Reels: Strategy and Build Rules

This folder makes short, funny, animated cartoon reels for Instagram and YouTube Shorts. Follow everything in this file for every reel unless I say otherwise in the chat. You come up with the ideas, the jokes and the character yourself, then show me before building.

## 0. Lessons from the reference reel (these refine the rules below)

The reference (Spanish "-aña" reel, 31 s, about 377K likes) showed what actually makes the format work:

- **One shared sound per reel.** Every taught word ends in, or contains, the same sound chunk (there it was "-aña": mañana, araña, maña, telaraña, extraña, España, montaña). That is where the song comes from. Pick the sound first, then the words.
- **Cue, then answer.** The on-screen text shows the plain word first ("Spider"), then the answer replaces it ("Araña"). The viewer guesses for half a beat, then gets it. Use this rhythm for every word.
- **Same word, two meanings.** Repeats with a new meaning (mañana = tomorrow and morning; araña = spider and scratches) are the cheapest laughs. Use one or two per reel when they are genuine.
- **Short.** Target 30 to 40 s (never over 45). The lesson is about 1.5 to 2 s per word; the sung payoff is about 10 to 13 s.
- **The payoff background flips colour on the beat** (light, then tinted, then light), which makes a static duet feel energetic. Do this.
- **Make it loop.** The last frame should cut cleanly back to frame 0 so the reel replays. The button (section 1, step 7) stays, but keep it to about 2 s.
- **Do better than the reference on text.** Its words were small and the payoff lyrics sat at the bottom where Instagram's caption covers them. Ours are big, at the top, inside the safe area (section 4).
- **Do not copy it.** No bald stick figure with a bean-shaped body, no armchair, no half-closed-eyes face from that reel, and never the "-aña" words or its stitched line (it is logged in `jokes-used.md`).

## 1. The format

A deadpan cartoon character teaches viewers a handful of words or phrases, one at a time. Each word appears on screen as it is said. Then the character says "Now try this", and the words get stitched together into one ridiculous sentence that sounds like a song or tongue twister. Then the teacher reads the stitched sentence in English, and the payoff is a second scene where two characters sing it in the real language, like a duet at a microphone.

Why it works:

- Each word on its own is easy, so viewers feel smart.
- The stitched sentence is absurd but makes sense, which is the laugh.
- The rhythm of the payoff makes it replayable and gets it shared.

Structure (30 to 40 seconds; see section 0):

1. **Hook, 0 to 2 s**: a title line on screen from frame 0, for example "Spanish is easy" or "Football English is easy". The character says it with total confidence.
2. **The lesson, about 13 to 18 s**: 5 to 8 words or short phrases, each shown big on screen as it is said (cue, then answer). Use pairs where it helps (normal meaning, then the twist). Words should share one sound so they rhyme or echo each other.
3. **"Now try this", about 1 s**: the turn.
4. **The sentence in English, about 6 s**: the teacher reads the whole stitched sentence in English, deadpan, one phrase on screen at a time (as in the reference: "Tomorrow morning, / the strange / spider from Spain…").
5. **Count-in, about 2 s**: "NOW IN FRENCH", the teacher lifts the pointer like a conductor while the song's lead-in bar plays.
6. **The payoff, about 10 to 13 s**: a new scene. The stitched sentence in the real language is **sung** as a song (ElevenLabs music, male and female duet), the two characters lip-syncing, lyrics on screen line by line as they are sung with the translation under each. Bigger, faster, louder.
7. **Button, about 2 s**: cut back to the first character for one deadpan word ("Easy.") and a "Sing it in the comments" tag. Do not frame it as a lesson or a series ("Follow for Lesson 2" is out).

## 2. Coming up with the idea (do this first, every time)

1. Give me 10 ideas for a word-song reel. Mix these kinds:
   - A real language where words sound alike (Spanish, Malayalam, Hindi, French, Japanese and so on).
   - A "dialect" of English: football commentary, manager press conferences, office jargon, estate agents, Gen Z slang, British politeness, mum texts.
   - A fan or culture angle: transfer window English, Premier League pundit English.
2. For each idea, list the 5 to 8 words or phrases and the final stitched sentence.
3. Score each idea out of 100 on: is the stitched line genuinely funny, does it have rhythm when read aloud, would someone send it to a friend.
4. Pick the top one, explain why in two lines, and wait for me to approve before writing the full script.

Joke rules:

- The stitched sentence must be grammatical (or close) and actually mean something absurd. Random word salad is not funny.
- Build in an escalation: each word slightly more ridiculous than the last.
- The best laugh comes last.
- Never reuse a joke or stitched sentence from an earlier reel in this folder. Keep a `jokes-used.md` log and check it.
- Keep it friendly. No jokes that punch down at a nationality, accent, religion or group. Laugh at the language, not the people.

Accuracy rules for real languages:

- Every word's meaning must be correct. Double-check translations and spelling, including accents (ñ, é and so on).
- Only claim words sound alike if they genuinely do.
- If you are not sure of a word, leave it out and tell me.

## 3. The character (design it yourself)

- Design an original character from scratch. Do not copy any existing creator's character, a known cartoon, a mascot, or a brand figure. No real people.
- Draw it with code (SVG inside HyperFrames), so it looks exactly the same in every shot.
- Style: simple, flat, thick dark outlines (about 6 px, colour `#1d1d1b`), a few flat colours, big readable face. One strong recognisable feature (a hat, a scarf, a hairstyle, an odd prop).
- Rig it in separate parts so it can move: head, eyebrows, eyes, mouth, body, left arm, right arm, legs.
- Animations it must have:
  - Idle breathing (a slow, small scale up and down).
  - Blinks every 2 to 3 seconds.
  - Mouth flaps that follow the voice (open and close in a loop while a line is spoken, closed when silent).
  - Gestures: a raised arm or point on the key words, a small hop or head tilt on the funny ones.
  - Eyebrow raises for deadpan reactions.
- The setting is minimal: one piece of furniture or prop and a soft background. Keep it uncluttered so the words are the star.
- The payoff scene has two characters (the main one plus a second one you design to match the style), a microphone or commentary desk, and a slightly more energetic setting.
- Show me the character as 3 still frames before building the full video.
- Once I approve a character, save its design in `character.md` and reuse it in every future reel so it becomes the series face.

## 4. Visual style and layout

- 1080x1920, 30 fps.
- Warm, soft background for the lesson scene (for example `#f4ead8`), darker or more colourful background for the payoff scene.
- On-screen words: big, centred, bold (Montserrat 800, about 76 to 96 px), at the top of the frame around y 330 to 700.
- Small coloured label above each word when useful (for example "NORMAL ENGLISH" in beige, "FOOTBALL ENGLISH" in green, "COMMENTARY BOX" in red).
- Series tag pill at the top centre around y 186.
- Keep everything important above y 1500 and out of the right 120 px between y 1100 and 1500 (Instagram buttons and caption).
- Words pop in with a small bounce on the funny ones and a clean fade on the plain ones.

## 5. Voice and sound

Voice options (ask me which one before recording):

1. Free local voice: `npx hyperframes tts "<line>" --voice <voice> --speed 1.0 --output <file>.wav`. Use one voice for the main character and different voices for the payoff duo. Run `npx hyperframes tts --help` to see the voices.
2. ElevenLabs, if I have connected it or given you an API key. Better for accents and emotion.
3. An MP3 I record or make in VoiceStudio and give you.

Singing: the payoff is sung, not chanted. Generate one song for the whole reel with the ElevenLabs music model (`music.py`): an instrumental intro as long as the lesson and the English sentence, then the sung chorus with the stitched line as lyrics, then a short tail. Transcribe the sung part with ElevenLabs speech-to-text and only keep a take where every lyric word is heard in order; use those word timings for the on-screen lyrics and lip-sync. Split the song into stems (vocals and instrumental) so the no-music version keeps the singing.

Sound:

- Music: the ElevenLabs song above (light and sparse under the lesson, a full-band drop for the sung chorus). Numpy-generated music is only a fallback if no music tool is connected.
- Pop or click on each new word, a whoosh on scene changes, a hit on the biggest laugh, crowd or room sound in the payoff if it fits.
- Duck the music under the voice. Final mix around -14 to -16 LUFS.
- Deliver two files: one with the full song, and one with voice, effects and the sung vocals only (so I can add Instagram music instead).

## 6. Tools

- HyperFrames for building and rendering (install the skills once with `npx skills add heygen-com/hyperframes` and read the `/hyperframes` skill before building).
- GSAP saved locally in `assets/gsap.min.js`.
- Python 3 with numpy and scipy for music and sound effects.
- ffmpeg for joining and mixing audio.
- If you need another skill, tool or connector (for example ElevenLabs, a music generator, or a font), tell me exactly what to install and why, and I will do it.
- Do not use the Lemo-Opuscar pipeline (`~/lemo-opuscar`) for these reels; they have their own fixed style.
- Each reel is its own HyperFrames project in `reels/<nn>-<slug>/`.

## 7. Work process

1. Ideas: give me the 10 scored ideas, and wait for my pick.
2. Script: write the full script with every on-screen word, who says it, and rough timings. Wait for my approval.
3. Character: show me 3 stills of the character and both scenes. Wait for approval.
4. Voice: record line by line, measure each line's length, and build the timeline from the real durations.
5. Build in HyperFrames, then run `npx hyperframes check --json` and fix every error.
6. Snapshot every beat (`npx hyperframes snapshot --at <times>`), look at the frames and fix overlaps, cut-off text, bad timing and empty moments.
7. Render, make the music and no-music versions, check duration and loudness, and give me both files.
8. Add the joke to `jokes-used.md`.

## 8. Writing style

- British spelling.
- No em dashes in on-screen text.
- Lines short enough to read in under 2 seconds.
- Deadpan delivery for the teacher, big energy for the payoff.
