#!/bin/bash
# recut_v8.sh — CAMBODIA v8 (V2.2): replace 6 shots, keep 7, no text, 1080x1920 30fps.
# V2.2 timeline (30fps, 946 frames, 31.533s):
# S01 2.70 | S02 2.20 + S03 3.00 xfade 0.3 = 4.90 | S04 0.90 | S05 1.90 | S06 2.50
# S07 1.83 | S08 2.90 | S09 3.40 | S10 2.70 | S11 2.83 | S12 2.83 | S13 2.14
# Sources are 720x1280 24fps; final encode upscales to 1080x1920 30fps.
set -e
cd ~/workspace/cambodia_unseen

S01G=media-generation-unseen-s01-island-ridge-g-0-c3f8a202-837f-44a0-ae31-a6424a6f1fd4.mp4
S02N=media-generation-v8-s02-golden-hills-walker-0-d7741ede-2c15-46a8-bbbb-ad75b4ca8d2c.mp4
S03M=media-generation-unseen-s03-salt-morning-0-0c0b197b-a294-4b4e-82ef-15153f72b9f4.mp4
S04N=media-generation-v8-s04-salt-rake-closeup-0-0567ac11-0c0b-4740-a222-11c6580b0e3e.mp4
S05M=media-generation-unseen-s05-salt-aerial-morning-0-36141b75-ae66-46f8-83b5-68a00f741f62.mp4
S06I=media-generation-unseen-s06-yeaklaom-i-0-df5aec6a-bddf-4128-9eeb-faaf166be2f1.mp4
S07=$(ls media-generation-unseen-s07-bamboo-weaving-*.mp4 | head -1)
S08L=media-generation-unseen-s08-fpv-ridge-l-0-a97cb1c8-9cfc-4061-b03f-40de926a9492.mp4
S09N=media-generation-v8-s09-tonlesap-nethaul-0-682e2102-1156-47c9-9937-98b2a9ab6dcf.mp4
S10N=media-generation-v8-s10-beach-lone-walker-0-4022718d-8a60-4234-88af-7149f6af79c3.mp4
S12N=media-generation-v8-s12-coastline-topdown-0-4898f883-3907-4bf5-a557-53d1ee58563b.mp4

# S01: G 0-2.7s, no desat, NO TEXT
ffmpeg -y -v error -i "$S01G" -t 2.7 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s01.mp4

# S02: NEW 3.0-5.2s (walker in frame throughout), sat 0.8
ffmpeg -y -v error -i "$S02N" -vf "trim=start=3.0:end=5.2,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s02.mp4

# S03: morning 0-3.0s, no desat
ffmpeg -y -v error -i "$S03M" -t 3.0 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s03.mp4

# S02+S03 xfade (fade 0.3s, offset 1.908) — the film's single dissolve
ffmpeg -y -v error -i cut_v8_s02.mp4 -i cut_v8_s03.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.908,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 21 -r 24 -an cut_v8_s02s03.mp4

# S04: NEW 1.0-1.9s (rake pushing), no desat
ffmpeg -y -v error -i "$S04N" -vf "trim=start=1.0:end=1.9,setpts=PTS-STARTPTS,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s04.mp4

# S05: morning aerial 0-1.9s, no desat
ffmpeg -y -v error -i "$S05M" -t 1.9 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s05.mp4

# S06: I 0-2.5s, no desat
ffmpeg -y -v error -i "$S06I" -t 2.5 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s06.mp4

# S07: bamboo 0-1.83s, no desat
ffmpeg -y -v error -i "$S07" -t 1.83 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s07.mp4

# S08: L 1.0-3.9s, sat 0.8
ffmpeg -y -v error -i "$S08L" -vf "trim=start=1.0:end=3.9,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s08.mp4

# S09: NEW 6.2-9.6s (pull-back to full boat), sat 0.8
ffmpeg -y -v error -i "$S09N" -vf "trim=start=6.2:end=9.6,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s09.mp4

# S10: NEW 2.5-5.2s (walker fully in frame), sat 0.8
ffmpeg -y -v error -i "$S10N" -vf "trim=start=2.5:end=5.2,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s10.mp4

# S12: NEW 1.0-3.83s (top-down coastline), sat 0.8
ffmpeg -y -v error -i "$S12N" -vf "trim=start=1.0:end=3.83,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s12.mp4

# S13: G 5.0-7.14s (2.14s, loop close), sat 0.8
ffmpeg -y -v error -i "$S01G" -vf "trim=start=5.0:end=7.14,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v8_s13.mp4

for f in cut_v8_s01.mp4 cut_v8_s02s03.mp4 cut_v8_s04.mp4 cut_v8_s05.mp4 cut_v8_s06.mp4 cut_v8_s07.mp4 cut_v8_s08.mp4 cut_v8_s09.mp4 cut_v8_s10.mp4 cut_v8_s12.mp4 cut_v8_s13.mp4; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$f $d"
done
echo "V8 CUTS DONE (S11 pending)"
