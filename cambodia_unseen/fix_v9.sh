#!/bin/bash
# fix_v9.sh — v9 修正：S01 加 CAMBODIA 字 / S02 重剪金色日落草原 / S06 调暖 /
# S08 换 Neam 绿色草原 2 倍速 / S09 重剪干净窗＋轻优化（不失真）
set -e
R=real_footage
REF=$R/reference
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf
ls "$FONT" || { echo "FONT MISSING"; exit 1; }

# S01 云海 + CAMBODIA 字（跟越南开场一个路子）
ffmpeg -y -v error -ss 13.5 -i $R/s01_cloudsea_4288015.mp4 -t 2.7 \
  -vf "crop=810:1440:875:0,scale=1080:1920:flags=lanczos,drawtext=fontfile=$FONT:text='CAMBODIA':fontsize=100:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.42,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s01.mp4

# S02 金色日落草原 — from-Above 44.0-46.2s（之前 28s 窗口是公路＋房子，错了）
ffmpeg -y -v error -ss 44.0 -i $REF/mondulkiri_above_1080.mp4 -t 2.2 \
  -vf "crop=608:1080:656:0,eq=saturation=0.8,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s02.mp4

# S02+S03 叠化重做
ffmpeg -y -v error -i cut_v9_s02.mp4 -i cut_v9_s03.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=1.9,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s02s03.mp4

# S06 叶拉隆 — 从源重切＋调暖（雨季鲜绿降饱和＋暖色，不过分）
ffmpeg -y -v error -ss 9.0 -i $REF/yeaklaom_btfoodstory.mkv -t 2.5 \
  -vf "crop=608:1080:656:0,eq=contrast=1.05:saturation=0.88,colorbalance=rs=0.08:bs=-0.08,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s06.mp4

# S08 换绿色草原 — Neam 9.2-15.0s，2 倍速（替 FPV），左裁躲开 Mondulkiri 大字＋右上 logo
ffmpeg -y -v error -i $REF/mondulkiri_neam_beauty.mp4 \
  -vf "trim=start=9.2:end=15.0,setpts=0.5*PTS,crop=810:1440:0:0,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s08.mp4

# S09 日落收网 — 干净窗 94.0-96.9s（前后都是女人讲话／网特写＋字幕），轻放慢到 3.4s＋轻锐化提亮
ffmpeg -y -v error -i $REF/tonlesap_traps.mp4 \
  -vf "trim=start=94.0:end=96.9,setpts=1.1724*PTS,crop=202:360:380:0,unsharp=3:3:0.4,eq=contrast=1.05:saturation=1.06,scale=1080:1920:flags=lanczos,setsar=1,fps=30" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -an cut_v9_s09.mp4

echo "--- recut specs ---"
for f in cut_v9_s01.mp4 cut_v9_s02.mp4 cut_v9_s02s03.mp4 cut_v9_s06.mp4 cut_v9_s08.mp4 cut_v9_s09.mp4; do
  printf "%s: " "$f"; ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,nb_read_frames -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null | tr '\n' ' '; echo
done

# 拼合 v9
cat > concat_v9.txt << 'EOF'
file 'cut_v9_s01.mp4'
file 'cut_v9_s02s03.mp4'
file 'cut_v9_s04.mp4'
file 'cut_v9_s05.mp4'
file 'cut_v9_s06.mp4'
file 'cut_v9_s07.mp4'
file 'cut_v9_s08.mp4'
file 'cut_v9_s09.mp4'
file 'cut_v9_s10.mp4'
file 'cut_v9_s11.mp4'
file 'cut_v9_s12.mp4'
file 'cut_v9_s13.mp4'
EOF
ffmpeg -y -v error -f concat -safe 0 -i concat_v9.txt -c:v libx264 -crf 18 -pix_fmt yuv420p -an cambodia_unseen_31s_v9_1080p30.mp4
echo "--- v9 final ---"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_read_frames -show_entries format=duration,size -of default=noprint_wrappers=1 cambodia_unseen_31s_v9_1080p30.mp4
