# "Blue Saree": first-love reel for *Nenchaadiye*

**Format:** 9:16 vertical, about 30 s, 11 shots of about 2.7 s each, painterly AI pictures with motion added by me.
**Song:** *Nenchaadiye* (Prempaatta, sung by Nihal Sadiq). Added by you in Instagram's music picker when you post.
The video I deliver is silent with **no lyrics burned in**. Use Instagram's lyrics sticker for the words.
**Story:** a rainy afternoon in Fort Kochi. Two strangers share a tea-stall awning, reach for the same glass of chai,
and fall for each other by evening.

---

## Budget (invideo, Nano Banana 2 at about 1.2 credits per picture)

| Step | Pictures | Credits |
|---|---|---|
| Character sheets (Meera, Arjun) | 2 | about 2.4 |
| Scene pictures (shots 1–11) | 11 | about 13.2 |
| Spare for 2–3 redos | – | about 4 |
| **Total** | **13** | **about 15.6 of your 20** |

The two character sheets go in as reference images for every scene, so both faces and outfits stay the same.

---

## The characters

**Meera:** a young Malayali woman in her early twenties, warm brown skin, long thick black hair in a loose side braid
with white jasmine flowers, small gold jhumka earrings, a small black bindi, a royal-blue cotton saree with a thin gold
border and matching blouse, thin gold bangles.

**Arjun:** a young Malayali man in his early twenties, warm brown skin, messy curly black hair, light stubble, big
expressive eyes, a cream short-sleeve shirt with rolled sleeves, a white mundu with a thin gold border, an old black bicycle.

**Style line added to every prompt:**
`painterly 3D animated film still, soft Pixar-meets-Ghibli illustration, rich warm colour, gentle film grain, cinematic
lighting, Kerala, vertical 9:16 composition, no text, no watermark`

---

## How I animate each character (free, done in code with HyperFrames)

The pictures are still images. I trace masks around parts of each picture by hand, then move those parts every frame:

| Part | Technique | Used in shots |
|---|---|---|
| **Meera: saree pallu** (the loose end of the saree) | Ripple the masked cloth with a wave, strongest at the free edge, about 0.6 cycles per second | 2, 6, 8 |
| **Meera: hair and braid** | Sway the loose strands slightly; the braid swings from the top of her head | 2, 5, 6, 11 |
| **Meera: jhumka earrings** | Swing from the ear like a pendulum, delayed slightly after her head moves | 5, 11 |
| **Meera: eyes** | Blink by painting skin-coloured eyelids over the eyes every 2–4 s (close-ups only) | 5, 11 |
| **Meera: jasmine** | Loose petals drift down and away | 5, 9, 11 |
| **Arjun: curly hair** | Small springy bounce in the hair; water drops fall in shot 4 | 1, 4, 7 |
| **Arjun: eyes** | Blink (close-up only) | 4 |
| **Arjun: breathing** | Chest and shoulders rise and fall about 1.5% | 1, 9, 10 |
| **Arjun: bicycle** | Spin the wheel spokes; small up-and-down bump from the road | 7 |
| **Both: hands** (shot 3) | Slide the two hands a few pixels towards each other until they almost touch | 3 |

**Added to every shot:** a slow camera push or pan, depth (foreground and background drifting at different speeds where
the picture allows it), light flares, a slow-pulsing light leak, film grain, and a soft fade to the next shot.

**What this can't do:** walking, turning heads, talking or big body movement. Those need paid AI video (about 3–7 credits
per second on your account). Every shot below is designed to look alive with small motions only.

---

## Shot list and prompts

### 1. Rain on the street (wide, 0.0–2.7 s)
**Prompt:** `Rainy afternoon on a narrow Fort Kochi street with old colonial shopfronts, a small tea stall with a tin awning,
Arjun standing under the awning beside his old black bicycle, looking out at the rain, steam rising from a glass of chai
on the wooden counter, puddles reflecting warm shop lights, wide shot` + Arjun + style
**Motion:** slow push in; falling rain streaks; ripples in the puddles; steam from the tea; Arjun breathing.

### 2. She runs in (medium, 2.7–5.4 s)
**Prompt:** `Meera running in under the same tea-stall awning to escape the rain, laughing, shaking water off the end of her blue
saree, raindrops on her face, jasmine in her braid, Arjun partly visible at the edge of frame, medium shot` + Meera + style
**Motion:** her saree end ripples; drops fall from her hair; rain in the foreground; a small sideways camera move.

