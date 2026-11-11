# Run of the Champions: project rules

A YouTube series. Each episode covers one Champions League winner's full run, from the group stage
(or the league phase from 2024/25) to the final, for every final from 2014/15 to 2025/26.

## Roles
- The user makes the analysis choices, picks the patterns, edits the video and publishes it.
- The user does NOT write code. Claude writes and runs all code and hands over finished files.

## Format
- Long-form YouTube, horizontal 16:9 (1920x1080), 5 to 8 minutes.
- AI voiceover. From Episode 1 on, Claude makes it offline with Kokoro (voice `bf_emma`, Apache 2.0;
  `code/voiceover.py`, spoken respellings for names in `RESPELL`) and renders the finished video in
  Remotion. CapCut text-to-speech is the fallback if the user edits by hand. Write scripts for the ear:
  short sentences, about 150 words per minute, 800 to 1,200 words.
- Chapters: hook, context, group stage (or league phase), each knockout round, the final, verdict.
- The user edits in CapCut. Deliver ready-made MP4 clips and PNG charts, plus a shot list that says
  which clip goes with which part of the script.

## Visuals
- Animated clips: 2D pitch with player dots, passing lanes, pressing patterns, route charts.
- Render as MP4, 1920x1080, 30 fps, dark background `#1a1a19`.
- Tools: Remotion (React, in each episode's `remotion/` folder) for the animated clips, Python
  (`statsbombpy`) to check and export the data the clips use. The user switched from matplotlib to
  Remotion in Episode 1 Step 5. Rendering needs `remotion.media` on the environment's allowed hosts.
- Any animated recreation of a real goal must say "reconstruction" on screen.
- Every chart that uses StatsBomb data carries the credit "Data: StatsBomb open data".
- No broadcast footage, club badges or UEFA logos. Player names are fine.
- Photos: only free-licence photos (Wikimedia Commons), each credited on screen (photographer, licence)
  and in the description. Captions say who, where and when, so a photo from another match or date never
  looks like the one being described. Club crests on shirts in these photos are incidental; the user
  asked for photos in Episode 1. Commons rate-limits this cloud connection, so fetch slowly.

## Data and facts
- StatsBomb open data (free, via `statsbombpy`) covers Champions League finals only up to 2018/19.
- For later finals, and for every non-final match, use verified results only. Never invent stats.
- Only use facts the user has verified, or facts Claude verifies from a reliable source and cites.
- If two sources disagree, tell the user and do not pick one silently.
- When StatsBomb and UEFA figures differ (for example shot counts), say "according to StatsBomb".

## Writing style
- British spelling.
- No em dashes anywhere (scripts, captions, descriptions, charts, posts, this file).
- No AI buzzwords: leverage, robust, seamless, transformative, impactful, game-changer.

## Way of working
- Work step by step. Before each new step, stop and ask the user a question.
  Do not move on until they answer.

## Episode pipeline
1. Verified run
2. Data and charts
3. Voiceover script with timestamps and chapter titles
4. Shot list matching each script line to a chart or clip
5. Render the animated clips (MP4)
6. CapCut assembly guide, YouTube title, description with sources and chapters, thumbnail text
7. Blog post version of the analysis, plus a publishing guide (the user publishes on a blog, Substack
   recommended; no LinkedIn samples to match, so the voice is a clear analyst telling the story)

## Episode status

### Episode 1: Barcelona 2014/15
Steps 1 and 2 done (by the user). Step 3 done: `episodes/01-barcelona-2014-15/script.md` (hook B, the Messi paradox). Step 4 done: `episodes/01-barcelona-2014-15/shotlist.md` (clip codes C1 to C5, three YOUR CHART slots). Step 5 done: all 12 clips in `episodes/01-barcelona-2014-15/clips/` (MP4, 1920x1080, 30 fps, each at its minimum length), remade in Remotion at the user's request: project `episodes/01-barcelona-2014-15/remotion/`, render with `sh render-clips.sh`. The first matplotlib versions are in git history; `code/` still holds the StatsBomb check and `export_remotion_data.py`. Contact sheet `clips/contact_sheet.png`. StatsBomb figures for the final re-checked before rendering and all match this file. Waiting for the user's change notes on the clips. Step 6 done: `episodes/01-barcelona-2014-15/capcut_guide.md` (assembly guide with sync words) and `youtube.md` (title option c, "Run of the Champions: Barcelona 2014/15"; thumbnail text "8 GOALS. THEN 2."; description with chapters and checked source links). Chapter times there are script estimates until the user's final edit. Step 7 done: `episodes/01-barcelona-2014-15/publish/` holds `blog_post.md`, `blog-images/` (6 frames from the clips), `thumbnail.png` (Remotion still `Thumbnail`) and `publishing_guide.md` (YouTube upload, Substack setup, sharing). Finished video: `publish/episode1_barcelona_2014-15.mp4` (6:14, voiceover by Kokoro bf_emma, Remotion composition `Episode1-full`, render with `sh remotion/render-episode.sh`; youtube.md chapters match it). Photos added at the user's request (Episode1-full): Messi full frame on L03 to L05, the three forwards on L10 to L11, picture-in-picture for Suárez (L28 to L29), Neymar (L34 to L36) and Messi (L40), Iniesta on L61; credits in `remotion/public/photos/CREDITS.md` and youtube.md. Wanted but blocked by Wikimedia rate limits: Luis Enrique, the 2015 final in Berlin, the team after the final, Xavi, Rakitić, fans in Berlin. Stand-ins for the three Step 2 chart slots until the user sends theirs: L23 to L24 C1b held on the group half; L45 to L48 a top scorers and assisters chart (UEFA figures); L60 Messi's 71 passes in the final (StatsBomb). No music yet. Open wording check: L60 says "290 on-ball actions", but 290 is Messi's total StatsBomb events (it includes 6 pressures and 3 fouls committed); the on-screen chart says "actions recorded by StatsBomb". Waiting for the user's notes on the finished video. Charts and run_goals.csv are not in the repo yet.

Verified run (Barcelona score first):
- MD1 APOEL home W 1-0 (Piqué)
- MD2 PSG away L 2-3 (Messi, Neymar)
- MD3 Ajax home W 3-1 (Neymar, Messi, Sandro)
- MD4 Ajax away W 2-0 (Messi 2)
- MD5 APOEL away W 4-0 (Messi 3, Suárez)
- MD6 PSG home W 3-1 (Messi, Neymar, Suárez). Won Group F, 15 pts, PSG 13.
- R16 Man City away W 2-1 (Suárez 2), home W 1-0 (Rakitić). Agg 3-1
- QF PSG away W 3-1 (Neymar, Suárez 2), home W 2-0 (Neymar 2). Agg 5-1
- SF Bayern home W 3-0 (Messi 2, Neymar), away L 2-3 (Neymar 2). Agg 5-3
- Final, 6 June 2015, Olympiastadion Berlin: Juventus 1-3 Barcelona.
  Rakitić 4', Morata 55', Suárez 68', Neymar 90+7'. Man of the Match: Iniesta.
- Totals: 13 played, 11 won, 2 lost (both away), 31 scored, 11 conceded.

Key findings (verified):
- Messi scored 8 of 15 group goals but 2 of 16 knockout goals. Neymar (7) and Suárez (5) scored
  12 of the 16 knockout goals.
- Messi was the competition's top assister with 6. Messi, Neymar and Ronaldo shared top scorer on 10.
  Sources disagree on assists: UEFA (official) has Messi top on 6; ESPN's stats page has Iniesta 5,
  Messi 4. The episode uses UEFA's figure and cites it.
- StatsBomb final data: Barcelona 2.27 xG from 17 shots, Juventus 1.38 xG from 15 shots (UEFA
  official shots: 18 v 14, so say "according to StatsBomb"). Passes 600 v 377. Pressures: Juventus
  144, Barcelona 122. Messi had the most on-ball actions for Barcelona (290, 71 passes).
- Second treble for Barcelona; first European club to win the treble twice.
- Xavi's 767th and final Barcelona appearance.
- Luis Enrique's first season; he called it "a transitional year". The same coach later won the
  Champions League with PSG in 2025 and 2026.

Chosen angle: the Luis Enrique bookend as the series frame, with "Messi went from scorer to creator
while Neymar and Suárez took over the goals" as the analysis inside it.

Planned Step 5 clips: route chart build-up, scorer split animation, final xG timeline, shot map, and a
labelled reconstruction of Rakitić's 4th-minute goal from StatsBomb event data.
