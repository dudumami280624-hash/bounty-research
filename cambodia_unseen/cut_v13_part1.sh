#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
R=real_footage
REF=$R/reference
# S01 cloud sea 80f, Ken Burns 1.2x, title added in second pass
ffmpeg -y -v error -ss 13.5 -i $R/s01_cloudsea_4288015.mp4 -t 2.667 \
  -vf "crop=810:1440:875:0,fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/79':h='2304-384*n/79':x='108*n/79':y='192*n/79',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s01_notitle.mp4
ffmpeg -y -v error -i cut_v13_s01_notitle.mp4 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=90:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0.3,1.5)',setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s01.mp4
# S02 golden grassland 98f source (for 89f dominant + 9f dissolve)
ffmpeg -y -v error -ss 305.0 -i $REF/mondulkiri_above_1080.mp4 -t 3.267 \
  -vf "crop=608:1080:656:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s02.mp4
# S03 salt pushing (Ins) 72f, medium shot, t=10.5-12.9
ffmpeg -y -v error -ss 10.5 -i $REF/kampot_salt_ig.mp4 -t 2.4 \
  -vf "transpose=2,crop=405:720:200:400,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s03.mp4
# S04 salt crystals low-angle (Ins) 40f, tight on rake head + salt, t=13.0-14.33
ffmpeg -y -v error -ss 13.0 -i $REF/kampot_salt_ig.mp4 -t 1.333 \
  -vf "transpose=2,crop=405:720:250:560,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s04.mp4
# S05 salt aerial 41f, t=25.0-26.367
ffmpeg -y -v error -ss 25.0 -i $REF/kampot_salt_ig.mp4 -t 1.367 \
  -vf "transpose=2,crop=405:720:437:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s05.mp4
# S07 bamboo 54f, Ken Burns 1.2x
ffmpeg -y -v error -ss 3.0 -i $R/s07_bamboo_2121092.mp4 -t 1.8 \
  -vf "crop=608:1080:656:0,fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/53':h='2304-384*n/53':x='108*n/53':y='192*n/53',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s07.mp4
# S08 green grassland 88f, 2x speed, t=12.0-17.867
ffmpeg -y -v error -ss 12.0 -i $REF/mondulkiri_fb_bunneammoy.mp4 -t 5.867 \
  -vf "trim=0:5.867,setpts=0.5*PTS,crop=562:1000:999:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s08.mp4
# S09 fisherman 101f, slowed 0.673x + Ken Burns 1.2x
ffmpeg -y -v error -ss 94.2 -i $REF/tonlesap_traps.mp4 -t 2.3 \
  -vf "crop=202:360:380:0,fps=30,setpts=1.485*PTS,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/100':h='2304-384*n/100':x='108*n/100':y='192*n/100',scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s09.mp4
# S10 beach walker 82f, Ken Burns 1.2x
ffmpeg -y -v error -ss 15.0 -i $R/s10_beach_39482006.mp4 -t 2.733 \
  -vf "fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/81':h='2304-384*n/81':x='108*n/81':y='192*n/81',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s10.mp4
# S11 Koh Rong 84f, Ken Burns 1.15x
ffmpeg -y -v error -ss 39.0 -i s11_8426080_koh_rong.mp4 -t 2.8 \
  -vf "crop=405:720:400:0,fps=30,scale=1242:2208:flags=lanczos,crop=w='1242-162*n/83':h='2208-288*n/83':x='81*n/83':y='144*n/83',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v13_s11.mp4
echo "--- frame counts ---"
for f in cut_v13_s01.mp4 cut_v13_s02.mp4 cut_v13_s03.mp4 cut_v13_s04.mp4 cut_v13_s05.mp4 cut_v13_s07.mp4 cut_v13_s08.mp4 cut_v13_s09.mp4 cut_v13_s10.mp4 cut_v13_s11.mp4; do printf "%s " $f; ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $f; done
echo "CUT_V13_PART1 DONE"
