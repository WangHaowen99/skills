#!/usr/bin/env bash
# 拼接 seg1..N.wav（段间静音）→ 响度统一 -16 LUFS → 输出 <name>.wav(44.1k) 与 <name>.mp3(192k)
# 用法: concat.sh OUT_DIR NAME [停顿秒数，默认 0.45；最后一个间隔自动 +0.15]
set -euo pipefail
dir=$1; name=$2; pause=${3:-0.45}
cd "$dir"
n=$(ls seg[0-9]*.wav | grep -E '^seg[0-9]+\.wav$' | wc -l)
[ "$n" -ge 1 ] || { echo "no seg*.wav in $dir" >&2; exit 1; }

inputs=(); filter=""; chain=""
for i in $(seq 1 "$n"); do
  inputs+=(-i "seg$i.wav")
  filter+="[$((i-1)):a]aformat=sample_rates=22050:channel_layouts=mono[a$i];"
  chain+="[a$i]"
  if [ "$i" -lt "$n" ]; then
    p=$pause; [ "$i" -eq $((n-1)) ] && p=$(awk "BEGIN{print $pause+0.15}")
    filter+="anullsrc=r=22050:cl=mono,atrim=0:$p[s$i];"
    chain+="[s$i]"
  fi
done
parts=$((2*n-1))
filter+="${chain}concat=n=$parts:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[out]"

ffmpeg -hide_banner -loglevel error -y "${inputs[@]}" -filter_complex "$filter" -map "[out]" "$name.wav"
ffmpeg -hide_banner -loglevel error -y -i "$name.wav" -c:a libmp3lame -b:a 192k "$name.mp3"
printf '%s.wav %ss\n' "$name" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$name.wav")"
