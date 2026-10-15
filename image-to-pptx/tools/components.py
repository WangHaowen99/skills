# -*- coding: utf-8 -*-
"""可复用的版面组件与页型模板（构建子系统 deck 沉淀，2026-10）。

    from components import *      # 含 draw_kit、icon_lib、deck_kit 的全部名字

组件编号与 ppt-deck 的 STYLE.md 一致（C1–C14），设计稿里写编号，落 pptx 时调这里的函数：

    C1  arch_layer / module_cell / fanout / bi_arrow      分层架构图
    C2  grouped_table                                     分组表格（原生表格）
    C5  line_chart_card / metric_card / ba_parts / stat_line   折线图卡、前后对比指标卡、统计条
    C6  step_chain / flow_band                            推导条、闭环条（C6 的两种变体）
    C7  milestone_timeline                                里程碑时间轴
    C8  feature_row                                       特性卡（图标 + 关键词说明 + 结果数字）
    C9  numbered_item                                     编号要点
    C10 cycle_diagram / cycle_arrows                      回路图
    C11 tag_title / icon_disc                             标签标题、图标圆底
    C12 hero_card 英雄数字卡      C13 dumbbell 哑铃图        C14 waterfall 瀑布图
    C15 harvey_matrix 哈维球矩阵  C16 quadrant 四象限        C17 driver_tree 指标拆解树
    C18 swimlane 泳道路标图       C20 chevron_flow 箭头流程   C22 fishbone 鱼骨图
    C23 funnel 漏斗图             C24 bullet_list 子弹图      C25 risk_matrix 风险矩阵
    C26 strategy_house 战略屋     C27 maturity_steps 成熟度阶梯  C28 hub_spoke 中心辐射图
    控件 delta_badge / status_dot / progress_bar / harvey_ball / callout / sample_tag / sparkline / chip
    框架 page_title / panel / section_title / footer
    页型 overview_page                                    页型 A：图表 + 指标卡 | 时间轴 + 统计条 / 特性卡

另有两个排版引擎（写规格、自动排版、自动体检），在单独的模块里：
    arch_diagram.py   C1 分层架构图 v2：from arch_diagram import *
    process_flow.py   C29 工序流程图（人机分工）：from process_flow import *

坐标一律写画布像素（默认 1672x941，见 deck_kit.canvas）。几何参数全部显式传入，
组件只负责「画什么、按什么顺序画」，不替调用方猜位置——复刻时照源图量，新做时照 STYLE.md 的栅格算。

风格：默认是复刻风 REPLICA（圆角、粉色强调，按原图取色，保证已交付页面重建不变）。新做页面先切风格：
    use_theme(LIGHT)   浅色复刻风：圆角 + 浅红强调，文字 #333 / #595959，图形不用黑色和深灰（推荐）
    use_theme(STYLE)   ppt-deck 规范风：直角、#C7000A，同样是浅色系
组件里取默认色和圆角的地方都会跟着变；显式传入的颜色不受影响。
"""
import re
from icon_lib import *        # 先导入：icon_lib 带着 deck_kit 的中性配色
from draw_kit import *        # 后导入：复刻风配色（RED、INK…）覆盖中性配色
import draw_kit as _dk

L, C, R = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM


# ====================================================================== 风格
class Theme(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)

REPLICA = Theme(
    name="replica",
    red=_dk.RED, ink=_dk.INK, txt=_dk.TXT, numd=_dk.NUMD, icn=_dk.ICN, foot=_dk.FOOT,
    panel=_dk.PANEL, card_border=_dk.CARD_B, sep=_dk.SEPL, pink=_dk.PINK,
    soft_panel=RGBColor(0xF5, 0xF7, 0xF9), pink_bg=RGBColor(0xFD, 0xEF, 0xEF),
    pink_border=RGBColor(0xF3, 0xC6, 0xC6), lab=RGBColor(0xEC, 0xED, 0xEF),
    cell_border=RGBColor(0xDC, 0xDF, 0xE3), arrow=RGBColor(0x5B, 0x65, 0x73),
    gray_text=RGBColor(0x6B, 0x6B, 0x6B), head=RGBColor(0xDE, 0xE1, 0xE4),
    radius=1.0,                       # 圆角缩放：1 为原样，0 为直角
)

# ---------- 浅色系灰阶：图形不用黑色和深灰，焦点用红，其余用中浅灰 ----------
G_SOLID = RGBColor(0xBF, 0xBF, 0xBF)    # 已完成、起点等实心块（上面配深字，不配白字）
G_BAR = RGBColor(0x8C, 0x8C, 0x8C)      # 子弹图实际值等细条（最深的图形色，要和浅灰区间拉开）
G_MID = RGBColor(0xA6, 0xA6, 0xA6)      # 点、轴、骨架线、哈维球
G_LINE = RGBColor(0xD0, 0xD0, 0xD0)     # 连线、框线
G_TRACK = RGBColor(0xE6, 0xE6, 0xE6)    # 轨道、网格
G_HAIR = RGBColor(0xEE, 0xEE, 0xEE)     # 行分隔
G_TEXT = RGBColor(0x7F, 0x7F, 0x7F)     # 次要文字、刻度
RED_SOFT = RGBColor(0xE6, 0xA5, 0xA8)   # 图表第四色：分项柱

# ppt-deck STYLE.md 规范：直角、#C7000A；浅色系——文字 #333333 / #595959，图形只用中浅灰，表头浅灰底深字
STYLE = Theme(
    name="style",
    red=RGBColor(0xC7, 0x00, 0x0A), ink=RGBColor(0x33, 0x33, 0x33), txt=RGBColor(0x59, 0x59, 0x59),
    numd=RGBColor(0x8C, 0x8C, 0x8C), icn=RGBColor(0x80, 0x80, 0x80), foot=G_TEXT,
    panel=RGBColor(0xF2, 0xF2, 0xF2), card_border=RGBColor(0xBF, 0xBF, 0xBF), sep=RGBColor(0xBF, 0xBF, 0xBF),
    pink=RGBColor(0xF2, 0xCC, 0xCE), soft_panel=RGBColor(0xF2, 0xF2, 0xF2),
    pink_bg=RGBColor(0xFB, 0xEC, 0xED), pink_border=RGBColor(0xC7, 0x00, 0x0A),
    lab=RGBColor(0xD9, 0xD9, 0xD9), cell_border=RGBColor(0xBF, 0xBF, 0xBF), arrow=G_MID,
    gray_text=G_TEXT, head=RGBColor(0xE6, 0xE6, 0xE6),
    radius=0.0,
)

# 浅色复刻风：复刻风的圆角与浅红强调 + 浅色系文字和灰阶。新做页面的默认推荐
LIGHT = Theme(**dict(REPLICA.__dict__, name="light",
                     ink=RGBColor(0x33, 0x33, 0x33), txt=RGBColor(0x59, 0x59, 0x59),
                     numd=RGBColor(0x8C, 0x8C, 0x8C), icn=RGBColor(0x80, 0x80, 0x80),
                     arrow=G_MID, gray_text=G_TEXT, foot=RGBColor(0x8C, 0x8C, 0x8C),
                     head=RGBColor(0xE6, 0xE6, 0xE6)))

T = REPLICA

def use_theme(theme):
    """切换组件默认风格（REPLICA 复刻风 / LIGHT 浅色复刻风 / STYLE 规范风）。返回旧风格，便于临时切换后还原。

    页面脚本里 `from components import *` 拿到的 T 是导入那一刻的对象；切换后要在页面里用 T 的话，
    再 `from components import T` 一次。
    """
    global T
    old, T = T, theme
    return old

def _r(px):
    """按当前风格缩放圆角半径。"""
    return px * T.radius

def _c(color, default):
    return default if color is None else color


# ====================================================================== 文本小工具
def txt(text, size, bold=False, color=None):
    """一个 run：(text, size, bold, color)，color 缺省取正文色。"""
    return (text, size, bold, _c(color, T.txt))

def kw_line(keyword, text, size=11, kw_color=None, color=None):
    """「关键词：说明」一行：关键词加粗。"""
    return [(keyword, size, True, _c(kw_color, T.ink)), (text, size, False, _c(color, T.txt))]

def num_parts(template, size, num_size, bold=True, color=None, num_color=None):
    """把「约 {1200} 次」拆成 runs：花括号里的数字放大标红，其余按正文。"""
    out = []
    for i, piece in enumerate(re.split(r'\{([^}]*)\}', template)):
        if not piece:
            continue
        if i % 2:
            out.append((piece, num_size, True, _c(num_color, T.red)))
        else:
            out.append((piece, size, bold, _c(color, T.ink)))
    return out

def ba_parts(before, after, unit=None, before_size=21, after_size=25,
             arrow=" → ", arrow_size=None, unit_size=None, before_color=None):
    """前后对比数字：灰色旧值 → 红色新值（+ 单位）。arrow_size 缺省时箭头并进旧值同字号。"""
    bc = _c(before_color, T.numd)
    if arrow_size is None:
        parts = [(before + arrow, before_size, True, bc)]
    else:
        parts = [(before, before_size, True, bc), (arrow, arrow_size, True, bc)]
    parts.append((after, after_size, True, T.red))
    if unit:
        parts.append((unit, unit_size or round(after_size * 0.52, 1), True, T.red))
    return parts


# ====================================================================== 框架
def page_title(sh, text, size=20.5, box=(26, 8, 1640, 46), color=None):
    x, y, w, h = box
    return label(sh, x, y, w, h, text, size, True, _c(color, T.red), align=L)

