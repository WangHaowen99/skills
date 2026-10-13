"""检查动画是否超出配音（超出会造成冷场），以及哪些旁白段没有被场景用到。在工程目录运行：
    ~/.venvs/manim/bin/python <skill>/scripts/check_timing.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

DUR = json.load(open("audio/durations.json"))
timed, over = set(), []
for f in sorted(glob.glob("logs/timing_*.json")):
    for sid, t0, t1 in json.load(open(f)):
        timed.add(sid)
        extra = (t1 - t0) - DUR[sid]
        if extra > 0.3:
            over.append((sid, round(extra, 2)))
unused = [s for s, _, _ in SEGMENTS if s not in timed]
print(f"已计时 {len(timed)} 段；超出配音 {len(over)} 段 {over}；未使用 {len(unused)} 段 {unused[:20]}")
print(f"配音总长 {round(sum(DUR[s] for s, _, _ in SEGMENTS if s in DUR), 1)}s")
