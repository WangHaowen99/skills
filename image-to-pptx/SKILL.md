---
name: image-to-pptx
description: 把截图或设计稿复刻成可编辑的 pptx（原生矢量形状，不贴图）。用户要把图片转成 PPT、按图还原成可编辑幻灯片、或往这类 deck 里加页时调用。
---

# 按图复刻可编辑 pptx

把截图**复刻**成全矢量 pptx——色块、箭头、图标都是原生形状，选中即可改色改字，没有一张位图。

工具在 [`tools/`](tools/)：

| 文件 | 内容 |
|---|---|
| `deck_kit.py` | 底层：坐标换算、基本形状、文本框、字体槽位、存盘 |
| `draw_kit.py` | 扩展图元：折线 / 弯箭头、独立圆角、混排多行文本、编号圆、胶囊标签、原生表格 |
| `components.py` | 版面组件（C1–C28）、控件与页型模板，编号和 ppt-deck 的 `STYLE.md` 一致 |
| `arch_diagram.py` | C1 分层架构图排版引擎：写规格 → 自动排版 → 自动体检 |
| `process_flow.py` | C29 工序流程图（人机分工）排版引擎：写规格 → 自动排版 → 自动体检 |
| `icon_lib.py` | 77 个线性图标，签名统一 `ic_xxx(sh, cx, cy, s, c)` |
| `preview.py` / `verify.py` | 单页渲染 / 交付体检 |

渲染器的坑见 [`PITFALLS.md`](PITFALLS.md)——**回看**发现图形不对时再读。

只要排版设计稿和文案、不落 pptx 文件，用 `ppt-deck` skill。

## 铁律

工具替不了的四条：

- **复刻不是重画。** 版式、配色、文案照源图，不做"更好的设计"。用户要的是那张图能编辑，不是你的审美。
- **糊字必须标注。** 源图的 CJK 常有渲染损坏（"业条"←业务、"实旆"←实施、"槌定"←稳定）。按语义补可以，**但交付时必须列出改了哪些字、原图糊成什么样**。默默编一个词是这个任务里最严重的错误——用户无从发现。拿不准的单独点出来。
- **箭头最后画。** 面板卡片会盖住先画的图形。跨面板连线、贯穿性长线，一律放在所有面板之后；长线要穿过表格时拆成两段绕开。
- **宽度留一成余量。** `word_wrap=False` 不是所有渲染器都认，本机无微软雅黑时回落字体宽 7~12%。`wpx()` 估宽后乘 1.1 再和可用宽比，不要卡边。

## 组件：先套组件，再拼图元

`from components import *` 一行拿到全部工具。组件只管「画什么、按什么顺序画」，几何参数照源图量了显式传入，不替你猜位置。

| 编号 | 组件 | 用途 |
|---|---|---|
| C1 | `arch_layer` `module_cell` `fanout` `bi_arrow` | 分层架构图底层件（整张图用下面的 `arch_diagram` 引擎） |
| C2 | `grouped_table` | 原生表格，首列分组合并、重点行底色、逐格框线 |
| C5 | `line_chart_card` `metric_card` `ba_parts` `stat_line` | 折线图卡（平滑 / 直线、网格、编号标注）；前后对比指标卡；数字标红的统计条 |
| C6 | `step_chain` `flow_band` | 推导条（①→②→③）、闭环条 |
| C7 | `milestone_timeline` | 里程碑时间轴，当前节点标红，阶段卡带状态带 |
| C8 | `feature_row` | 一排特性卡：图标 + 关键词说明 + 结果数字 |
| C9 | `numbered_item` | 红圆编号 + 标题 + 说明 |
| C10 | `cycle_diagram` `cycle_arrows` | 回路图：节点盒 + 弯箭头 |
| C11 | `tag_title` `icon_disc` | 胶囊标签标题、图标圆底 |
| 框架 | `page_title` `panel` `section_title` `footer` | 标题、面板、区块标题、页脚 |
| 页型 A | `overview_page` | 左上图表 + 指标卡，右上时间轴 + 统计条，下方特性卡 |
| C12–C16 | `hero_card` `dumbbell` `waterfall` `harvey_matrix` `quadrant` | 英雄数字卡、哑铃图、瀑布图、哈维球矩阵、四象限 |
| C17、C22–C28 | `driver_tree` `fishbone` `funnel` `bullet_list` `risk_matrix` `strategy_house` `maturity_steps` `hub_spoke` | 指标拆解树、鱼骨图、漏斗图、子弹图、风险矩阵、战略屋、成熟度阶梯、中心辐射图（对应范式八–十三） |
| C18、C20 | `swimlane` `chevron_flow` | 泳道路标图、箭头流程 |
| 控件 | `delta_badge` `status_dot` `progress_bar` `harvey_ball` `callout` `sample_tag` `sparkline` `chip` | 涨跌徽标、状态点、细进度条、哈维球、引线标注、示意数据角标、迷你趋势线、全圆角胶囊 |

**两个排版引擎**（只写内容，不写坐标；出图同时返回体检结果，有 error 就改文案或规格再出）：

