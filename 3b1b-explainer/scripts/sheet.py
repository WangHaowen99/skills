"""每段旁白结尾抽一帧，拼成 3 列联系表 logs/sheet_<场景>.png，用来逐段检查重叠、出界、字幕遮挡。
用法：python sheet.py <场景> [视频路径]（render.sh preview 会自动调用）
"""
import json, subprocess, sys, os, glob, shutil
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
from PIL import Image, ImageDraw
scene, cols = sys.argv[1], 3
vid = sys.argv[2] if len(sys.argv) > 2 else glob.glob(f"media/**/480p15/{scene}.mp4", recursive=True)[0]
timing = json.load(open(f"logs/timing_{scene}.json"))
os.makedirs("logs/frames", exist_ok=True)
tiles = []
for sid, t0, t1 in timing:
    out = f"logs/frames/{sid}.png"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", f"{max(t1-0.15,0):.2f}", "-i", vid, "-frames:v", "1", "-vf", "scale=640:-1", out], check=True)
    im = Image.open(out).convert("RGB"); ImageDraw.Draw(im).text((6, 4), sid, fill=(255, 80, 80)); tiles.append(im)
w, h = tiles[0].size; rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(f"logs/sheet_{scene}.png"); print(f"logs/sheet_{scene}.png", len(tiles))
