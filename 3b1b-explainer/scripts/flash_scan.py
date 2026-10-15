"""扫描成片里的“实色闪烁”：Indicate 等动画把不透明底色整块染成主题色、盖住文字的瞬间。在工程目录运行：
    python <skill>/scripts/flash_scan.py out/<成片名>.mp4 [阈值%=1.2]
每秒取 5 帧（192x108），不看字幕区，某主题色像素占比超过阈值即报出时间段。主题由 THEME 环境变量决定（dark / light）。
"""
import os
import shutil
import subprocess
import sys

import numpy as np

W, H = 192, 108
PAL = {
    "light": {"YELLOW": "#B07800", "GREEN": "#2F9E44", "RED": "#E03131", "BLUE": "#1C7ED6", "PURPLE": "#7048E8", "TEAL": "#0C8599"},
    "dark": {"YELLOW": "#F7D96F", "GREEN": "#83C167", "RED": "#FC6255", "BLUE": "#58C4DD", "PURPLE": "#B794D6", "TEAL": "#5CD0B3"},
}["light" if os.environ.get("THEME", "dark") in ("light", "white") else "dark"]


def main():
    path, thr = sys.argv[1], float(sys.argv[2]) / 100 if len(sys.argv) > 2 else 0.012
    cols = {k: np.array([int(v[i:i + 2], 16) for i in (1, 3, 5)]) for k, v in PAL.items()}
    proc = subprocess.Popen([os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=5,scale={W}:{H}",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    i, runs = 0, []
    while True:
        b = proc.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(int)[:int(H * 0.72)]
        for k, c in cols.items():
            share = (np.abs(a - c).sum(axis=2) < 60).mean()
            if share > thr:
                t = i / 5
                if runs and runs[-1][1] == k and t - runs[-1][2] <= 0.4:
                    runs[-1][2], runs[-1][3] = t, max(runs[-1][3], share)
                else:
                    runs.append([t, k, t, share])
        i += 1
    for t0, k, t1, m in runs:
        print(f"{t0:7.1f}-{t1:6.1f}s  {k:<6} 最大占比 {m:.1%}")
    print(f"扫描 {i} 帧，可疑 {len(runs)} 处")


if __name__ == "__main__":
    main()