```python
from arch_diagram import *                      # 分层架构图
use_theme(LIGHT)
h, report = arch_diagram(sh, x, y, w, dict(
    layers=[Layer("业务\n平台层", title="…", rows=[Row(M("模块", icon=ic_chat), ...)]),
            Layer("协议层", focus=True, rows=[...]),
            Layer("引擎\n实现层", boxes=[Box("实现 A", Group(None, "能力1", "能力2")), ...])],
    actors=Edge("使用者", ...), external=Edge("外部依赖", ...), side=Side("安全\n管控", ...),
    fanout=dict(a=1, b=2, label="按项目切换"), boundary="系统边界"))

from process_flow import *                      # 工序流程图
h, report = process_flow(sh, x, y, w, dict(
    lanes=dict(left=("专家", ic_person), right=("系统", ic_gear)), input=("资料", "投入"),
    steps=[Step("读料", hot=True, left=Check("定目标"), right=Cap("长文档解析", "分页 / 检索")), Product("阶段产物"), ...],
    output=("发布", "交付"), loop=dict(src=6, dst=4, out="不过", note="定位问题\n回到 ④")))
```

- 文本小工具：`txt` 单个 run，`kw_line` 生成「**关键词：**说明」，`num_parts("约 {1200} 次")` 生成花括号内放大标红的数字。
- 风格：默认是复刻风 `REPLICA`（按原图取色，已交付页面重建不变）。新做页面先切风格：`use_theme(LIGHT)` 浅色复刻风（圆角、浅红强调），`use_theme(STYLE)` ppt-deck 规范风（直角）。两者都是浅色系：图形不用黑色和深灰，实心灰块配深字。切换后页面里要用 `T` 时再 `from components import T` 一次。
- 用法样例：`tools/page_template.py`（常用组件各调一次，数据都是示意值）。
- **改了组件或 icon_lib 之后**，拿现有页面重建，比对 slide XML（C14N 规范化）和渲染图，确认旧页面没被牵连。

## 步骤 1 · 定画布，清点区块

读源图，按**源图像素**建坐标系——脚本里的数字能直接和图对照，不必反复算英寸。

```python
CANVAS = (1673, 951)      # 源图尺寸；幻灯片恒为 13.333x7.5in，比例差 1% 内不可察
```

逐块记下边界与文字：面板、卡片、表格、箭头、图标、页脚。文字**逐字抄**，遇到看不清的先标记，不要当场猜。

**完成判据**：每个区块都有 (x, y, w, h)，每段文字都已转录或标记为待定。

## 步骤 2 · 搭版面

一页一个模块文件（`p1.py`、`p2.py`…），每个定义 `build(sh)`，照 `tools/page_template.py`。入口脚本串起来调 `save()`。

先对照上面的组件表：源图里有的结构能用组件就用组件，与页型 A 同构的整页直接用 `overview_page`；组件覆盖不到的再用 `draw_kit` 图元拼。

工具层已经替你处理掉的，不用操心：
- 字体四槽位 + `noProof`（`style_run`）、主题字体（`save`）。
- 弯箭头的实心三角（`bez` / `curve_arrow`）。
- QuickLook 的几处渲染差异：编号圆、拼接色差、表格行高，见 PITFALLS。

自己要守的：
- **图标不编组**、**箭头最后画**、**留宽度余量**。
- **表格用原生表格**（`grouped_table` / `native_table`），不要拼文本框——用户要在 PowerPoint 里增删行、拖列宽。
- **新画的图标进 `icon_lib`**：签名 `ic_xxx(sh, cx, cy, s, c, accent=None)`，不要把写死坐标的图标留在页面脚本里。

**完成判据**：`build` 跑通，形状数非零。

## 步骤 3 · 回看

**只有渲染出来才知道对不对。** XML 合规、python-pptx 不报错，和版面没压字是两回事——折行、溢出、被盖住的图形，全部只在渲染图上现形。

```bash
python3 tools/preview.py p3                          # 渲染单页（qlmanage 只渲第一页，必须单独构建）
python3 tools/preview.py p3 --crop 1240,180,1660,760 # 放大某块核对细节
```

把渲染图和源图逐块比。**每一页都要看**，不能只看第一页。典型问题：文字折行撑破框、两段文字重叠、图形被后画的面板盖掉、预置几何没渲染出来。对不上先查 [`PITFALLS.md`](PITFALLS.md)。

**完成判据**：每一页都渲染并比对过；无折行、无压字、无缺失图形。

## 步骤 4 · 体检交付

```bash
python3 tools/verify.py out.pptx     # 退出码 0 才算过
```

查字体槽位、`noProof`、以及 QuickLook 不渲染的高危预置几何。**不要靠肉眼代替这一步。**

交付时一并给出：

- 生成脚本位置（用户要改文案时搜中文替换重跑）
- **糊字清单**——改了哪些字、原图糊成什么样、哪几处没把握
- 本机若无微软雅黑，说明预览是回落字体，pptx 里字体名正确

**完成判据**：`verify.py` 退出码 0；糊字清单已交给用户。
