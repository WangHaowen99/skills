#!/usr/bin/env bash
# 按 scenes.txt 顺序拼接 1080p 场景，统一响度（-16 LUFS），输出 mp4。在工程目录运行：
#   concat.sh out/<成片名>.mp4
# VCODEC=h264_nvenc 改用 NVIDIA GPU 编码（快几倍）；默认 libx264 软编，兼容性最好。
set -euo pipefail
out=${1:?用法: concat.sh out/<成片名>.mp4}
FF=${FFMPEG:-ffmpeg}
FP=${FFPROBE:-ffprobe}
mkdir -p "$(dirname "$out")"
list=$(mktemp)
grep -vE '^\s*(#|$)' scenes.txt | while IFS=: read -r F C; do
  echo "file '$PWD/media_hq/$C/videos/$F/1080p30/$C.mp4'"
done > "$list"
if [ "${VCODEC:-libx264}" = h264_nvenc ]; then
  venc=(-c:v h264_nvenc -preset p6 -tune hq -rc vbr -cq 21 -b:v 0)
else
  venc=(-c:v libx264 -preset medium -crf 20)
fi
$FF -y -loglevel error -f concat -safe 0 -i "$list" "${venc[@]}" -pix_fmt yuv420p \
  -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$out"
rm -f "$list"
$FP -v error -show_entries format=duration,size -of default=nw=1 "$out"
