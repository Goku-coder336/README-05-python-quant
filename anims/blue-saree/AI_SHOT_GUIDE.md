# Blue Saree: shot-by-shot AI production guide

A 30-second, 9:16 first-love reel set to *Nenchaadiye* (you add the song in Instagram).
11 shots. For each one you make **one picture** in an image AI, then **animate that picture** in a video AI
(image-to-video), then send me the clips and I'll edit them together.

---

## How it works (read once)

**1. Make the two characters first, in one image tool.**
Generate Meera and Arjun as full-body character pictures on a plain background. Keep the best one of each.
In every later shot, **upload these two pictures as reference** and say "the same woman / the same man as in the
reference image". This is what keeps their faces the same across 11 shots.

**2. Always paste the same style line** at the end of every picture prompt (below). Never change it.

**3. Make every picture vertical (9:16).** Then animate it: "image to video", 5 seconds, using the picture as the
**start frame**. I'll trim each clip to its best 2–3 seconds.

**4. Name each file by shot number** (`shot01.mp4`, `shot02.mp4`…) and upload them all here. I'll cut them to the
beat, match the colours, add grain, light leaks and soft transitions, and export the reel.

### Free tools (free limits change often, so check inside each app)
| Job | Tool | Why this one |
|---|---|---|
| Pictures and keeping faces the same | **Google Gemini app** (Nano Banana image model) | Best at "same person in a new scene" from a reference picture |
| Pictures (backup) | **Meta AI** (in WhatsApp or Instagram), **Microsoft Bing Image Creator** | Free, good painterly style; weaker at keeping faces the same |
| Video: cloth, wind, water, physics | **Kling AI** (free daily credits) | Best saree, hair and water movement |
| Video: faces and emotion | **Hailuo AI (MiniMax)** (free daily credits) | Best small facial expressions: blinks, smiles, glances |
| Video: simple background motion | **PixVerse** or **Meta AI "Animate"** | Quick and free for rain, steam, light and a gentle camera move |

Free daily credits only cover a few videos a day, so spread the 11 shots over 3–4 days, starting with the hero shots (★).

---

## Copy-paste blocks

**STYLE LINE (end of every picture prompt):**
`painterly 3D animated film still, soft Pixar-meets-Ghibli illustration, rich warm colour, gentle film grain, cinematic
lighting, Kerala, India, vertical 9:16, no text, no watermark`

**MEERA:**
`Meera, a young Malayali woman in her early twenties, warm brown skin, long thick black hair in a loose side braid with
white jasmine flowers, small gold jhumka earrings, a small black bindi, a royal-blue cotton saree with a thin gold border
and matching blouse, thin gold bangles`

**ARJUN:**
`Arjun, a young Malayali man in his early twenties, warm brown skin, messy curly black hair, light stubble, big
expressive eyes, a cream short-sleeve shirt with rolled sleeves, a white mundu with a thin gold border`

**AVOID (add as negative prompt where the tool allows one):**
`extra fingers, deformed hands, distorted face, text, logo, watermark, blurry, photorealistic, harsh shadows`

**VIDEO RULE (add to every motion prompt):**
`keep the face and outfit identical to the image, no morphing, smooth natural motion`

---

## Step 0: character sheets (pictures only)

**0A, Meera:** `Full-body character sheet of MEERA, standing, front view and three-quarter view side by side, gentle
smile, plain warm cream background` + STYLE LINE
**0B, Arjun:** `Full-body character sheet of ARJUN, standing, front view and three-quarter view side by side, shy grin,
plain warm cream background` + STYLE LINE
Tool: **Gemini**. Make 3–4 tries each, keep the best, and use these two pictures as the reference for every shot below.

---

## The shots

