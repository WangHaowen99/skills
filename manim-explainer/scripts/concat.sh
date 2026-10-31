#!/usr/bin/env bash
# 按 scenes.txt 顺序拼接渲染好的场景。在工程目录运行：concat.sh out/成片.mp4
set -euo pipefail
out=${1:?用法: concat.sh out/成片.mp4}
mkdir -p "$(dirname "$out")"
list=$(mktemp)
grep -vE '^\s*(#|$)' scenes.txt | while IFS=: read -r mod cls; do
  f=$(ls -t media/videos/"$mod"/*/"$cls".mp4 | head -1)
  echo "file '$PWD/$f'" >> "$list"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c:v libx264 -pix_fmt yuv420p -c:a aac "$out"
rm -f "$list"
echo "已生成 $out"
