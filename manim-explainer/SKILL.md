---
name: manim-explainer
description: 用 Manim 做带配音和字幕的中文讲解短视频：写分段旁白 → Edge 在线配音 → 写 Manim 场景 → 渲染 → 拼接成片。用户说“做个讲解视频”“用 Manim 做动画讲解”时使用。
---

# Manim 讲解视频

`$SK` = 本 skill 目录。模板在 `$SK/template/`，脚本在 `$SK/scripts/`。

## 环境

| 依赖 | 说明 |
|---|---|
| Manim Community Edition 0.18+ | `pip install manim`；`MANIM` 环境变量可指定可执行文件 |
| edge-tts | `pip install edge-tts`；旁白会发送到微软在线服务，敏感内容不要用 |
| ffmpeg / ffprobe | 需在 `PATH` 里 |
| 中文字体 | 默认 Noto Sans SC，可用 `FONT` 环境变量改 |

## 流程

### 1. 建工程
```bash
bash $SK/scripts/new_project.sh <工作目录>/video
```
工程放在 git 仓库之外。生成 `common.py`、`narration.py`、`scenes_demo.py`、`scenes.txt`。

### 2. 写旁白（`narration.py`）
- 每段是一个元组 `(段id, 字幕文本)`，一两句话。
- 开场提一个问题，中间逐步展开，最后总结。

### 3. 配音
```bash
python $SK/scripts/tts.py
```
生成 `audio/<段id>.mp3` 和 `audio/durations.json`。`EDGE_VOICE`、`EDGE_RATE` 可改音色和语速。

### 4. 写场景
场景继承 `common.Narrated`。`self.narrate(段id)` 显示字幕、加入配音，并返回这段配音的秒数。
动画时长要自己安排，让每段画面不短于配音：

```python
class Intro(Narrated):
    def construct(self):
        d = self.narrate("s1_1")
        self.play(Write(T("标题")), run_time=1.5)
        self.wait(max(d - 1.5, 0))
```

`scenes.txt` 每行写一个 `模块:场景类`，决定成片顺序。

### 5. 渲染与拼接
```bash
bash $SK/scripts/render.sh       # 默认 1080p；QUALITY=l 出低清预览
bash $SK/scripts/concat.sh out/成片.mp4
```
渲染完自己打开视频检查画面和声音。
