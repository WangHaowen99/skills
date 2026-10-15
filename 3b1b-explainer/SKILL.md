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
  - Edge 免费通道的普通话音色只有：晓晓、晓伊（女），云扬（新闻播报，沉稳）、云健、云希、云夏（男）。云泽等 Azure 专有音色会返回 NoAudioReceived，要 Azure Speech 密钥。用户点名的音色先试一句，不行就出几个试听样本让用户选。
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
| Edge 晓晓（默认） | `TTS_WORKERS=8 ~/.venvs/tts/bin/python $SK/scripts/tts_edge.py [段id…]` | `EDGE_VOICE`/`EDGE_RATE` 可改（如 `zh-CN-YunyangNeural`）。已内置 2026-10 的 403 绕行（新主机）。90 段约 25 秒 |
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

**核对**（不能跳过，模型听不到声音）。放后台跑（有 GPU 用 CUDA，见 `asr_check.py` 开头），同时去写场景，不要干等。
脚本默认 `HF_HUB_OFFLINE=1`，跳过 HuggingFace 联网检查（网络不通时会白等约 280 秒）；首次下载模型时设 `HF_HUB_OFFLINE=0`。
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
- 不要对带不透明底色的组合用 `Indicate`：它把底色整块染成实色、盖住文字（白底尤其明显）。用 `common.soft_indicate`。
- 同一对象的多段 `.animate.move_to` 串在 `Succession` 里（尤其套在 `LaggedStart` 中）时，后几段会从初始位置起跳、斜穿画面。改用一条折线路径 + `MoveAlongPath`。
- `Arc.add_tip` 会改变弧的尺寸；JetBrains Mono 会把 `->` 连写成箭头字形。
- 节点连线用 `edge_arrow`：端点按外接矩形求交（圆角矩形用 `get_boundary_point` 会落到角上，水平线发歪），箭头尖固定大小。

### 并行写场景（场景 ≥ 6 个时推荐）
写场景是全流程最大的耗时块（单次输出 1~4 万 token，串行写 11 个场景约 40~50 分钟）。做法：
1. 主会话先写共享部件 `kit.py`：贯穿全片的主图（固定坐标）、标题条、收益标签行、代码块等；`scenes.txt` 先按“模块:场景类”定好。
2. 按模块把场景分给 3~4 个子代理（后台运行），每个只写自己的模块文件，禁止改 common/kit/narration/scenes.txt；给出各自场景的分镜、核实过的事实、章节号；预览用 `JOBS=3`。
3. 子代理自己跑预览、读联系表和 `logs/layout_*.txt`，修到干净再回报。主会话收到一个就终检一个，通过的立即后台 `render.sh hq <场景>`（流水线，不等全部写完）。
4. kit 有缺陷时由主会话统一修，再通知仍在工作的子代理重渲。
5. 多个子代理并行时，白底直接把 `common.py` 里 `THEME` 的默认值改成 `"light"`，免得有人漏设环境变量。

## 5. 预览与检查（每批改动都走一遍）
```bash
bash $SK/scripts/render.sh preview [场景…]   # 480p，并行，独立 media 目录，自动出联系表 + 超时检查
```
- 先看自动排版检查：`common.py` 在每段结束时检查出界、压字幕、文字重叠、字太小（正文 <18、代码 <16），写 `logs/layout_<场景>.txt`，render.sh 结尾汇总。日志为空不代表没问题，仍要看图。
- **逐张 Read** `logs/sheet_<场景>.png`。每格是一段旁白结束时的画面，左上角标着段 id。
- 检查：重叠、出界、被字幕挡住、字太小、标签离对象太远、遗留元素没清掉、白底下颜色太淡。
- 修完只重渲改动的场景。
- 想细看某几格时，用 PIL 把那几格裁出来拼在一起再 Read。
- 超时检查：`check_timing.py` 报“超出配音”的段落会出现冷场，要缩短该段动画。

## 6. 成片
```bash
JOBS=8 bash $SK/scripts/render.sh hq                            # 1080p30，多场景并行（JOBS 默认 7）
bash $SK/scripts/concat.sh out/<成片名>.mp4                     # 按 scenes.txt 拼接：视频流直接拷贝（约 15 秒），音频 loudnorm -16 LUFS
python $SK/scripts/flash_scan.py out/<成片名>.mp4                # 查过渡中的实色闪烁；白底加 THEME=light
```
- 提速靠多进程并行，不靠 Manim 的 OpenGL 渲染器：实测单场景 OpenGL 比 Cairo 还慢，还要处理 `VMobject`、`z_index` 等兼容问题。
  12 核机器上 10 个场景 1080p 并行约 2~3 分钟。
- 拼接默认不重编码视频（实测各场景交界音画偏移 0 ms）；播放异常时 `VCODEC=libx264` 或 `VCODEC=h264_nvenc` 回退到重编码。
- GPU 用在配音核对（CUDA 版 faster-whisper）上。
- 渲染目录放 Linux 本地盘（ext4）而不是 Windows 挂载盘，实测只快约 8%，不值得折腾。

验收：
- `ffprobe` 看分辨率和时长。
- `volumedetect` 平均约 -19 dB。
- `silencedetect=n=-45dB:d=2.5` 应该是 0 段。
- 用成片再出一两张联系表抽查。联系表只看每段结尾，过渡中的问题（如 Indicate 实色闪烁）要靠 `flash_scan.py`。

### 耗时参考（8.5 分钟成片，11 场景 89 段）
| 阶段 | 耗时 | 备注 |
|---|---|---|
| Edge 配音 | 约 25 秒 | `TTS_WORKERS=8` |
| ASR 核对 | 约 1 分钟 | GPU + 离线加载模型 |
| 写场景（4 个子代理并行） | 约 40 分钟 | 单个子代理 25~40 分钟；按段数均分可再省一点 |
| 1080p 渲染 | 每批 3~4 个场景 1~2 分钟 | 与写场景流水线并行 |
| 拼接 | 约 15 秒 | 视频流拷贝；整片重编码要 4~5 分钟 |

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
