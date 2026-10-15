#!/usr/bin/env bash
# 按 scenes.txt 顺序拼接 1080p 场景，统一响度（-16 LUFS），输出 mp4。在工程目录运行：
#   concat.sh out/<成片名>.mp4
# 默认视频流直接拷贝（各场景同为 manim 输出的 libx264 1080p30），只重编码音频：10 分钟成片约 15 秒，
# 整片重编码要 4~5 分钟。实测各场景起点音画偏移 0 ms。播放异常时设 VCODEC 回退到重编码：
#   VCODEC=libx264 软编，兼容性最好；VCODEC=h264_nvenc 用 NVIDIA GPU 编码（个别驱动下会崩）。
set -euo pipefail
out=${1:?用法: concat.sh out/<成片名>.mp4}
FF=${FFMPEG:-ffmpeg}
FP=${FFPROBE:-ffprobe}
mkdir -p "$(dirname "$out")"
list=$(mktemp)
grep -vE '^\s*(#|$)' scenes.txt | while IFS=: read -r F C; do
  echo "file '$PWD/media_hq/$C/videos/$F/1080p30/$C.mp4'"
done > "$list"
case "${VCODEC:-copy}" in
  h264_nvenc) venc=(-c:v h264_nvenc -preset p6 -tune hq -rc vbr -cq 21 -b:v 0 -pix_fmt yuv420p) ;;
  libx264) venc=(-c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p) ;;
  *) venc=(-c:v copy) ;;
esac
$FF -y -loglevel error -f concat -safe 0 -i "$list" "${venc[@]}" \
  -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$out"
rm -f "$list"
$FP -v error -show_entries format=duration,size -of default=nw=1 "$out"
