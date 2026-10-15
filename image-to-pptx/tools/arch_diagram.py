# -*- coding: utf-8 -*-
"""C1 分层架构图 v2：写规格 → 自动排版 → 自动体检。

    from arch_diagram import *          # 含 components 的全部名字
    use_theme(LIGHT)                    # 新做页面先切浅色复刻风（或 STYLE）
    spec = dict(layers=[Layer(...), ...], actors=..., side=..., external=..., fanout=..., boundary="本方案范围")
    h, report = arch_diagram(sh, x, y, w, spec)          # 返回实际高度与体检结果

元素（23 种）：
  结构  层带 / 层名栏 / 焦点层 / 层标题 / 行标签 / 系统边界框 / 跨层贯通栏
  内容  模块（图标 + 文字 + 副文字）/ 容器 / 容器分组 / 能力标签 / 占位容器
  状态  重点 / 缺口 / 新增 / 规划中（模块、容器、标签通用）
  外围  使用者行 / 外部依赖行 / 注释栏
  标注  编号 / 图例
  连线  层间箭头（可对齐到指定模块、可标红为关键路径）/ 分发线

所有坐标由下面的栅格常量算出；调用方只写内容，不写坐标。
"""
import math
from components import *
from components import _r, _c

# ---------------- 栅格（1672 像素画布；1 cm ≈ 49 px） ----------------
RAIL_W, PAD, GAP_X, GAP_Y = 80, 10, 8, 8          # 层名栏 1.6 cm；层内边距；模块横 / 纵间距
ROW_H, TITLE_H = 44, 26                           # 模块行高 0.9 cm；层标题行
LAYER_GAP, FAN_GAP, EDGE_GAP = 24, 44, 26         # 层间距；带分发线的层间距；边界内外的间距
CHIP_H, CHIP_GAP, BOX_TITLE_H, GROUP_LABEL_H = 28, 6, 30, 22
SIDE_W, NOTE_W, COL_GAP, BPAD = 104, 108, 10, 12   # 跨层栏；注释栏；栏间距；边界内边距
EDGE_H = 40                                       # 使用者 / 外部依赖行高
MOD_SIZE, SUB_SIZE, CHIP_SIZE, MIN_SIZE = 10, 8.5, 9, 9
ICON_S = 22
LIMITS = dict(layers=(3, 5), per_row=(6, 8), chars=(6, 8), numbers=6, hot_ratio=0.25, hot_max=3)

# ---------------- 浅色系配色 ----------------
LAYER_FILL, LAYER_BORDER, RAIL = RGBColor(0xFC, 0xFC, 0xFD), RGBColor(0xE2, 0xE5, 0xE9), RGBColor(0xEC, 0xED, 0xEF)
F_FILL, F_BORDER, F_RAIL = RGBColor(0xFD, 0xEF, 0xEF), RGBColor(0xF3, 0xC6, 0xC6), RGBColor(0xF8, 0xE4, 0xE4)
CELL_B, CHIP_FILL = RGBColor(0xDC, 0xDF, 0xE3), RGBColor(0xEE, 0xF0, 0xF2)
SIDE_FILL, EXT_FILL, GAP_FILL = RGBColor(0xF6, 0xF7, 0xF9), RGBColor(0xF7, 0xF7, 0xF8), RGBColor(0xFF, 0xF7, 0xF7)
HOT_BOX_B, HOT_GROUP_B = RGBColor(0xEF, 0xB8, 0xB8), RGBColor(0xEB, 0xD5, 0xD5)


# ---------------- 规格构造 ----------------
def M(text, icon=None, sub=None, n=None, state=None):
    """模块。state：None / hot 重点 / gap 缺口 / new 新增 / plan 规划中。"""
    return dict(text=text, icon=icon, sub=sub, n=n, state=state)

def Row(*items, label=None, n=None):
    return dict(items=list(items), label=label, n=n)

def Chip(text, state=None):
    return dict(text=text, state=state)

def Group(label, *chips, state=None):
    return dict(label=label, state=state, chips=[c if isinstance(c, dict) else Chip(c) for c in chips])

def Box(title, *groups, n=None, state=None, placeholder=None, rows=2, weight=None):
    """容器。groups 为空且给了 placeholder 时画成占位容器。"""
    return dict(title=title, groups=list(groups), n=n, state=state, placeholder=placeholder, rows=rows, weight=weight)

