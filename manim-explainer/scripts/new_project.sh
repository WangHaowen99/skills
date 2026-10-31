#!/usr/bin/env bash
# 新建视频工程：复制模板到目标目录。用法: new_project.sh <工作目录>/video
set -euo pipefail
dst=${1:?目标目录}
src="$(cd "$(dirname "$0")/../template" && pwd)"
if [ -e "$dst/common.py" ]; then echo "已存在 $dst/common.py，不覆盖" >&2; exit 1; fi
mkdir -p "$dst"/{audio,out}
cp "$src"/*.py "$src"/scenes.txt "$dst"/
echo "已创建 $dst"
