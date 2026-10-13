"""按 spec.json 分段合成：每段一个情绪向量，输出 seg<N>.wav 与 params.json。

用法（在 index-tts 根目录用其 venv 运行）:
    .venv/bin/python <skill>/scripts/synth.py spec.json OUT_DIR [段号 ...]
传段号时只重做这些段，旧文件先改名为 seg<N>_v<k>.wav 保留。
"""
import json
import os
import shutil
import sys

INDEX_TTS_ROOT = os.environ.get("INDEX_TTS_ROOT", os.path.expanduser("~/index-tts"))
sys.path.insert(0, INDEX_TTS_ROOT)
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from indextts.infer_v2_5 import IndexTTS2  # noqa: E402

DEFAULT_SPEAKER = os.path.join(INDEX_TTS_ROOT, "examples", "voice_06.wav")


def backup(path):
    if not os.path.exists(path):
        return
    stem = path[:-4]
    k = 1
    while os.path.exists(f"{stem}_v{k}.wav"):
        k += 1
    shutil.move(path, f"{stem}_v{k}.wav")


def main():
    spec_path, out_dir, *only = sys.argv[1:]
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    speaker = spec.get("speaker", DEFAULT_SPEAKER)
    emo_alpha = float(spec.get("emo_alpha", 0.6))
    lang = spec.get("lang", "ZH")
    os.makedirs(out_dir, exist_ok=True)

    tts = IndexTTS2(cfg_path=os.path.join(INDEX_TTS_ROOT, "checkpoints", "config.yaml"),
                    model_dir=os.path.join(INDEX_TTS_ROOT, "checkpoints"), use_bf16=True)
    for i, seg in enumerate(spec["segments"], 1):
        if only and str(i) not in only:
            continue
        out = os.path.join(out_dir, f"seg{i}.wav")
        backup(out)
        tts.infer(spk_audio_prompt=speaker, text=seg["text"], lang=lang, output_path=out,
                  emo_vector=seg.get("emo_vector"), emo_alpha=emo_alpha, use_random=False,
                  duration_factor=float(seg.get("duration_factor", 1.0)))

    with open(os.path.join(out_dir, "params.json"), "w", encoding="utf-8") as f:
        json.dump({**spec, "speaker": speaker, "emo_alpha": emo_alpha, "model": "IndexTTS-2.5 bf16",
                   "emo_order": "喜,怒,哀,惧,厌恶,低落,惊讶,平静"}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
