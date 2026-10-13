#!/usr/bin/env bash
# 新建视频工程：复制模板到目标目录（应在任何 git 仓库之外），建好 audio/ logs/ out/
# 用法: new_project.sh <仓库外的目录>/<任务>/video
set -euo pipefail
dst=${1:?目标目录}
src="$(cd "$(dirname "$0")/../template" && pwd)"
if [ -e "$dst/common.py" ]; then echo "已存在 $dst/common.py，不覆盖" >&2; exit 1; fi
mkdir -p "$dst"/{audio,logs,out}
cp "$src"/*.py "$src"/scenes.txt "$dst"/
if git -C "$dst" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "警告：$dst 在 git 仓库内，含人名/内部信息的视频工程应放到仓库外" >&2
fi
echo "已创建 $dst"
