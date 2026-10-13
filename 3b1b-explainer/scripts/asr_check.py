"""用 faster-whisper（large-v3-turbo，默认 CPU int8）转写 audio/<段id>.wav，与朗读文本对照，
列出相似度最低的段，并把全部转写写到 logs/asr.txt。在工程目录运行：
  GPU（快，约 2 分钟/100 段）：用装了 faster-whisper 和 pip 版 nvidia-cublas/cudnn 的 venv（下例 ~/.venvs/asr），
  把这些库加进 LD_LIBRARY_PATH（WSL 另加 /usr/lib/wsl/lib）：
    SP=$(ls -d ~/.venvs/asr/lib/python3*/site-packages)
    LD_LIBRARY_PATH=$(ls -d $SP/nvidia/*/lib | tr '\n' ':')/usr/lib/wsl/lib ASR_DEVICE=cuda \
        ~/.venvs/asr/bin/python <skill>/scripts/asr_check.py [显示条数=15]
  CPU（慢，约 30 分钟/100 段）：
    uv run --quiet --python 3.11 --with faster-whisper --with soundfile --with scipy python <skill>/scripts/asr_check.py
同音字（会话/绘画、待/带、期/七）属识别误差；漏字、多字、英文词错位才需要返工。
"""
import difflib
import os
import re
import sys

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

CN = str.maketrans("0123456789", "零一二三四五六七八九")


def norm(t):
    return re.sub(r"[\s，。；：？！、,.;:?!“”\"'（）()·\-—…]", "", t).lower().translate(CN)


def main():
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    device = os.environ.get("ASR_DEVICE", "cpu")
    model = WhisperModel(os.environ.get("ASR_MODEL", "mobiuslabsgmbh/faster-whisper-large-v3-turbo"), device=device,
                         compute_type="float16" if device == "cuda" else "int8")
    rows = []
    os.makedirs("logs", exist_ok=True)
    with open("logs/asr.txt", "w", encoding="utf-8") as out:
        for sid, sub, say in SEGMENTS:
            audio, sr = sf.read(f"audio/{sid}.wav", dtype="float32")
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            parts, _ = model.transcribe(resample_poly(audio, 16000, sr).astype(np.float32), language="zh",
                                        initial_prompt="以下是普通话的句子。")
            hyp = "".join(p.text for p in parts)
            ref = say or sub
            r = difflib.SequenceMatcher(None, norm(ref), norm(hyp)).ratio()
            rows.append((r, sid, ref, hyp))
            out.write(f"{sid}\t{r:.2f}\t{ref}\t{hyp}\n")
    rows.sort()
    for r, sid, ref, hyp in rows[:top]:
        print(f"{r:.2f} {sid}\n  原文 {ref}\n  转写 {hyp}")


if __name__ == "__main__":
    main()
