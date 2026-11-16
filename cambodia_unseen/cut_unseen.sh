#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
U=~/workspace/cambodia_unseen
M=~/workspace/cambodia_montage
S01=$(ls $U/media-generation-cambodia-unseen-s01-mondulkiri-*.mp4 | head -1)
S02=$(ls $U/media-generation-unseen-s02-mondulkiri-person-*.mp4 | head -1)
S03=$(ls $U/media-generation-unseen-s03-salt-workers-*.mp4 | head -1)
S05=$(ls $U/media-generation-unseen-s05-salt-aerial-*.mp4 | head -1)
S06=$(ls $U/media-generation-unseen-s06-volcanic-lake-*.mp4 | head -1)
S07=$(ls $U/media-generation-unseen-s07-bamboo-weaving-*.mp4 | head -1)
S09=$(ls $U/media-generation-unseen-s09-fishermen-boat-*.mp4 | head -1)
OMPIL=$(ls $M/media-generation-cambodia-s07-koh-ompil-*.mp4 | head -1)
ISLAND=$(ls $M/media-generation-cambodia-s10-island-aerial-*.mp4 | head -1)
F="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0.3,1.8)'"
# S01 2.7s + CAMBODIA 1.5s
ffmpeg -y -v error -ss 0 -i "$S01" -t 2.7 -vf "$F,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s01.mp4
# S02 2.2s
ffmpeg -y -v error -ss 0 -i "$S02" -t 2.2 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s02.mp4
# S03 3.0s
ffmpeg -y -v error -ss 0 -i "$S03" -t 3.0 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s03.mp4
# S04 0.9s: S03 2.0-2.9s, 1.5x center zoom crop
ffmpeg -y -v error -ss 2.0 -i "$S03" -t 0.9 -vf "crop=480:853:120:213,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s04.mp4
# S05 1.9s
ffmpeg -y -v error -ss 0 -i "$S05" -t 1.9 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s05.mp4
# S06 2.5s
ffmpeg -y -v error -ss 0 -i "$S06" -t 2.5 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s06.mp4
# S07 1.8s
ffmpeg -y -v error -ss 0 -i "$S07" -t 1.8 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s07.mp4
# S08 2.9s: S02 0-5.8s sped 2x
ffmpeg -y -v error -ss 0 -i "$S02" -t 5.8 -vf "setpts=0.5*PTS,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s08.mp4
# S09 3.4s
ffmpeg -y -v error -ss 0 -i "$S09" -t 3.4 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s09.mp4
# S10 2.7s: Koh Ompil 3.5-6.2s (person on beach)
ffmpeg -y -v error -ss 3.5 -i "$OMPIL" -t 2.7 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s10.mp4
# S11 2.8s: island aerial 0-2.8s
ffmpeg -y -v error -ss 0 -i "$ISLAND" -t 2.8 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s11.mp4
# S12 2.8s: Koh Ompil 0-2.8s (high aerial coastline)
ffmpeg -y -v error -ss 0 -i "$OMPIL" -t 2.8 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s12.mp4
# S13 1.9s: S01 source 5.0-6.9s (cloud hills, ends bright)
ffmpeg -y -v error -ss 5.0 -i "$S01" -t 1.9 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s13.mp4
for f in cut_s01.mp4 cut_s02.mp4 cut_s03.mp4 cut_s04.mp4 cut_s05.mp4 cut_s06.mp4 cut_s07.mp4 cut_s08.mp4 cut_s09.mp4 cut_s10.mp4 cut_s11.mp4 cut_s12.mp4 cut_s13.mp4; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  echo "$f $d"
done