def Layer(name, *, title=None, rows=(), boxes=(), focus=False, note=None, n=None):
    return dict(name=name, title=title, rows=list(rows), boxes=list(boxes), focus=focus, note=note, n=n)

def Edge(name, *items):
    """使用者 / 外部依赖行：items = [(名称, 副文字, 图标)]。"""
    return dict(name=name, items=list(items))

def Side(name, *items):
    return dict(name=name, items=list(items))


# ---------------- 文字适配 ----------------
def _chars(t):
    return sum(0.5 if ord(c) < 0x2E80 else 1.0 for c in t)

def _tw(t, size):
    return wpx(t, size) * 1.1                      # 留一成给回落字体

def _split(t):
    if " " in t:
        sp = [i for i, c in enumerate(t) if c == " "]
        k = min(sp, key=lambda i: abs(i - len(t) / 2.0))
        return t[:k].strip(), t[k + 1:].strip()
    k = int(math.ceil(len(t) / 2.0))
    while 0 < k < len(t) and t[k - 1].isascii() and t[k - 1].isalnum() and t[k].isascii() and t[k].isalnum():
        k += 1
    return t[:k], t[k:]

def _fit(t, size, avail, can_wrap, qa, where):
    """依次尝试：原字号 → 降半号 → 换两行（不能换行时跳过）→ 记一条错误。"""
    if _tw(t, size) <= avail:
        return [t], size
    if size - 0.5 >= MIN_SIZE and _tw(t, size - 0.5) <= avail:
        return [t], size - 0.5
    if can_wrap:
        a, b = _split(t)
        if a and b and max(_tw(a, size), _tw(b, size)) <= avail:
            return [a, b], size
    qa.append(("error", "%s「%s」放不下（可用 %d px），请缩短文案" % (where, t, avail)))
    return [t], max(size - 0.5, MIN_SIZE)


def _dash(s, val="dash"):
    d = etree.SubElement(s.line._get_or_add_ln(), qn('a:prstDash')); d.set('val', val)
    return s

def _new_tag(sh, x1, y0):
    """NEW 角标：压在元素右上沿，离右边缘留 10px，免得和相邻格子的编号挤在一起。"""
    rect(sh, x1 - 40, y0 - 7, 30, 14, T.red, None)
    label(sh, x1 - 42, y0 - 9, 34, 18, "NEW", 7, True, WHITE)

def _arrow(sh, x, y1, y2, color, lw, head=True, tail=False):
    """竖向连线，小号箭头：层间距只有二十几像素，中号箭头两头一叠会变成菱形。"""
    c = sh.add_connector(MSO_CONNECTOR.STRAIGHT, X(x), Y(y1), X(x), Y(y2))
    c.line.color.rgb = color; c.line.width = Pt(lw)
    ln = c.line._get_or_add_ln()
    for on, tag in ((tail, 'a:headEnd'), (head, 'a:tailEnd')):
        if on:
            e = etree.SubElement(ln, qn(tag)); e.set('type', 'triangle'); e.set('w', 'sm'); e.set('len', 'sm')
    return c


# ---------------- 高度计算 ----------------
def _box_h(b):
    R = b.get('rows', 2)
    grid = R * CHIP_H + (R - 1) * CHIP_GAP
    if any(g['label'] for g in b['groups']):
        return BOX_TITLE_H + GROUP_LABEL_H + grid + 8 + 8
    return BOX_TITLE_H + grid + 10

def _layer_h(L):
    h = 2 * PAD
    if L['title']:
        h += TITLE_H
    if L['rows']:
        h += len(L['rows']) * ROW_H + (len(L['rows']) - 1) * GAP_Y
    if L['boxes']:
        if L['rows']:
            h += GAP_Y
        h += max(_box_h(b) for b in L['boxes'])
    return max(h, 58)


# ---------------- 绘制：模块 / 容器 / 标签 ----------------
STATE_STYLE = {      # 填充, 边框色, 线宽, 虚线, 文字色, 文字加粗
    None: (WHITE, CELL_B, 0.75, False, None, False),
    "new": (WHITE, CELL_B, 0.75, False, None, False),
    "hot": (WHITE, None, 1.5, False, "red", True),
    "gap": (GAP_FILL, None, 1.25, True, "red", True),
    "plan": (WHITE, G_MID, 0.75, True, "gray", False),
    "ext": (EXT_FILL, G_MID, 0.75, True, None, False),       # 外部依赖：系统边界外
}

