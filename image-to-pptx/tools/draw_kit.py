# -*- coding: utf-8 -*-
"""deck_kit 之上的扩展图元：折线 / 曲线箭头、独立圆角、混排多行文本、编号圆、胶囊标签、原生表格。

    from draw_kit import *        # 已包含 deck_kit 的全部名字

坐标一律写源图像素，换算见 deck_kit。下面的配色是「复刻风」默认值（取自构建子系统 deck 源图），
会覆盖 deck_kit 里同名的中性配色；要按 ppt-deck 规范出图时用 components.use_theme(STYLE)。

QuickLook 相关的处理已经内化在这里，改动前先看 PITFALLS.md：
- numc：数字放独立文本框，小圆的内切文字区放不下一行
- rshape：代替「圆角矩形 + 方块压角」，QuickLook 把 roundRect 填充渲染得浅一档
- cell_set / cell_lines：固定行距，QuickLook 忽略单元格边距、行高按行距撑
"""
import math
from deck_kit import *
from deck_kit import _paint

# ---------- 配色：复刻风默认值（按构建子系统 deck 源图取样） ----------
RED    = RGBColor(0xC8, 0x00, 0x0A)
INK    = RGBColor(0x1F, 0x1F, 0x1F)
TXT    = RGBColor(0x33, 0x33, 0x33)
NUMD   = RGBColor(0x33, 0x37, 0x3C)
ICN    = RGBColor(0x3D, 0x40, 0x45)
FOOT   = RGBColor(0x80, 0x80, 0x80)
PANEL  = RGBColor(0xF2, 0xF2, 0xF2)
CARD_B = RGBColor(0xE0, 0xE0, 0xE0)
SEPL   = RGBColor(0xC6, 0xC6, 0xC6)
PINK   = RGBColor(0xFC, 0xDE, 0xDD)
ACCENT = RED          # 图标点缀色、编号圆默认色

def roundcap(s):
    """线端、拐角改圆头，图标线条更接近源图。"""
    ln = s.line._get_or_add_ln()
    ln.set('cap', 'rnd')
    for t in ('a:round', 'a:bevel', 'a:miter'):
        for e in ln.findall(qn(t)): ln.remove(e)
    rnd = etree.SubElement(ln, qn('a:round'))
    # a:round 必须排在 headEnd / tailEnd 之前
    for t in ('a:headEnd', 'a:tailEnd'):
        e = ln.find(qn(t))
        if e is not None:
            ln.remove(rnd); e.addprevious(rnd); break
    return s

def pl(sh, pts, color=None, lw=1.0, close=False, fill=None, rc=True):
    """绝对坐标折线 / 多边形。"""
    ff = sh.build_freeform(X(pts[0][0]), Y(pts[0][1]))
    ff.add_line_segments([(X(a), Y(b)) for a, b in pts[1:]], close=close)
    s = _paint(ff.convert_to_shape(), fill, color, lw)
    if color is not None and rc: roundcap(s)
    return s

def seg(sh, x1, y1, x2, y2, color, lw=1.0):
    return roundcap(line(sh, x1, y1, x2, y2, color, lw))

def arc_pts(cx, cy, r, a0, a1, n=24, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / float(n))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / float(n)))) for i in range(n + 1)]

def cubic(p0, c1, c2, p3, n=30):
    out = []
    for i in range(n + 1):
        t = i / float(n); m = 1 - t
        out.append((m**3*p0[0] + 3*m*m*t*c1[0] + 3*m*t*t*c2[0] + t**3*p3[0],
                    m**3*p0[1] + 3*m*m*t*c1[1] + 3*m*t*t*c2[1] + t**3*p3[1]))
    return out

def tri_head(sh, tip, frm, color, L=14, Wd=15):
    """实心三角箭头：tip 为尖端，frm 为来向上的一点（决定方向）。"""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    bx, by = tip[0] - ux * L, tip[1] - uy * L
    px, py = -uy * Wd / 2, ux * Wd / 2
    return pl(sh, [tip, (bx + px, by + py), (bx - px, by - py)], None, 0, close=True, fill=color)

