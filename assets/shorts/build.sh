#!/usr/bin/env bash
# Rebuild the "My Week as a Smoothie" YouTube Short.
#
# Inputs (place alongside this script before running):
#   f1_hyped.png  - smoothie, arms up / hyped      (Monday)
#   f2_happy.png  - smoothie, calm & happy          (Tuesday / Wednesday)
#   f3_tired.png  - smoothie, sweating / drained     (Thursday)
#   f4_out.png    - smoothie, dizzy / knocked over   (Friday)
#   audio.mp3     - ~64s backing track
#
# Requirements: ffmpeg, python3 with pillow numpy scipy.
set -euo pipefail
cd "$(dirname "$0")"

# 1) Flood-fill the solid white background to transparent (keeps interior
#    whites: eyes, straw, umbrella, dizzy spirals).
python3 process.py

# 2) Composite: animated pink gradient + per-day character animation + captions.
ffmpeg -hide_banner -loglevel warning -stats \
  -f lavfi -i "gradients=s=1080x1920:c0=0xFF5C9E:c1=0xFFD9EA:x0=0:y0=0:x1=1080:y1=1920:d=64:speed=0.010" \
  -loop 1 -i f1_t.png -loop 1 -i f2_t.png -loop 1 -i f3_t.png -loop 1 -i f4_t.png \
  -i audio.mp3 \
  -filter_complex_script filter.txt \
  -map "[vout]" -map 5:a \
  -t 64 -r 30 \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  smoothie_week_short.mp4 -y

echo "Wrote smoothie_week_short.mp4"