def panel(sh, x, y, w, h, title=None, size=17, title_box=None, fill=None, radius=6,
          border=None, accent_bar=None):
    """灰底面板 + 左上标题。accent_bar=(x, y, w, h) 时在标题左侧加红色竖条，标明主栏。"""
    rrect(sh, x, y, w, h, _c(fill, T.panel), border, 0.75, radius=_r(radius))
    if accent_bar:
        rect(sh, *accent_bar, fill=T.red, line=None)
    if title:
        tx, ty, tw, th = title_box or (x + 16, y + 8, w - 32, 34)
        label(sh, tx, ty, tw, th, title, size, True, T.ink, align=L)

def section_title(sh, text, box, size=17):
    x, y, w, h = box
    return label(sh, x, y, w, h, text, size, True, T.ink, align=L)

def footer(sh, lines, size=8.6, box=(28, 888, 1560, 44), pitch=20, color=None,
           page=None, page_box=(1610, 902, 38, 26), page_size=12):
    """页脚：数据来源（多行）+ 右下页码。"""
    col = _c(color, T.foot)
    x, y, w, h = box
    lines_box(sh, x, y, w, h, [[(t, size, False, col)] for t in lines], L, TOP, pitch=pitch)
    if page is not None:
        px, py, pw, ph = page_box
        label(sh, px, py, pw, ph, str(page), page_size, False, col, align=R)


# ====================================================================== C5 折线图卡
def line_chart_card(sh, card, title, title_box, xs, values, y0, scale, *,
                    xlabels, yticks, axis_top, axis_left, axis_right,
                    title_size=13.5, axis_color=None, axis_lw=0.75, tick=5,
                    ylabel_box=(66, 48), xlabel_y=451, xlabel_w=60, axis_size=10,
                    grid=None, grid_right=None, grid_color=RGBColor(0xE6, 0xE6, 0xE6),
                    ytitle=None, ytitle_center=None, ytitle_w=200, ytitle_size=9.5,
                    smooth=False, line_w=2.25, dot_r=6, data_labels=(), label_size=10.5,
                    annotations=(), ann_color=None, ann_lw=1.0, ann_circle=False,
                    card_border=RGBColor(0xD0, 0xD3, 0xD6)):
    """折线图卡：白卡 + 结论标题 + 坐标轴 + 折线 + 数据点与标签 + 编号标注。

    y 映射：y0 - v * scale。yticks = [(v, 文本)]；data_labels = [(x, y, 文本)]（标签中心）。
    title 传字符串时单 run，传 parts 列表时混排。
    grid=[v, ...] 时画水平网格线，并在每个 x 位置画竖向网格线（到 grid 最大值为止）。
    annotations = [dict(at=(x, y), text=..., arrow=(x1, y1, x2, y2), n=1)]：
      ann_circle=False 时 at 是文字左端中心，文字自带①；True 时 at 是编号圆心，文字放在圆右侧。
    """
    ax = _c(axis_color, RGBColor(0x9A, 0x9A, 0x9A))
    YV = lambda v: y0 - v * scale
    cx, cy, cw, ch = card
    rect(sh, cx, cy, cw, ch, WHITE, card_border, 0.75)
    tx, ty, tw, th = title_box
    if isinstance(title, str):
        label(sh, tx, ty, tw, th, title, title_size, True, T.ink, align=L)
    else:
        rich(sh, tx, ty, tw, th, title)

    if grid:
        for v in grid:
            line(sh, axis_left, YV(v), _c(grid_right, axis_right), YV(v), grid_color, 0.75)
        for x in xs:
            line(sh, x, YV(max(grid)), x, y0, grid_color, 0.75)
    line(sh, axis_left, axis_top, axis_left, y0, ax, axis_lw)
    line(sh, axis_left, y0, axis_right, y0, ax, axis_lw)
    lx, lw_ = ylabel_box
    for v, t in yticks:
        line(sh, axis_left - tick, YV(v), axis_left, YV(v), ax, axis_lw)
        label(sh, lx, YV(v) - 10, lw_, 20, t, axis_size, False, T.txt, align=R)
    for x, d in zip(xs, xlabels):
        line(sh, x, y0, x, y0 + tick, ax, axis_lw)
        label(sh, x - xlabel_w / 2.0, xlabel_y, xlabel_w, 22, d, axis_size, False, T.txt)
    if ytitle:
        # 竖排轴名：文本框旋转 270°。PowerPoint / WPS 正常；QuickLook 不画旋转文字（见 PITFALLS）
        mx, my = ytitle_center
        yt = label(sh, mx - ytitle_w / 2.0, my - 11, ytitle_w, 22, ytitle, ytitle_size, False, T.txt)
        yt.rotation = 270

    pts = [(x, YV(v)) for x, v in zip(xs, values)]
    pl(sh, monotone(xs, [p[1] for p in pts]) if smooth else pts, T.red, line_w)
    for x, y in pts:
        oval(sh, x - dot_r, y - dot_r, 2 * dot_r, 2 * dot_r, T.red, None)
    for x, y, t in data_labels:
        label(sh, x - 25, y - 10, 50, 20, t, label_size, True, T.red)

    ac = _c(ann_color, RGBColor(0x70, 0x70, 0x70))
    for a in annotations:
        x, y = a['at']
        if ann_circle:
            oval(sh, x - 13.5, y - 13.5, 27, 27, WHITE, ac, 1.25)
            label(sh, x - 15, y - 15, 30, 30, str(a['n']), 11, False, T.ink)
            label(sh, x + 21.5, y - 11, 200, 22, a['text'], label_size, False, T.ink, align=L)
        else:
            label(sh, x, y - 11, 200, 22, a['text'], label_size, False, T.ink, align=L)
        x1, y1, x2, y2 = a['arrow']
        line(sh, x1, y1, x2, y2, ac, ann_lw, arrow=True)


# ====================================================================== C5 指标卡
def metric_card(sh, x, y, w, h, parts, caption, *, num_cy, cap_cy, pad=18, inner_w=None,
                num_h=52, cap_size=9.5, border=RGBColor(0xDC, 0xDD, 0xDE), radius=3):
    """白底指标卡：一行大数字（parts，常用 ba_parts 生成）+ 一行说明。"""
    iw = inner_w or (w - 2 * pad)
    rrect(sh, x, y, w, h, WHITE, border, 0.75, radius=_r(radius))
    rich(sh, x + pad, num_cy - num_h / 2.0, iw, num_h, parts)
    label(sh, x + pad, cap_cy - 12, iw, 24, caption, cap_size, False, T.txt, align=L)


# ====================================================================== C5 统计条 / C6 推导条、闭环条
def stat_line(sh, x, y, w, h, template, size, num_size, align=None):
    """一行统计：「线上：约 {120} 名用户 · {300} 个项目」，花括号内数字放大标红。"""
    return rich(sh, x, y, w, h, num_parts(template, size, num_size), _c(align, L))

def step_chain(sh, x0, y, steps, *, w=306, gap=31, h=210, title_size=13, num_r=14,
               body_pitch=22, border=RGBColor(0xE6, 0xE9, 0xEC), radius=8):
    """推导条：①→②→③ 白卡横排，卡间红色实心三角。

    steps = [(标题, 大数字 parts, 说明 lines)]；大数字常用 [("7", 30, True, red), (" 个问题", 14, True, red)]。
    """
    for i, (title, big, body) in enumerate(steps):
        x = x0 + i * (w + gap)
        rrect(sh, x, y, w, h, WHITE, border, 0.75, radius=_r(radius))
        numc(sh, x + 26, y + 28, num_r, i + 1, 12, fill=T.red)
        label(sh, x + 48, y + 14, w - 66, 28, title, title_size, True, T.ink, align=L)
        rich(sh, x + 18, y + 42, w - 26, 64, big)
        lines_box(sh, x + 18, y + 112, w - 26, h - 120, body, L, TOP, pitch=body_pitch)
        if i < len(steps) - 1:
            ax = x + w + gap / 2.0
            pl(sh, [(ax - 6, y + 93), (ax + 7, y + 105), (ax - 6, y + 117)], None, 0, True, T.red)

def flow_band(sh, x, y, w, h, lead, steps, size=11, fill=None, border=None, radius=8):
    """闭环条：粉底横条，「闭环：A → B → C」，首尾标红。"""
    rrect(sh, x, y, w, h, _c(fill, T.pink_bg), _c(border, T.pink_border), 0.75, radius=_r(radius))
    A = ("  →  ", size, True, T.red)
    parts = [(lead, size, True, T.red)]
    for i, s in enumerate(steps):
        if i:
            parts.append(A)
        parts.append((s, size, True, T.red if i == len(steps) - 1 else T.ink))
    rich(sh, x, y, w, h, parts, C)


