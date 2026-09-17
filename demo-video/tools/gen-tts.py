#!/usr/bin/env python3
"""从分镜文件里读出每一镜的字幕，批量生成配音。

字幕是唯一来源：改了分镜就重跑这个脚本，不用手抄一遍文案，也就不会出现
画面上的字和念出来的话对不上。已经生成且文本没变的直接跳过。
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get('DEMO_VIDEO_ROOT', '/tmp/demo-video')
STAMP = os.path.join(ROOT, 'audio', '.texts.json')


def shots():
    text = open(os.path.join(ROOT, '分镜与文案.md'), encoding='utf-8').read()
    pat = re.compile(r'### (\S+) [^\n]*\n(?:- \*\*(?:操作|高亮)\*\*：[^\n]*\n)+- \*\*字幕\*\*：([^\n]+)')
    return [(m.group(1), m.group(2).strip()) for m in pat.finditer(text)]


def main():
    only = set(sys.argv[1:])
    done = json.load(open(STAMP)) if os.path.exists(STAMP) else {}
    made, skipped = [], []
    for cue_id, text in shots():
        if only and cue_id not in only:
            continue
        out = os.path.join(ROOT, 'audio', f'{cue_id}.m4a')
        digest = hashlib.md5(text.encode()).hexdigest()
        if done.get(cue_id) == digest and os.path.exists(out):
            skipped.append(cue_id)
            continue
        proc = subprocess.run([os.path.join(ROOT, 'tts.sh'), cue_id, text],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            print(f'  ✗ {cue_id}: {proc.stderr.strip()[-160:]}')
            continue
        done[cue_id] = digest
        made.append(f'{cue_id} {proc.stdout.strip()}')
        print(f'  ✓ {cue_id}  {proc.stdout.strip()}')
    json.dump(done, open(STAMP, 'w'), ensure_ascii=False, indent=1)
    print(f'\n新生成 {len(made)} 条，跳过 {len(skipped)} 条（文本未变）')


if __name__ == '__main__':
    main()
