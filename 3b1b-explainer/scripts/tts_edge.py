"""微软 Edge 在线语音配音（默认晓晓甜美女声，+40% 即 1.4 倍速）。在工程目录运行：
    ~/.venvs/tts/bin/python <skill>/scripts/tts_edge.py [段id ...]
输出 audio/<段id>.wav 与 audio/durations.json。环境变量：EDGE_VOICE、EDGE_RATE、TTS_WORKERS。
注意：文本会发送到微软在线服务；含敏感内容时改用 tts_kokoro.py 或 IndexTTS（离线）。
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys

import edge_tts
import edge_tts.communicate as communicate
import numpy as np
import soundfile as sf
from edge_tts.constants import TRUSTED_CLIENT_TOKEN

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

# 2026-10 起旧主机 speech.platform.bing.com 返回 403（rany2/edge-tts#490），改用 Edge 155 的新主机；
# 若 edge-tts 发布了修复版，升级后可删掉这一行
communicate.WSS_URL = ("wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
                       f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}")

VOICE = os.environ.get("EDGE_VOICE", "zh-CN-XiaoxiaoNeural")
RATE = os.environ.get("EDGE_RATE", "+40%")
WORKERS = int(os.environ.get("TTS_WORKERS", "4"))
SR, PAD = 24000, 0.12
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def decode(mp3):
    raw = subprocess.run([FFMPEG, "-loglevel", "error", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", str(SR), "pipe:1"],
                         input=mp3, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768


def trim(wav, thr=0.008, keep=0.04):
    idx = np.flatnonzero(np.abs(wav) > thr)
    if not len(idx):
        return wav
    return wav[max(idx[0] - int(keep * SR), 0): min(idx[-1] + int(keep * SR), len(wav))]


async def synth(text):
    err = None
    for attempt in range(6):
        try:
            mp3 = b""
            async for chunk in edge_tts.Communicate(text, VOICE, rate=RATE).stream():
                if chunk["type"] == "audio":
                    mp3 += chunk["data"]
            if mp3:
                return mp3
        except Exception as e:  # noqa: BLE001
            err = e
        await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError(f"合成失败：{err!r}")


async def main():
    only = set(sys.argv[1:])
    dur_path = "audio/durations.json"
    durations = json.load(open(dur_path)) if os.path.exists(dur_path) else {}
    jobs = [(sid, say or sub) for sid, sub, say in SEGMENTS if not only or sid in only]
    sem, failed = asyncio.Semaphore(WORKERS), []

    async def run(sid, text):
        async with sem:
            try:
                wav = trim(decode(await synth(text)))
            except Exception as e:  # noqa: BLE001
                failed.append(sid)
                print(sid, "FAILED", e, flush=True)
                return
            wav = np.concatenate([wav, np.zeros(int(PAD * SR), dtype=np.float32)])
            sf.write(f"audio/{sid}.wav", wav, SR)
            durations[sid] = round(len(wav) / SR, 3)

    await asyncio.gather(*[run(sid, text) for sid, text in jobs])
    keep = {sid for sid, _, _ in SEGMENTS}
    durations = {k: v for k, v in durations.items() if k in keep}
    json.dump(durations, open(dur_path, "w"), indent=1)
    print(f"{len(jobs) - len(failed)} ok, total {round(sum(durations.values()), 1)}s, failed: {sorted(failed)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