# ====================================================================== C7 里程碑时间轴
def milestone_timeline(sh, nodes, *, cxs, boxes, axis_y, axis_color, axis_lw=1.5,
                       axis_from=None, axis_to=None,
                       date_y, date_size=11.5, dot_d=20, dot_color=RGBColor(0x45, 0x48, 0x4D),
                       stem_from=None, stem_color=RGBColor(0xBB, 0xBB, 0xBB),
                       box_y, box_h, box_border=RGBColor(0xE3, 0xE3, 0xE3),
                       band_y, band_h, band_fill=RGBColor(0xE8, 0xE8, 0xE8), current_fill=None,
                       title_y=None, title_size=11.5,
                       desc_y=None, desc_h=90, desc_size=10, desc_pitch=25, desc_color=None,
                       single_desc_y=None, single_desc_size=10,
                       status_size=11, current_status_size=12, status_pitch=24):
    """横向里程碑：日期 / 节点圆点 / 竖线 / 阶段卡（可选标题、说明、状态带），当前节点标红。

    nodes = [dict(date=, desc=[...], status=[...], title=None, current=False)]
    两种阶段卡：
      - 无 title：说明在卡上部，状态文字写进状态带形状（单行）。
      - 有 title：标题 + 说明（1 行用 single_desc_y）+ 状态（可两行），当前节点状态单独放大标红。
    """
    line(sh, _c(axis_from, cxs[0]), axis_y, _c(axis_to, cxs[-1]), axis_y, axis_color, axis_lw)
    stem_top = _c(stem_from, axis_y + dot_d / 2.0)
    for cx, (x, w), nd in zip(cxs, boxes, nodes):
        cur = nd.get('current', False)
        label(sh, cx - 40, date_y, 80, 24, nd['date'], date_size, False, T.ink)
        line(sh, cx, stem_top, cx, box_y, stem_color, 0.75)
        oval(sh, cx - dot_d / 2.0, axis_y - dot_d / 2.0, dot_d, dot_d, T.red if cur else dot_color, None)
        rect(sh, x, box_y, w, box_h, WHITE, box_border, 0.75)
        band = rect(sh, x, band_y, w, band_h, _c(current_fill, T.pink) if cur else band_fill, None)
        dc = _c(desc_color, T.ink)
        if nd.get('title') is None:
            st = nd['status'][0]
            shape_text(band, st, status_size, cur, T.red if cur else T.txt)
            lines_box(sh, x, desc_y, w, desc_h, [[(s, desc_size, False, dc)] for s in nd['desc']], C,
                      pitch=desc_pitch)
            continue
        label(sh, x, title_y, w, 26, nd['title'], title_size, True, T.ink)
        if len(nd['desc']) > 1:
            lines_box(sh, x, desc_y, w, desc_h, [[(s, desc_size, False, dc)] for s in nd['desc']], C, TOP,
                      pitch=desc_pitch)
        else:
            label(sh, x, single_desc_y, w, 24, nd['desc'][0], single_desc_size, False, dc)
        if cur:
            label(sh, x, band_y + 21, w, 28, nd['status'][0], current_status_size, True, T.red)
        else:
            lines_box(sh, x, band_y, w, band_h, [[(s, status_size, True, T.ink)] for s in nd['status']], C,
                      pitch=status_pitch)


# ====================================================================== C8 特性卡
def feature_row(sh, cards, *, y, h, title_y, title_size=13.5, body_dx=21, body_rpad=24,
                body2=(732, 56, 28), body3=(727.5, 75, 25), sep_y, sep_inset=(20, 20),
                res1=(827, 30), resn=(815, 56, 27), icons=(), fill=None, border=None):
    """一排特性卡：大图标 + 标题 + 「关键词：说明」+ 分隔线 + 结果行（数字标红）。

    cards = [(x, w, 标题, 说明 lines, 结果 lines)]；说明常用 kw_line，结果常用 num_parts。
    body2 / body3 = (顶, 高, 行距)：说明两行 / 三行时的文本框；res1 = (顶, 高) 单行结果，resn 多行结果。
    icons = [(图标函数, cx, cy, s, kwargs)]，卡片全部画完后再画图标。
    """
    for x, w, title, body, res in cards:
        rect(sh, x, y, w, h, _c(fill, T.panel), _c(border, T.card_border), 0.75)
        label(sh, x, title_y, w, 30, title, title_size, True, T.ink)
        by, bh, bp = body2 if len(body) <= 2 else body3
        lines_box(sh, x + body_dx, by, w - body_rpad, bh, body, L, TOP, pitch=bp)
        seg(sh, x + sep_inset[0], sep_y, x + w - sep_inset[1], sep_y, T.sep, 0.75)
        if len(res) == 1:
            lines_box(sh, x, res1[0], w, res1[1], res, C)
        else:
            lines_box(sh, x, resn[0], w, resn[1], res, C, TOP, pitch=resn[2])
    for fn, cx, cy, s, kw in icons:
        fn(sh, cx, cy, s, kw.pop('c', T.icn), **kw)


# ====================================================================== C1 分层架构图
def arch_layer(sh, x, y, w, h, name, *, lab_w=88, name_size=12, pitch=25,
               fill=RGBColor(0xFC, 0xFC, 0xFD), border=RGBColor(0xE2, 0xE5, 0xE9), lab=None, radius=6):
    """一层：整行圆角底 + 左侧层名列（只圆左两角，用单个自由形状，避免 QuickLook 拼接色差）。"""
    rrect(sh, x, y, w, h, fill, border, 0.75, radius=_r(radius))
    rr = max(_r(radius) - 0.5, 0)
    rshape(sh, x + 0.5, y + 0.5, lab_w, h - 1, (rr, 0, 0, rr), _c(lab, T.lab))
    lines_box(sh, x, y, lab_w, h, [[(t, name_size, True, T.ink)] for t in name.split("\n")], C, pitch=pitch)

def module_cell(sh, x, y, w, h, text, *, size=9.5, icon=None, text_cx=None, text_w=90,
                fill=WHITE, border=None, radius=4):
    """模块格：图标在左、文字在右。icon = (图标函数, cx, s, 颜色)。"""
    rrect(sh, x, y, w, h, fill, _c(border, T.cell_border), 0.75, radius=_r(radius))
    cy = y + h / 2.0
    if icon:
        fn, icx, s, col = icon
        fn(sh, icx, cy, s, col)
    tcx = _c(text_cx, x + w / 2.0)
    label(sh, tcx - text_w / 2.0, cy - 11.5, text_w, 22, text, size, False, T.txt)

def bi_arrow(sh, x, y1, y2, color=None, lw=1.25):
    """层间双向箭头。"""
    return line(sh, x, y1, x, y2, _c(color, T.arrow), lw, arrow=True, back=True)

def fanout(sh, y, downs, *, ups=(), hline=None, label_text=None, label_box=None, label_size=9,
           label_bg=WHITE, color=None, lw=1.0):
    """分发连线：一条横线（可选）+ 向下箭头 + 向上箭头 + 横线上的说明（如「按项目切换」）。

    downs / ups = [(x, 终点 y)]。label_bg=None 时说明是普通文字，否则带底色挡住横线。
    """
    col = _c(color, T.arrow)
    if hline:
        line(sh, hline[0], y, hline[1], y, col, lw)
    for x, ye in downs:
        line(sh, x, y, x, ye, col, lw, arrow=True)
    for x, ye in ups:
        line(sh, x, y, x, ye, col, lw, arrow=True)
    if label_text:
        bx, by, bw, bh = label_box
        if label_bg is None:
            label(sh, bx, by, bw, bh, label_text, label_size, False, T.gray_text)
        else:
            shape_text(rect(sh, bx, by, bw, bh, label_bg, None), label_text, label_size, False, T.txt)


# ====================================================================== C9 编号要点
def numbered_item(sh, n, num_at, title, title_box, body, body_box, *, r=13, num_size=11.5,
                  title_size=11.5, pitch=22, sep=None, sep_color=RGBColor(0xE6, 0xE6, 0xE6)):
    """红圆编号 + 标题 + 说明（可选底部分隔线 sep=(x1, x2, y)）。"""
    numc(sh, num_at[0], num_at[1], r, n, num_size, fill=T.red)
    label(sh, *title_box, title, title_size, True, T.ink, align=L)
    lines_box(sh, *body_box, body, L, TOP, pitch=pitch)
    if sep:
        seg(sh, sep[0], sep[2], sep[1], sep[2], sep_color, 0.75)


# ====================================================================== C10 回路图
def cycle_diagram(sh, nodes, center=None):
    """回路节点：圆角盒 + 图标 + 文字；center = (文字, (x, y, w, h), 字号)。箭头用 cycle_arrows 最后画。

    nodes = [dict(box=(x, y, w, h), fill=, border=, icon=(fn, cx, cy, s, color),
                  texts=[(x, y, w, h, text, size, bold, color, align)],
                  lines=(x, y, w, h, lines, pitch))]
    """
    for nd in nodes:
        rrect(sh, *nd['box'], nd.get('fill', WHITE), nd.get('border'), nd.get('lw', 1.0), radius=_r(8))
        if nd.get('icon'):
            fn, icx, icy, s, col = nd['icon'][:5]
            fn(sh, icx, icy, s, col, *nd['icon'][5:])
        for x, y, w, h, t, size, bold, col, al in nd.get('texts', ()):
            label(sh, x, y, w, h, t, size, bold, col, align=al)
        if nd.get('lines'):
            x, y, w, h, lines, pitch = nd['lines']
            lines_box(sh, x, y, w, h, lines, L, TOP, pitch=pitch)
    if center:
        t, (x, y, w, h), size = center
        label(sh, x, y, w, h, t, size, True, T.red)

def cycle_arrows(sh, arrows, color=None, lw=3.0, L=17, Wd=18):
    """回路弯箭头：arrows = [(起点, 控制点1, 控制点2, 终点)]。跨面板时放在所有面板之后调用。"""
    for p0, c1, c2, p3 in arrows:
        curve_arrow(sh, p0, c1, c2, p3, _c(color, T.red), lw, L, Wd)


