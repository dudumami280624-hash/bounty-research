#!/bin/bash
# assemble_v10.sh — CAMBODIA v10: v9 + S04 optimized (t=11.0-11.9, crop x=560) + S06 re-cut (t=15.8-18.3, no subtitle, no platform).
# S01 81 | S02S03 147 | S04 27 | S05 57 | S06 75 | S07 55 | S08 87 | S09 68 | S10 81 | S11 85 | S12 85 | S13 64 = 912f, 30.40s, 1080x1920 30fps, no audio.
set -e
cd ~/workspace/cambodia_unseen

ffmpeg -y -v error \
  -i cut_v9_s01.mp4 -i cut_v9_s02s03.mp4 -i cut_v10_s04.mp4 -i cut_v9_s05.mp4 \
  -i cut_v10_s06.mp4 -i cut_v9_s07.mp4 -i cut_v9_s08.mp4 -i cut_v9_s09.mp4 \
  -i cut_v9_s10.mp4 -i cut_v9_s11.mp4 -i cut_v9_s12.mp4 -i cut_v9_s13.mp4 \
  -filter_complex "\
[0:v]fps=30,trim=start_frame=0:end_frame=81,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v0];\
[1:v]fps=30,trim=start_frame=0:end_frame=147,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v1];\
[2:v]fps=30,trim=start_frame=0:end_frame=27,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v2];\
[3:v]fps=30,trim=start_frame=0:end_frame=57,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v3];\
[4:v]fps=30,trim=start_frame=0:end_frame=75,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v4];\
[5:v]fps=30,trim=start_frame=0:end_frame=55,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v5];\
[6:v]fps=30,trim=start_frame=0:end_frame=87,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v6];\
[7:v]fps=30,trim=start_frame=0:end_frame=68,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v7];\
[8:v]fps=30,trim=start_frame=0:end_frame=81,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v8];\
[9:v]fps=30,trim=start_frame=0:end_frame=85,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v9];\
[10:v]fps=30,trim=start_frame=0:end_frame=85,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v10];\
[11:v]fps=30,trim=start_frame=0:end_frame=64,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v11];\
[v0][v1][v2][v3][v4][v5][v6][v7][v8][v9][v10][v11]concat=n=12:v=1:a=0,format=yuv420p[out]" \
  -map "[out]" -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 -an cambodia_unseen_31s_v10_1080p30.mp4

echo "--- specs ---"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames -show_entries format=duration,size -of default=noprint_wrappers=1 cambodia_unseen_31s_v10_1080p30.mp4
ffprobe -v error -show_entries stream=index,codec_type -of csv=p=0 cambodia_unseen_31s_v10_1080p30.mp4
echo "V10 ASSEMBLY DONE"
