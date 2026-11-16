#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
U=~/workspace/cambodia_unseen
M=~/workspace/cambodia_montage
S01=$(ls $U/media-generation-cambodia-unseen-s01-mondulkiri-*.mp4 | head -1)
S02=$(ls $U/media-generation-unseen-s02-mondulkiri-person-*.mp4 | head -1)
S03=$(ls $U/media-generation-unseen-s03-salt-workers-*.mp4 | head -1)
S05=$(ls $U/media-generation-unseen-s05-salt-aerial-*.mp4 | head -1)
S09=$(ls $U/media-generation-unseen-s09-fishermen-boat-*.mp4 | head -1)
S08N=$(ls $U/media-generation-unseen-s08-fpv-low-*.mp4 | head -1)
DESAT="eq=saturation=0.8"
F="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0.3,1.8)'"
# S01 2.7s + CAMBODIA + desat
ffmpeg -y -v error -ss 0 -i "$S01" -t 2.7 -vf "$DESAT,$F,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s01.mp4
# S02 2.2s + desat
ffmpeg -y -v error -ss 0 -i "$S02" -t 2.2 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s02.mp4
# S03 3.0s + desat
ffmpeg -y -v error -ss 0 -i "$S03" -t 3.0 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s03.mp4
# S04 0.9s: S03 2.0-2.9s, 1.5x crop + desat
ffmpeg -y -v error -ss 2.0 -i "$S03" -t 0.9 -vf "$DESAT,crop=480:853:120:213,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s04.mp4
# S05 1.9s + desat
ffmpeg -y -v error -ss 0 -i "$S05" -t 1.9 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s05.mp4
# S08 2.9s: new FPV 2.5-5.4s + desat
ffmpeg -y -v error -ss 2.5 -i "$S08N" -t 2.9 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s08.mp4
# S09 3.4s + desat
ffmpeg -y -v error -ss 0 -i "$S09" -t 3.4 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s09.mp4
# S13 1.9s: S01 source 5.0-6.9s + desat
ffmpeg -y -v error -ss 5.0 -i "$S01" -t 1.9 -vf "$DESAT,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s13.mp4
# S02->S03 dissolve (from corrected cuts)
ffmpeg -y -v error -i cut_s02.mp4 -i cut_s03.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.908[v]" -map "[v]" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s02s03.mp4
# concat (S06, S07, S10, S11, S12 unchanged from before)
ffmpeg -y -v error -f concat -safe 0 -i concat_unseen.txt -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cambodia_unseen_31s_silent.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 cambodia_unseen_31s_silent.mp4
for t in 1.0 6.4 12.0 16.4 19.6 30.5; do ffmpeg -y -v error -ss $t -i cambodia_unseen_31s_silent.mp4 -frames:v 1 "v2_${t}s.jpg"; done
ls v2_*.jpg