def curve_arrow(sh, p0, c1, c2, p3, color, lw=3.0, L=16, Wd=17):
    """任意方向的三次贝塞尔箭头。折线提前 L*0.6 收住，另画实心三角（QuickLook 不渲染 custGeom 的 line-end）。"""
    pts = cubic(p0, c1, c2, p3, 40)
    # 找到离尖端约 L 的点作为方向参考，并把线收在三角内部
    k = len(pts) - 1
    while k > 0 and math.hypot(pts[k][0] - p3[0], pts[k][1] - p3[1]) < L: k -= 1
    body = pts[:k + 1]
    pl(sh, body, color, lw)
    tri_head(sh, p3, pts[k], color, L, Wd)

def monotone(xs, ys, n=16):
    """Fritsch-Carlson 单调三次插值，折线图平滑但不过冲。"""
    m = len(xs)
    d = [(ys[i+1] - ys[i]) / (xs[i+1] - xs[i]) for i in range(m - 1)]
    t = [d[0]] + [0.0] * (m - 2) + [d[-1]]
    for i in range(1, m - 1):
        t[i] = 0.0 if d[i-1] * d[i] <= 0 else (d[i-1] + d[i]) / 2
    for i in range(m - 1):
        if d[i] == 0: t[i] = t[i+1] = 0; continue
        a, b = t[i] / d[i], t[i+1] / d[i]
        s = a * a + b * b
        if s > 9:
            k = 3 / math.sqrt(s); t[i] = k * a * d[i]; t[i+1] = k * b * d[i]
    out = []
    for i in range(m - 1):
        h = xs[i+1] - xs[i]
        for j in range(n + (1 if i == m - 2 else 0)):
            u = j / float(n)
            h00 = 2*u**3 - 3*u**2 + 1; h10 = u**3 - 2*u**2 + u
            h01 = -2*u**3 + 3*u**2;    h11 = u**3 - u**2
            out.append((xs[i] + u * h, h00*ys[i] + h10*h*t[i] + h01*ys[i+1] + h11*h*t[i+1]))
    return out

def rshape(sh, x, y, w, h, radii, fill=None, color=None, lw=0.75):
    """四角各自圆角的单个自由形状，radii = (左上, 右上, 右下, 左下)。

    用来代替「圆角矩形 + 方块压角」：QuickLook 把 roundRect 的填充渲染得比 rect 浅一档，两块拼接会露出色差。
    """
    tl, tr, br, bl = radii
    pts = []
    pts += arc_pts(x + tl, y + tl, tl, 180, 270, 8) if tl else [(x, y)]
    pts += arc_pts(x + w - tr, y + tr, tr, 270, 360, 8) if tr else [(x + w, y)]
    pts += arc_pts(x + w - br, y + h - br, br, 0, 90, 8) if br else [(x + w, y + h)]
    pts += arc_pts(x + bl, y + h - bl, bl, 90, 180, 8) if bl else [(x, y + h)]
    return pl(sh, pts, color, lw, close=True, fill=fill, rc=False)

# ---------- 原生表格 ----------
NO_STYLE = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"   # 无样式、无网格：底色和框线全部逐格显式写

def native_table(sh, x, y, col_w, row_h):
    """原生表格，列宽 / 行高按源图像素给。关掉内置样式，免得套上蓝色表头和隔行底纹。"""
    gf = sh.add_table(len(row_h), len(col_w), X(x), Y(y), W(sum(col_w)), H(sum(row_h)))
    tbl = gf.table
    tbl.first_row = False; tbl.horz_banding = False
    tbl._tbl.tblPr.find(qn('a:tableStyleId')).text = NO_STYLE
    for j, w in enumerate(col_w): tbl.columns[j].width = W(w)
    for i, h in enumerate(row_h): tbl.rows[i].height = H(h)
    return gf, tbl

def cell_border(cell, side, color=None, lw=0.6):
    """side 取 L/R/T/B。color=None 表示无线。ln* 必须排在 tcPr 的填充元素之前。"""
    tcPr = cell._tc.get_or_add_tcPr()
    tag = qn('a:ln' + side)
    for e in tcPr.findall(tag): tcPr.remove(e)
    ln = etree.Element(tag)
    if color is None:
        ln.set('w', '0'); etree.SubElement(ln, qn('a:noFill'))
    else:
        ln.set('w', str(int(Pt(lw)))); ln.set('cap', 'flat'); ln.set('cmpd', 'sng'); ln.set('algn', 'ctr')
        sf = etree.SubElement(ln, qn('a:solidFill'))
        etree.SubElement(sf, qn('a:srgbClr')).set('val', '%02X%02X%02X' % tuple(color))
        etree.SubElement(ln, qn('a:prstDash')).set('val', 'solid')
    order = ['L', 'R', 'T', 'B']
    idx = 0
    for o in order[:order.index(side)]:
        if tcPr.find(qn('a:ln' + o)) is not None: idx += 1
    tcPr.insert(idx, ln)

