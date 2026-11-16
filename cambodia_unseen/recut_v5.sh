#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
U=~/workspace/cambodia_unseen
S01D=$(ls $U/media-generation-unseen-s01-cloudsea-ridge-d-0-*.mp4 | head -1)
D08="eq=saturation=0.8"
# CAMBODIA: fade in 0.3-0.5, full 0.5-1.5, fade out 1.5-1.8
F="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.3),0,if(lt(t,0.5),(t-0.3)/0.2,if(lt(t,1.5),1,if(lt(t,1.8),1-(t-1.5)/0.3,0))))'"
# S01 v5: cloudsea-ridge D 0-2.7s + CAMBODIA fade, NO desat
# D chosen: cloud sea fills upper 2/3 at 0s (shock) + dark forested ridge with golden grass below (real Mondulkiri identity, gentle slopes, no sharp peaks)
ffmpeg -y -v error -ss 0 -i "$S01D" -t 2.7 -vf "$F,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s01.mp4
# S13 v5: cloudsea-ridge D 5.0-6.9s (layered misty ridges + golden grass) + desat 0.8, same source as S01 for loop
ffmpeg -y -v error -ss 5.0 -i "$S01D" -t 1.9 -vf "$D08,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s13.mp4
# concat (S02-S12 cuts from v4 unchanged)
ffmpeg -y -v error -f concat -safe 0 -i concat_unseen.txt -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cambodia_unseen_31s_silent.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 cambodia_unseen_31s_silent.mp4
echo OK
