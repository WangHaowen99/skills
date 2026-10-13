---
name: 3b1b-explainer
description: 用 Manim 做 3Blue1Brown 风格的中文讲解视频（动画 + 配音 + 烧录字幕，1080p）：定提纲→写分段旁白→配音（Edge 晓晓甜美女声 / IndexTTS 情绪配音 / 离线 Kokoro）→按配音时长写场景→480p 预览 + 逐段联系表检查排版→1080p 并行渲染→拼接响度统一→归档。用户说“做成视频”“3b1b 风格讲解”“动画讲解视频”“把这份方案/文档讲成视频”时使用；“待决策项/方案对比”类内容有现成的“背景→分析→选项→建议”模板。
---

# 3b1b 风格讲解视频

`$SK` = 本 skill 目录。模板在 `$SK/template/`，脚本在 `$SK/scripts/`。
所有脚本都在**工程目录**里运行（它们从当前目录读 `narration.py`、`audio/`、`scenes.txt`）。

## 环境

| 依赖 | 默认位置 | 改用其他位置 |
|---|---|---|
| Manim CE 0.22（python 3.11） | `~/.venvs/manim` | `MANIM=…/manim`、`MANIM_PY=…/python` |
| TTS：edge-tts、kokoro | `~/.venvs/tts` | 直接换解释器路径 |
| ffmpeg / ffprobe | `PATH` 里的 | `FFMPEG=…`、`FFPROBE=…` |
| IndexTTS（可选，情绪配音） | — | `INDEX_TTS_ROOT=…`，见 skill `voice06-narration` |
| 字体 | 正文 LXGW WenKai，代码 JetBrains Mono | 改 `common.py` 的 `FONT` / `MONO` |

可选开关：
- `THEME=light`：白底配色（强调色自动换成深色版）。不设为深色底。
- `VCODEC=h264_nvenc`：拼接时用 NVIDIA GPU 编码，比 libx264 快几倍；个别驱动或滤镜组合下 NVENC 会崩，崩了就去掉。

## 0. 先定四件事（用户没说就按默认，开工时说明）
- **受众和时长**：中文讲解约 7 字/秒（1.4 倍速女声）或 4.5 字/秒（常速）。10 分钟大约 4000 字。
- **配音**：
  - 默认：Edge 晓晓甜美女声，+40%。
  - 敏感内容不能出网时：离线 Kokoro，或 IndexTTS（本机 GPU）。
- **画面**：16:9 1080p30，深色或白色底，字幕烧录在底部。
- **输出**：工程放在 `<工作目录>/<任务>/video/`，成片放在 `out/`。
  - 工作目录必须在任何 git 仓库之外。内容含人名、内部信息时绝不提交。

安全：
- 人名只在画面上出现，旁白里用角色称呼，如“core 负责人”。
- 要用户亲自决定的事项，称呼用用户指定的说法，例如“工具负责人”，不要用“你”。
- 云 TTS 会把旁白发出去，内容敏感时先确认。

## 1. 建工程
```bash
bash $SK/scripts/new_project.sh <工作目录>/<任务>/video
```
生成的文件：
- 库：`common.py`（同步框架 + 部件）、`dkit.py`（待决策项模板）。
- 示例：`narration.py`、`scenes_demo.py`、`scenes.txt`。可以先跑通示例再改。

## 2. 提纲与旁白（`narration.py`）
**结构**：
1. 开场：用一个具体问题或场景引入。
2. 先讲规则或全局图。
3. 再逐项展开。
4. 最后汇总，并回扣开场。

讲“待决策项”时，每项按 **背景 → 分析 → 选项（2~3 个，带优缺点）→ 建议（含条件/理由）** 四步，最后给汇总表。

**每段**：
- 格式是元组 `(段id, 字幕文本, 朗读文本或None)`。
- 1~2 句，30~60 字。字幕最多两行，约 66 字以内；超过会变三行，挤占画面。
- 段 id 写成 `<场景前缀>_<序号>`，例如 `d3_5`。前缀对应场景，序号连续。

**朗读文本**（第三项）专门处理读音：
- 数字写成汉字：`10 月 15 日` → `十月十五日`；`801 号` → `八零一号`；`404` → `四零四`。
- 缩写拆成字母：`SHA-256` → `S H A 二五六`；`ID` → `I D`；`doc` → `D O C`。
- 难读的专名音译：`openJiuwen` → `open 九文`。
- 怎么拼都读不准的缩写，朗读时改说全称，字幕保留缩写并注明，例如字幕 `MMR（最大边际相关）`、朗读 `最大边际相关`。