# ====================================================================== C11 标签标题 / 图标圆底
def tag_title(sh, x, y, tag, title, *, tag_w=58, size=13, tag_size=9.5, title_w=480):
    """红色胶囊标签 + 标题，如「下一步｜……」。"""
    pill(sh, x, y + 2, tag_w, 24, tag, tag_size, T.red, WHITE, bold=True, radius=_r(12))
    label(sh, x + tag_w + 10, y, title_w, 28, title, size, True, T.ink, align=L)

def icon_disc(sh, cx, cy, r, fill=WHITE):
    """图标的圆形底托。"""
    return oval(sh, cx - r, cy - r, 2 * r, 2 * r, fill, None)


# ====================================================================== C2 分组表格
def grouped_table(sh, x, y, col_w, row_h, header, rows, groups, *,
                  header_size=9, header_spacing=None, header_border=None,
                  col_align=None, col_margin=None, spacing=None,
                  highlight=None, endpara=8,
                  outer=RGBColor(0xD9, 0xDD, 0xE1), inner_h=RGBColor(0xE3, 0xE6, 0xEA),
                  inner_v=RGBColor(0xD5, 0xD9, 0xDE)):
    """原生表格：首列按组合并（组底色、组名可标红），其余列逐行填写，逐格写框线。

    header   = ["类别", "现象", ...]，第 0 列是分组列
    rows     = 每个数据行除分组列外的单元格；单元格是 parts（一段）或 lines（多段）
    groups   = [(首行, 末行, 组名 lines, 底色, 行距)]，行号从 1 起（0 是表头）
    highlight= {行号: 底色}，整行（分组列除外）铺底色
    col_align / col_margin 从第 1 列起：对齐、(左边距, 右边距)
    spacing  = 固定行距 pt；None 时每段取「最大字号 + 2」
    header_border = 表头上下框线颜色，None 不画
    """
    _, tbl = native_table(sh, x, y, col_w, row_h)
    n_r, n_c = len(row_h), len(col_w)
    hs = header_spacing or (header_size + 2)
    for j, t in enumerate(header):
        cell_lines(tbl.cell(0, j), [[(t, header_size, True, T.ink)]], C, T.head, spacing=hs)

    col_align = col_align or [L] * (n_c - 1)
    col_margin = col_margin or [(0, 0)] * (n_c - 1)
    highlight = highlight or {}
    for i, cells in enumerate(rows, 1):
        bg = highlight.get(i, WHITE)
        for j, cell in enumerate(cells, 1):
            lines = cell if cell and isinstance(cell[0], list) else [cell]
            sp = spacing or (max(sz for ln in lines for _, sz, _, _ in ln) + 2)
            ml, mr = col_margin[j - 1]
            cell_lines(tbl.cell(i, j), lines, col_align[j - 1], bg, ml=ml, mr=mr, spacing=sp)

    starts = set()
    for r0, r1, glines, fill, gsp in groups:
        starts.add(r0)
        for r in range(r0, r1 + 1):
            c = tbl.cell(r, 0); c.fill.solid(); c.fill.fore_color.rgb = fill
        tbl.cell(r0, 0).merge(tbl.cell(r1, 0))
        cell_lines(tbl.cell(r0, 0), glines, C, fill, spacing=gsp)
    table_endpara(tbl, endpara)

    first = min(starts) if starts else 1
    for r in range(n_r):
        for c in range(n_c):
            def hline(er):
                if er in (0, 1):
                    return header_border
                if er == n_r:
                    return outer
                if c == 0:
                    return inner_h if (er in starts and er != first) else None
                return inner_h
            def vline(ec):
                return outer if ec in (0, n_c) else inner_v
            cell = tbl.cell(r, c)
            cell_border(cell, 'L', vline(c)); cell_border(cell, 'R', vline(c + 1))
            cell_border(cell, 'T', hline(r)); cell_border(cell, 'B', hline(r + 1))
    return tbl


# ====================================================================== 页型 A：总览页
def overview_page(sh, *, title, left, chart, metrics, right, timeline, stat, section, features, footer_spec):
    """页型 A：左上图表 + 指标卡，右上里程碑 + 统计条，下方一排特性卡，页脚。

    每个参数都是对应组件的关键字参数字典：
      title       -> page_title         left / right -> panel（right 另含 inner=(x,y,w,h,边框色)）
      chart       -> line_chart_card    metrics      -> [metric_card 参数]
      timeline    -> milestone_timeline stat         -> stat_line
      section     -> section_title      features     -> feature_row
      footer_spec -> footer
    """
    page_title(sh, **title)
    panel(sh, **left)
    line_chart_card(sh, **chart)
    for m in metrics:
        metric_card(sh, **m)
    rp = dict(right)
    inner = rp.pop('inner', None)
    panel(sh, **rp)
    if inner:
        rect(sh, *inner[:4], WHITE, inner[4], 0.75)
    milestone_timeline(sh, **timeline)
    stat_line(sh, **stat)
    section_title(sh, **section)
    feature_row(sh, **features)
    footer(sh, **footer_spec)

# ######################################################################
# 第二批（2026-10）：控件 + 数据 / 结构组件。默认按浅色系取灰阶（G_*），焦点用 T.red
#   控件：badge_width / delta_badge 涨跌徽标、status_dot 状态点、progress_bar 细进度条、harvey_ball 哈维球、
#         callout 引线标注、sample_tag 示意数据角标、sparkline 迷你趋势线、chip 全圆角胶囊、tag_pill 红色小标签
#   组件：C12 hero_card 英雄数字卡、C13 dumbbell 哑铃图、C14 waterfall 瀑布图、C15 harvey_matrix 哈维球矩阵、
#         C16 quadrant 四象限、C18 swimlane 泳道路标图、C20 chevron_flow 箭头流程
# ######################################################################
import math

# ============================================================ 控件
def badge_width(value, size=9):
    """涨跌徽标宽度。▲▼ 实际渲染接近一个字宽，wpx 按半宽算会偏窄导致折行。"""
    return wpx("中 " + value, size) * 1.15 + 16

def delta_badge(sh, x, cy, value, direction="down", emphasis=True, size=9):
    """涨跌徽标：▼ 96% / ▲ 1.7×。emphasis=True 红字浅红底，否则灰字灰底。返回宽度。"""
    t = ("▼ " if direction == "down" else "▲ ") + value
    w = badge_width(value, size)
    h = size * 2.2
    pill(sh, x, cy - h / 2.0, w, h, t, size,
         T.pink_bg if emphasis else T.lab, T.red if emphasis else T.gray_text, bold=True, radius=h / 2.0)
    return w

def status_dot(sh, x, cy, state, text=None, size=10, r=5.5):
    """状态点：done 已完成（中灰实心）/ doing 进行中（红色半实心）/ now 当前（红色实心）/ plan 规划中（空心）。"""
    if state == "done":
        oval(sh, x, cy - r, 2 * r, 2 * r, G_MID, None)
    elif state == "now":
        oval(sh, x, cy - r, 2 * r, 2 * r, T.red, None)
    elif state == "doing":
        oval(sh, x, cy - r, 2 * r, 2 * r, WHITE, T.red, 1.25)
        pl(sh, [(x + r, cy)] + arc_pts(x + r, cy, r, 90, 270, 16), None, 0, True, T.red)
    else:
        oval(sh, x, cy - r, 2 * r, 2 * r, WHITE, G_MID, 1.25)
    if text:
        hot = state in ("now", "doing")
        label(sh, x + 2 * r + 7, cy - 11, 160, 22, text, size, hot, T.red if hot else T.txt, align=L)

def progress_bar(sh, x, cy, w, pct, text=None, h=7, size=9.5):
    """细进度条：灰轨道 + 红填充 + 右侧百分比（或自定义文字）。"""
    rrect(sh, x, cy - h / 2.0, w, h, G_TRACK, None, radius=h / 2.0)
    if pct > 0:
        rrect(sh, x, cy - h / 2.0, max(w * min(pct, 1.0), h), h, T.red, None, radius=h / 2.0)
    label(sh, x + w + 8, cy - 11, 70, 22, text or "%d%%" % round(pct * 100), size, True, T.ink, align=L)

def harvey_ball(sh, cx, cy, r, level, color=None, outline=None):
    """哈维球：level 0–4 对应 ○ ◔ ◑ ◕ ●。"""
    col = _c(color, G_MID)
    oval(sh, cx - r, cy - r, 2 * r, 2 * r, WHITE, _c(outline, G_MID), 1.0)
    if level >= 4:
        oval(sh, cx - r, cy - r, 2 * r, 2 * r, col, None)
    elif level > 0:
        pl(sh, [(cx, cy)] + arc_pts(cx, cy, r, -90, -90 + 90 * level, 8 * level), None, 0, True, col)

def callout(sh, anchor, elbow, end_x, text, size=9.5, color=None, dot=None, lw=0.75):
    """引线标注：锚点小圆 → 折线 → 文字。end_x 在折点右侧时文字左对齐，否则右对齐。"""
    ax, ay = anchor
    ex, ey = elbow
    pl(sh, [anchor, elbow, (end_x, ey)], G_MID, lw)
    oval(sh, ax - 3.5, ay - 3.5, 7, 7, _c(dot, T.red), None)
    if end_x >= ex:
        label(sh, end_x + 5, ey - 11, 260, 22, text, size, False, _c(color, T.ink), align=L)
    else:
        label(sh, end_x - 265, ey - 11, 260, 22, text, size, False, _c(color, T.ink), align=R)