def _style(state):
    fill, bc, lw, dash, tc, bold = STATE_STYLE[state]
    bc = T.red if bc is None else bc
    tc = {None: T.ink, "red": T.red, "gray": G_TEXT}[tc]
    return fill, bc, lw, dash, tc, bold

def _module(sh, ctx, m, x, y, w, h, where):
    fill, bc, lw, dash, tc, bold = _style(m['state'])
    s = rrect(sh, x, y, w, h, fill, bc, lw, radius=_r(4))
    if dash:
        _dash(s)
    icon_w = ICON_S + 6 if m['icon'] else 0
    avail = w - 14 - icon_w
    lines, size = _fit(m['text'], MOD_SIZE, avail, not m['sub'], ctx['qa'], where)
    sub_lines = []
    if m['sub']:
        sub_lines, _ = _fit(m['sub'], SUB_SIZE, avail, False, ctx['qa'], where + "副文字")
    text_w = max([_tw(t, size) for t in lines] + [_tw(t, SUB_SIZE) for t in sub_lines])
    gx = x + (w - icon_w - text_w) / 2.0
    if m['icon']:
        m['icon'](sh, gx + ICON_S / 2.0, y + h / 2.0, ICON_S, G_MID if m['state'] in ("plan", "ext") else T.red)
    rows = [[(t, size, bold, tc)] for t in lines] + [[(t, SUB_SIZE, m['state'] == "gap", T.red if m['state'] == "gap" else G_TEXT)]
                                                    for t in sub_lines]
    lines_box(sh, gx + icon_w, y, text_w + 12, h, rows, L, pitch=21 if len(rows) > 1 else None)
    if m['state'] == "new":
        _new_tag(sh, x + w, y)
    if m['n']:
        ctx['marks'].append((x + 12, y + 2, m['n']))      # 压在上沿、往里收，归属不会和相邻格子混淆
    ctx['centers'][m['text']] = x + w / 2.0
    ctx['count']['modules'] += 1
    ctx['states'].add(m['state'])

def _chip(sh, ctx, c, x, y, w, h, where):
    st = c['state']
    if st == "gap":
        s = rrect(sh, x, y, w, h, F_FILL, T.red, 1.0, radius=_r(4)); _dash(s)
        col, bold = T.red, True
    elif st == "hot":
        rrect(sh, x, y, w, h, WHITE, T.red, 1.25, radius=_r(4)); col, bold = T.red, True
    elif st == "plan":
        s = rrect(sh, x, y, w, h, WHITE, G_MID, 0.75, radius=_r(4)); _dash(s)
        col, bold = G_TEXT, False
    else:
        rrect(sh, x, y, w, h, CHIP_FILL, None, radius=_r(4)); col, bold = T.txt, False
    lines, size = _fit(c['text'], CHIP_SIZE, w - 8, False, ctx['qa'], where)
    label(sh, x - 4, y - 4, w + 8, h + 8, lines[0], size, bold, col)
    ctx['states'].add(st)

