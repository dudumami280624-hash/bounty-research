#!/bin/bash
# cut_v9.sh — CAMBODIA v9: all 13 shots from REAL footage.
# Timeline (30fps, same as v8): S01 81f | S02+S03 147f (dissolve 0.3s) | S04 27f | S05 57f | S06 75f | S07 55f | S08 87f | S09 102f | S10 81f | S11 85f | S12 85f | S13 64f = 946f, 31.533s
set -e
cd ~/workspace/cambodia_unseen
R=real_footage
REF=$R/reference

# S01 cloud sea — Pexels 4288015, 13.5-16.2s (deep green ridge + cloud sea)
ffmpeg -y -v error -ss 13.5 -i $R/s01_cloudsea_4288015.mp4 -t 2.7 \
  -vf "crop=810:1440:875:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s01.mp4

# S02 golden hills — from-Above, 28.0-30.2s (golden grassland + dirt track + tiny people)
ffmpeg -y -v error -ss 28.0 -i $REF/mondulkiri_above_1080.mp4 -t 2.2 \
  -vf "crop=608:1080:656:0,eq=saturation=0.8,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s02.mp4

# S03 salt workers — FB reel, 2.0-5.0s (ponds + workers + mountains)
ffmpeg -y -v error -ss 2.0 -i $REF/kampot_salt_bestofcambodia.mp4 -t 3.0 \
  -vf "scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s03.mp4

# S02+S03 with 0.3s dissolve (offset 1.9s) -> 147f
ffmpeg -y -v error -i cut_v9_s02.mp4 -i cut_v9_s03.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.9,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s02s03.mp4

# S04 rake close-up — IG salt, 13.5-14.4s (transpose=2 corrects sideways storage)
ffmpeg -y -v error -ss 13.5 -i $REF/kampot_salt_ig.mp4 -t 0.9 \
  -vf "transpose=2,crop=405:720:437:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s04.mp4

# S05 salt aerial — IG salt, 25.0-26.9s (pond grid + red roofs)
ffmpeg -y -v error -ss 25.0 -i $REF/kampot_salt_ig.mp4 -t 1.9 \
  -vf "transpose=2,crop=405:720:437:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s05.mp4

# S06 Yeak Laom lake — BT Food Story, 9.0-11.5s (clean circular lake, no text)
ffmpeg -y -v error -ss 9.0 -i $REF/yeaklaom_btfoodstory.mkv -t 2.5 \
  -vf "crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s06.mp4

# S07 bamboo splitting — Pexels 2121092, 3.0-4.83s
ffmpeg -y -v error -ss 3.0 -i $R/s07_bamboo_2121092.mp4 -t 1.83 \
  -vf "crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s07.mp4

# S08 REPLACEMENT: golden plain sped up 2x — from-Above, trim 296.0-301.8s (setpts, per v8 lesson: trim in filter, not -ss)
ffmpeg -y -v error -i $REF/mondulkiri_above_1080.mp4 \
  -vf "trim=start=296.0:end=301.8,setpts=0.5*PTS,crop=608:1080:656:0,eq=saturation=0.8,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s08.mp4

# S09 sunset fisherman — Tonle Sap, 93.8-97.2s (fisherman + boat + net, no subtitle)
ffmpeg -y -v error -ss 93.8 -i $REF/tonlesap_traps.mp4 -t 3.4 \
  -vf "crop=202:360:380:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s09.mp4

# S10 beach walker — Pexels 39482006, 15.0-17.7s (native vertical)
ffmpeg -y -v error -ss 15.0 -i $R/s10_beach_39482006.mp4 -t 2.7 \
  -vf "scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s10.mp4

# S11 Koh Rong — user's own, 39.0-41.83s, x=400 (same as v8)
ffmpeg -y -v error -ss 39.0 -i s11_8426080_koh_rong.mp4 -t 2.83 \
  -vf "crop=405:720:400:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s11.mp4

# S12 top-down coast — Pexels 32349947, 13.0-15.83s
ffmpeg -y -v error -ss 13.0 -i $R/s12_coast_32349947.mp4 -t 2.83 \
  -vf "crop=810:1440:875:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s12.mp4

# S13 cloud sea closing — Pexels 4288015, 0-2.13s (fog)
ffmpeg -y -v error -ss 0 -i $R/s01_cloudsea_4288015.mp4 -t 2.13 \
  -vf "crop=810:1440:875:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s13.mp4

echo "--- cut specs ---"
for f in cut_v9_s01.mp4 cut_v9_s02s03.mp4 cut_v9_s04.mp4 cut_v9_s05.mp4 cut_v9_s06.mp4 cut_v9_s07.mp4 cut_v9_s08.mp4 cut_v9_s09.mp4 cut_v9_s10.mp4 cut_v9_s11.mp4 cut_v9_s12.mp4 cut_v9_s13.mp4; do
  ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,nb_read_frames -show_entries format=duration -of default=noprint_wrappers=1 "$f" | tr '\n' ' '; echo " <- $f"
done
echo "CUT_V9 DONE"
