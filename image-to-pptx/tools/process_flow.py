# -*- coding: utf-8 -*-
"""C29 工序流程图（人机分工 / 三泳道纵向流程）：写规格 → 自动排版 → 自动体检。

    from process_flow import *        # 含 components 的全部名字
    use_theme(LIGHT)
    h, report = process_flow(sh, x, y, w, spec)

中间一条主干讲工序先后，左泳道写「人在哪一步做什么判断」，右泳道写「系统在这一步提供什么能力」。
一眼能看出谁干活、谁把关——适合「专家只在关口点头」「人机协同」「两方分工」类论点。

元素：
  主干  投入梯形、带编号的工序框（重点工序浅红底）、产物节点（双线框）、产出梯形、通过 / 不过分支
  回路  返工回路（红虚线，从关口工序退回指定工序，带说明）
  泳道  泳道头（图标 + 名称）、左侧确认点（红色 ✓ + 两行文字）、右侧能力（粗体名 + 灰色说明）、虚线引线
  其他  主干标题 + 副标题、底部技术底座条 + 说明

spec：
  title / subtitle      主干上方的标题和一句副标题
  lanes                 dict(left=(名称, 图标), right=(名称, 图标))
  input / output        (第一行, 第二行)：投入 / 产出梯形
  steps                 [Step(...) 或 Product(...)]，Step 自动编号 ①②③…
  loop                  dict(src=关口工序序号, dst=退回工序序号, out="不过", note="说明\\n第二行")，序号从 1 起
  pass_label            关口到产出那条线上的字，默认「通过」
  base                  dict(text=技术底座, notes=[说明行])
"""
import math
from components import *
from components import _r, _c, _bd, _ln
from arch_diagram import _fit, _tw, _dash, _arrow, F_FILL, F_BORDER, CELL_B

STEP_H, PROD_H, TRAP_H, GAP = 40, 54, 46, 24
LANE_HEAD_H, TITLE_H = 52, 54
MAX_STEPS = 8
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"


def Check(text, sub=None):
    """左泳道确认点（人做的判断）。"""
    return dict(text=text, sub=sub)

def Cap(text, sub=None):
    """右泳道能力（系统提供的支撑）。"""
    return dict(text=text, sub=sub)

def Step(title, *, hot=False, left=None, right=None):
    return dict(kind="step", title=title, hot=hot, left=left, right=right)

def Product(title, sub=None, *, left=None, right=None):
    """产物节点：工序中间产出的阶段成果（如「知识包 v1.0」），双线框。"""
    return dict(kind="product", title=title, sub=sub, hot=False, left=left, right=right)


def _trap(sh, cx, y, w_top, w_bot, h, lines, size=10.5):
    pl(sh, [(cx - w_top / 2.0, y), (cx + w_top / 2.0, y), (cx + w_bot / 2.0, y + h), (cx - w_bot / 2.0, y + h)],
       _bd(None, G_MID), 1.0, close=True, fill=WHITE, rc=False)
    lines_box(sh, cx - w_top / 2.0, y, w_top, h, [[(t, size, True, T.ink)] for t in lines], C, pitch=19)

def _check_mark(sh, x, cy):
    pl(sh, [(x, cy), (x + 4.5, cy + 4.5), (x + 12, cy - 5)], T.red, 1.75)