def table_endpara(tbl, size=8):
    """给每格每段补段末标记字号。空格子（含合并后隐藏的格）默认按 18pt 算行高，会把行撑高。"""
    for row in tbl.rows:
        for cell in row.cells:
            for p in cell.text_frame.paragraphs:
                e = p._p.get_or_add_endParaRPr()
                e.set('sz', str(int(size * 100))); e.set('lang', 'zh-CN'); e.set('noProof', '1')

def cell_set(cell, parts, align=PP_ALIGN.LEFT, fill=None, ml=0, mr=0):
    """单元格写入混排文本（parts 同 rich），垂直居中，上下边距清零以贴合源图行高。"""
    if fill is not None:
        cell.fill.solid(); cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left, cell.margin_right = X(ml), X(mr)
    cell.margin_top = cell.margin_bottom = Pt(0.5)
    tf = cell.text_frame
    p = tf.paragraphs[0]; p.alignment = align
    # 固定行距 = 字号 + 2pt：微软雅黑单倍行距约 1.32 倍字号，会把 22px 的源图行高撑开
    p.line_spacing = Pt(max(size for _, size, _, _ in parts) + 2)
    for t, size, bold, color in parts:
        r = p.add_run(); r.text = t; style_run(r, size, bold, color)
    return cell

def cell_lines(cell, lines, align=PP_ALIGN.LEFT, fill=None, ml=0, mr=0, spacing=None):
    """单元格写多段：lines = [[(text, size, bold, color), ...], ...]，每个内层列表一段。"""
    if fill is not None:
        cell.fill.solid(); cell.fill.fore_color.rgb = fill
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left, cell.margin_right = X(ml), X(mr)
    cell.margin_top = cell.margin_bottom = Pt(0.5)
    tf = cell.text_frame
    for i, parts in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = Pt(spacing or (max(sz for _, sz, _, _ in parts) + 4))
        for t, size, bold, color in parts:
            r = p.add_run(); r.text = t; style_run(r, size, bold, color)
    return cell

# ---------- 文本 ----------
def lines_box(sh, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, pitch=None):
    """多段混排：lines = [[(text, size, bold, color), ...], ...]，一行一段。

    pitch 为源图行距（像素），换成固定磅值行距，和源图逐行对齐。
    """
    box = sh.add_textbox(X(x), Y(y), W(w), H(h))
    tf = box.text_frame
    tf.word_wrap = False; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, parts in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if pitch: p.line_spacing = Pt(pt_of(pitch))
        for t, size, bold, color in parts:
            r = p.add_run(); r.text = t; style_run(r, size, bold, color)
    return box

def shape_text(s, text, size, bold=False, color=TXT, align=PP_ALIGN.CENTER):
    """把文字写进形状本身（圆圈编号、胶囊标签），选中形状即可改字。"""
    tf = s.text_frame
    tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text; style_run(r, size, bold, color)
    return s

def numc(sh, cx, cy, r, n, size, fill=RED):
    """红底编号圆。数字放独立文本框：小圆的内切文字区放不下一行，QuickLook 会把字压到下沿。"""
    oval(sh, cx - r, cy - r, 2 * r, 2 * r, fill, None)
    return label(sh, cx - 20, cy - 20, 40, 40, str(n), size, True, WHITE)

def pill(sh, x, y, w, h, text, size, fill, color=TXT, border=None, bold=False, lw=0.75, radius=4):
    return shape_text(rrect(sh, x, y, w, h, fill, border, lw, radius), text, size, bold, color)

# ---------- 几何 ----------
def shield_pts(x, y, w, h):
    # 上沿两角微收、下部圆弧收尖
    top = [(x + w*.5, y), (x + w, y + h*.16)]
    side_r = cubic((x + w, y + h*.16), (x + w, y + h*.62), (x + w*.78, y + h*.86), (x + w*.5, y + h), 14)
    side_l = cubic((x + w*.5, y + h), (x + w*.22, y + h*.86), (x, y + h*.62), (x, y + h*.16), 14)
    return top + side_r[1:] + side_l[1:]
