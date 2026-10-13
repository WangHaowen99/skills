"""把 IndexTTS 的分段输出（seg<N>.wav，顺序同 spec）导入视频：变速、去首尾静音、统一音量、补尾静音，
写 audio/<段id>.wav 并更新 audio/durations.json。

在工程目录运行：~/.venvs/tts/bin/python <skill>/scripts/apply_voice.py SPEC_JSON SEG_DIR [--speed 1.4]
换配音前先把旧 audio/ 复制为 audio_ref/，动画会按新旧时长比自动调节节奏（见 common.py 的 PACE_REF）。
"""
import argparse
import json
import os
import shutil
import subprocess

import numpy as np
import soundfile as sf

FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
SR, PAD, TARGET_RMS_DB, PEAK = 24000, 0.12, -20.0, 0.89


def load(path, speed):
    filters = f"atempo={speed}" if abs(speed - 1.0) > 1e-3 else "anull"
    raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", path, "-af", filters, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "pipe:1"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def trim(wav, thr=0.01, keep=0.04):
    idx = np.flatnonzero(np.abs(wav) > thr)
    if not len(idx):
        return wav
    return wav[max(idx[0] - int(keep * SR), 0): min(idx[-1] + int(keep * SR), len(wav))]


def level(wav):
    rms = np.sqrt(np.mean(wav ** 2)) + 1e-9
    wav = wav * (10 ** (TARGET_RMS_DB / 20) / rms)
    peak = np.max(np.abs(wav))
    return wav * (PEAK / peak) if peak > PEAK else wav


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("seg_dir")
    ap.add_argument("--speed", type=float, default=1.4)
    a = ap.parse_args()
    segs = json.load(open(a.spec, encoding="utf-8"))["segments"]
    dur_path = "audio/durations.json"
    durations = json.load(open(dur_path)) if os.path.exists(dur_path) else {}
    for i, seg in enumerate(segs, 1):
        wav = level(trim(load(os.path.join(a.seg_dir, f"seg{i}.wav"), a.speed)))
        wav = np.concatenate([wav, np.zeros(int(PAD * SR), dtype=np.float32)])
        sf.write(f"audio/{seg['id']}.wav", wav, SR)
        durations[seg["id"]] = round(len(wav) / SR, 3)
    json.dump(durations, open(dur_path, "w"), indent=1)
    print(f"{len(segs)} segments, speed {a.speed}, total {round(sum(durations.values()), 1)}s")


if __name__ == "__main__":
    main()