### Shot 1: Rain on the street · 0.0–2.7 s · wide · opening
**Scenario:** a grey, rainy afternoon in Fort Kochi. Old colonial shopfronts, a tiny tea stall with a rusty tin awning.
Arjun waits out the rain under the awning beside his old black bicycle, watching the street. It feels calm and lonely, just before something happens.
**Picture prompt:** `Rainy afternoon on a narrow Fort Kochi street with old colonial shopfronts, a small tea stall with a
rusty tin awning, ARJUN standing under the awning beside an old black bicycle, looking out at the rain, a glass of chai
steaming on the wooden counter, puddles reflecting warm shop lights, wide shot` + STYLE LINE
**Motion prompt:** `Heavy rain falling, raindrops rippling in the puddles, water dripping from the awning edge, steam
rising from the tea, the man breathes calmly and glances at the street, slow dolly push in` + VIDEO RULE
**Tool:** PixVerse or Meta AI Animate (simple background motion)

### Shot 2: She runs in · 2.7–5.4 s · medium
**Scenario:** Meera dashes in from the rain, laughing, and ducks under the same awning. She shakes the water off the
loose end of her saree. Arjun is at the edge of the frame and turns to look.
**Picture prompt:** `MEERA running in under a tea-stall tin awning to escape the rain, laughing, shaking water off the
loose end of her blue saree, raindrops on her face and hair, ARJUN partly visible at the right edge turning to look,
medium shot` + STYLE LINE (upload both references)
**Motion prompt:** `The woman slows down and shakes the end of her saree, water droplets flying off the fabric, her braid
swings, rain falling behind her, the man turns his head towards her, smooth 35mm handheld track` + VIDEO RULE
**Tool:** ★ **Kling** (wet cloth and braid movement)

### Shot 3: Same glass of chai · 5.4–8.1 s · close-up
**Scenario:** both reach for the last glass of chai on the counter at the same moment. Their fingers stop a breath apart. This is the meet-cute.
**Picture prompt:** `Close-up of two hands reaching for the same last glass of chai on a wet wooden tea-stall counter,
fingers almost touching, her hand with thin gold bangles, his hand from a cream rolled sleeve, steam curling up,
rain-blurred street bokeh behind, shallow depth of field` + STYLE LINE
**Motion prompt:** `Both hands slowly move towards the glass and stop just before touching, the bangles shimmer, steam
curls upward, rack focus from the glass to the hands, static tripod locked-off shot` + VIDEO RULE
**Tool:** Kling (hands look best there). If the fingers come out wrong, regenerate. Hands are the hardest part.

### Shot 4: He freezes · 8.1–10.8 s · close-up
**Scenario:** Arjun looks up and sees her properly for the first time. He forgets to breathe. His curls are still dripping.
**Picture prompt:** `Close-up portrait of ARJUN, wide surprised eyes, lips slightly parted, wet curly hair dripping,
warm rain-soft bokeh background, looking slightly off-camera to the left` + STYLE LINE
**Motion prompt:** `He blinks once slowly, his eyes widen a little, a drop of water falls from his curls, a tiny
nervous swallow, very slow push in` + VIDEO RULE
**Tool:** ★ **Hailuo** (small facial expressions)

### Shot 5: She smiles · 10.8–13.5 s · close-up
**Scenario:** Meera notices him staring, looks away shyly, then glances back with a small smile. Her earrings sway.
**Picture prompt:** `Close-up of MEERA glancing sideways with a shy smile, gold jhumka earrings, jasmine flowers in her
hair, soft rim light, rain-washed street bokeh behind her` + STYLE LINE
**Motion prompt:** `She looks down shyly, then glances back towards camera with a small smile, her jhumka earrings
swing gently, a loose strand of hair moves in the breeze, slow push in` + VIDEO RULE
**Tool:** ★ **Hailuo**

### Shot 6: Fishing nets at golden hour · 13.5–16.2 s · wide
**Scenario:** the rain has stopped. Evening at Fort Kochi beach, the giant Chinese fishing nets against a glowing sea.
Meera walks along the wet shore, the end of her saree trailing in the breeze.
**Picture prompt:** `Golden hour after rain at Fort Kochi beach, giant Chinese fishing nets silhouetted against a glowing
sea, MEERA walking along the shore away from camera, blue saree end trailing in the breeze, wet sand reflecting the
sun` + STYLE LINE
**Motion prompt:** `She walks slowly along the shore, the saree end flows in the wind, gentle waves roll in, sun
sparkles on the water, slow lateral tracking shot to the right` + VIDEO RULE
**Tool:** Kling