**原则**：先给结论再给原因。一段只讲一个点。事实要有依据：涉及代码就去核对源码，文档之间有冲突就照实讲出来。

## 3. 配音（任选一种，产出 `audio/<段id>.wav` + `audio/durations.json`）
| 方式 | 命令 | 说明 |
|---|---|---|
| Edge 晓晓（默认） | `~/.venvs/tts/bin/python $SK/scripts/tts_edge.py [段id…]` | `EDGE_VOICE`/`EDGE_RATE` 可改。已内置 2026-10 的 403 绕行（新主机） |
| IndexTTS | 见下 | 本机离线、带情绪；按 skill `voice06-narration` 的流程走 |
| Kokoro | `~/.venvs/tts/bin/python $SK/scripts/tts_kokoro.py [段id…]` | 离线男声；英文和数字容易读错，靠朗读文本修 |

IndexTTS 流程：
1. `~/.venvs/tts/bin/python $SK/scripts/narration_to_spec.py $INDEX_TTS_ROOT/<任务>/spec.json <标题>`
   - 情绪按段落角色分配：每场景第 1 段友好，“建议/所以”开头和最后一段自信，其余平静。
2. 用 `voice06-narration` 的 `synth.py` 后台合成。RTF≈1.1~1.3，70 段约 15 分钟。
3. 用它的 `verify.py` 核对。
4. 导入工程：`~/.venvs/tts/bin/python $SK/scripts/apply_voice.py <spec.json> <seg目录> --speed 1.4`
   - 会做变速、去首尾静音、统一音量。
   - 改倍速只需重跑这一步，不必重新合成。

IndexTTS 合成要十几分钟。可以先按“字数 ÷ 6.3 秒”生成静音占位音频和 `durations.json`，把场景写完、预览排版；
导入真配音前把占位 `audio/` 复制成 `audio_ref/`，动画会按新旧时长比自动调节节奏（见下）。

**核对**（不能跳过，模型听不到声音）：
```bash
uv run --quiet --python 3.11 --with faster-whisper --with soundfile --with scipy python $SK/scripts/asr_check.py
```
- 有 GPU 时按 `asr_check.py` 开头的说明用 CUDA 跑，100 段约 2 分钟。
- 同音字（会话/绘画、待/带、期/七、时/十）是识别误差，可以忽略；转写成繁体也会拉低相似度。
- 漏字、多字、英文错位才需要返工：改朗读文本，然后只重配该段。

**换配音但不想改动画**：
1. 先把旧音频目录复制为 `audio_ref/`，再生成新音频。
2. `common.py` 会按每段“新/旧”时长之比自动加速动画，只加速不减速。也可以用 `PACE_REF=<目录>` 指定参考目录。

## 4. 写场景（按配音时长编排）
同步模型：
```python
class S1Foo(Base):                     # 待决策项用 Decision（dkit.py）
    def construct(self):
        with self.voice("s1_1"):       # 进入时挂音频和字幕
            self.play(...)             # 块内动画总时长 ≤ DUR["s1_1"]，不足部分自动等待
        self.fade_all()
```
- 写之前打印每段时长，按时长分配动画。
- 每个场景 5~12 段。`scenes.txt` 按顺序列出 `模块:场景类`。
- 部件：`pill` `container` `arrow` `darrow`（虚线箭头）`edge_arrow`（环形流程）`chip`（编号标题条）`tagged` `check` `xmark` `strike` `db_icon` `file_icon` `folder_icon` `image_icon` `browser_icon` `person_icon` `name_tag` `toggle` `clock_icon` `envelope` `flow_dot`。
- 项目里反复出现的部件（流程行、卡片、计数器）放到工程自己的 `wk.py`，`from common import *` 后在上面扩展。
- Decision 模板的用法：
  - `header()` 显示标题条。
  - `step(i)` 切换背景/分析/选项/建议，并清空正文。
  - `options(segs, specs)` 每段旁白亮一张选项卡。
  - `recommend(cards, {下标: "建议"})` 高亮建议的选项，可以有多个标签，例如“现在”“目标”。
  - `note(text)` 在卡片下逐行加理由。

