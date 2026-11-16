#!/bin/bash
set -e
cd ~/workspace/cambodia_unseen
R=real_footage
# S01 cloud sea + Ken Burns 1.2x push-in (81f) — title added in second pass
ffmpeg -y -v error -ss 13.5 -i $R/s01_cloudsea_4288015.mp4 -t 2.7 \
  -vf "crop=810:1440:875:0,fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/80':h='2304-384*n/80':x='108*n/80':y='192*n/80',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s01_notitle.mp4
# S01 title (same as v9: DejaVuSerif-Bold 90, white/black border 3, centered, 0.3-1.5s)
ffmpeg -y -v error -i cut_v12_s01_notitle.mp4 \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:text='CAMBODIA':fontsize=90:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0.3,1.5)',setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s01.mp4
# S07 bamboo + Ken Burns 1.2x (55f)
ffmpeg -y -v error -ss 3.0 -i $R/s07_bamboo_2121092.mp4 -t 1.83 \
  -vf "crop=608:1080:656:0,fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/54':h='2304-384*n/54':x='108*n/54':y='192*n/54',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s07.mp4
# S10 beach walker + Ken Burns 1.2x (81f)
ffmpeg -y -v error -ss 15.0 -i $R/s10_beach_39482006.mp4 -t 2.7 \
  -vf "fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/80':h='2304-384*n/80':x='108*n/80':y='192*n/80',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s10.mp4
# S11 Koh Rong + Ken Burns 1.15x (85f, gentler — source already 2.67x upscaled)
ffmpeg -y -v error -ss 39.0 -i s11_8426080_koh_rong.mp4 -t 2.83 \
  -vf "crop=405:720:400:0,fps=30,scale=1242:2208:flags=lanczos,crop=w='1242-162*n/84':h='2208-288*n/84':x='81*n/84':y='144*n/84',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s11.mp4
# S13 cloud sea closing + Ken Burns 1.2x (64f)
ffmpeg -y -v error -ss 0 -i $R/s01_cloudsea_4288015.mp4 -t 2.13 \
  -vf "crop=810:1440:875:0,fps=30,scale=1296:2304:flags=lanczos,crop=w='1296-216*n/63':h='2304-384*n/63':x='108*n/63':y='192*n/63',scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v12_s13.mp4
echo "--- frame counts ---"
for f in cut_v12_s01.mp4 cut_v12_s07.mp4 cut_v12_s10.mp4 cut_v12_s11.mp4 cut_v12_s13.mp4; do ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 $f; done
echo "CUTS DONE"
