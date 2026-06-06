#!/usr/bin/env bash
# Rebuild the "My Week as a Smoothie" YouTube Short (optimized 25s cut).
#
# Inputs (place alongside this script before running):
#   f1_hyped.png  - smoothie, arms up / hyped      (Monday)
#   f2_happy.png  - smoothie, calm & happy          (Tuesday / Wednesday)
#   f3_tired.png  - smoothie, sweating / drained     (Thursday)
#   f4_out.png    - smoothie, dizzy / knocked over   (Friday)
#   audio.mp3     - backing track (first 25s is used)
#
# Requirements: ffmpeg, python3 with pillow numpy scipy.
set -euo pipefail
cd "$(dirname "$0")"

# 1) Flood-fill the solid white background to transparent (keeps interior
#    whites: eyes, straw, umbrella, dizzy spirals).
python3 process.py

# 2) Generate the dynamic filter_complex graph (pops, bounces, jitter,
#    drunk-wobble, spring-in captions) — timing math lives here.
python3 gen_filter.py

# 3) Composite: animated pink gradient + per-day character animation +
#    captions, muxed with a trimmed/faded 25s slice of the track.
ffmpeg -hide_banner -loglevel warning -stats \
  -f lavfi -i "gradients=s=1080x1920:c0=0xFF4D97:c1=0xFFC2DF:x0=0:y0=1920:x1=1080:y1=0:d=25:speed=0.06" \
  -loop 1 -i f1_t.png -loop 1 -i f2_t.png -loop 1 -i f3_t.png -loop 1 -i f4_t.png \
  -i audio.mp3 \
  -filter_complex_script filter_fast.txt \
  -map "[vout]" -map 5:a \
  -af "afade=t=in:st=0:d=0.12,afade=t=out:st=24.5:d=0.5" \
  -t 25 -r 30 \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  smoothie_week_short.mp4 -y

echo "Wrote smoothie_week_short.mp4"
