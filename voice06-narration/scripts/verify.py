"""用本机缓存的 faster-whisper 转写每段，和 spec 原文对照，用于发现漏读/读歪。

用法:
    uv run --quiet --python 3.11 --with faster-whisper --with soundfile --with scipy \
        python <skill>/scripts/verify.py spec.json OUT_DIR
CPU int8 运行（本机 GPU 缺 libcublas）；直接传 numpy，绕开 av 版本不兼容。
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from scipy.signal import resample_poly


def main():
    spec_path, out_dir = sys.argv[1:3]
    with open(spec_path, encoding="utf-8") as f:
        segments = json.load(f)["segments"]
    model = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8")
    for i, seg in enumerate(segments, 1):
        path = os.path.join(out_dir, f"seg{i}.wav")
        audio, sr = sf.read(path, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        parts, _ = model.transcribe(resample_poly(audio, 16000, sr).astype(np.float32),
                                    language="zh", initial_prompt="以下是普通话的句子。")
        print(f"[{i}] 原文: {seg['text']}")
        print(f"[{i}] 转写: {''.join(p.text for p in parts)}\n")


if __name__ == "__main__":
    main()
