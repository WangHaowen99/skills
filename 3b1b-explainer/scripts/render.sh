#!/usr/bin/env bash
# 并行渲染 scenes.txt 里的场景（每个场景独立 --media_dir，避免 Text 的 SVG 缓存并发竞争）。在工程目录运行：
#   render.sh preview [场景 ...]   480p15 → media/<场景>/，并生成 logs/sheet_<场景>.png（每段旁白结尾一帧）
#   render.sh hq [场景 ...]        1080p30 → media_hq/<场景>/
# 不给场景名则渲染全部。并行数 JOBS（默认 7，16G 内存够用）。最后自动跑 check_timing.py。
set -uo pipefail
mode=${1:?用法: render.sh preview|hq [场景 ...]}; shift
SK="$(cd "$(dirname "$0")" && pwd)"
MANIM=${MANIM:-$HOME/.venvs/manim/bin/manim}
PY=${MANIM_PY:-$HOME/.venvs/manim/bin/python}
mapfile -t all < <(grep -vE '^\s*(#|$)' scenes.txt)
sel=()
for p in "${all[@]}"; do
  c=${p##*:}
  if [ $# -eq 0 ] || printf '%s\n' "$@" | grep -qx "$c"; then sel+=("$p"); fi
done
mkdir -p logs
export mode SK MANIM PY
printf '%s\n' "${sel[@]}" | xargs -P "${JOBS:-7}" -I{} bash -c '
  p={}; F=${p%%:*}; C=${p##*:}
  if [ "$mode" = hq ]; then
    $MANIM --resolution 1920,1080 --frame_rate 30 --media_dir media_hq/$C $F.py $C > logs/hq_$C.log 2>&1; e=$?
  else
    $MANIM -ql --media_dir media/$C $F.py $C > logs/ql_$C.log 2>&1; e=$?
    [ $e = 0 ] && $PY "$SK/sheet.py" $C media/$C/videos/$F/480p15/$C.mp4 >/dev/null 2>&1
  fi
  if [ $e = 0 ]; then echo "$C ok"; else echo "$C FAILED"; grep -E "Error" logs/*_$C.log | tail -2; fi'
$PY "$SK/check_timing.py"
# 自动排版检查汇总（common.py 在每段结束时写 logs/layout_<场景>.txt）
for p in "${sel[@]}"; do c=${p##*:}; f=logs/layout_$c.txt; [ -s "$f" ] && echo "排版 $c: $(wc -l < "$f") 条，见 $f"; done; true
