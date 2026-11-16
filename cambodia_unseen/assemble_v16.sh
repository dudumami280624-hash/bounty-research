#!/bin/bash
# assemble_v16.sh — CAMBODIA v16: 946f (31.533s). User's 9 fixes:
# 1. S02->S03 hard cut at f169 (no dissolve), S02 ends f168.
# 2. S10 darker/warmer/no green. 3. S02 new window t=358 (clouds visible), highlight compressed.
# 4. S06 lake darker + teal. 5. S09 warm orange sky; S10 warmer for natural S09->S10 transition.
# 6. S13 NEW: Tonle Sap floating village sunset aerial (boat+people, 3 layers, ends bright).
# 7. S03 opening 10f salt-field wide, then pushing; still 72f.
# 8. S08 NEW window t=9.0-14.867 (same source, no splice at f516).
# 9. S07 slightly brighter, less saturated.
# Cut points: 80,169,241,281,322,397,451,539,640,722,806,889,946
# S01 80 | S02 89 | S03 72 | S04 40 | S05 41 | S06 75 | S07 54 | S08 88 | S09 101 | S10 82 | S11 84 | S12 83 | S13 57 = 946f
# S02,S03,S04,S09,S13 already graded in cuts; others graded here.
set -e
cd ~/workspace/cambodia_unseen
ffmpeg -y -v error \
  -i cut_v13_s01.mp4 -i cut_v16_s02.mp4 -i cut_v16_s03.mp4 -i cut_v14_s04.mp4 -i cut_v13_s05.mp4 \
  -i cut_v10_s06.mp4 -i cut_v13_s07.mp4 -i cut_v16_s08.mp4 -i cut_v16_s09.mp4 \
  -i cut_v13_s10.mp4 -i cut_v13_s11.mp4 -i cut_v13_s12.mp4 -i cut_v16_s13.mp4 \
  -filter_complex "\
[0:v]fps=30,trim=start_frame=0:end_frame=80,setpts=PTS-STARTPTS,eq=brightness=-0.18:contrast=1.15:saturation=1.5,scale=1080:1920:flags=lanczos,setsar=1[v0];\
[1:v]fps=30,trim=start_frame=0:end_frame=89,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v1];\
[2:v]fps=30,trim=start_frame=0:end_frame=72,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v2];\
[3:v]fps=30,trim=start_frame=0:end_frame=40,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v3];\
[4:v]fps=30,trim=start_frame=0:end_frame=41,setpts=PTS-STARTPTS,eq=saturation=1.4:contrast=1.1,scale=1080:1920:flags=lanczos,setsar=1[v4];\
[5:v]fps=30,trim=start_frame=0:end_frame=75,setpts=PTS-STARTPTS,eq=brightness=-0.10:saturation=0.8,colorbalance=rm=-0.05:gm=0.03:bm=0.05,scale=1080:1920:flags=lanczos,setsar=1[v5];\
[6:v]fps=30,trim=start_frame=0:end_frame=54,setpts=PTS-STARTPTS,eq=brightness=0.05:saturation=1.0:contrast=1.05,scale=1080:1920:flags=lanczos,setsar=1[v6];\
[7:v]fps=30,trim=start_frame=0:end_frame=88,setpts=PTS-STARTPTS,eq=saturation=0.6,scale=1080:1920:flags=lanczos,setsar=1[v7];\
[8:v]fps=30,trim=start_frame=0:end_frame=101,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v8];\
[9:v]fps=30,trim=start_frame=0:end_frame=82,setpts=PTS-STARTPTS,eq=brightness=-0.08:saturation=1.3:contrast=1.1,colorbalance=rm=0.05:gm=-0.04:bm=-0.06,scale=1080:1920:flags=lanczos,setsar=1[v9];\
[10:v]fps=30,trim=start_frame=0:end_frame=84,setpts=PTS-STARTPTS,eq=saturation=1.4:contrast=1.1,scale=1080:1920:flags=lanczos,setsar=1[v10];\
[11:v]fps=30,trim=start_frame=0:end_frame=83,setpts=PTS-STARTPTS,eq=saturation=1.8:contrast=1.15,scale=1080:1920:flags=lanczos,setsar=1[v11];\
[12:v]fps=30,trim=start_frame=0:end_frame=57,setpts=PTS-STARTPTS,scale=1080:1920:flags=lanczos,setsar=1[v12];\
[v0][v1][v2][v3][v4][v5][v6][v7][v8][v9][v10][v11][v12]concat=n=13:v=1:a=0,format=yuv420p[out]" \
  -map "[out]" -c:v libx264 -crf 18 -pix_fmt yuv420p -r 30 -an cambodia_unseen_31s_v16_1080p30.mp4
echo "--- specs ---"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames -show_entries format=duration,size -of default=noprint_wrappers=1 cambodia_unseen_31s_v16_1080p30.mp4
echo "V16 ASSEMBLY DONE"