def sample_tag(sh, x, y, text="示意数据", size=8, right=None):
    """示意数据角标：灰框小字，放在图表右上角。给 right 时按右边缘对齐（x 忽略）。返回宽度。"""
    w = wpx(text, size) * 1.15 + 12
    if right is not None:
        x = right - w
    shape_text(rect(sh, x, y, w, 18, WHITE, G_LINE, 0.75), text, size, False, T.gray_text)
    return w

def sparkline(sh, x, y, w, h, values, color=None, lw=2.0, dot_r=3.5, end_labels=None, size=9):
    """迷你趋势线：无坐标轴，首尾标值。返回各点坐标，便于再挂引线标注。"""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = len(values)
    pts = [(x + w * i / float(n - 1), y + h - (v - lo) / span * h) for i, v in enumerate(values)]
    line(sh, x, y + h, x + w, y + h, G_TRACK, 0.75)
    pl(sh, pts, _c(color, T.red), lw)
    for i, (px, py) in enumerate(pts):
        last = i == n - 1
        oval(sh, px - dot_r, py - dot_r, 2 * dot_r, 2 * dot_r, _c(color, T.red) if (i == 0 or last) else WHITE,
             None if (i == 0 or last) else _c(color, T.red), 1.25)
    if end_labels:
        a, b = end_labels
        label(sh, pts[0][0] - 4, pts[0][1] - 26, 80, 20, a, size, True, G_TEXT, align=L)
        label(sh, pts[-1][0] - 76, pts[-1][1] - 26, 80, 20, b, size, True, _c(color, T.red), align=R)
    return pts


# ============================================================ C12 英雄数字卡
def hero_card(sh, x, y, w, h, metric, big, sub, *, badge=None, series=None, series_labels=None,
              xlabels=None, callouts=(), big_h=150, big_y=28, sub_gap=-8):
    """一个大数字讲一个结论：指标名 + 大数字（parts）+ 一两行解释 + 迷你趋势线。

    badge = (值, 方向, 是否强调)；series 给出时在底部画 sparkline，callouts = [(点序号, 文字, dx, dy)]。
    """
    rrect(sh, x, y, w, h, WHITE, T.card_border, 0.75, radius=_r(4))
    label(sh, x + 20, y + 14, w - 140, 26, metric, 12, True, T.ink, align=L)
    if badge:
        v, d, e = badge
        delta_badge(sh, x + w - 20 - badge_width(v), y + 27, v, d, e)
    # 大数字框高要盖住整行行高（72pt 约 150px），否则 QuickLook 会把字挤到下面的说明上
    rich(sh, x + 20, y + big_y, w - 40, big_h, big)
    lines_box(sh, x + 20, y + big_y + big_h + sub_gap, w - 40, 50, sub, L, TOP, pitch=22)
    if series:
        sx, sy, sw, shh = x + 28, y + h - 104, w - 56, 62
        pts = sparkline(sh, sx, sy, sw, shh, series, end_labels=series_labels)
        if xlabels:
            label(sh, sx - 20, sy + shh + 6, 60, 18, xlabels[0], 8.5, False, T.gray_text, align=L)
            label(sh, sx + sw - 40, sy + shh + 6, 60, 18, xlabels[1], 8.5, False, T.gray_text, align=R)
        for i, t, dx, dy in callouts:
            px, py = pts[i]
            callout(sh, (px, py), (px + dx, py + dy), px + dx + 14, t, 9)


# ============================================================ C13 哑铃图
def dumbbell(sh, x, y, w, rows, *, vmin, vmax, ticks, label_w=140, delta_w=78, row_h=50,
             legend=("改进前", "改进后"), delta_head="变化", fmt="{:g}", delta_fmt="{:+g}", highlight=None):
    """多项前后对比：每行灰点（前）→ 红点（后），右列涨跌徽标。共用一根刻度轴。

    rows = [(名称, 前值, 后值)]；highlight = 行号集合，名称加粗标红。
    """
    px0, px1 = x + label_w, x + w - delta_w - 10
    X = lambda v: px0 + (v - vmin) / float(vmax - vmin) * (px1 - px0)
    # 图例
    oval(sh, x, y + 6, 10, 10, G_MID, None)
    label(sh, x + 16, y, 80, 22, legend[0], 9.5, False, T.txt, align=L)
    oval(sh, x + 90, y + 6, 10, 10, T.red, None)
    label(sh, x + 106, y, 80, 22, legend[1], 9.5, False, T.txt, align=L)
    label(sh, x + w - delta_w, y + 28, delta_w, 20, delta_head, 9, True, T.gray_text)
    # 刻度
    ty = y + 38
    for t in ticks:
        label(sh, X(t) - 25, ty - 10, 50, 20, fmt.format(t), 8.5, False, T.gray_text)
    top = ty + 14
    bottom = top + row_h * len(rows)
    for t in ticks:
        line(sh, X(t), top, X(t), bottom, G_HAIR, 0.75)
    for i, (name, a, b) in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        hot = highlight and i in highlight
        label(sh, x, cy - 11, label_w - 12, 22, name, 10.5, hot, T.red if hot else T.ink, align=L)
        line(sh, X(a), cy, X(b), cy, G_LINE, 3.0)
        oval(sh, X(a) - 6, cy - 6, 12, 12, G_MID, None)
        oval(sh, X(b) - 7, cy - 7, 14, 14, T.red, None)
        left, right = (a, b) if a <= b else (b, a)
        label(sh, X(left) - 58, cy - 10, 48, 20, fmt.format(left), 9, left == b, T.red if left == b else G_TEXT, align=R)
        label(sh, X(right) + 10, cy - 10, 48, 20, fmt.format(right), 9, right == b, T.red if right == b else G_TEXT,
              align=L)
        d = b - a
        dv = delta_fmt.format(abs(d)).lstrip("+")
        delta_badge(sh, x + w - delta_w + (delta_w - badge_width(dv)) / 2.0, cy, dv,
                    "up" if d >= 0 else "down", emphasis=bool(hot))
        if i < len(rows) - 1:
            line(sh, x, top + row_h * (i + 1), x + w, top + row_h * (i + 1), G_HAIR, 0.75)


# ============================================================ C14 瀑布图
def waterfall(sh, x, y, w, h, start, steps, end, *, vmax, fmt="{:g}", delta_fmt="{:+g}", label_h=40):
    """瀑布图：起点柱（深灰）→ 各分项浮动柱（浅红，下降）/（浅灰，上升）→ 终点柱（红）。

    start / end = (标签, 值)；steps = [(标签, 增量)]。分项标签可用 "\\n" 换两行。
    """
    n = len(steps) + 2
    slot = w / float(n)
    bw = slot * 0.56
    base = y + h - label_h
    k = (h - label_h - 30) / float(vmax)
    Y = lambda v: base - v * k
    bars = [(start[0], 0, start[1], G_SOLID, fmt.format(start[1]), T.ink)]
    cum = start[1]
    for lab, d in steps:
        lo, hi = sorted((cum, cum + d))
        bars.append((lab, lo, hi, RED_SOFT if d < 0 else G_LINE, delta_fmt.format(d).replace("-", "−"),
                     T.red if d < 0 else G_TEXT))
        cum += d
    bars.append((end[0], 0, end[1], T.red, fmt.format(end[1]), T.red))
    line(sh, x, base, x + w, base, G_MID, 1.0)
    for i, (lab, lo, hi, col, vt, vc) in enumerate(bars):
        bx = x + slot * i + (slot - bw) / 2.0
        top, bot = Y(hi), Y(lo)
        rect(sh, bx, top, bw, max(bot - top, 1.5), col, None)
        label(sh, bx - 20, top - 22, bw + 40, 20, vt, 10, True, vc)
        label(sh, x + slot * i, base + 4, slot, label_h - 4, lab, 9, i in (0, n - 1), T.ink if i in (0, n - 1) else T.txt)
        if i < n - 1:
            lvl = hi if i == 0 else (lo if steps[i - 1][1] < 0 else hi)
            nx = x + slot * (i + 1) + (slot - bw) / 2.0
            c = line(sh, bx + bw, Y(lvl), nx, Y(lvl), G_MID, 0.75)
            d_ = etree.SubElement(c.line._get_or_add_ln(), qn('a:prstDash')); d_.set('val', 'sysDash')


# ============================================================ C15 哈维球矩阵
def harvey_matrix(sh, x, y, w, header, rows, *, label_w=200, row_h=38, head_h=34, r=9,
                  highlight_col=None, legend=True):
    """能力对比矩阵：行是能力，列是方案，单元格是哈维球。highlight_col 的整列铺浅红底、表头标红。"""
    n = len(header)
    cw = (w - label_w) / float(n)
    total_h = head_h + row_h * len(rows)
    if highlight_col is not None:
        rect(sh, x + label_w + cw * highlight_col + 4, y, cw - 8, total_h, T.pink_bg, None)
    for j, hd in enumerate(header):
        hot = j == highlight_col
        label(sh, x + label_w + cw * j, y, cw, head_h, hd, 10.5, True, T.red if hot else T.ink)
    line(sh, x, y + head_h, x + w, y + head_h, G_MID, 1.0)
    for i, (name, levels) in enumerate(rows):
        cy = y + head_h + row_h * (i + 0.5)
        label(sh, x + 4, cy - 11, label_w - 8, 22, name, 10, False, T.ink, align=L)
        for j, lv in enumerate(levels):
            harvey_ball(sh, x + label_w + cw * (j + 0.5), cy, r, lv,
                        color=T.red if j == highlight_col else None)
        line(sh, x, y + head_h + row_h * (i + 1), x + w, y + head_h + row_h * (i + 1),
             G_MID if i == len(rows) - 1 else G_HAIR, 1.0 if i == len(rows) - 1 else 0.75)
    if legend:
        ly = y + total_h + 22
        lx = x + 4
        for lv, t in enumerate(["不支持", "少量", "一半", "大部分", "完整"]):
            harvey_ball(sh, lx + 7, ly, 7, lv)
            label(sh, lx + 18, ly - 10, 60, 20, t, 8.5, False, T.gray_text, align=L)
            lx += 78


