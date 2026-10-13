"""把 narration.py 转成 voice06-narration（IndexTTS）的 spec.json，按段落角色配情绪。在工程目录运行：
    ~/.venvs/tts/bin/python <skill>/scripts/narration_to_spec.py $INDEX_TTS_ROOT/<任务>/spec.json [标题]
规则：开场与每个场景第 1 段 → 友好引入；以“建议/总结/所以”开头或标了 confident 的段 → 自信；其余 → 平静讲解。
讲解类内容情绪宜轻，英文术语多的段落保持平静，减少读歪。
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

CALM = [0, 0, 0, 0, 0, 0, 0, 0.8]
FRIENDLY = [0.2, 0, 0, 0, 0, 0, 0, 0.6]
CONFIDENT = [0.3, 0, 0, 0, 0, 0, 0, 0.5]


def main():
    out, title = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "讲解视频旁白")
    segs = []
    last_id = SEGMENTS[-1][0]
    for sid, sub, say in SEGMENTS:
        text = say or sub
        if sid.endswith("_1"):
            emo, label = FRIENDLY, "引入"
        elif text.startswith(("建议", "总结", "所以")) or sid == last_id:
            emo, label = CONFIDENT, "建议"
        else:
            emo, label = CALM, "讲解"
        segs.append({"label": f"{sid}·{label}", "id": sid, "text": text, "emo_vector": emo})
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"title": title, "lang": "ZH", "emo_alpha": 0.6, "segments": segs},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(segs)} segments -> {out}")


if __name__ == "__main__":
    main()
