#!/bin/bash
# 在线 TTS：生成一条旁白并按 1.3 倍速导出
# 用法：tts.sh <输出名> <文本>
set -e
VOICE="${VOICE:-zh-CN-XiaoxiaoNeural}"
ROOT="${DEMO_VIDEO_ROOT:-/tmp/demo-video}"
FF="${DEMO_VIDEO_FFMPEG:-$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null || echo ffmpeg)}"
OUT="$ROOT/audio/$1.m4a"
mkdir -p "$ROOT/audio"
# 需要走代理时设 DEMO_VIDEO_PROXY，例如 http://127.0.0.1:8118
HTTPS_PROXY="${DEMO_VIDEO_PROXY:-$HTTPS_PROXY}" HTTP_PROXY="${DEMO_VIDEO_PROXY:-$HTTP_PROXY}" \
  python3 -m edge_tts --voice "$VOICE" --text "$2" --write-media "/tmp/tts_raw.mp3" >/dev/null 2>&1
"$FF" -y -loglevel error -i /tmp/tts_raw.mp3 -filter:a "atempo=${SPEED:-1.3}" -c:a aac -b:a 160k "$OUT"
"$FF" -i "$OUT" 2>&1 | grep -o 'Duration: [0-9:.]*'