### Shot 7: He cycles beside her · 16.2–18.9 s · medium-wide
**Scenario:** Arjun rides up on his old bicycle, grinning and ringing the bell to catch up with her. Kids with balloons on the promenade.
**Picture prompt:** `ARJUN riding an old black bicycle along a seaside promenade, grinning and ringing the bell,
children holding a bunch of colourful balloons and a peanut seller in the background, warm evening light` + STYLE LINE
**Motion prompt:** `He pedals forward smoothly, the wheels turn, his curls bounce, the balloons bob in the breeze, the
background passes by, smooth tracking shot alongside him` + VIDEO RULE
**Tool:** Kling (wheels and pedalling). Say "the wheels turn" or they may stay frozen.

### Shot 8: Saree against the sunset · 18.9–21.6 s · low angle · ★ the hero shot for the chorus
**Scenario:** the most beautiful moment of the video. The sea wind lifts the loose end of Meera's saree high against the setting sun, and the light glows through the thin blue cotton.
**Picture prompt:** `Low-angle shot of MEERA from behind, her blue saree end lifting high in the sea wind against a
setting sun, strong backlight glowing through the thin cotton, lens flare, hair blowing` + STYLE LINE
**Motion prompt:** `A strong sea breeze lifts the saree end high and it ripples slowly in the wind, her hair blows,
the sun flares, slow motion, slow tilt up` + VIDEO RULE
**Tool:** ★ **Kling** (make this one first: it's the shot people will remember)

### Shot 9: Peanuts on the sea wall · 21.6–24.3 s · medium
**Scenario:** they sit together on the old sea wall sharing a paper cone of roasted peanuts and laughing, seen through swaying palm leaves.
**Picture prompt:** `MEERA and ARJUN sitting together on an old sea wall sharing a paper cone of roasted peanuts,
laughing, framed through coconut palm leaves in the foreground, pastel evening sky over the sea` + STYLE LINE
(upload both references)
**Motion prompt:** `They laugh together and he offers her a peanut, palm leaves sway in the foreground, gentle waves
behind, slow push in through the leaves` + VIDEO RULE
**Tool:** Hailuo (two faces at once)

### Shot 10: Festival lamps · 24.3–27.0 s · night
**Scenario:** that night, at a small temple festival lit by rows of brass oil lamps, Meera lights a lamp. Arjun watches her across the flames.
**Picture prompt:** `Night at a small Kerala temple festival, rows of glowing brass oil lamps, MEERA lighting a lamp,
ARJUN watching her across the flames, warm firelight on their faces, soft bokeh` + STYLE LINE (upload both references)
**Motion prompt:** `The lamp flames flicker gently, embers drift upward, she lights one more wick, he smiles softly,
rack focus from her to him` + VIDEO RULE
**Tool:** PixVerse or Kling

### Shot 11: Closing · 27.0–30.0 s · extreme close-up
**Scenario:** Meera's eyes are closed, her smile is soft and warm light is on her face. A single jasmine flower in Arjun's hand is blurred in the foreground. Fade to warm white.
**Picture prompt:** `Extreme close-up of MEERA with eyes gently closed and a soft smile, warm golden light on her face, a
single jasmine flower held in a man's hand in the blurry foreground` + STYLE LINE
**Motion prompt:** `She breathes softly, a slight smile grows, warm light shimmers across her face, a jasmine petal
drifts down, very slow push in` + VIDEO RULE
**Tool:** Hailuo

---

## Order to make them (free credits are limited)
1. Character sheets 0A and 0B (Gemini).
2. ★ Shot 8, ★ Shot 2, ★ Shots 4 and 5: the shots that make the video work.
3. Shots 6, 7, 3, 9, 10, 11.
4. Shot 1 last. If credits run out, I can animate its picture myself (rain, steam and a camera move are easy for me in code).

**Any shot you only get a picture for**, without video credits, still works. Send me the picture and I'll add rain,
steam, light, sparkles and camera moves myself, so the reel never stalls.

## What to send me
- `shot01.mp4` … `shot11.mp4` (or `shotNN.png` if a shot has a picture only)
- A screen recording of the 30 s of *Nenchaadiye* you'll use, so I can find the beats (not used in the video)