# ============================================================ C16 四象限
def quadrant(sh, x, y, w, h, *, xlabel, ylabel, names, points, hot_quad=1):
    """四象限：两轴 + 中线 + 象限名，hot_quad（1 右上 2 左上 3 左下 4 右下）铺浅红底。

    points = [(名称, x 值 0–1, y 值 0–1, 是否重点)]。
    """
    mx, my = x + w / 2.0, y + h / 2.0
    quads = {1: (mx, y), 2: (x, y), 3: (x, my), 4: (mx, my)}
    qx, qy = quads[hot_quad]
    rect(sh, qx, qy, w / 2.0, h / 2.0, T.pink_bg, None)
    rect(sh, x, y, w, h, None, G_LINE, 0.75)
    for (x1, y1, x2, y2) in ((mx, y, mx, y + h), (x, my, x + w, my)):
        c = line(sh, x1, y1, x2, y2, G_LINE, 0.75)
        d_ = etree.SubElement(c.line._get_or_add_ln(), qn('a:prstDash')); d_.set('val', 'dash')
    pos = {1: (mx + 10, y + 8, R), 2: (x + 10, y + 8, L), 3: (x + 10, y + h - 30, L), 4: (mx + 10, y + h - 30, R)}
    for q, nm in zip((1, 2, 3, 4), names):
        px, py, al = pos[q]
        bx = px if al == L else px - 20
        label(sh, bx, py, w / 2.0 - 20, 22, nm, 10, True, T.red if q == hot_quad else T.gray_text, align=al)
    line(sh, x, y + h + 14, x + w, y + h + 14, G_MID, 1.0, arrow=True)
    label(sh, x + w - 200, y + h + 18, 200, 20, xlabel, 9.5, False, T.gray_text, align=R)
    line(sh, x - 14, y + h, x - 14, y, G_MID, 1.0, arrow=True)
    label(sh, x - 8, y - 22, 200, 20, ylabel, 9.5, False, T.gray_text, align=L)
    for nm, vx, vy, hot in points:
        cx, cy = x + vx * w, y + (1 - vy) * h
        r = 8 if hot else 6.5
        oval(sh, cx - r, cy - r, 2 * r, 2 * r, T.red if hot else G_MID, None)
        label(sh, cx + r + 5, cy - 10, 150, 20, nm, 9.5, hot, T.red if hot else T.ink, align=L)


# ============================================================ C18 泳道路标图
def swimlane(sh, x, y, w, periods, lanes, *, lane_w=130, head_h=26, lane_h=56, today=None, today_text="今天"):
    """泳道路标图：横轴是时间段，每条泳道一个工作流。

    lanes = [(泳道名, [(起, 止, 文字, 状态)])]，起止以时间段为单位（可带小数），起 == 止 画里程碑菱形；
    状态 done / doing / plan；today = 时间段坐标（小数），画红色竖线。
    """
    gx0 = x + lane_w
    pw = (w - lane_w) / float(len(periods))
    X = lambda t: gx0 + t * pw
    for i, p in enumerate(periods):
        label(sh, X(i), y, pw, head_h, p, 10, True, T.ink)
    total = head_h + lane_h * len(lanes)
    for i in range(len(periods) + 1):
        line(sh, X(i), y + head_h, X(i), y + total, G_HAIR, 0.75)
    for li, (name, items) in enumerate(lanes):
        ly = y + head_h + lane_h * li
        if li % 2 == 0:
            rect(sh, gx0, ly, w - lane_w, lane_h, RGBColor(0xFA, 0xFA, 0xFA), None)
        shape_text(rect(sh, x, ly + 3, lane_w - 8, lane_h - 6, T.lab, None), name, 10, True, T.ink)
        for s, e, t, st in items:
            cy = ly + lane_h / 2.0
            if s == e:
                cx = X(s)
                pl(sh, [(cx, cy - 9), (cx + 9, cy), (cx, cy + 9), (cx - 9, cy)], None, 0, True, T.red)
                label(sh, cx + 12, cy - 11, 160, 22, t, 9, True, T.red, align=L)
                continue
            fill, col, bd = {"done": (G_SOLID, T.ink, None), "doing": (T.red, WHITE, None),
                             "plan": (WHITE, T.gray_text, G_MID)}[st]
            b = rrect(sh, X(s) + 2, cy - 13, X(e) - X(s) - 4, 26, fill, bd, 0.75, radius=_r(4))
            if st == "plan":
                d_ = etree.SubElement(b.line._get_or_add_ln(), qn('a:prstDash')); d_.set('val', 'dash')
            shape_text(b, t, 9, st != "plan", col)
        line(sh, x, ly + lane_h, x + w, ly + lane_h, G_HAIR, 0.75)
    if today is not None:
        # 「今天」标签放在泳道底部，避免压住表头的时间段名
        tx = X(today)
        line(sh, tx, y + head_h - 2, tx, y + total + 2, T.red, 1.5)
        tw = wpx(today_text, 8.5) * 1.15 + 14
        pill(sh, tx - tw / 2.0, y + total + 2, tw, 20, today_text, 8.5, T.red, WHITE, bold=True, radius=_r(10))


# ============================================================ C20 箭头流程
def chevron_flow(sh, x, y, w, h, steps, *, current=None, notch=18, gap=6, desc_h=60, desc_pitch=21, size=11.5):
    """箭头流程：首尾相扣的箭头块，当前步骤红底白字，已完成深灰，未开始浅灰；下方各步说明。

    steps = [(标题, 说明 lines)]。
    """
    n = len(steps)
    sw = (w + (n - 1) * (notch - gap)) / float(n)      # 末块右尖正好落在 x + w
    for i, (title, desc) in enumerate(steps):
        x0 = x + i * (sw + gap - notch)
        x1 = x0 + sw
        ym = y + h / 2.0
        pts = [(x0, y), (x1 - notch, y), (x1, ym), (x1 - notch, y + h), (x0, y + h)]
        if i > 0:
            pts.append((x0 + notch, ym))
        if current is None or i < current:
            fill, col = G_SOLID, T.ink
        elif i == current:
            fill, col = T.red, WHITE
        else:
            fill, col = T.lab, G_TEXT
        if current is None:
            fill, col = T.lab, T.ink
        pl(sh, pts, None, 0, True, fill)
        tx = x0 + (notch if i > 0 else 0)
        label(sh, tx, y, x1 - notch - tx + notch * 0.4, h, title, size, True, col)
        if desc:
            lines_box(sh, tx + 2, y + h + 10, sw - notch - 4, desc_h, desc, C, TOP, pitch=desc_pitch)

# ######################################################################
# 新范式组件（2026-10）：范式八–十三
#   C22 fishbone 鱼骨图（归因）、C17 driver_tree 指标拆解树（拆解）、C23 funnel 漏斗图（转化）、
#   C24 bullet_list 子弹图 / C25 risk_matrix 风险矩阵（评估）、C26 strategy_house 战略屋 /
#   C27 maturity_steps 成熟度阶梯（蓝图）、C28 hub_spoke 中心辐射图（生态）
# ######################################################################

def _dash(s, val="dash"):
    d = etree.SubElement(s.line._get_or_add_ln(), qn('a:prstDash')); d.set('val', val)
    return s

def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def pill_w(text, size):
    """胶囊标签宽度：中文按回落字体再放宽，避免 QuickLook 里截字。"""
    return wpx(text, size) * 1.25 + 24

def chip(sh, x, y, w, h, text, size, fill, color, bold=True, border=None):
    """全圆角胶囊：形状和文字分开画。roundRect 半径到半高时内置文字区被压扁，QuickLook 会把字挤到下沿。"""
    rrect(sh, x, y, w, h, fill, border, 0.75, radius=h / 2.0)
    label(sh, x - 4, y - 4, w + 8, h + 8, text, size, bold, color)
    return w

def tag_pill(sh, x, y, text, size=9.5):
    """红色胶囊小标签，宽度按字数算。返回宽度。"""
    return chip(sh, x, y, pill_w(text, size), 24, text, size, T.red, WHITE)