def _box(sh, ctx, b, x, y, w, h, where):
    st = b['state']
    hot = st == "hot"
    ph = b['placeholder'] is not None and not b['groups']
    if ph or st == "plan":
        s = rrect(sh, x, y, w, h, SIDE_FILL, G_MID, 0.75, radius=_r(6)); _dash(s)
        tc = G_TEXT
    else:
        rrect(sh, x, y, w, h, F_FILL if hot else WHITE, HOT_BOX_B if hot else CELL_B, 1.0 if hot else 0.75, radius=_r(6))
        tc = T.red if hot else T.ink
    ctx['states'].add(st if not ph else "plan")
    tx = x + (30 if b['n'] else 12)
    lines, size = _fit(b['title'], 10.5, w - (tx - x) - 12, False, ctx['qa'], where + "容器标题")
    label(sh, tx, y + 3, w - (tx - x) - 10, BOX_TITLE_H - 4, lines[0], size, True, tc, align=L)
    if b['n']:
        ctx['marks'].append((x + 16, y + BOX_TITLE_H / 2.0 + 1, b['n']))
    if st == "new":
        _new_tag(sh, x + w, y)
    ctx['centers'][b['title']] = x + w / 2.0
    ctx['count']['boxes'] += 1
    if hot:
        ctx['count']['hot'] += 1
    if ph:
        label(sh, x, y + BOX_TITLE_H, w, h - BOX_TITLE_H - 6, b['placeholder'], 10, False, G_TEXT)
        return
    R = b['rows']
    groups = b['groups']
    cols = [max(1, int(math.ceil(len(g['chips']) / float(R)))) for g in groups]
    labeled = any(g['label'] for g in groups)
    inner_x, inner_w = x + 8, w - 16
    gw_total = inner_w - 8 * (len(groups) - 1)
    gx = inner_x
    grid_h = R * CHIP_H + (R - 1) * CHIP_GAP
    for g, c in zip(groups, cols):
        gw = gw_total * c / float(sum(cols))
        if labeled:
            gy = y + BOX_TITLE_H
            rrect(sh, gx, gy, gw, h - BOX_TITLE_H - 8, WHITE, HOT_GROUP_B if hot else CELL_B, 0.75, radius=_r(5))
            gcol = T.red if g['state'] == "gap" else T.ink
            label(sh, gx + 8, gy + 2, gw - 16, GROUP_LABEL_H - 2, g['label'] or "", 9.5, True, gcol, align=L)
            cx0, cy0, cw_ = gx + 6, gy + GROUP_LABEL_H, gw - 12
        else:
            cx0, cw_ = gx, gw
            cy0 = y + BOX_TITLE_H + (h - BOX_TITLE_H - 6 - grid_h) / 2.0
        chip_w = (cw_ - (c - 1) * CHIP_GAP) / float(c)
        for k, ch in enumerate(g['chips']):
            r_, c_ = k // c, k % c
            _chip(sh, ctx, ch, cx0 + c_ * (chip_w + CHIP_GAP), cy0 + r_ * (CHIP_H + CHIP_GAP), chip_w, CHIP_H,
                  where + "能力标签")
        gx += gw + 8