def process_flow(sh, x, y, w, spec, *, left_w=None, right_w=None, spine_w=None, draw=True):
    """按规格画工序流程图。返回 (高度, 体检结果)。"""
    qa = []
    steps = spec['steps']
    has_loop = bool(spec.get('loop'))
    lw_ = _c(left_w, w * 0.25)
    rw_ = _c(right_w, w * 0.27)
    sw = _c(spine_w, min(w * 0.34, 260))
    chan = 46 if has_loop else 20                       # 左泳道和主干之间：回路通道
    lx0, lx1 = x, x + lw_
    sx0 = lx1 + chan
    sx1 = sx0 + sw
    rx0, rx1 = x + w - rw_, x + w
    if sx1 > rx0 - 24:
        qa.append(("error", "宽度不够：主干与右泳道重叠，请加宽或减小 spine_w"))
    cx = (sx0 + sx1) / 2.0

    # 纵向位置
    cy = y
    title_y = cy
    if spec.get('title'):
        cy += TITLE_H
    lane_y = cy
    in_y = cy + (LANE_HEAD_H - TRAP_H) / 2.0
    cy += LANE_HEAD_H + GAP
    rows = []
    for st in steps:
        hh = PROD_H if st['kind'] == "product" else STEP_H
        rows.append((cy, hh))
        cy += hh + GAP
    out_y = cy + 4
    cy = out_y + TRAP_H
    base = spec.get('base')
    if base:
        cy += 22
        base_y = cy
        cy += 34
        if base.get('notes'):
            cy += 8 + 20 * len(base['notes'])
    height = cy - y
    if not draw:
        return height, qa

    # 标题
    if spec.get('title'):
        label(sh, x, title_y, w, 26, spec['title'], 12, True, T.ink)
        if spec.get('subtitle'):
            label(sh, x, title_y + 26, w, 20, spec['subtitle'], 9, False, G_TEXT)

    # 泳道头
    lanes = spec.get('lanes', {})
    for side, (lx_a, lx_b) in (("left", (lx0, lx1)), ("right", (rx0, rx1))):
        if side not in lanes:
            continue
        name, icon = lanes[side]
        mx = (lx_a + lx_b) / 2.0
        if icon:
            icon(sh, mx, lane_y + 15, 28, G_MID)
        label(sh, mx - 60, lane_y + 32, 120, 20, name, 10, True, G_TEXT)

    # 投入梯形
    if spec.get('input'):
        _trap(sh, cx, in_y, sw * 0.62, sw * 0.42, TRAP_H, list(spec['input']))
        _arrow(sh, cx, in_y + TRAP_H + 1, rows[0][0] - 1, _ln(None, G_MID), 1.25)

    # 工序与产物
    n_step = 0
    centers = []
    for i, (st, (ry, rh)) in enumerate(zip(steps, rows)):
        cyy = ry + rh / 2.0
        centers.append(cyy)
        if st['kind'] == "product":
            rect(sh, sx0 - 4, ry - 4, sw + 8, rh + 8, None, T.red, 1.25)
            rect(sh, sx0, ry, sw, rh, WHITE, G_LINE, 0.75)
            lines_ = [[(st['title'], 11.5, True, T.red)]]
            if st.get('sub'):
                sub, _ = _fit(st['sub'], 8.5, sw - 16, False, qa, "产物说明")
                lines_.append([(sub[0], 8.5, False, G_TEXT)])
            lines_box(sh, sx0, ry, sw, rh, lines_, C, pitch=20)
        else:
            n_step += 1
            if n_step > MAX_STEPS:
                qa.append(("warn", "工序 %d 道，建议不超过 %d" % (n_step, MAX_STEPS)))
            fill, bc = (F_FILL, F_BORDER) if st['hot'] else (WHITE, _bd(None, G_MID))
            rect(sh, sx0, ry, sw, rh, fill, bc, 1.0)
            t = CIRCLED[n_step - 1] + " " + st['title'] if n_step <= len(CIRCLED) else st['title']
            got, size = _fit(t, 10.5, sw - 16, False, qa, "工序")
            label(sh, sx0, ry, sw, rh, got[0], size, True, T.ink)
            st['_n'] = n_step
        if i < len(steps) - 1:
            _arrow(sh, cx, ry + rh + (5 if st['kind'] == "product" else 1), rows[i + 1][0] - (5 if steps[i + 1]['kind'] == "product" else 1),
                   _ln(None, G_MID), 1.25)

        # 左泳道：确认点
        if st.get('left'):
            ck = st['left']
            tx = lx0 + 20
            avail = lw_ - 34
            a, _ = _fit(ck['text'], 10, avail, False, qa, "确认点")
            rows_ = [[(a[0], 10, False, T.ink)]]
            if ck.get('sub'):
                b, _ = _fit(ck['sub'], 9, avail, False, qa, "确认点说明")
                rows_.append([(b[0], 9, False, T.txt)])
            _check_mark(sh, lx0 + 2, cyy - (9 if ck.get('sub') else 0))
            lines_box(sh, tx, cyy - 22, avail + 6, 44, rows_, L, pitch=20)
            text_end = tx + max(_tw(r[0][0], r[0][1]) for r in rows_) + 4
            end_x = sx0 - (chan - 14) if has_loop else sx0
            if end_x - text_end > 12:
                c = line(sh, text_end + 4, cyy, end_x, cyy, _ln(None, G_LINE), 0.75)
                _dash(c, "sysDot")
            oval(sh, end_x - 3, cyy - 3, 6, 6, _ln(None, G_MID), None)
        # 右泳道：系统能力
        if st.get('right'):
            cp = st['right']
            avail = rw_ - 8
            a, _ = _fit(cp['text'], 10, avail, False, qa, "能力")
            rows_ = [[(a[0], 10, True, T.ink)]]
            if cp.get('sub'):
                b, _ = _fit(cp['sub'], 9, avail, False, qa, "能力说明")
                rows_.append([(b[0], 9, False, G_TEXT)])
            lines_box(sh, rx0 + 8, cyy - 22, avail, 44, rows_, L, pitch=20)
            start_x = sx1 + (4 if st['kind'] == "product" else 0)
            c = line(sh, start_x, cyy, rx0 - 2, cyy, _ln(None, G_LINE), 0.75)
            _dash(c, "sysDot")
            oval(sh, rx0 - 5, cyy - 3, 6, 6, _ln(None, G_MID), None)

    # 产出梯形 + 通过
    last_y, last_h = rows[-1]
    if spec.get('output'):
        _arrow(sh, cx, last_y + last_h + 1, out_y - 1, _ln(None, G_MID), 1.25)
        _trap(sh, cx, out_y, sw * 0.42, sw * 0.62, TRAP_H, list(spec['output']))
        pt = spec.get('pass_label', "通过")
        if pt:
            label(sh, cx + 8, last_y + last_h + 2, 80, 20, pt, 9, False, T.txt, align=L)

    # 返工回路：最后画
    if has_loop:
        lp = spec['loop']
        idx = {}
        for k, st in enumerate(steps):
            if st.get('_n'):
                idx[st['_n']] = k
        if lp['src'] not in idx or lp['dst'] not in idx:
            qa.append(("error", "回路的工序序号不存在：%s → %s" % (lp['src'], lp['dst'])))
        else:
            ys = centers[idx[lp['src']]]
            yd = centers[idx[lp['dst']]]
            vx = sx0 - chan / 2.0 - 4
            col = T.red
            for p, q in (((sx0, ys + 6), (vx, ys + 6)), ((vx, ys + 6), (vx, yd))):
                c = line(sh, p[0], p[1], q[0], q[1], col, 1.5)
                _dash(c)
            c = line(sh, vx, yd, sx0 - 1, yd, col, 1.5, arrow=True)
            _dash(c)
            if lp.get('out'):
                label(sh, vx + 4, ys + 8, chan, 20, lp['out'], 9, False, T.txt, align=L)
            if lp.get('note'):
                nl = lp['note'].split("\n")
                nw = max(_tw(t, 9) for t in nl) + 8
                nh = 18 * len(nl) + 6
                # 放在两道工序之间的空档（引线都在工序中线上），取最靠回路中段的一个
                i0, i1 = sorted((idx[lp['dst']], idx[lp['src']]))
                mids = [(centers[k] + centers[k + 1]) / 2.0 for k in range(i0, i1)]
                my = min(mids, key=lambda v: abs(v - (ys + yd) / 2.0)) if mids else (ys + yd) / 2.0
                ncx = min(vx, sx0 - 8 - nw / 2.0)              # 右边缘不越过主干，免得压到产物框
                rect(sh, ncx - nw / 2.0, my - nh / 2.0, nw, nh, _c(spec.get('bg'), T.soft_panel), None)
                lines_box(sh, ncx - nw / 2.0, my - nh / 2.0, nw, nh, [[(t, 9, True, T.red)] for t in nl], C, pitch=18)
                if nw > chan + lw_ * 0.6:
                    qa.append(("warn", "回路说明较宽，可能压到左泳道文字"))

    # 底座
    if base:
        rect(sh, x + 20, base_y, w - 40, 34, T.lab, None)
        label(sh, x + 20, base_y, w - 40, 34, base['text'], 10.5, True, T.ink)
        for k, t in enumerate(base.get('notes', [])):
            label(sh, x, base_y + 42 + 20 * k, w, 20, t, 9.5 if k == 0 else 9, k == 0, T.ink if k == 0 else G_TEXT)

    return height, dict(issues=qa, steps=n_step, products=sum(1 for s in steps if s['kind'] == "product"),
                        checks=sum(1 for s in steps if s.get('left')), caps=sum(1 for s in steps if s.get('right')))
