"""离线 Kokoro 中文配音（男声 zm_010，1.1 倍速）。在工程目录运行：
    ~/.venvs/tts/bin/python <skill>/scripts/tts_kokoro.py [段id ...]
英文走 misaki 英文管线；读错的词在 narration.py 第三项写读法（如 "S H A 二五六"、"open 九文"）。
"""
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ["HF_HUB_DISABLE_XET"] = "1"
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from kokoro import KModel, KPipeline  # noqa: E402

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

REPO, VOICE, SPEED, SR = "hexgrad/Kokoro-82M-v1.1-zh", os.environ.get("KOKORO_VOICE", "zm_010"), 1.1, 24000
only = set(sys.argv[1:])
model = KModel(repo_id=REPO).eval()
en = KPipeline(lang_code="a", repo_id=REPO, model=False)
zh = KPipeline(lang_code="z", repo_id=REPO, model=model, en_callable=lambda t: next(en(t)).phonemes)

dur_path = "audio/durations.json"
durations = json.load(open(dur_path)) if os.path.exists(dur_path) else {}
for seg_id, sub, say in SEGMENTS:
    if only and seg_id not in only:
        continue
    wav = np.concatenate([r.audio.numpy() for r in zh(say or sub, voice=VOICE, speed=lambda n: SPEED)])
    wav = np.concatenate([wav, np.zeros(int(0.12 * SR), dtype=wav.dtype)])
    sf.write(f"audio/{seg_id}.wav", wav, SR)
    durations[seg_id] = round(len(wav) / SR, 3)
    print(seg_id, durations[seg_id], flush=True)
json.dump(durations, open(dur_path, "w"), indent=1)
print("total", round(sum(durations.values()), 1))
