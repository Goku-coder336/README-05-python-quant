# YouTube package: Word Song #01 (French "-eau"), v5

Made with the youtube-agent skills: yt-viral, yt-package, yt-seo, yt-script, yt-shorts, yt-edit, yt-comment. Nothing here publishes: copy it into YouTube Studio or the app when you upload.

- **Upload:** `renders/01-french-eau-v5-music.mp4` (36.7 s, vertical, so YouTube makes it a Short). Keep `-nomusic` for Instagram if you want to add a trending sound there.
- Voice profile used for every line below: `~/.claude/youtube/voice.md` (deadpan Barnaby, curious Odette, British spelling, one call to action).

## 1. What's working in this niche (yt-viral)

Shorts ranked by how far each beat its own channel's median (100 Shorts, 3 channels, read through public listings on 19 Nov 2026):

| Multiple | Views | Channel median | Short |
|---|---|---|---|
| 160x | 3.2M | 20K | 7 Minute Language School: "10 Useful Phrases in Spanish" |
| 9.2x | 377 | 41 | PronounceRight: "Braille (Can You Say It Right?)" |
| 5.7x | 1.1K | 194 | "Spanish is easy right?" channel: "Spanish is easy right ? Song" |
| 4.3x | 177 | 41 | PronounceRight: "Liaise (Can You Say It Right?)" |
| 3.3x | 66K | 20K | 7 Minute Language School: "The Most basic Spanish phrases for Beginners!" |

**The one thing they share:** the viewer already half-knows the words. Everyday phrases, words they already say (and maybe say wrong), or a song they've already heard. That fits ours: water, hat, bird, boat, cake.

**What we can use this week:** the reference song is literally called "Spanish Is Easy, Right?", and copies of it beat their channels several times over, so people search for that phrase. Our title borrows the phrase, not the joke: our words and sentence are our own.

(The formula labels from the tool were mostly "Unclassified"; they describe titles, not why a video worked.)

## 2. Title and thumbnail (yt-package)

**Title (100/100, 39 characters, fits the mobile feed):**

```
French is easy, right? 8 words, 1 sound
```

| Runner-up | Score | Note |
|---|---|---|
| French is easy: 8 words, 1 sound | 100 | no trend phrase |
| You can sing 8 French words by tonight | 100 | a promise, not the hook |
| Why do 8 French words all end in "eau"? | 98 | repeats "eau" from the thumbnail |

**Thumbnail (Shorts frame picker):** the frame at about **6.2 s**, "SPOT THE DIFFERENCE / EAU · HAUT · OH". Three big words, none of them in the title. Barnaby's raised eyebrow is in shot, and the cream background holds contrast at feed size. Second choice: the drawing frame at about 27 s ("LE BEL OISEAU AU CHAPEAU", the bird in the top hat).

## 3. Description, tags and hashtags (yt-seo)

```
French is easy, right? 8 French words that all sound like "oh": eau, haut, chapeau, oiseau, bateau, gâteau, château, couteau.
Then we stitch them into one sentence and sing it.

Le bel oiseau au chapeau, sur le bateau, coupe le gâteau du château au couteau… et tombe à l'eau !
(The fine bird in a hat, on the boat, cuts the castle's cake with a knife… and falls in the water!)

eau = water · haut = high · chapeau = hat · oiseau = bird · bateau = boat · gâteau = cake · château = castle · couteau = knife

Can you sing it in one breath? Try it in the comments.

Animation drawn in code. Voices and song made with AI (ElevenLabs).

#shorts #learnfrench #frenchiseasy
```

**Tags** (a weak signal, kept short):

```
french is easy right, learn french, french words, french pronunciation, eau, french for beginners, funny french, french song, language learning, animated short
```

**Query test** (title and the first two description lines contain the words for each):

- "french is easy right": title, line 1, hashtag.
- "french words that sound the same": line 1 has "French words" and "all sound like".
- "french eau words": line 1 lists every "-eau" word.

## 4. The hook and the loop (yt-script, yt-shorts)

**Opening lines scored with hookscore.py.** The tool was tuned on talking-head hooks, so treat a low score as "look again", not a verdict.

| Opening | Score | Formula |
|---|---|---|
| You'll never forget these 8 French words. Here's why. | 58, workable | The Impossible Claim (a soft overclaim; against our voice rules) |
| 8 French words in 20 seconds, but you only need to learn one sound. | 51 | The Clock |
| You can learn 8 French words in 20 seconds. | 48 | The Clock |
| How do you say water in French? (Odette's line) | 42 | The Question |
| French is easy. (current) | 26 | none |

**Verdict:** the spoken hook stays. "French is easy." is the series' deadpan catchphrase and the joke the whole reel pays off. What the Shorts skill flags is that **the on-screen text in the first 2 seconds repeats the spoken line word for word** ("FRENCH IS EASY"). Suggested fix, not applied yet: keep the voice, change the first on-screen card to **"8 WORDS. 1 SOUND."** so the eye and the ear get two different reasons to stay. It's a small rebuild of the hook card (about 10 minutes of rendering).

**Loop point (already works):** the reel ends on Barnaby's deadpan "Easy." and cuts back to frame 0, where he says "French is easy." The ending sets up the opening, so it replays cleanly.

## 5. Edit check (yt-edit)

`deadair.py` on the timed transcript flagged 11 gaps totalling 1.7 s. None should be cut:

- the 0.5 s gaps before each French answer are the "guess it" beat (cue, then answer);
- 5.4 to 5.8 s is the "EAU · HAUT · OH, same." gag;
- 29.0 to 29.5 s is the music between sung lines;
- 34.1 to 34.6 s is the splash before "Easy.".

The cut of the 1, 2, 3 count-in (v5) already removed the only dead stretch. Length 36.7 s is inside our 30 to 40 s target.

## 6. Comments (yt-comment)

**Pin this (your own comment, posted right after upload):**

```
Your turn: sing the whole line in one breath 🎤
Le bel oiseau au chapeau, sur le bateau, coupe le gâteau du château au couteau… et tombe à l'eau !
```

**Ready replies for the comments that will come (each under 30 words):**

| Comment type | Reply |
|---|---|
| "Is haut really said 'oh'?" | Yes. The h and the t are both silent, so haut sounds exactly like eau. French is easy. |
| "Do Spanish / Italian next!" | Noted. Which word should be in it? |
| A correction that is right | You're right, thank you. Fixing it in the next one. |
| Someone sings it in the comments | Chapeau. 🎩 (that's "hats off" in French) |
| Praise | (Heart it. Reply to a few with something specific from their comment.) |
| Bait or rudeness | Don't reply. |

Pin the most common real question once comments arrive if it beats the sing-it prompt.

## 7. After it's live (yt-retention, yt-audit)

- **48 hours after posting:** Studio → this Short → Analytics → Engagement → audience retention → download. Send me the file and yt-retention will find exactly where viewers leave.
- **Channel audit:** send the channel link once 3 or more videos are up.
- **yt-chapters:** not used. Shorts don't show chapters.

## Ship it, or change it?