**3b1b 风格要点**：
- 一个节拍只引入一个新东西，逐步搭出全图。
- 颜色固定代表含义：黄=强调/建议，红=风险/错误，绿=正确。
- 优先用 Transform/移动表达变化，少硬切。
- 用 Indicate、ShowPassingFlash、flow_dot 引导视线。
- 结尾回扣开场的问题。

**排版规则**（预览里最常见的问题都来自这里）：
- 内容放在 y ∈ [-2.3, 3.6]，|x| ≤ 6。
- 字幕两行时顶部约在 -2.75，三行时约在 -2.2。三行字幕的段落，内容底边要 > -2.1。
- 字号 ≥ 18，代码 ≥ 16。
- 补充说明不要放到底部和字幕抢位置，改为替换标题位，或者放在已腾空的区域。
- 文字压在线上时，加 `BackgroundRectangle`，或者给图形垫一层实心 BG 底。
- 箭头标签两两之间要错开，相邻箭头间距 ≥ 0.55。图块之间留够放标签的空隙（≥ 1.8）。
- 两位数编号会溢出圆形，`chip`/`item_card` 已自动缩小。
- `Text` 会吞掉前导空格，缩进用 `NBSP`，或者直接 `shift`。

**常见坑**：
- `Group`（含 Image 等）不能放进 `VGroup`。要收集“场上所有对象”时用 `Group(*self.mobjects…)`。
- 不要在 `DashedVMobject` 上调 `point_from_proportion`。
- `NumberLine(include_numbers=True)` 需要 LaTeX；没装 LaTeX 时关掉，用 `T()` 自己画刻度。
- 不要给 `VGroup` 设名为 `color` 的属性（如 `box.color = …`），会把整组染成同一色。自定义属性换个名字。
- 想“暗掉”一个已有边框和底色的部件，`set_opacity` 会把填充也拉满；换成用颜色插值重建一个，再 `Transform`。
- 清场时列出要保留的对象，要按场上的实际成员列：用 `LaggedStart` 逐个 `FadeIn` 的组，场上是一个个成员而不是组本身，`keep` 里要展开成 `*group`。

## 5. 预览与检查（每批改动都走一遍）
```bash
bash $SK/scripts/render.sh preview [场景…]   # 480p，并行，独立 media 目录，自动出联系表 + 超时检查
```
- **逐张 Read** `logs/sheet_<场景>.png`。每格是一段旁白结束时的画面，左上角标着段 id。
- 检查：重叠、出界、被字幕挡住、字太小、标签离对象太远、遗留元素没清掉、白底下颜色太淡。
- 修完只重渲改动的场景。
- 想细看某几格时，用 PIL 把那几格裁出来拼在一起再 Read。
- 超时检查：`check_timing.py` 报“超出配音”的段落会出现冷场，要缩短该段动画。

## 6. 成片
```bash
JOBS=8 bash $SK/scripts/render.sh hq                            # 1080p30，多场景并行（JOBS 默认 7）
VCODEC=h264_nvenc bash $SK/scripts/concat.sh out/<成片名>.mp4   # 按 scenes.txt 拼接，loudnorm -16 LUFS
```
- 提速靠多进程并行，不靠 Manim 的 OpenGL 渲染器：实测单场景 OpenGL 比 Cairo 还慢，还要处理 `VMobject`、`z_index` 等兼容问题。
  12 核机器上 10 个场景 1080p 并行约 2~3 分钟。
- GPU 用在拼接编码（`VCODEC=h264_nvenc`）和配音核对（CUDA 版 faster-whisper）上。

验收：
- `ffprobe` 看分辨率和时长。
- `volumedetect` 平均约 -19 dB。
- `silencedetect=n=-45dB:d=2.5` 应该是 0 段。
- 用成片再出一两张联系表抽查。

## 7. 归档与汇报
- **归档**：按用户习惯放到对应项目目录或云盘收件箱。文件名带日期，不覆盖旧版；配音源文件和视频工程源码（不含 `media/`）可以一起打包。
- **汇报**：
  - 成片路径、时长、做法。
  - 章节/要点表。
  - 核对结果，以及残留的同音误识别。
  - 与资料不一致或需要用户拍板的地方。
  - 怎么改：改词 → 重配该段 → 重渲染 → 拼接。

## 参考实现
`template/scenes_demo.py`：一个普通场景加一个待决策项场景，跑通后照着扩展。