# ============================================================ C22 鱼骨图
def fishbone(sh, x, y, w, h, head, bones, *, head_w=130, label_h=30, cat_size=10, sub_size=9):
    """鱼骨图：右侧问题（红底），脊骨向右，类别骨上下交替斜出，子因横线挂在骨上。

    bones = [(类别, [(子因, 是否重点)], 是否重点类别)]。重点类别红底标签、红骨；重点子因红字红线。
    子因横线长度 = 列距 − 24，同一高度上左邻骨正好在一个列距之外，不会压线。
    """
    my = y + h / 2.0
    hx = x + w - head_w
    cols = (len(bones) + 1) // 2
    step = (hx - x) / (cols + 0.35)
    dy = h / 2.0 - label_h
    dx = dy * 0.45
    sub_len = step - 24
    rect(sh, hx, my - 36, head_w, 72, T.red, None)
    lines_box(sh, hx, my - 36, head_w, 72, [[(t, 11, True, WHITE)] for t in head.split("\n")], C, pitch=22)
    line(sh, x, my, hx, my, G_MID, 2.5, arrow=True)
    for i, (cat, subs, hot) in enumerate(bones):
        col, top = i // 2, i % 2 == 0
        ax = x + step * (col + 1.15)
        ey = y + label_h if top else y + h - label_h
        ex = ax - dx
        line(sh, ax, my, ex, ey, T.red if hot else G_MID, 1.75)
        bw = wpx(cat, cat_size) * 1.15 + 24
        by = y if top else y + h - label_h + 2
        shape_text(rect(sh, ex - bw / 2.0, by, bw, label_h - 2, T.red if hot else T.lab, None),
                   cat, cat_size, True, WHITE if hot else T.ink)
        for k, (t, shot) in enumerate(subs):
            f = (k + 1) / (len(subs) + 1.0)
            px, py = ex + (ax - ex) * f, ey + (my - ey) * f
            line(sh, px - sub_len, py, px, py, T.red if shot else G_LINE, 1.0 if shot else 0.75)
            label(sh, px - sub_len, py - 19, sub_len - 6, 18, t, sub_size, shot, T.red if shot else T.txt, align=R)
            if shot:
                oval(sh, px - 3.5, py - 3.5, 7, 7, T.red, None)


# ============================================================ C17 指标拆解树
def _tree_node(sh, nx, ny, nw, nh, nd):
    hot = nd.get('hot')
    rect(sh, nx, ny, nw, nh, WHITE, T.red if hot else G_LINE, 1.5 if hot else 0.75)
    label(sh, nx + 10, ny + 5, nw - 20, 18, nd['name'], 9, False, T.gray_text, align=L)
    label(sh, nx + 10, ny + 22, nw - 20, 30, nd['value'], 15, True, T.red if hot else T.ink, align=L)
    if nd.get('delta'):
        v, d, e = nd['delta']
        delta_badge(sh, nx + nw - 10 - badge_width(v), ny + 38, v, d, e)

def driver_tree(sh, x, y, h, root, *, col_x, node_w, node_h=58):
    """指标拆解树：从左到右逐层拆，节点是「名称 / 数值 / 涨跌徽标」，最大杠杆那条路径标红。

    节点 dict(name, value, delta=(值, 方向, 是否强调), hot, op, children)；op 是子节点之间的运算（× / +），
    画在父节点出线的拐点上。col_x / node_w 按层给出。
    """
    leaves = []
    def walk(nd, depth):
        nd['_d'] = depth
        if nd.get('children'):
            for c in nd['children']:
                walk(c, depth + 1)
        else:
            leaves.append(nd)
    walk(root, 0)
    for i, lf in enumerate(leaves):
        lf['_cy'] = y + h * (i + 0.5) / len(leaves)
    def fix(nd):                    # 叶子定位后重新算父节点中线
        if nd.get('children'):
            for c in nd['children']:
                fix(c)
            nd['_cy'] = sum(c['_cy'] for c in nd['children']) / float(len(nd['children']))
    fix(root)

    edges, ops, nodes = [], [], []
    def collect(nd):
        d = nd['_d']
        nodes.append(nd)
        if nd.get('children'):
            px = col_x[d] + node_w[d]
            mx = (px + col_x[d + 1]) / 2.0
            for c in nd['children']:
                edges.append(([(px, nd['_cy']), (mx, nd['_cy']), (mx, c['_cy']), (col_x[d + 1], c['_cy'])],
                              bool(c.get('hot'))))
                collect(c)
            if nd.get('op'):
                ops.append((mx, nd['_cy'], nd['op']))
    collect(root)
    for pts, hot in sorted(edges, key=lambda e: e[1]):
        pl(sh, pts, T.red if hot else G_LINE, 1.5 if hot else 1.0, rc=False)
    for nd in nodes:
        d = nd['_d']
        _tree_node(sh, col_x[d], nd['_cy'] - node_h / 2.0, node_w[d], node_h, nd)
    for mx, my, op in ops:
        oval(sh, mx - 11, my - 11, 22, 22, WHITE, G_MID, 1.0)
        label(sh, mx - 12, my - 12, 24, 24, op, 11, True, G_TEXT)


# ============================================================ C23 漏斗图
def funnel(sh, x, y, w, h, stages, *, label_w=118, conv_w=104, gap=6, fmt="{:g}", min_ratio=0.2):
    """漏斗图：左列环节名，中间梯形宽度按数量等比，右列段间转化率；转化率最低的一段红色徽标。"""
    n = len(stages)
    fw = w - label_w - conv_w
    cx = x + label_w + fw / 2.0
    sh_ = (h - gap * (n - 1)) / float(n)
    v0 = float(stages[0][1])
    widths = [max(fw * v / v0, fw * min_ratio) for _, v in stages]
    convs = [stages[i + 1][1] / float(stages[i][1]) for i in range(n - 1)]
    worst = convs.index(min(convs))
    a, b = (0xA6, 0xA6, 0xA6), (0xE6, 0xE6, 0xE6)      # 浅色系：中灰渐到浅灰，字一律深色
    for i, (name, v) in enumerate(stages):
        t = i / float(max(n - 1, 1))
        col = RGBColor(*(int(a[k] + (b[k] - a[k]) * t) for k in range(3)))
        ty = y + i * (sh_ + gap)
        wt = widths[i]
        wb = widths[i + 1] if i < n - 1 else widths[i] * 0.85
        pl(sh, [(cx - wt / 2.0, ty), (cx + wt / 2.0, ty), (cx + wb / 2.0, ty + sh_), (cx - wb / 2.0, ty + sh_)],
           None, 0, True, col)
        label(sh, cx - 60, ty, 120, sh_, fmt.format(v), 12, True, T.ink)
        label(sh, x, ty, label_w - 12, sh_, name, 10, True, T.ink, align=R)
    for i, cv in enumerate(convs):
        yb = y + (i + 1) * (sh_ + gap) - gap / 2.0
        t = "转化 %d%%" % round(cv * 100)
        cx0 = x + label_w + fw + 10
        if i == worst:
            chip(sh, cx0, yb - 11, pill_w(t, 9), 22, t, 9, T.pink_bg, T.red)
        else:
            label(sh, cx0 + 8, yb - 10, conv_w, 20, t, 9, False, T.gray_text, align=L)


# ============================================================ C24 子弹图
def bullet_list(sh, x, y, w, rows, *, label_w=170, val_w=236, row_h=48, vmax=100, bands=(60, 80),
                unit="%", ticks=(0, 25, 50, 75, 100)):
    """目标达成：每行一条子弹图——灰度区间（差 / 中 / 良）+ 深灰实际值条 + 红色目标刻度；未达标行名标红。

    rows = [(名称, 实际值, 目标值)]。
    """
    tx0 = x + label_w
    tw = w - label_w - val_w
    X = lambda v: tx0 + tw * v / float(vmax)
    for t in ticks:
        label(sh, X(t) - 20, y, 40, 18, "%g" % t, 8.5, False, T.gray_text)
    top = y + 22
    shades = (RGBColor(0xD9, 0xD9, 0xD9), RGBColor(0xE6, 0xE6, 0xE6), RGBColor(0xF2, 0xF2, 0xF2))
    for i, (name, actual, target) in enumerate(rows):
        cy = top + row_h * (i + 0.5)
        miss = actual < target
        label(sh, x, cy - 11, label_w - 12, 22, name, 10.5, miss, T.red if miss else T.ink, align=L)
        edges = [0, bands[0], bands[1], vmax]
        for k in range(3):
            rect(sh, X(edges[k]), cy - 10, X(edges[k + 1]) - X(edges[k]), 20, shades[k], None)
        rect(sh, tx0, cy - 4, X(actual) - tx0, 8, G_BAR, None)
        rect(sh, X(target) - 1.5, cy - 14, 3, 28, T.red, None)
        vx = x + w - val_w + 14
        rich(sh, vx, cy - 12, 110, 24, [("%g%s" % (actual, unit), 11, True, T.ink),
                                        (" / %g%s" % (target, unit), 9, False, T.gray_text)])
        if miss:
            gap_t = "差 %g 点" % (target - actual)
            delta_badge(sh, x + w - 6 - badge_width(gap_t), cy, gap_t, "down", True)
        else:
            status_dot(sh, x + w - 62, cy, "done", "达标", size=9.5)
        if i < len(rows) - 1:
            line(sh, x, top + row_h * (i + 1), x + w, top + row_h * (i + 1), G_HAIR, 0.75)
    ly = top + row_h * len(rows) + 14
    lx = x
    for col, t in zip(shades, ("差", "中", "良")):
        rect(sh, lx, ly - 6, 18, 12, col, None)
        label(sh, lx + 22, ly - 10, 30, 20, t, 8.5, False, T.gray_text, align=L)
        lx += 52
    rect(sh, lx + 6, ly - 3, 22, 6, G_BAR, None)
    label(sh, lx + 32, ly - 10, 50, 20, "实际", 8.5, False, T.gray_text, align=L)
    rect(sh, lx + 80, ly - 9, 3, 18, T.red, None)
    label(sh, lx + 88, ly - 10, 50, 20, "目标", 8.5, False, T.gray_text, align=L)


# ============================================================ C25 风险矩阵
def risk_level(score):
    if score >= 15:
        return T.red, "极高"
    if score >= 8:
        return RED_SOFT, "高"
    if score >= 4:
        return T.pink_bg, "中"
    return RGBColor(0xF2, 0xF2, 0xF2), "低"

