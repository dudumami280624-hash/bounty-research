#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
U=~/workspace/cambodia_unseen
M=~/workspace/cambodia_montage
S01N=$(ls $U/media-generation-unseen-s01-cloudsea-a-0-*.mp4 | head -1)
S02=$(ls $U/media-generation-unseen-s02-mondulkiri-person-*.mp4 | head -1)
S03=$(ls $U/media-generation-unseen-s03-salt-workers-*.mp4 | head -1)
S05=$(ls $U/media-generation-unseen-s05-salt-aerial-*.mp4 | head -1)
S09=$(ls $U/media-generation-unseen-s09-fishermen-boat-*.mp4 | head -1)
S08N=$(ls $U/media-generation-unseen-s08-fpv-low-*.mp4 | head -1)
S10=$(ls $U/media-generation-unseen-s10-person-seaside-*.mp4 | head -1)
ISLAND=$(ls $M/media-generation-cambodia-s10-island-aerial-*.mp4 | head -1)
OMPIL=$(ls $M/media-generation-cambodia-s07-koh-ompil-*.mp4 | head -1)
D08="eq=saturation=0.8"
D07="eq=saturation=0.7"
# CAMBODIA: fade in 0.3-0.5, full 0.5-1.5, fade out 1.5-1.8
F="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.3),0,if(lt(t,0.5),(t-0.3)/0.2,if(lt(t,1.5),1,if(lt(t,1.8),1-(t-1.5)/0.3,0))))'"
# S01 NEW: cloudsea A 0-2.7s + CAMBODIA fade, NO desat (already cold natural light)
ffmpeg -y -v error -ss 0 -i "$S01N" -t 2.7 -vf "$F,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s01.mp4
# S03 3.0s + desat 0.7 (stronger, kill pink-purple water)
ffmpeg -y -v error -ss 0 -i "$S03" -t 3.0 -vf "$D07,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s03.mp4
# S04 0.9s: S03 2.0-2.9s, 1.5x crop + desat 0.7
ffmpeg -y -v error -ss 2.0 -i "$S03" -t 0.9 -vf "$D07,crop=480:853:120:213,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s04.mp4
# S05 1.9s + desat 0.7
ffmpeg -y -v error -ss 0 -i "$S05" -t 1.9 -vf "$D07,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s05.mp4
# S08 NEW: FPV 3.5-6.4s (clearest forward motion) + desat 0.8
ffmpeg -y -v error -ss 3.5 -i "$S08N" -t 2.9 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s08.mp4
# S10 2.7s: seaside person 0-2.7s + desat 0.8 (unify coast color)
ffmpeg -y -v error -ss 0 -i "$S10" -t 2.7 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s10.mp4
# S11 2.8s: island aerial 0-2.8s + desat 0.8
ffmpeg -y -v error -ss 0 -i "$ISLAND" -t 2.8 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s11.mp4
# S12 2.8s: Koh Ompil 0-2.8s + desat 0.8
ffmpeg -y -v error -ss 0 -i "$OMPIL" -t 2.8 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s12.mp4
# S13 NEW: cloudsea A 5.0-6.9s (golden cloud sea) + desat 0.8
ffmpeg -y -v error -ss 5.0 -i "$S01N" -t 1.9 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s13.mp4
# S02->S03 dissolve (rebuild from corrected S03)
ffmpeg -y -v error -i cut_s02.mp4 -i cut_s03.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.908[v]" -map "[v]" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s02s03.mp4
# concat (S02, S06, S07, S09 unchanged)
ffmpeg -y -v error -f concat -safe 0 -i concat_unseen.txt -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cambodia_unseen_31s_silent.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 cambodia_unseen_31s_silent.mp4
echo OK
