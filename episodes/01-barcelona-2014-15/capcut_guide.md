# Episode 1 CapCut assembly guide: Barcelona 2014/15

How to put the episode together in CapCut from the files in this folder. Follow it top to bottom.

**You need:** `script-capcut.txt` (voiceover text, one line per script line), the 12 MP4s in `clips/`, and
your three Step 2 charts (not in the repo yet, see step 4). Line numbers (L01 to L79) match `script.md`
and `shotlist.md`.

## 1. Project settings

- New project, ratio **16:9**, resolution **1920x1080**.
- Set the project frame rate to **30 fps** (all clips are 30 fps).
- Background colour for text cards and gaps: **#1a1a19** (the same as the clips).

## 2. Voiceover first

The voiceover sets the timing, so lay it down before any picture.

1. Add a text layer, paste all of `script-capcut.txt`, and use **Text to speech** with the voice you chose.
2. Put the audio on the main audio track starting at 0:00, then delete the text layer.
3. Use **Split** at the start of each chapter (L01, L07, L14, L27, L33, L39, L49, L63) so you can nudge
   chapters separately. Leave about 0.3 s of silence between chapters if a cut feels rushed.
4. Write down the real start time of each chapter. You need them for the YouTube chapters (step 7).

The script timestamps were estimated at 150 words per minute, so the real audio will drift by a few
seconds. That is fine: you line clips up to the audio, not to the estimates.

## 3. Place the clips

Put every clip on the main video track. **Start each clip at the first word of the line in the "starts on"
column**, then check the sync word: the reveal in the clip should land on that word. If it lands early or
late, slide the clip (not the audio) until it does.

| starts on | file | in-point | sync check (clip time: word) | notes |
|---|---|---|---|---|
| L01 | `C1a_messi_paradox.mp4` | 0:00 | 4.2 s: "Eight." / 11.0 s: "two of them" | Runs to the end of L05. The slow zoom and the dim on "supplier" are built in. |
| L06 | TEXT CARD | | | See step 5. |
| L07 | TEXT CARD | | | See step 5. Keep the quote up through L09. |
| L10 | `C2_route_intro.mp4` | 0:00 | 2.0 s: "Messi." | Covers L10 to L13. |
| L14 | `C2a_route_group_stage.mp4` | 0:00 | 8.0 s: "Gerard Piqué" / 35.0 s: "fifteen points" | Covers L14 to L22. |
| L23 | YOUR CHART: group goals by scorer | | | No chart yet? Use `C1b_scorer_split.mp4` from **0:09** and **Freeze** that frame (group-stage half only) for L23 to L24. |
| L25 | `C2a_route_group_stage.mp4` | last frame | | **Freeze** the last frame through L25, then cut hard to black on "You would be wrong." (L26). |
| L27 | `C2b_route_r16.mp4` | 0:00 | 6.4 s: "Suárez" (L28) / 21.2 s: "not one goal from Messi" | Covers L27 to L32. |
| L33 | `C2c_route_qf.mp4` | 0:00 | 13.3 s: start of L37 | Covers L33 to L37. The dashed link to the MD2 defeat draws on L37. |
| L38 | `C1b_scorer_split.mp4` | 0:00 | 2.0 s: "Suárez four" | **Trim at 0:05.** Only the first 5 seconds go here. |
| L39 | `C2d_route_sf.mp4` | 0:00 | 4.4 s: "Twice" / 20.4 s: start of L44 | Covers L39 to L44. |
| L45 | YOUR CHART: top scorers and assisters | | | Placeholder. Must use your verified figures (Messi 6 assists, 10 goals, level with Neymar and Ronaldo). |
| L49 | `C2e_route_final.mp4` | 0:00 | 1.4 s: "The sixth of June" | 8 s clip. |
| L50 | `C5_rakitic_goal_reconstruction.mp4` | 0:00 | 3.6 s: ball in the net, just after "One-nil" | If you want the goal exactly on "One-nil", start the clip about half a second before L50. Do not crop: "RECONSTRUCTION" and the StatsBomb credit must stay visible. |
| L52 | `C3_final_xg_timeline.mp4` | 0:00 | 2.4 s: "equalised" / 22.6 s: "seventeen shots" | Covers L52 to L57 in one go. |
| L58 | `C4_final_shot_map.mp4` | 0:00 | | Add the lower third from step 5 over it. |
| L60 | YOUR CHART: Messi in the final | | | Placeholder. Needs "Data: StatsBomb open data" on screen. |
| L61 | TEXT CARD | | | See step 5. |
| L63 | `C2f_route_full.mp4` | 0:00 | 3.0 s: "Thirteen games" / 14.3 s: start of L66 | Covers L63 to L66. |
| L67 | `C1b_scorer_split.mp4` | **0:05** | 12.6 s: "Seven in the knockouts" | Set the in-point to 0:05 (the first 5 seconds were used at L38). Runs to the end of L74. |
| L75 | TEXT CARD | | | See step 5. |
| L78 | END CARD | | | See step 5. |

**If a clip is shorter than its lines:** select the last frame and use **Freeze** to hold it.
**If it is longer:** trim the tail. Each clip has about 2 seconds of spare tail for this.

## 4. Your three charts

The YOUR CHART slots at L23, L45 and L60 need your Step 2 PNGs. They are not in the repo yet. Until they
are, use the fallback for L23 above and leave L45 and L60 as gaps on your timeline so you can see them.
Send me the PNGs (or tell me to make them) and I will fill in the file names.

## 5. Text cards, end card and lower third

All on a **#1a1a19** background, font **Inter** (or CapCut's closest plain sans if Inter is missing),
left-aligned, at least 80 px from the edges. Colours: text **#f2f0ea**, Barcelona **#e0476a**,
Messi gold **#f2b84b**, grey for secondary lines **#9a978f**. No badges, logos or photos.

| line(s) | card |
|---|---|
| L06 | Large: **Run of the Champions**. Below, smaller: **Barcelona 2014/15** |
| L07 to L09 | First: **Luis Enrique. First season.** Then, on "transitional year", add the quote: **"A transitional year"** |
| L58 to L59 (lower third over C4) | **Passes: Barcelona 600, Juventus 377** then **Pressures: Juventus 144, Barcelona 122**, with **according to StatsBomb** underneath in grey. Keep it in the bottom 220 px (left clear in the clip). |
| L61 to L62 | **Man of the Match: Andrés Iniesta**, then **Xavi: 767th and final appearance** |
| L75 to L77 | **"A transitional year"** returns. Then one line: **2015 Barcelona · 2025 PSG · 2026 PSG** |
| L78 to L79 | **Next: 2015/16**, leaving room for YouTube's end screen elements (right half of the frame, last 5 to 20 seconds) |

Transitions: hard cuts throughout. The only special one is the cut to black on "You would be wrong." (L26).

## 6. Sound and export

- Voiceover: aim for a steady level with peaks around -6 dB. Use CapCut's **Normalise loudness** on the
  voice track if it has it.
- Music is optional. If you add it, keep it well under the voice (around -25 dB) and use a track you are
  licensed to use on YouTube, such as one from the YouTube Audio Library.
- Export: **1080p, 30 fps, MP4**, bitrate "Recommended" or higher.

## 7. Before you upload

1. Watch the whole export once. Check every sync word in the table above.
2. Write down the real start time of each chapter and update the chapter list in `youtube.md`. The first
   chapter must stay at 0:00, and every chapter must be at least 10 seconds long.
3. Check that "RECONSTRUCTION" and "Data: StatsBomb open data" are visible in C5, and the credit in C3 and C4.