# ---------------- 主函数 ----------------
def arch_diagram(sh, x, y, w, spec, *, bg=None, draw=True):
    """按规格自动排版并绘制分层架构图。返回 (高度, 体检结果)。

    spec 键：layers（必填）、actors、external、side、boundary（边界名）、fanout、links、legend（默认 True）。
    """
    layers = spec['layers']
    side, actors, external = spec.get('side'), spec.get('actors'), spec.get('external')
    boundary, fan = spec.get('boundary'), spec.get('fanout')
    bg = _c(bg, T.soft_panel)
    qa = []
    ctx = dict(qa=qa, marks=[], centers={}, states=set(), count=dict(modules=0, boxes=0, hot=0))

    # 横向栅格
    has_notes = any(L['note'] for L in layers)
    note_x = x + w - NOTE_W if has_notes else None
    bx0, bx1 = x, (note_x - COL_GAP) if has_notes else x + w
    in0, in1 = bx0 + (BPAD if boundary else 0), bx1 - (BPAD if boundary else 0)
    if side:
        side_x0 = in1 - SIDE_W
        band_x1 = side_x0 - COL_GAP
    else:
        band_x1 = in1
    band_x0 = in0
    mod_x0, mod_x1 = band_x0 + RAIL_W + PAD, band_x1 - PAD
    mod_w = mod_x1 - mod_x0
    mid_x = (mod_x0 + mod_x1) / 2.0

    # 纵向栅格
    cy = y
    if actors:
        actor_y = cy
        cy += EDGE_H + EDGE_GAP
    if boundary:
        b_top = cy
        cy += BPAD + 8
    ly, lh = [], []
    for i, Lr in enumerate(layers):
        h = _layer_h(Lr)
        ly.append(cy); lh.append(h)
        cy += h
        if i < len(layers) - 1:
            cy += FAN_GAP if (fan and fan['a'] == i) else LAYER_GAP
    layers_bottom = cy
    if boundary:
        cy += BPAD
        b_bottom = cy
    if external:
        cy += EDGE_GAP
        ext_y = cy
        cy += EDGE_H
    legend_y = None
    if spec.get('legend', True):
        cy += 14
        legend_y = cy
        cy += 20
    height = cy - y
    if not draw:
        return height, qa

    # 边界框
    if boundary:
        s = rrect(sh, bx0, b_top, bx1 - bx0, b_bottom - b_top, None, G_MID, 1.0, radius=_r(8)); _dash(s)
        tw_ = pill_w(boundary, 9)
        rect(sh, bx0 + 14, b_top - 10, tw_, 20, bg, None)
        label(sh, bx0 + 14, b_top - 10, tw_, 20, boundary, 9, True, G_TEXT)

    # 使用者 / 外部依赖行
    def edge_row(E, ey, dashed):
        rrect(sh, band_x0, ey, RAIL_W, EDGE_H, RAIL, None, radius=_r(5))
        label(sh, band_x0, ey, RAIL_W, EDGE_H, E['name'], 10, True, T.ink)
        n = len(E['items'])
        iw = min(200.0, (mod_w - GAP_X * (n - 1)) / n)
        xs = []
        for k, (name, sub, icon) in enumerate(E['items']):
            ix = mod_x0 + k * (iw + GAP_X)
            _module(sh, ctx, dict(text=name, icon=icon, sub=sub, n=None, state="ext" if dashed else None),
                    ix, ey, iw, EDGE_H, E['name'])
            ctx['count']['modules'] -= 1
            xs.append(ix + iw / 2.0)
        return xs

    if actors:
        edge_row(actors, actor_y, False)
    ext_xs = edge_row(external, ext_y, True) if external else []

    # 层
    total_rows_items = 0
    for i, Lr in enumerate(layers):
        y0, h = ly[i], lh[i]
        foc = Lr['focus']
        rrect(sh, band_x0, y0, band_x1 - band_x0, h, F_FILL if foc else LAYER_FILL, F_BORDER if foc else LAYER_BORDER,
              0.75, radius=_r(6))
        rr = max(_r(6) - 0.5, 0)
        rshape(sh, band_x0 + 0.5, y0 + 0.5, RAIL_W, h - 1, (rr, 0, 0, rr), F_RAIL if foc else RAIL)
        names = []
        for part in Lr['name'].split("\n"):              # 层名放不下就拆两行，不压边
            got, nsz = _fit(part, 11.5, RAIL_W - 16, True, qa, "层名")
            names += [(t, nsz) for t in got]
        lines_box(sh, band_x0, y0, RAIL_W, h, [[(t, nsz, True, T.red if foc else T.ink)] for t, nsz in names],
                  C, pitch=22)
        if Lr['n']:
            ctx['marks'].append((band_x0 + 12, y0 + 12, Lr['n']))
        if foc:
            ctx['states'].add("focus")
        cy = y0 + PAD
        if Lr['title']:
            label(sh, mod_x0, cy, mod_w, TITLE_H - 4, Lr['title'], 11, True, T.red if foc else T.ink, align=L)
            cy += TITLE_H
        lab_w = 0
        if any(r['label'] for r in Lr['rows']):
            lab_w = max(pill_w(r['label'], 10) for r in Lr['rows'] if r['label'])
        for r in Lr['rows']:
            n = len(r['items'])
            total_rows_items += n
            lo, hi = LIMITS['per_row']
            if n > hi:
                qa.append(("error", "%s 一行 %d 个模块，超过上限 %d" % (Lr['name'].replace("\n", ""), n, hi)))
            elif n > lo:
                qa.append(("warn", "%s 一行 %d 个模块，建议不超过 %d" % (Lr['name'].replace("\n", ""), n, lo)))
            ix0 = mod_x0
            if lab_w:
                if r['label']:
                    rrect(sh, mod_x0, cy, lab_w, ROW_H, RAIL, None, radius=_r(4))
                    label(sh, mod_x0, cy, lab_w, ROW_H, r['label'], 10, True, T.ink)
                    if r['n']:
                        ctx['marks'].append((mod_x0 + 12, cy + 2, r['n']))
                ix0 = mod_x0 + lab_w + GAP_X
            iw = (mod_x1 - ix0 - GAP_X * (n - 1)) / float(n)
            for k, m in enumerate(r['items']):
                ch_lo, ch_hi = LIMITS['chars']
                c_ = _chars(m['text'])
                if c_ > ch_hi:
                    qa.append(("error", "模块名「%s」%g 字，超过上限 %d" % (m['text'], c_, ch_hi)))
                elif c_ > ch_lo:
                    qa.append(("warn", "模块名「%s」%g 字，建议不超过 %d" % (m['text'], c_, ch_lo)))
                _module(sh, ctx, m, ix0 + k * (iw + GAP_X), cy, iw, ROW_H, "模块")
                if m['state'] == "hot":
                    ctx['count']['hot'] += 1
            cy += ROW_H + GAP_Y
        if Lr['boxes']:
            if not Lr['rows']:
                cy -= 0
            bh = max(_box_h(b) for b in Lr['boxes'])
            ws = []
            for b in Lr['boxes']:
                if b['weight']:
                    ws.append(b['weight'])
                elif b['groups']:
                    R = b['rows']
                    ws.append(sum(max(1, math.ceil(len(g['chips']) / float(R))) for g in b['groups'])
                              + 0.3 * (len(b['groups']) - 1))
                else:
                    ws.append(1.6)
            avail = mod_w - GAP_X * (len(ws) - 1)
            bx = mod_x0
            for b, wt in zip(Lr['boxes'], ws):
                bw = avail * wt / sum(ws)
                _box(sh, ctx, b, bx, cy, bw, bh, "容器")
                bx += bw + GAP_X
        if Lr['note']:
            s = rrect(sh, note_x, y0 + 6, NOTE_W, h - 12, WHITE, G_LINE, 0.75, radius=_r(5)); _dash(s)
            lines_box(sh, note_x + 4, y0 + 6, NOTE_W - 8, h - 12,
                      [[(t, 9, False, G_TEXT)] for t in Lr['note'].split("\n")], C, pitch=17)

    # 跨层贯通栏
    if side:
        top, bot = ly[0], layers_bottom
        rrect(sh, side_x0, top, SIDE_W, bot - top, SIDE_FILL, CELL_B, 0.75, radius=_r(6))
        lines_box(sh, side_x0, top + 8, SIDE_W, 46, [[(t, 10.5, True, T.ink)] for t in side['name'].split("\n")], C,
                  pitch=20)
        n = len(side['items'])
        area0, area1 = top + 62, bot - 10
        step = (area1 - area0) / float(n)
        for k, it in enumerate(side['items']):
            c = it if isinstance(it, dict) else Chip(it)
            ccy = area0 + step * (k + 0.5)
            _chip(sh, ctx, dict(text=c['text'], state=c['state']), side_x0 + 10, ccy - 15, SIDE_W - 20, 30, "跨层栏")
        ctx['states'].add("side")

    # 连线：最后画
    def lay_x(name, default):
        return ctx['centers'].get(name, default) if name else default
    fan_pair = (fan['a'], fan['b']) if fan else None
    links = spec.get('links')
    if links is None:
        links = [dict(a=i, b=i + 1) for i in range(len(layers) - 1) if (i, i + 1) != fan_pair]
    for lk in links:
        a = lk['a']
        ax = lay_x(lk.get('at'), mid_x)
        y1, y2 = ly[a] + lh[a], ly[a + 1]
        hot = lk.get('hot', False)
        kind = lk.get('kind', "down" if hot else "bi")          # 关键路径默认单向，读得出走向
        _arrow(sh, ax, y1 + 1, y2 - 1, T.red if hot else G_MID, 1.75 if hot else 1.25,
               head=kind in ("bi", "down"), tail=kind in ("bi", "up"))
        if hot:
            ctx['states'].add("path")
    if fan:
        a, b = fan['a'], fan['b']
        y1, y2 = ly[a] + lh[a], ly[b]
        busy = (y1 + y2) / 2.0
        downs = [ctx['centers'][bx['title']] for bx in layers[b]['boxes']]
        ups = [ctx['centers'].get(u, mid_x) for u in fan.get('ups', [])] or [mid_x]
        xs = downs + ups
        line(sh, min(xs), busy, max(xs), busy, G_MID, 1.0)
        for dx in downs:
            _arrow(sh, dx, busy, y2 - 1, G_MID, 1.0)
        for ux in ups:
            _arrow(sh, ux, busy, y1 + 1, G_MID, 1.0)
        if fan.get('label'):
            t = fan['label']
            lw_ = pill_w(t, 9)
            lx = fan.get('label_x', (min(xs) + max(xs)) / 2.0)
            occupied = [v for v in xs if abs(v - lx) < lw_ / 2.0 + 6]
            if occupied:                                     # 说明别压在箭头上：挪到最近的空档
                gaps = sorted(set(xs))
                cands = [(gaps[k] + gaps[k + 1]) / 2.0 for k in range(len(gaps) - 1)
                         if gaps[k + 1] - gaps[k] > lw_ + 16]
                if cands:
                    lx = min(cands, key=lambda v: abs(v - mid_x))
            rect(sh, lx - lw_ / 2.0, busy - 10, lw_, 20, bg, None)
            label(sh, lx - lw_ / 2.0, busy - 10, lw_, 20, t, 9, False, T.txt)
            if fan.get('n'):
                ctx['marks'].append((lx - lw_ / 2.0 - 10, busy, fan['n']))
    if actors:
        _arrow(sh, mid_x, actor_y + EDGE_H + 1, ly[0] - 1, G_MID, 1.25)
    for ex in ext_xs:
        _arrow(sh, ex, ext_y - 1, (b_bottom if boundary else layers_bottom) + 1, G_MID, 1.0, tail=True)

    # 编号：最上层
    nums = []
    for mx, my, n in ctx['marks']:
        numc(sh, mx, my, 9.5, n, 9, fill=T.red)
        nums.append(n)
    if nums:
        ctx['states'].add("num")

    # 图例：只列用到的
    if legend_y is not None:
        items = []
        if "focus" in ctx['states']:
            items.append(("focus", "焦点层"))
        if "hot" in ctx['states']:
            items.append(("hot", "重点"))
        if "gap" in ctx['states']:
            items.append(("gap", "缺口 / 待补齐"))
        if "new" in ctx['states']:
            items.append(("new", "本期新增"))
        if "plan" in ctx['states']:
            items.append(("plan", "规划中"))
        if "path" in ctx['states']:
            items.append(("path", "关键路径"))
        if "num" in ctx['states']:
            items.append(("num", "编号见说明"))
        lx = band_x0
        label(sh, lx, legend_y, 40, 20, "图例", 8.5, True, G_TEXT, align=L)
        lx += 40
        for kind, t in items:
            cy_ = legend_y + 10
            if kind == "focus":
                rect(sh, lx, cy_ - 7, 24, 14, F_FILL, F_BORDER, 0.75)
            elif kind == "hot":
                rect(sh, lx, cy_ - 7, 24, 14, WHITE, T.red, 1.5)
            elif kind == "gap":
                _dash(rect(sh, lx, cy_ - 7, 24, 14, GAP_FILL, T.red, 1.0))
            elif kind == "new":
                rect(sh, lx, cy_ - 7, 30, 14, T.red, None)
                label(sh, lx - 2, cy_ - 9, 34, 18, "NEW", 7, True, WHITE)
                lx += 6
            elif kind == "plan":
                _dash(rect(sh, lx, cy_ - 7, 24, 14, WHITE, G_MID, 0.75))
            elif kind == "path":
                line(sh, lx, cy_, lx + 24, cy_, T.red, 1.75, arrow=True)
            elif kind == "num":
                numc(sh, lx + 9, cy_, 8, 1, 8, fill=T.red)
                lx -= 6
            label(sh, lx + 30, legend_y, 90, 20, t, 8.5, False, G_TEXT, align=L)
            lx += 30 + _tw(t, 8.5) + 22

    # 体检
    lo, hi = LIMITS['layers']
    if not lo <= len(layers) <= hi:
        qa.append(("warn", "共 %d 层，建议 %d–%d 层" % (len(layers), lo, hi)))
    if sum(1 for L_ in layers if L_['focus']) > 1:
        qa.append(("error", "焦点层超过 1 个"))
    total = ctx['count']['modules'] + ctx['count']['boxes']
    cap = min(LIMITS['hot_max'], max(1, int(total * LIMITS['hot_ratio'])))
    if ctx['count']['hot'] > cap:
        qa.append(("error", "重点元素 %d 个，超过预算 %d" % (ctx['count']['hot'], cap)))
    if len(nums) != len(set(nums)):
        qa.append(("error", "编号重复：%s" % sorted(n for n in set(nums) if nums.count(n) > 1)))
    if nums and sorted(nums) != list(range(1, len(nums) + 1)):
        qa.append(("warn", "编号不连续：%s" % sorted(nums)))
    if len(nums) > LIMITS['numbers']:
        qa.append(("warn", "编号 %d 个，建议不超过 %d" % (len(nums), LIMITS['numbers'])))
    report = dict(issues=qa, layers=len(layers), modules=ctx['count']['modules'], boxes=ctx['count']['boxes'],
                  hot=ctx['count']['hot'], hot_cap=cap, numbers=sorted(nums))
    return height, report
