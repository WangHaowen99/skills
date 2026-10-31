#!/usr/bin/env bash
# 按 scenes.txt 顺序逐个渲染场景。在工程目录运行：render.sh
# QUALITY=h（默认 1080p）| m | l（低清预览）
set -euo pipefail
MANIM=${MANIM:-manim}
grep -vE '^\s*(#|$)' scenes.txt | while IFS=: read -r mod cls; do
  echo "渲染 $cls"
  $MANIM -q"${QUALITY:-h}" "$mod.py" "$cls"
done
