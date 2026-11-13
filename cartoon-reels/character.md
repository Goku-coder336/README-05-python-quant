# Series characters

The series face for every Word Song reel. Reuse these designs exactly; the source of truth is the SVG code in `reels/01-french-eau/characters.py` (copy it into each new reel).

Status: **Option A saved as the default.** Options B and C are alternatives the owner may pick instead; if one is picked, mark it default here and keep the others as archived.

## Shared rules (all options)

- Flat colours, outlines `#1d1d1b` at 6 px, big readable face.
- Rigged parts, each a `<g>` with id `<prefix>-<part>`: `head`, `brow-l`, `brow-r`, `eye-l`, `eye-r`, `mouth-c` (closed), `mouth-o` (open), `body`, `arm-l`, `arm-r`, `legs`. Pivots are in `*_PIVOTS` in `characters.py`; pass them to GSAP as `svgOrigin`.
- Acting: idle breath (body scale about 1.5 %, 3 s cycle), blink every 2 to 3 s (eyes scaleY to 0.1 for 2 frames), mouth flaps while speaking, arm or pointer up on key words, hop or head tilt on funny words, eyebrow raise for deadpan beats. Offset parts (head leads, arms follow); never move both arms or both eyes in unison.

## Teacher

### Option A (default): Barnaby

- Human, tall rounded-rectangle head, skin `#f3cfa8`.
- **Signature:** a tall curl of dark brown hair (`#3b2a20`) springing up from the top of the head, plus big round glasses.
- Mustard cardigan `#e8b13c` with three brown buttons, white shirt collar, teal bow tie `#2fa39a`, dark trousers `#3a3f55`, brown shoes.
- Prop: wooden pointer in the right hand. Lesson set: a wooden lectern on a cream background `#f4ead8`.
- Personality: deadpan, flat mouth line, brows do the acting.
- Voice: ElevenLabs **George** (calm British, deadpan).

### Option B: Gilbert (pigeon)

- A grey pigeon teacher, see `characters.py` (`teacher_pigeon`). Signature: red knitted scarf with tassels, orange pigeon eyes, iridescent neck band. Wings are the arms; the beak opens for speech.
- Bonus: a bird teaching the word for "bird" (oiseau) is a running gag.

### Option C: Unit 7 (robot)

- A boxy robot teacher, see `characters.py` (`teacher_robot`). Signature: antenna with a glowing red bulb; screen face with rectangle eyes and a grille mouth.

## Duet partner

### Odette

- Human, round head, skin `#c98b5e`.
- **Signature:** big black hair bun (`#2b2233`) and yellow hoop earrings `#ffd23f`.
- Coral top `#ff6f61` with a white collar, dark leggings, yellow trainers.
- Personality: big energy, open smile, raised brows.
- Voice: ElevenLabs **Laura** (bright, quirky). Not yet confirmed by the owner.

## Payoff set

Dark purple stage `#2b1d4f`, tint flash `#7a2e8c` on the beat, spotlight ellipse `#4a3580`, floor `#1d1436`, a hanging retro microphone between the two characters.
