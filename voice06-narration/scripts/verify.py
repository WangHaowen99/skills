"""用本机缓存的 faster-whisper 转写每段，和 spec 原文对照，用于发现漏读/读歪。

用法:
    uv run --quiet --python 3.11 --with faster-whisper --with soundfile --with scipy \
        python <skill>/scripts/verify.py spec.json OUT_DIR
默认 CPU int8。有 GPU 时设 ASR_DEVICE=cuda（需要 CUDA 版 faster-whisper 和 cublas/cudnn 库，
用法同 3b1b-explainer 的 asr_check.py 开头说明）。直接传 numpy，绕开 av 版本不兼容。
默认 HF_HUB_OFFLINE=1：模型已缓存时跳过联网检查（连不上时会卡约 280 秒）；首次下载设 HF_HUB_OFFLINE=0。
"""
import json
import os
import sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402
from scipy.signal import resample_poly  # noqa: E402


def main():
    spec_path, out_dir = sys.argv[1:3]
    with open(spec_path, encoding="utf-8") as f:
        segments = json.load(f)["segments"]
    model = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo",
                         device=os.environ.get("ASR_DEVICE", "cpu"),
                         compute_type="float16" if os.environ.get("ASR_DEVICE") == "cuda" else "int8")
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
