# Matchday Flat

Real football moments redrawn as flat illustration: the players move exactly as they did in the match, but every
shape on screen is ours. It's the look of the "who is this player?" football reels, built from the user's own
reference clips: the clip is only measured (17 body points per player per frame, plus the ball), never shown.
Use it for goals, skills and duels in vertical reels, with a hook question on top and the answer at the end.

## The look

- Background: one bold colour, deep teal (#1F8E86 lifting to #23A096 in the middle, #0D4A48 at the edges), with
  three wide, dark, soft diagonal brush streaks (#06303255) behind the action. No pitch, no crowd, no adverts.
- Players: flat fills on the measured skeleton. Tapered limbs, a four-corner torso, round faceless head with a
  hair shape (curly, short or thin from the cast sheet), one shadow tone on the far side of the shirt, limbs the
  pose can't see drawn a shade darker, and one dark outline (#14181B) round the whole silhouette.
- Kits: plain colours from `assets/players.js` and `flat.js` (Barcelona away #D6F53A with blue trim, PSG #1B2440
  with a red collar). Numbers on the back when the player faces away. No badges, no sponsors, no faces.
- Ball: white with a black pentagon and a dark outline, sized to the players.
- Ground: a dark soft brush-shadow under each player's feet.
- Type: Oswald Bold for the hook and the reveal (white with a hard teal-black drop, the name in kit yellow),
  Inter ExtraBold for captions on a dark pill, Inter SemiBold for the small "Recreation · based on match footage".

## How it moves

- The players follow the measured poses frame by frame, smoothed so nothing jitters.
- Slow motion (0.4x) on the moments that matter (a nutmeg, a shot), with a white flash, a whoosh and a quick
  punch-in on the way in; normal speed in between.
- The hook question sits at the top the whole time and gives way to the answer: the name slams in big with a
  small shake, then one factual line as a caption.
- The camera only pushes in slowly. No orbit, no shake except the reveal.

## Never

- Show any pixel of the broadcast: no crowd, adverts, scoreboard, badge or face.
- Draw a player we can only half see. Partly visible players are left out.
- Claim anything the footage or a verified source doesn't show.
- Copy another channel's colours, title text or watermark.

## Make one

1. `python recreate/poses.py CLIP.mp4 out.json --crop x,y,w,h --start S --end E --teams "BARA:#d6f53a,PSG:#1c2236,REF:#3aa0d8"`
2. `python recreate/prep.py out.json poses.js POSES_NAME`
3. Build the clip like `recreate/clip/index.html`: pick the slow-motion frames, the hook, the reveal and the line.
