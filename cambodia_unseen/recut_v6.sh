#!/bin/bash
# recut_v6.sh — CAMBODIA final polish (5 items), v6
# 1. S01 = E (three-layer) 0-2.7s, CAMBODIA text 0.3s in / 1.5s out
# 2. S03-S05 = NEW morning sources (soft cool daylight, no sunset)
# 3. S08 = FPV re-cut 6.5-9.4s (stable, clear parallax)
# 4. S09-S12 = re-grade (S09/S10 cool 10000K + desat 0.55, S11/S12 desat 0.55)
# 5. Full technical check after assembly
set -e
cd ~/workspace/cambodia_unseen

S01E=media-generation-unseen-s01-three-layer-e-0-42cbe817-f896-43c7-b2a7-50d589675fbf.mp4
S02=media-generation-unseen-s02-mondulkiri-person-0-8691a89a-9d43-4286-a244-ecc788759210.mp4
S03M=media-generation-unseen-s03-salt-morning-0-0c0b197b-a294-4b4e-82ef-15153f72b9f4.mp4
S05M=media-generation-unseen-s05-salt-aerial-morning-0-36141b75-ae66-46f8-83b5-68a00f741f62.mp4
FPV=media-generation-unseen-s08-fpv-low-0-a040dbdd-fcb9-42b8-bcba-250bc83642c7.mp4
S09=media-generation-unseen-s09-fishermen-boat-0-6b58c3c4-4879-43cc-8647-6e7b412123d1.mp4
S10=media-generation-unseen-s10-person-seaside-0-19979631-e342-468f-adfa-2079e906ed78.mp4
S11=../cambodia_montage/media-generation-cambodia-s10-island-aerial-0-8daffafd-1939-410d-a14e-a7a92629ef10.mp4
S12=../cambodia_montage/media-generation-cambodia-s07-koh-ompil-0-47f9dd21-6ab4-4197-a888-021962ae5343.mp4
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf

# S01: E 0-2.7s, CAMBODIA text 0.3 in / 1.5 out, no desat
ffmpeg -y -v error -ss 0 -i "$S01E" -t 2.7 -vf "scale=720:1280,drawtext=fontfile=$FONT:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,0.3),0,if(lt(t,0.5),(t-0.3)/0.2,if(lt(t,1.2),1,if(lt(t,1.5),1-(t-1.2)/0.3,0))))'" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s01.mp4

# S02: 0-2.2s, sat 0.8
ffmpeg -y -v error -ss 0 -i "$S02" -t 2.2 -vf "eq=saturation=0.8,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s02.mp4

# S03: NEW morning source 0-3.0s, no desat (already cool morning light)
ffmpeg -y -v error -ss 0 -i "$S03M" -t 3.0 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s03.mp4

# S02+S03 xfade (fade 0.3s, offset 1.908)
ffmpeg -y -v error -i cut_s02.mp4 -i cut_s03.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.908,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 21 -r 24 -an cut_s02s03.mp4

# S04: from NEW S03-morning 2.0-2.9s, crop 1.5x zoom, no desat
ffmpeg -y -v error -ss 2.0 -i "$S03M" -t 0.9 -vf "crop=480:853:120:213,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s04.mp4

# S05: NEW morning aerial 0-1.9s, no desat
ffmpeg -y -v error -ss 0 -i "$S05M" -t 1.9 -vf "scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s05.mp4

# S06, S07: reuse v4 cuts (unchanged)
# (cut_s06.mp4, cut_s07.mp4 already exist)

# S08: FPV re-cut 6.5-9.4s (stable, clear parallax), sat 0.8
ffmpeg -y -v error -ss 6.5 -i "$FPV" -t 2.9 -vf "eq=saturation=0.8,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s08.mp4

# S09: fishermen, desat 0.55 + cool 10000K
ffmpeg -y -v error -ss 0 -i "$S09" -t 3.4 -vf "eq=saturation=0.55,colortemperature=temperature=10000,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s09.mp4

# S10: seaside, desat 0.55 + cool 10000K
ffmpeg -y -v error -ss 0 -i "$S10" -t 2.7 -vf "eq=saturation=0.55,colortemperature=temperature=10000,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s10.mp4

# S11: island aerial, desat 0.55
ffmpeg -y -v error -ss 0 -i "$S11" -t 2.8 -vf "eq=saturation=0.55,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s11.mp4

# S12: Koh Ompil, desat 0.55
ffmpeg -y -v error -ss 0 -i "$S12" -t 2.8 -vf "eq=saturation=0.55,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s12.mp4

# S13: E source 5.0-6.9s, sat 0.8
ffmpeg -y -v error -ss 5.0 -i "$S01E" -t 1.9 -vf "eq=saturation=0.8,scale=720:1280" -c:v libx264 -crf 21 -pix_fmt yuv420p -r 24 -an cut_s13.mp4

# Concat (same order as v5)
cat > concat_unseen_v6.txt <<'EOF'
file '/home/hatch/workspace/cambodia_unseen/cut_s01.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s02s03.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s04.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s05.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s06.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s07.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s08.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s09.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s10.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s11.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s12.mp4'
file '/home/hatch/workspace/cambodia_unseen/cut_s13.mp4'
EOF
ffmpeg -y -v error -f concat -safe 0 -i concat_unseen_v6.txt -c copy cambodia_unseen_31s_silent_v6.mp4
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate,codec_name -of default=noprint_wrappers=1 cambodia_unseen_31s_silent_v6.mp4
echo "V6 ASSEMBLED"
