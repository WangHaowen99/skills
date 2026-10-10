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
    框架 page_title / panel / section_title / footer
    页型 overview_page                                    页型 A：图表 + 指标卡 | 时间轴 + 统计条 / 特性卡

坐标一律写画布像素（默认 1672x941，见 deck_kit.canvas）。几何参数全部显式传入，
组件只负责「画什么、按什么顺序画」，不替调用方猜位置——复刻时照源图量，新做时照 STYLE.md 的栅格算。

风格：默认是复刻风（圆角、粉色强调，见 draw_kit 配色）。按 ppt-deck 规范出图时先 use_theme(STYLE)，
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

# ppt-deck STYLE.md 规范：直角、#C7000A、#404040 表头、#F2F2F2 块底、#BFBFBF 框线
STYLE = Theme(
    name="style",
    red=RGBColor(0xC7, 0x00, 0x0A), ink=RGBColor(0, 0, 0), txt=RGBColor(0, 0, 0),
    numd=RGBColor(0x40, 0x40, 0x40), icn=RGBColor(0x40, 0x40, 0x40), foot=RGBColor(0x59, 0x59, 0x59),
    panel=RGBColor(0xF2, 0xF2, 0xF2), card_border=RGBColor(0xBF, 0xBF, 0xBF), sep=RGBColor(0xBF, 0xBF, 0xBF),
    pink=RGBColor(0xF2, 0xCC, 0xCE), soft_panel=RGBColor(0xF2, 0xF2, 0xF2),
    pink_bg=RGBColor(0xFB, 0xEC, 0xED), pink_border=RGBColor(0xC7, 0x00, 0x0A),
    lab=RGBColor(0xD9, 0xD9, 0xD9), cell_border=RGBColor(0, 0, 0), arrow=RGBColor(0x59, 0x59, 0x59),
    gray_text=RGBColor(0x59, 0x59, 0x59), head=RGBColor(0x40, 0x40, 0x40),
    radius=0.0,
)

T = REPLICA

def use_theme(theme):
    """切换组件默认风格。返回旧风格，便于临时切换后还原。"""
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
