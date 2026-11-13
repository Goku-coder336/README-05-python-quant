# Delivery note

## Files
- `renders/barcelona_2014-15_full.mp4`: picture, voice, music and effects.
- `renders/barcelona_2014-15_nomusic.mp4`: picture, voice and effects only.
- Both are 1920x1080, 30 fps, about 7:03.

## Sound
- I measured the sound but could not listen to it. The voice is set to about -16 LUFS and the music to -22 LUFS, ducked about 45% under the voice. Each file is finished at about -15 LUFS with a true peak limit of -1.5 dBTP.
- Every voice line was checked with speech to text. One flag is left on purpose: 7.6b ("Juventus'"), where the transcriber writes "Juventus's". The voice says it correctly.

## Accuracy changes from the earlier script
- Messi as top assister: left out (UEFA 6, ESPN 4).
- Shot counts in the final: left out (StatsBomb 17 v 15, UEFA 18 v 14).
- 290 for Messi is described as StatsBomb "events", not on-ball actions.
- No claims about why anything happened, and no photos.

## Weakest moment
- Chapter 5 opens on a short empty board before the Berlin title lands.

## Check warnings kept on purpose
- `rotation_pivot_drift` on Pip's arms and legs: the limbs turn about their joints, so the drift is intended.
- Overlapping tweens on Pip: each pose takes over from the last one.
