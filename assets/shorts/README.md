# My Week as a Smoothie — YouTube Short

A vertical 1080×1920 / 30fps / ~64s Short built from four smoothie-character
illustrations and a backing track.

![cover](cover.jpg)

## The hook
Relatable "decline" meme: the same little smoothie deteriorates across the
work week. Each day swaps the character art and the energy of its animation:

| Beat | Day | Art | Animation | Caption |
|------|-----|-----|-----------|---------|
| 0–12s  | MONDAY    | arms-up, hyped     | big fast bounce        | NEW WEEK / NEW ME |
| 12–25s | TUESDAY   | calm & happy       | happy sway-bounce      | STILL / GOT THIS |
| 25–38s | WEDNESDAY | calm & happy       | smaller, slower bounce | HALFWAY / THERE... |
| 38–51s | THURSDAY  | sweating, drained  | low trembling jitter   | RUNNING ON / FUMES |
| 51–64s | FRIDAY    | dizzy, knocked over| slow drunk wobble      | I MADE IT / ...BARELY |

Bounce amplitude shrinks beat by beat so the character visibly runs out of
energy as the week goes on.

## Files
- `smoothie_week_short.mp4` — the finished Short (H.264 + AAC, faststart).
- `cover.jpg` — thumbnail (Monday frame).
- `process.py` — flood-fills the solid white image backgrounds to transparent
  via edge-connected labeling, preserving interior whites (eyes, straw,
  umbrella, dizzy spirals).
- `filter.txt` — the ffmpeg `filter_complex` graph (gradient bg, time-gated
  character overlays with animated position/rotation, burned-in captions).
- `build.sh` — end-to-end rebuild.

## Rebuild
Drop the four source PNGs (`f1_hyped.png`, `f2_happy.png`, `f3_tired.png`,
`f4_out.png`) and `audio.mp3` next to the scripts, then:

```bash
./build.sh
```

Needs `ffmpeg` and `python3` with `pillow numpy scipy`.

## Publishing tips
- Upload vertical; YouTube auto-classifies <3min vertical video as a Short.
- Suggested title: **"My week as a smoothie 🥤"**
- Suggested tags: `#shorts #relatable #mood #smoothie #workweek`
