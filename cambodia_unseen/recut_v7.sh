#!/bin/bash
# recut_v7.sh — CAMBODIA v7: only S01, S06, S08 change; other 10 shots reuse v6 cuts.
set -e
cd ~/workspace/cambodia_unseen

S01G=media-generation-unseen-s01-island-ridge-g-0-c3f8a202-837f-44a0-ae31-a6424a6f1fd4.mp4
S06I=media-generation-unseen-s06-yeaklaom-i-0-df5aec6a-bddf-4128-9eeb-faaf166be2f1.mp4
S08L=media-generation-unseen-s08-fpv-ridge-l-0-a97cb1c8-9cfc-4061-b03f-40de926a9492.mp4
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf

# S01: G 0-2.7s, CAMBODIA text 0.3s in / 1.5s out, no desat
ffmpeg -y -v error -i "$S01G" -t 2.7 -vf "scale=720:1280,drawtext=fontfile=$FONT:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.3),0,if(lt(t,0.5),(t-0.3)/0.2,if(lt(t,1.2),1,if(lt(t,1.5),1-(t-1.2)/0.3,0))))'" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v7_s01.mp4

# S06: I 0-2.5s, no desat (water already natural deep blue-green)
ffmpeg -y -v error -i "$S06I" -t 2.5 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v7_s06.mp4

# S08: L 1.0-3.9s (skip blurry 0-1.0s), sat 0.8; trim+setpts (input -ss/-t with setpts does not work)
ffmpeg -y -v error -i "$S08L" -vf "trim=start=1.0:end=3.9,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v7_s08.mp4

# S13: G 5.0-6.9s (same source as new S01, loop), sat 0.8
ffmpeg -y -v error -i "$S01G" -vf "trim=start=5.0:end=6.9,setpts=PTS-STARTPTS,scale=720:1280,eq=saturation=0.8" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_v7_s13.mp4

cat > concat_unseen_v7.txt <<'EOF'
file '/home/hatch/workspace/cambodia_unseen/cut_v7_s01.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s02s03.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s04.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s05.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_v7_s06.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s07.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_v7_s08.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s09.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s10.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s11.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s12.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_v7_s13.mp4'
EOF

ffmpeg -y -v error -f concat -safe 0 -i concat_unseen_v7.txt -c copy cambodia_unseen_31s_silent_v7.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name -of default=noprint_wrappers=1 cambodia_unseen_31s_silent_v7.mp4
