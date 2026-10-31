"""Edge 在线配音。在工程目录运行：python <skill>/scripts/tts.py
输出 audio/<段id>.mp3 和 audio/durations.json。环境变量：EDGE_VOICE、EDGE_RATE。
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys

import edge_tts
import edge_tts.communicate as communicate
from edge_tts.constants import TRUSTED_CLIENT_TOKEN

sys.path.insert(0, os.getcwd())
from narration import SEGMENTS  # noqa: E402

# 旧主机 speech.platform.bing.com 返回 403（rany2/edge-tts#490），改用新主机
communicate.WSS_URL = ("wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
                       f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}")

VOICE = os.environ.get("EDGE_VOICE", "zh-CN-XiaoxiaoNeural")
RATE = os.environ.get("EDGE_RATE", "+20%")
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def duration(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out), 3)


async def main():
    os.makedirs("audio", exist_ok=True)
    durations = {}
    for sid, text in SEGMENTS:
        path = f"audio/{sid}.mp3"
        await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)
        durations[sid] = duration(path)
        print(sid, durations[sid])
    json.dump(durations, open("audio/durations.json", "w"), indent=1)


if __name__ == "__main__":
    asyncio.run(main())
