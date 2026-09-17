#!/usr/bin/env python3
"""成片前的硬检查。三条红线：配音不能被截、字幕必须有画面、高亮必须有来源。

这些问题肉眼一条条看片才能发现，代价太高；放在构建后自动跑，不通过就不出片。
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get('DEMO_VIDEO_ROOT', '/tmp/demo-video')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import FFMPEG as FF  # noqa: E402


def duration(path):
    if not os.path.exists(path):
        return 0.0
    proc = subprocess.run([FF, '-i', path], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', proc.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def subtitles():
    text = open(os.path.join(ROOT, '分镜与文案.md'), encoding='utf-8').read()
    pat = re.compile(r'### (\S+) [^\n]*\n(?:- \*\*(?:操作|高亮)\*\*：[^\n]*\n)+- \*\*字幕\*\*：([^\n]+)')
    return {m.group(1): m.group(2).strip() for m in pat.finditer(text)}


def main(acts):
    book = subtitles()
    bad = []
    for act in acts:
        path = os.path.join(ROOT, 'cues', f'{act}.json')
        if not os.path.exists(path):
            continue
        for cue in json.load(open(path, encoding='utf-8')):
            cid = cue['id']
            voice = duration(os.path.join(ROOT, 'audio', f'{cid}.m4a'))
            done = os.path.join(ROOT, 'work', act, cid, 'done')
            shot = (len([f for f in os.listdir(done) if f.endswith('.jpg')]) / 30.0
                    if os.path.isdir(done) else None)

            if not cue.get('subtitle'):
                bad.append(f'{cid}: cue 里没有字幕')
            elif book.get(cid) and cue['subtitle'] != book[cid]:
                bad.append(f'{cid}: cue 字幕与分镜不一致')
            if voice <= 0:
                bad.append(f'{cid}: 没有配音')
            if shot is None:
                bad.append(f'{cid}: 不是连续视频镜头（仍在用拼帧）')
            elif shot + 0.02 < voice + 0.15:
                bad.append(f'{cid}: 画面 {shot:.2f}s < 配音 {voice:.2f}s，会截断')
            if not cue.get('video'):
                bad.append(f'{cid}: 没有绑定录像源')

    if bad:
        print('检查未通过：')
        for b in bad:
            print('  ✗', b)
        sys.exit(1)
    print(f'检查通过：{sum(1 for a in acts for _ in json.load(open(os.path.join(ROOT, "cues", f"{a}.json"), encoding="utf-8"))) if acts else 0} 镜，无截断、字幕画面齐备')


if __name__ == '__main__':
    main(sys.argv[1:])