def risk_marker(sh, cx, cy, rid, r=13):
    """风险编号圈：白底黑边，矩阵和右侧清单共用，保证一一对应。"""
    oval(sh, cx - r, cy - r, 2 * r, 2 * r, WHITE, G_MID, 1.0)
    label(sh, cx - r - 4, cy - r, 2 * r + 8, 2 * r, rid, 8, True, T.ink)

def risk_matrix(sh, x, y, cell, risks, *, n=5, xlabel="发生可能性", ylabel="影响程度"):
    """5×5 风险矩阵：可能性 × 影响，格子按乘积分四档上色；风险用带编号的白圈标在格子里。

    risks = [(编号, 可能性 1–5, 影响 1–5)]；同一格多个风险自动错开。
    """
    for i in range(n):
        for j in range(n):
            col, _ = risk_level((j + 1) * (n - i))
            rect(sh, x + j * cell, y + i * cell, cell - 2, cell - 2, col, None)
    gs = n * cell - 2
    lines_box(sh, x - 46, y, 20, gs, [[(ch, 9.5, True, T.gray_text)] for ch in ylabel], C, pitch=16)
    label(sh, x - 24, y, 20, 20, "高", 8.5, False, T.gray_text)
    label(sh, x - 24, y + gs - 20, 20, 20, "低", 8.5, False, T.gray_text)
    label(sh, x, y + gs + 4, 20, 18, "低", 8.5, False, T.gray_text, align=L)
    label(sh, x + gs - 20, y + gs + 4, 20, 18, "高", 8.5, False, T.gray_text, align=R)
    label(sh, x, y + gs + 4, gs, 18, xlabel + " →", 9.5, True, T.gray_text)
    groups = {}
    for rid, lk, im in risks:
        groups.setdefault((lk, im), []).append(rid)
    for (lk, im), ids in groups.items():
        ccx = x + (lk - 1) * cell + (cell - 2) / 2.0
        ccy = y + (n - im) * cell + (cell - 2) / 2.0
        for k, rid in enumerate(ids):
            off = (k - (len(ids) - 1) / 2.0) * 28
            risk_marker(sh, ccx + off, ccy, rid)
    ly = y + gs + 30
    lx = x
    for sc in (16, 9, 5, 1):
        col, t = risk_level(sc)
        rect(sh, lx, ly - 6, 16, 12, col, G_LINE, 0.5)
        label(sh, lx + 20, ly - 10, 34, 20, t, 8.5, False, T.gray_text, align=L)
        lx += 60


# ============================================================ C26 战略屋
def strategy_house(sh, x, y, w, roof, beam, pillars, bases, *, roof_h=62, beam_h=30, pillar_h=150,
                   base_h=28, gap=8):
    """战略屋：屋顶（愿景，红）→ 横梁（目标，深灰）→ 3–5 根支柱（名称 + 要点）→ 1–2 层地基。

    pillars = [(名称, [要点], 是否重点)]；bases = [(标签, 内容)]，第一层深灰底，其余浅灰底。
    """
    pl(sh, [(x - 6, y + roof_h), (x + w * 0.2, y), (x + w * 0.8, y), (x + w + 6, y + roof_h)], None, 0, True, T.red)
    label(sh, x, y + 8, w, roof_h - 8, roof, 13, True, WHITE)
    by = y + roof_h + 6
    shape_text(rect(sh, x, by, w, beam_h, RGBColor(0xD9, 0xD9, 0xD9), None), beam, 10.5, True, T.ink)
    py = by + beam_h + gap
    n = len(pillars)
    pw = (w - gap * (n - 1)) / float(n)
    for i, (name, pts, hot) in enumerate(pillars):
        px = x + i * (pw + gap)
        shape_text(rect(sh, px, py, pw, 30, T.pink_bg if hot else T.lab, T.red if hot else None, 1.25),
                   name, 10.5, True, T.red if hot else T.ink)
        rect(sh, px, py + 30, pw, pillar_h - 30, WHITE, G_LINE, 0.75)
        lines_box(sh, px + 12, py + 40, pw - 18, pillar_h - 48,
                  [[("■ ", 7, False, T.red), (t, 9.5, False, T.txt)] for t in pts], L, TOP, pitch=22)
    yb = py + pillar_h + gap
    for k, (tag, body) in enumerate(bases):
        dark = k == 0
        fill = G_SOLID if dark else T.lab
        col = T.ink
        rect(sh, x, yb, w, base_h, fill, None)
        rich(sh, x, yb, w, base_h, [(tag + "：", 10, True, col), (body, 10, False, col)], C)
        yb += base_h + 4


# ============================================================ C27 成熟度阶梯
def maturity_steps(sh, x, y_bottom, w, levels, *, current, target=None, base_h=100, rise=38, band_h=30, gap=6,
                   current_text="当前位置", target_text="目标"):
    """成熟度阶梯：台阶逐级升高，已达到深灰、当前红色、未达到虚线框；当前台阶上方标位置，目标台阶插旗。

    levels = [(代号, 名称, [说明行])]；current / target 是台阶序号。
    """
    n = len(levels)
    sw = (w - gap * (n - 1)) / float(n)
    tops = []
    for i, (code, name, desc) in enumerate(levels):
        sx = x + i * (sw + gap)
        top = y_bottom - (base_h + rise * i)
        tops.append((sx, top))
        if i < current:
            band, bcol, body, dcol = G_SOLID, T.ink, T.lab, T.txt
        elif i == current:
            band, bcol, body, dcol = T.red, WHITE, T.pink_bg, T.ink
        else:
            band, bcol, body, dcol = WHITE, T.gray_text, WHITE, T.gray_text
        b = rect(sh, sx, top + band_h, sw, y_bottom - top - band_h, body, G_MID if i > current else None, 0.75)
        bb = rect(sh, sx, top, sw, band_h, band, G_MID if i > current else None, 0.75)
        if i > current:
            _dash(b); _dash(bb)
        rich(sh, sx, top, sw, band_h, [(code + "  ", 10, True, bcol), (name, 10, True, bcol)], C)
        lines_box(sh, sx + 8, top + band_h + 8, sw - 12, y_bottom - top - band_h - 12,
                  [[(t, 9, i == current, dcol)] for t in desc], C, TOP, pitch=19)
    sx, top = tops[current]
    tw = pill_w(current_text, 9)
    chip(sh, sx + sw / 2.0 - tw / 2.0, top - 32, tw, 22, current_text, 9, T.red, WHITE)
    pl(sh, [(sx + sw / 2.0 - 6, top - 10), (sx + sw / 2.0 + 6, top - 10), (sx + sw / 2.0, top - 3)], None, 0, True,
       T.red)
    if target is not None:
        sx, top = tops[target]
        fx = sx + sw / 2.0 - 10
        line(sh, fx, top - 2, fx, top - 30, G_MID, 1.5)
        pl(sh, [(fx, top - 30), (fx + 22, top - 24), (fx, top - 18)], None, 0, True, T.red)
        label(sh, fx + 26, top - 32, 80, 18, target_text, 9, True, T.red, align=L)


# ============================================================ C28 中心辐射图
def hub_spoke(sh, cx, cy, r, center, nodes, *, rx, ry, box_w=150, box_h=50, start_angle=-90):
    """中心辐射：中心红圆是我方，周围是伙伴 / 角色，连线上写往来内容；重点伙伴红框红线。

    nodes = [(名称, 角色说明, 连线文字, 是否重点, 是否双向)]，从 start_angle 起顺时针等分排布。
    """
    n = len(nodes)
    pos = []
    for k, (name, role, flow, hot, both) in enumerate(nodes):
        a = math.radians(start_angle + 360.0 * k / n)
        bx, by = cx + rx * math.cos(a), cy + ry * math.sin(a)
        pos.append((bx, by))
        rrect(sh, bx - box_w / 2.0, by - box_h / 2.0, box_w, box_h, WHITE, T.red if hot else G_LINE,
              1.5 if hot else 0.75, radius=_r(4))
        lines_box(sh, bx - box_w / 2.0, by - box_h / 2.0, box_w, box_h,
                  [[(name, 10, True, T.red if hot else T.ink)], [(role, 8.5, False, T.gray_text)]], C, pitch=18)
    oval(sh, cx - r, cy - r, 2 * r, 2 * r, T.red, None)
    lines_box(sh, cx - r, cy - r, 2 * r, 2 * r, [[(t, 11.5, True, WHITE)] for t in center.split("\n")], C, pitch=21)
    for (name, role, flow, hot, both), (bx, by) in zip(nodes, pos):
        ddx, ddy = bx - cx, by - cy
        dist = math.hypot(ddx, ddy)
        ux, uy = ddx / dist, ddy / dist
        tb = min((box_w / 2.0) / abs(ux) if abs(ux) > 1e-6 else 1e9, (box_h / 2.0) / abs(uy) if abs(uy) > 1e-6 else 1e9)
        sx, sy = cx + ux * (r + 3), cy + uy * (r + 3)
        ex, ey = bx - ux * (tb + 3), by - uy * (tb + 3)
        line(sh, sx, sy, ex, ey, T.red if hot else G_MID, 1.5 if hot else 1.0, arrow=True, back=both)
        if flow:
            mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
            fc = T.red if hot else T.gray_text
            if abs(ux) < 0.3:                      # 竖线太短，文字放在线旁
                label(sh, mx + 8, my - 10, 120, 20, flow, 8.5, hot, fc, align=L)
            else:
                fw_ = wpx(flow, 8.5) * 1.15 + 10
                shape_text(rect(sh, mx - fw_ / 2.0, my - 10, fw_, 20, T.soft_panel, None), flow, 8.5, hot, fc)