### 3. Same glass of chai (close-up, 5.4–8.1 s)
**Prompt:** `Close-up of two hands reaching for the same last glass of chai on a wet wooden tea-stall counter, fingers almost
touching, her hand with thin gold bangles, his hand from a cream rolled sleeve, steam curling up, shallow depth of field`
+ style
**Motion:** the hands slide closer; steam curls; the focus shifts from the glass to the hands.

### 4. He freezes (close-up, 8.1–10.8 s)
**Prompt:** `Close-up portrait of Arjun, wide surprised eyes, frozen mid-breath, wet curly hair dripping, rain-soft
background with warm bokeh` + Arjun + style
**Motion:** one blink at about 1 s; drops fall from his curls; a slow push in.

### 5. She smiles (close-up, 10.8–13.5 s)
**Prompt:** `Close-up of Meera glancing sideways with a shy smile, gold jhumka earrings, jasmine flowers in her hair,
soft rim light from the rain-washed street behind her` + Meera + style
**Motion:** a blink; the jhumka swings; loose strands of hair sway; a jasmine petal drifts down.

### 6. Fishing nets at golden hour (wide, 13.5–16.2 s)
**Prompt:** `Golden hour after the rain at Fort Kochi beach, the giant Chinese fishing nets silhouetted against a glowing sea,
Meera walking along the shore away from camera, blue saree end trailing in the breeze, wet sand reflecting the sun` + Meera + style
**Motion:** the sea shimmers; sun glints sparkle; her saree end ripples; a slow pan to the right.

### 7. He cycles beside her (medium-wide, 16.2–18.9 s)
**Prompt:** `Arjun riding his old black bicycle along the seaside promenade, grinning and ringing the bell, children with a
bunch of colourful balloons and a peanut seller in the background, warm evening light` + Arjun + style
**Motion:** the wheel spokes spin; the bike bumps on the road; the balloons bob; the background drifts slower than he does.

### 8. Saree against the sun (low angle, 18.9–21.6 s)
**Prompt:** `Low-angle shot of Meera from behind, her blue saree end lifting high in the sea wind against the setting sun,
strong backlight glowing through the thin cotton, lens flare` + Meera + style
**Motion:** the biggest cloth movement of the video; the flare pulses; light glows through the fabric. This is the hero moment for the song's chorus.

### 9. Peanuts on the sea wall (medium, 21.6–24.3 s)
**Prompt:** `Meera and Arjun sitting on the old sea wall sharing a paper cone of roasted peanuts, laughing, framed through
swaying coconut palm leaves in the foreground, pastel sky` + Meera + Arjun + style
**Motion:** the foreground leaves sway; specks of dust float in the light; both breathe; a slow push through the leaves.

### 10. Festival lamps (night, 24.3–27.0 s)
**Prompt:** `Night at a small Kerala temple festival, rows of glowing brass oil lamps, Meera lighting a lamp, Arjun watching
her across the flames, warm firelight on their faces, bokeh` + Meera + Arjun + style
**Motion:** the flames flicker and glow; embers drift up; the background bokeh pulses; a small focus shift onto him.

### 11. Closing (close-up, 27.0–30.0 s)
**Prompt:** `Extreme close-up of Meera with eyes gently closed and a soft smile, warm golden light on her face, a single
jasmine flower held in Arjun's hand in the blurry foreground` + Meera + style
**Motion:** a very slow push in; she breathes; jasmine petals fall; a slow fade to warm white at the end.

---

## Timing

The cuts above are evenly spaced. To land them exactly on the beat, send me a screen recording of the 30 s of
*Nenchaadiye* you plan to use, like your earlier reference clips. I'll only measure the beats from it. The song itself
won't go into the video file.

## Order of work after you approve

1. Generate the 2 character sheets and check that the faces look right (about 2.4 credits).
2. Generate the 11 scenes with the sheets as references (about 13 credits) and redo any that drift.
3. Trace the masks and animate each shot in HyperFrames; send you preview frames.
4. Render the silent 9:16 MP4. You add *Nenchaadiye* and the lyrics sticker in Instagram.
