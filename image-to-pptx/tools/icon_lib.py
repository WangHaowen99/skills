# -*- coding: utf-8 -*-
"""矢量图标库：全部用基础形状 / freeform 拼，**绝不编组**。

python-pptx 生成的 custGeom 一旦放进 p:grpSp，macOS 的 QuickLook / 预览 / Keynote
会把它整个吞掉，渲染出来只剩圆和直线——XML 合规、PowerPoint 正常，所以只有在
访达里预览才会发现。代价是形状数多，编辑性不受影响。

每个图标签名统一为 ic_xxx(sh, cx, cy, size, color, lw=...)，cx/cy 是中心点。
"""
import math
from deck_kit import *

def _o(sh,x,y,w,h,c,lw=1.2): return oval(sh,x,y,w,h,None,c,lw)
def _r(sh,x,y,w,h,c,lw=1.2,rad=2): return rrect(sh,x,y,w,h,None,c,lw,rad)
def _l(sh,x1,y1,x2,y2,c,lw=1.2): return line(sh,x1,y1,x2,y2,c,lw)
def _arc(cx,cy,r,a0,a1,n=18):
    return [(cx+r*math.cos(math.radians(a0+(a1-a0)*i/float(n))),
             cy+r*math.sin(math.radians(a0+(a1-a0)*i/float(n)))) for i in range(n+1)]

# ---------- 第 1 页 ----------
def ic_funnel(sh, cx, cy, s, c, lw=1.4):
    poly(sh, cx-s*.44, cy-s*.40, s*.88, s*.44, [(0,0),(1,0),(.62,1),(.38,1)], None, c, lw)
    _l(sh, cx-s*.06, cy+s*.04, cx-s*.06, cy+s*.40, c, lw)
    _l(sh, cx+s*.06, cy+s*.04, cx+s*.06, cy+s*.40, c, lw)
    _l(sh, cx-s*.06, cy+s*.40, cx+s*.06, cy+s*.40, c, lw)

def ic_xcircle(sh, cx, cy, s, c, lw=1.5):
    _o(sh, cx-s*.46, cy-s*.46, s*.92, s*.92, c, lw)
    _l(sh, cx-s*.17, cy-s*.17, cx+s*.17, cy+s*.17, c, lw)
    _l(sh, cx+s*.17, cy-s*.17, cx-s*.17, cy+s*.17, c, lw)

def ic_search(sh, cx, cy, s, c, lw=1.6):
    _o(sh, cx-s*.44, cy-s*.44, s*.62, s*.62, c, lw)
    _l(sh, cx+s*.14, cy+s*.14, cx+s*.42, cy+s*.42, c, lw)

def ic_robot(sh, cx, cy, s, c, lw=1.3):
    _l(sh, cx, cy-s*.50, cx, cy-s*.36, c, lw)
    oval(sh, cx-s*.05, cy-s*.58, s*.10, s*.10, c, None)
    _r(sh, cx-s*.38, cy-s*.36, s*.76, s*.62, c, lw, s*.14)
    for dx in (-.17, .09):
        oval(sh, cx+s*dx, cy-s*.20, s*.09, s*.09, c, None)
    _l(sh, cx-s*.16, cy+s*.06, cx+s*.16, cy+s*.06, c, lw)
    _l(sh, cx-s*.48, cy-s*.18, cx-s*.48, cy+s*.06, c, lw)
    _l(sh, cx+s*.48, cy-s*.18, cx+s*.48, cy+s*.06, c, lw)

def ic_db(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.40, cy-s*.48, s*.80, s*.26, c, lw)
    for dy in (-.35, -.10):
        _l(sh, cx-s*.40, cy+s*dy, cx-s*.40, cy+s*(dy+.27), c, lw)
        _l(sh, cx+s*.40, cy+s*dy, cx+s*.40, cy+s*(dy+.27), c, lw)
        _o(sh, cx-s*.40, cy+s*(dy+.14), s*.80, s*.26, c, lw)

def ic_person(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.20, cy-s*.46, s*.40, s*.40, c, lw)
    poly(sh, cx-s*.38, cy+s*.04, s*.76, s*.42,
         [(0,1),(0,.42),(.17,.04),(.83,.04),(1,.42),(1,1)], None, c, lw)

def ic_cube(sh, cx, cy, s, c, lw=1.3):
    poly(sh, cx-s*.42, cy-s*.46, s*.84, s*.92,
         [(.5,0),(1,.26),(1,.74),(.5,1),(0,.74),(0,.26)], None, c, lw)
    _l(sh, cx-s*.42, cy-s*.22, cx, cy, c, lw)
    _l(sh, cx+s*.42, cy-s*.22, cx, cy, c, lw)
    _l(sh, cx, cy, cx, cy+s*.46, c, lw)

def ic_file(sh, cx, cy, s, c, lw=1.2):
    poly(sh, cx-s*.34, cy-s*.46, s*.68, s*.92,
         [(0,0),(.66,0),(1,.24),(1,1),(0,1)], None, c, lw)
    _l(sh, cx+s*.00, cy-s*.46, cx+s*.00, cy-s*.24, c, lw)
    _l(sh, cx+s*.00, cy-s*.24, cx+s*.34, cy-s*.24, c, lw)
    for dy in (.02, .18):
        _l(sh, cx-s*.18, cy+s*dy, cx+s*.16, cy+s*dy, c, lw*.85)

def ic_bulb(sh, cx, cy, s, c, lw=1.4):
    _o(sh, cx-s*.30, cy-s*.48, s*.60, s*.60, c, lw)
    _l(sh, cx-s*.14, cy+s*.16, cx+s*.14, cy+s*.16, c, lw)
    _l(sh, cx-s*.10, cy+s*.30, cx+s*.10, cy+s*.30, c, lw)
    _l(sh, cx-s*.12, cy+s*.12, cx-s*.12, cy+s*.20, c, lw)
    _l(sh, cx+s*.12, cy+s*.12, cx+s*.12, cy+s*.20, c, lw)

# ---------- 第 2 页 ----------
def ic_target(sh, cx, cy, s, c, lw=1.5):
    _o(sh, cx-s*.46, cy-s*.46, s*.92, s*.92, c, lw)
    _o(sh, cx-s*.24, cy-s*.24, s*.48, s*.48, c, lw)
    oval(sh, cx-s*.08, cy-s*.08, s*.16, s*.16, c, None)
    _l(sh, cx+s*.10, cy-s*.10, cx+s*.46, cy-s*.46, c, lw)

def ic_qbubble(sh, cx, cy, s, c, lw=1.4):
    _r(sh, cx-s*.44, cy-s*.44, s*.88, s*.70, c, lw, s*.16)
    poly(sh, cx-s*.24, cy+s*.24, s*.28, s*.24, [(0,0),(.9,0),(.15,1)], None, c, lw)
    label(sh, cx-s*.5, cy-s*.46, s, s*.66, "?", pt_of(s)*0.62, True, c)

def ic_hier(sh, cx, cy, s, c, lw=1.3):
    _r(sh, cx-s*.16, cy-s*.48, s*.32, s*.26, c, lw, s*.05)
    for dx in (-.48, -.16, .16):
        _r(sh, cx+s*dx, cy+s*.22, s*.32, s*.26, c, lw, s*.05)
    _l(sh, cx, cy-s*.22, cx, cy+s*.02, c, lw)
    _l(sh, cx-s*.32, cy+s*.02, cx+s*.32, cy+s*.02, c, lw)
    for dx in (-.32, 0, .32):
        _l(sh, cx+s*dx, cy+s*.02, cx+s*dx, cy+s*.22, c, lw)

GEAR_PTS = [(0.5+r*math.cos(math.radians(a)), 0.5+r*math.sin(math.radians(a)))
            for i in range(8) for a, r in ((45.*i-11,.48),(45.*i+11,.48),(45.*i+19,.34),(45.*i+26,.34))]
def ic_gear(sh, cx, cy, s, c, lw=1.4, fill=None):
    poly(sh, cx-s*.50, cy-s*.50, s, s, GEAR_PTS, fill, None if fill else c, 0 if fill else lw)
    if fill is None:
        _o(sh, cx-s*.15, cy-s*.15, s*.30, s*.30, c, lw)

def ic_gear_solid(sh, cx, cy, s, c, hole=WHITE):
    poly(sh, cx-s*.50, cy-s*.50, s, s, GEAR_PTS, c, None, 0)
    oval(sh, cx-s*.15, cy-s*.15, s*.30, s*.30, hole, None)

def ic_doc(sh, cx, cy, s, c, lw=1.3):
    poly(sh, cx-s*.32, cy-s*.46, s*.64, s*.92,
         [(0,0),(.66,0),(1,.24),(1,1),(0,1)], None, c, lw)
    for dy in (-.10, .06, .22):
        _l(sh, cx-s*.16, cy+s*dy, cx+s*.14, cy+s*dy, c, lw*.85)

def ic_people(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.40, cy-s*.40, s*.30, s*.30, c, lw)
    _o(sh, cx+s*.08, cy-s*.36, s*.26, s*.26, c, lw)
    poly(sh, cx-s*.48, cy-s*.02, s*.46, s*.34, [(0,1),(0,.4),(.2,.05),(.8,.05),(1,.4),(1,1)], None, c, lw)
    poly(sh, cx-s*.00, cy+s*.02, s*.44, s*.30, [(0,1),(0,.4),(.2,.05),(.8,.05),(1,.4),(1,1)], None, c, lw)

def ic_play(sh, cx, cy, s, c, lw=1.4):
    _o(sh, cx-s*.46, cy-s*.46, s*.92, s*.92, c, lw)
    poly(sh, cx-s*.14, cy-s*.22, s*.40, s*.44, [(0,0),(1,.5),(0,1)], c, None, 0)

def ic_check(sh, cx, cy, s, c, lw=1.4):
    _o(sh, cx-s*.46, cy-s*.46, s*.92, s*.92, c, lw)
    poly(sh, cx-s*.24, cy-s*.18, s*.48, s*.40,
         [(.02,.46),(.20,.28),(.40,.52),(.80,.06),(.98,.24),(.40,.90)], c, None, 0)

def ic_checkbox(sh, cx, cy, s, c, lw=1.5):
    _r(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw, s*.14)
    poly(sh, cx-s*.24, cy-s*.18, s*.48, s*.40,
         [(.02,.46),(.20,.28),(.40,.52),(.80,.06),(.98,.24),(.40,.90)], c, None, 0)

def ic_overlap(sh, cx, cy, s, c, lw=1.5):
    _o(sh, cx-s*.46, cy-s*.34, s*.50, s*.50, c, lw)
    _o(sh, cx-s*.04, cy-s*.34, s*.50, s*.50, c, lw)
    _o(sh, cx-s*.25, cy-s*.52, s*.50, s*.50, c, lw)

def ic_dashring(sh, cx, cy, s, c, lw=2.0):
    o = oval(sh, cx-s*.46, cy-s*.46, s*.92, s*.92, None, c, lw)
    ln = o.line._get_or_add_ln()
    d = etree.SubElement(ln, qn('a:prstDash')); d.set('val', 'dash')
    return o

# ---------- 第 3~5 页补充 ----------
def ic_pencil(sh, cx, cy, s, c, lw=1.3):
    _r(sh, cx-s*.42, cy-s*.42, s*.84, s*.84, c, lw, s*.12)
    poly(sh, cx-s*.06, cy-s*.30, s*.42, s*.42, [(.72,0),(1,.28),(.28,1),(0,1),(0,.72)], None, c, lw)

def ic_ban(sh, cx, cy, s, c, lw=1.5):
    _o(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw)
    _l(sh, cx-s*.20, cy-s*.20, cx+s*.20, cy+s*.20, c, lw)

def ic_shield(sh, cx, cy, s, c, lw=1.3, fill=None):
    poly(sh, cx-s*.36, cy-s*.44, s*.72, s*.88,
         [(.5,0),(1,.20),(1,.56),(.5,1),(0,.56),(0,.20)], fill, c if fill is None else None, lw)

def ic_info(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw)
    oval(sh, cx-s*.05, cy-s*.24, s*.10, s*.10, c, None)
    _l(sh, cx, cy-s*.06, cx, cy+s*.24, c, lw*1.2)

def ic_link(sh, cx, cy, s, c, lw=1.4):
    shape(sh, MSO_SHAPE.ROUNDED_RECTANGLE, cx-s*.44, cy-s*.14, s*.46, s*.28, None, c, lw, rot=-32)
    shape(sh, MSO_SHAPE.ROUNDED_RECTANGLE, cx-s*.02, cy-s*.14, s*.46, s*.28, None, c, lw, rot=-32)

def ic_book(sh, cx, cy, s, c, lw=1.3):
    _r(sh, cx-s*.44, cy-s*.34, s*.42, s*.68, c, lw, s*.06)
    _r(sh, cx+s*.02, cy-s*.34, s*.42, s*.68, c, lw, s*.06)
    _l(sh, cx, cy-s*.34, cx, cy+s*.34, c, lw)

def ic_table(sh, cx, cy, s, c, lw=1.2):
    _r(sh, cx-s*.42, cy-s*.38, s*.84, s*.76, c, lw, s*.06)
    _l(sh, cx-s*.42, cy-s*.14, cx+s*.42, cy-s*.14, c, lw)
    _l(sh, cx-s*.42, cy+s*.10, cx+s*.42, cy+s*.10, c, lw)
    _l(sh, cx-s*.12, cy-s*.38, cx-s*.12, cy+s*.38, c, lw)

def ic_md(sh, cx, cy, s, c, lw=1.2):
    poly(sh, cx-s*.32, cy-s*.46, s*.64, s*.92,
         [(0,0),(.66,0),(1,.24),(1,1),(0,1)], None, c, lw)
    _r(sh, cx-s*.22, cy+s*.06, s*.44, s*.24, c, lw*.9, s*.05)

def ic_scales(sh, cx, cy, s, c, lw=1.3):
    _l(sh, cx, cy-s*.40, cx, cy+s*.34, c, lw)
    _l(sh, cx-s*.40, cy-s*.26, cx+s*.40, cy-s*.26, c, lw)
    _l(sh, cx-s*.20, cy+s*.34, cx+s*.20, cy+s*.34, c, lw)
    for dx in (-.40, .40):
        poly(sh, cx+s*dx-s*.18, cy-s*.12, s*.36, s*.24, [(0,0),(1,0),(.74,1),(.26,1)], None, c, lw)

def ic_ruler(sh, cx, cy, s, c, lw=1.2):
    shape(sh, MSO_SHAPE.RECTANGLE, cx-s*.44, cy-s*.16, s*.88, s*.32, None, c, lw, rot=-35)
    for d in (-.22, 0, .22):
        _l(sh, cx+s*d+s*.06, cy+s*d*0.7-s*.10, cx+s*d-s*.02, cy+s*d*0.7+s*.02, c, lw*.8)

def ic_code(sh, cx, cy, s, c, lw=1.3):
    _r(sh, cx-s*.44, cy-s*.36, s*.88, s*.72, c, lw, s*.10)
    _l(sh, cx-s*.20, cy-s*.12, cx-s*.30, cy, c, lw)
    _l(sh, cx-s*.30, cy, cx-s*.20, cy+s*.12, c, lw)
    _l(sh, cx+s*.20, cy-s*.12, cx+s*.30, cy, c, lw)
    _l(sh, cx+s*.30, cy, cx+s*.20, cy+s*.12, c, lw)

def ic_list(sh, cx, cy, s, c, lw=1.2):
    _r(sh, cx-s*.42, cy-s*.42, s*.84, s*.84, c, lw, s*.10)
    for dy in (-.20, 0, .20):
        oval(sh, cx-s*.26, cy+s*dy-s*.04, s*.08, s*.08, c, None)
        _l(sh, cx-s*.10, cy+s*dy, cx+s*.26, cy+s*dy, c, lw*.85)

def ic_key(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.44, cy-s*.22, s*.40, s*.40, c, lw)
    _l(sh, cx-s*.04, cy, cx+s*.44, cy-s*.30, c, lw)
    _l(sh, cx+s*.30, cy-s*.20, cx+s*.36, cy-s*.06, c, lw)

# ---------- 第 6~8 页补充 ----------
def ic_in(sh, cx, cy, s, c, lw=1.4):
    _r(sh, cx-s*.42, cy-s*.42, s*.84, s*.84, c, lw, s*.14)
    _l(sh, cx-s*.26, cy, cx+s*.18, cy, c, lw)
    poly(sh, cx+s*.10, cy-s*.14, s*.20, s*.28, [(0,0),(1,.5),(0,1)], c, None, 0)

def ic_out(sh, cx, cy, s, c, lw=1.4):
    _r(sh, cx-s*.42, cy-s*.42, s*.84, s*.84, c, lw, s*.14)
    _l(sh, cx-s*.18, cy, cx+s*.26, cy, c, lw)
    poly(sh, cx+s*.18, cy-s*.14, s*.20, s*.28, [(0,0),(1,.5),(0,1)], c, None, 0)

def ic_cross(sh, cx, cy, s, c, lw=1.6):
    _o(sh, cx-s*.34, cy-s*.34, s*.68, s*.68, c, lw)
    for a in (0, 90, 180, 270):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        _l(sh, cx+dx*s*.34, cy+dy*s*.34, cx+dx*s*.52, cy+dy*s*.52, c, lw)

def ic_bars(sh, cx, cy, s, c, lw=1.2):
    _r(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw, s*.10)
    for dx, h in ((-.24, .22), (-.04, .40), (.16, .30)):
        rect(sh, cx+s*dx, cy+s*.28-s*h, s*.12, s*h, c, None)

def ic_monitor(sh, cx, cy, s, c, lw=1.3):
    _r(sh, cx-s*.46, cy-s*.38, s*.92, s*.62, c, lw, s*.08)
    _l(sh, cx, cy+s*.24, cx, cy+s*.38, c, lw)
    _l(sh, cx-s*.20, cy+s*.38, cx+s*.20, cy+s*.38, c, lw)
    _l(sh, cx-s*.30, cy-s*.20, cx-s*.06, cy-s*.20, c, lw*.9)
    _l(sh, cx-s*.30, cy-s*.04, cx-s*.14, cy-s*.04, c, lw*.9)

def ic_flower(sh, cx, cy, s, c, lw=1.3):
    for a in range(0, 360, 60):
        r = math.radians(a)
        _o(sh, cx+math.cos(r)*s*.16-s*.20, cy+math.sin(r)*s*.16-s*.20, s*.40, s*.40, c, lw)

def ic_share(sh, cx, cy, s, c, lw=1.4):
    _o(sh, cx+s*.14, cy-s*.44, s*.28, s*.28, c, lw)
    _o(sh, cx+s*.14, cy+s*.16, s*.28, s*.28, c, lw)
    _o(sh, cx-s*.42, cy-s*.14, s*.28, s*.28, c, lw)
    _l(sh, cx-s*.16, cy-s*.06, cx+s*.16, cy-s*.26, c, lw)
    _l(sh, cx-s*.16, cy+s*.02, cx+s*.16, cy+s*.24, c, lw)

def ic_git(sh, cx, cy, s, c, lw=1.4):
    _o(sh, cx-s*.44, cy-s*.14, s*.26, s*.26, c, lw)
    _o(sh, cx+s*.18, cy-s*.44, s*.26, s*.26, c, lw)
    _o(sh, cx+s*.18, cy+s*.16, s*.26, s*.26, c, lw)
    _l(sh, cx-s*.18, cy, cx+s*.18, cy-s*.30, c, lw)
    _l(sh, cx-s*.18, cy, cx+s*.18, cy+s*.30, c, lw)

def ic_js(sh, cx, cy, s, c, lw=1.4):
    _r(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw, s*.14)
    _l(sh, cx-s*.06, cy-s*.18, cx-s*.06, cy+s*.10, c, lw)
    _l(sh, cx-s*.06, cy+s*.10, cx-s*.24, cy+s*.20, c, lw)
    _l(sh, cx+s*.26, cy-s*.16, cx+s*.08, cy-s*.16, c, lw)
    _l(sh, cx+s*.08, cy-s*.16, cx+s*.08, cy+s*.02, c, lw)
    _l(sh, cx+s*.08, cy+s*.02, cx+s*.26, cy+s*.02, c, lw)
    _l(sh, cx+s*.26, cy+s*.02, cx+s*.26, cy+s*.20, c, lw)
    _l(sh, cx+s*.26, cy+s*.20, cx+s*.08, cy+s*.20, c, lw)

def ic_brain(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.44, cy-s*.40, s*.44, s*.80, c, lw)
    _o(sh, cx-s*.00, cy-s*.40, s*.44, s*.80, c, lw)
    _l(sh, cx, cy-s*.30, cx, cy+s*.34, c, lw)
    _l(sh, cx-s*.22, cy-s*.10, cx-s*.02, cy-s*.10, c, lw*.85)
    _l(sh, cx+s*.02, cy+s*.10, cx+s*.22, cy+s*.10, c, lw*.85)

def ic_excel(sh, cx, cy, s, c, lw=1.2):
    _r(sh, cx-s*.40, cy-s*.44, s*.80, s*.88, c, lw, s*.08)
    _l(sh, cx-s*.10, cy-s*.44, cx-s*.10, cy+s*.44, c, lw)
    _l(sh, cx-s*.02, cy-s*.20, cx+s*.28, cy+s*.20, c, lw)
    _l(sh, cx+s*.28, cy-s*.20, cx-s*.02, cy+s*.20, c, lw)

def ic_slider(sh, cx, cy, s, c, lw=1.4):
    for i, dy in enumerate((-.26, 0, .26)):
        _l(sh, cx-s*.42, cy+s*dy, cx+s*.42, cy+s*dy, c, lw)
        px = (-.14, .18, -.02)[i]
        oval(sh, cx+s*px-s*.09, cy+s*dy-s*.09, s*.18, s*.18, c, None)

def ic_trophy(sh, cx, cy, s, c, lw=1.3):
    poly(sh, cx-s*.26, cy-s*.42, s*.52, s*.52, [(0,0),(1,0),(.82,1),(.18,1)], None, c, lw)
    _l(sh, cx-s*.26, cy-s*.32, cx-s*.44, cy-s*.10, c, lw)
    _l(sh, cx+s*.26, cy-s*.32, cx+s*.44, cy-s*.10, c, lw)
    _l(sh, cx, cy+s*.10, cx, cy+s*.28, c, lw)
    _l(sh, cx-s*.20, cy+s*.40, cx+s*.20, cy+s*.40, c, lw)

def ic_folder(sh, cx, cy, s, c, lw=1.2):
    _r(sh, cx-s*.44, cy-s*.24, s*.88, s*.58, c, lw, s*.08)
    poly(sh, cx-s*.44, cy-s*.40, s*.44, s*.18, [(0,1),(0,.1),(.14,0),(.72,0),(.88,1)], None, c, lw)

def ic_flowdoc(sh, cx, cy, s, c, lw=1.3, accent=None):
    a = accent or c
    poly(sh, cx-s*.42, cy-s*.50, s*.84, s*1.0, [(0,0),(.72,0),(1,.20),(1,1),(0,1)], None, c, lw)
    rect(sh, cx-s*.28, cy-s*.26, s*.20, s*.14, a, None)
    rect(sh, cx-s*.06, cy-s*.10, s*.22, s*.16, a, None)
    poly(sh, cx-s*.30, cy+s*.04, s*.22, s*.22, [(.5,0),(1,.5),(.5,1),(0,.5)], a, None, 0)
    poly(sh, cx+s*.06, cy-s*.34, s*.20, s*.20, [(.5,0),(1,.5),(.5,1),(0,.5)], None, a, lw)
    _l(sh, cx-s*.18, cy-s*.20, cx-s*.06, cy-s*.04, c, lw*.8)
    _l(sh, cx-s*.19, cy-s*.02, cx-s*.19, cy+s*.06, c, lw*.8)

# ---------- 第 9~10 页补充 ----------
def ic_snow(sh, cx, cy, s, c, lw=1.4):
    for a in (0, 60, 120):
        r = math.radians(a)
        dx, dy = math.cos(r)*s*.44, math.sin(r)*s*.44
        _l(sh, cx-dx, cy-dy, cx+dx, cy+dy, c, lw)
    for a in (0, 60, 120, 180, 240, 300):
        r = math.radians(a)
        bx, by = cx+math.cos(r)*s*.44, cy+math.sin(r)*s*.44
        for d in (-32, 32):
            r2 = math.radians(a + 180 + d)
            _l(sh, bx, by, bx+math.cos(r2)*s*.16, by+math.sin(r2)*s*.16, c, lw*.8)

def ic_zip(sh, cx, cy, s, c, lw=1.2):
    poly(sh, cx-s*.32, cy-s*.46, s*.64, s*.92, [(0,0),(.66,0),(1,.24),(1,1),(0,1)], None, c, lw)
    for i in range(4):
        rect(sh, cx-s*.06, cy-s*.34+i*s*.15, s*.12, s*.08, c, None)
    _r(sh, cx-s*.10, cy+s*.16, s*.20, s*.20, c, lw)

def ic_globe(sh, cx, cy, s, c, lw=1.3):
    _o(sh, cx-s*.44, cy-s*.44, s*.88, s*.88, c, lw)
    _o(sh, cx-s*.18, cy-s*.44, s*.36, s*.88, c, lw)
    _l(sh, cx-s*.44, cy, cx+s*.44, cy, c, lw)
    _l(sh, cx-s*.38, cy-s*.22, cx+s*.38, cy-s*.22, c, lw*.85)
    _l(sh, cx-s*.38, cy+s*.22, cx+s*.38, cy+s*.22, c, lw*.85)


# ======================================================================
# 构建子系统 deck 沉淀（2026-10）：线性图标 + 一处红色点缀
#
# 签名同上：ic_xxx(sh, cx, cy, s, c, ...)；c 是主体色，accent 是点缀色（默认 ACCENT 红）。
# 后 11 个由源图逐个描出：函数里保留设计稿坐标，按 (设计中心, 设计尺寸) 等比换算，
# 所以 s 取设计尺寸、cx/cy 取设计中心时，输出和源图描摹完全一致。
# ======================================================================
from draw_kit import pl, seg, arc_pts, cubic, shield_pts, ACCENT, PANEL

def _xf(cx, cy, s, CX, CY, S):
    """设计稿坐标 → 实际坐标。返回 (点换算, 长度换算)。"""
    k = s / float(S)
    return (lambda x, y: (cx + (x - CX) * k, cy + (y - CY) * k)), (lambda l: l * k)

def ic_chat_solid(sh, cx, cy, s, c, dot=WHITE):
    """实心对话气泡 + 三个白点。"""
    rrect(sh, cx - s*.48, cy - s*.40, s*.96, s*.66, c, None, radius=s*.30)
    pl(sh, [(cx - s*.22, cy + s*.20), (cx - s*.30, cy + s*.44), (cx - s*.02, cy + s*.22)], None, 0, True, c)
    for dx in (-.22, 0, .22):
        oval(sh, cx + s*dx - s*.07, cy - s*.14, s*.14, s*.14, dot, None)

def ic_chat(sh, cx, cy, s, c, lw=1.6):
    """描边方形对话气泡（尾巴在左下）。"""
    x0, x1, y0, y1 = cx - s*.46, cx + s*.46, cy - s*.40, cy + s*.22
    pl(sh, [(x0 + s*.20, y1), (x0 + s*.12, cy + s*.44), (x0 + s*.38, y1),
            (x1, y1), (x1, y0), (x0, y0), (x0, y1), (x0 + s*.20, y1)], c, lw)

def ic_screen(sh, cx, cy, s, c, lw=1.6):
    rrect(sh, cx - s*.48, cy - s*.40, s*.96, s*.62, None, c, lw, radius=s*.06)
    seg(sh, cx, cy + s*.22, cx, cy + s*.40, c, lw)
    seg(sh, cx - s*.24, cy + s*.42, cx + s*.24, cy + s*.42, c, lw)

def ic_bullets(sh, cx, cy, s, c, lw=1.6):
    for dy in (-.30, 0, .30):
        seg(sh, cx - s*.46, cy + s*dy, cx - s*.34, cy + s*dy, c, lw)
        seg(sh, cx - s*.16, cy + s*dy, cx + s*.46, cy + s*dy, c, lw)

def ic_shield_ck(sh, cx, cy, s, c, lw=1.6, ck=None):
    ic_shield2(sh, cx, cy, s, c, lw)
    pl(sh, [(cx - s*.17, cy + s*.01), (cx - s*.03, cy + s*.15), (cx + s*.20, cy - s*.12)], ck or c, lw)

def ic_shield2(sh, cx, cy, s, c, lw=1.6, fill=None):
    return pl(sh, shield_pts(cx - s*.38, cy - s*.46, s*.76, s*.92), c, lw, close=True, fill=fill)

def ic_swap(sh, cx, cy, s, c, lw=1.8):
    seg(sh, cx - s*.42, cy - s*.16, cx + s*.40, cy - s*.16, c, lw)
    pl(sh, [(cx + s*.22, cy - s*.36), (cx + s*.44, cy - s*.16), (cx + s*.22, cy + s*.04)], c, lw)
    seg(sh, cx + s*.42, cy + s*.20, cx - s*.40, cy + s*.20, c, lw)
    pl(sh, [(cx - s*.22, cy + s*.00), (cx - s*.44, cy + s*.20), (cx - s*.22, cy + s*.40)], c, lw)

def ic_term(sh, cx, cy, s, c, lw=1.5):
    rrect(sh, cx - s*.48, cy - s*.38, s*.96, s*.76, None, c, lw, radius=s*.06)
    pl(sh, [(cx - s*.26, cy - s*.14), (cx - s*.08, cy + s*.02), (cx - s*.26, cy + s*.18)], c, lw)
    seg(sh, cx + s*.02, cy + s*.18, cx + s*.24, cy + s*.18, c, lw)

def ic_group3(sh, cx, cy, s, c, lw=1.5):
    for dx in (-.30, .30):
        oval(sh, cx + s*dx - s*.11, cy - s*.36, s*.22, s*.22, None, c, lw)
        pl(sh, arc_pts(cx + s*dx, cy + s*.30, s*.19, 180, 360, 14, ry=s*.32), c, lw)
    oval(sh, cx - s*.14, cy - s*.42, s*.28, s*.28, WHITE, c, lw)
    pts = arc_pts(cx, cy + s*.40, s*.26, 180, 360, 18, ry=s*.40)
    pl(sh, pts + [pts[0]], c, lw, fill=WHITE)

def ic_dbase(sh, cx, cy, s, c, lw=1.5):
    w, eh = s*.76, s*.24
    x0 = cx - w/2
    oval(sh, x0, cy - s*.46, w, eh, None, c, lw)
    for dy in (-.11, .12, .34):
        pl(sh, arc_pts(cx, cy + s*dy, w/2, 0, 180, 16, ry=eh/2), c, lw)
    seg(sh, x0, cy - s*.34, x0, cy + s*.34, c, lw)
    seg(sh, x0 + w, cy - s*.34, x0 + w, cy + s*.34, c, lw)

def ic_docf(sh, cx, cy, s, c, lw=1.5, n=3):
    """折角文档 + n 条横线。"""
    x0, y0, w, h = cx - s*.34, cy - s*.46, s*.68, s*.92
    pl(sh, [(x0 + w*.62, y0), (x0, y0), (x0, y0 + h), (x0 + w, y0 + h), (x0 + w, y0 + h*.28),
            (x0 + w*.62, y0), (x0 + w*.62, y0 + h*.28), (x0 + w, y0 + h*.28)], c, lw)
    for i in range(n):
        yy = y0 + h*(.48 + i*.16)
        seg(sh, x0 + w*.24, yy, x0 + w*(.76 if i < n - 1 else .60), yy, c, lw*.9)

def ic_box3d(sh, cx, cy, s, c, lw=1.6):
    pl(sh, [(cx, cy - s*.46), (cx + s*.42, cy - s*.24), (cx + s*.42, cy + s*.24), (cx, cy + s*.46),
            (cx - s*.42, cy + s*.24), (cx - s*.42, cy - s*.24), (cx, cy - s*.46)], c, lw)
    pl(sh, [(cx - s*.42, cy - s*.24), (cx, cy - s*.02), (cx + s*.42, cy - s*.24)], c, lw)
    seg(sh, cx, cy - s*.02, cx, cy + s*.46, c, lw)

def ic_gear2(sh, cx, cy, s, c, lw=1.6):
    pts = []
    for i in range(8):
        for a, r in ((45.*i - 12, .48), (45.*i + 12, .48), (45.*i + 20, .35), (45.*i + 25, .35)):
            pts.append((cx + s*r*math.cos(math.radians(a)), cy + s*r*math.sin(math.radians(a))))
    pl(sh, pts + [pts[0]], c, lw)
    oval(sh, cx - s*.15, cy - s*.15, s*.30, s*.30, None, c, lw)

def ic_bulbq(sh, cx, cy, s, c, q=None, lw=1.6):
    """灯泡 + 红色问号。"""
    pts = arc_pts(cx, cy - s*.12, s*.30, 140, 400, 28)
    pl(sh, [(cx - s*.14, cy + s*.22)] + pts + [(cx + s*.14, cy + s*.22), (cx - s*.14, cy + s*.22)], c, lw)
    seg(sh, cx - s*.14, cy + s*.32, cx + s*.14, cy + s*.32, c, lw)
    seg(sh, cx - s*.09, cy + s*.42, cx + s*.09, cy + s*.42, c, lw)
    q = q or ACCENT
    pl(sh, arc_pts(cx, cy - s*.18, s*.09, 190, 400, 12) + [(cx, cy - s*.02)], q, lw*1.1)
    oval(sh, cx - s*.035, cy + s*.06, s*.07, s*.07, q, None)


def ic_bars_solid(sh, cx, cy, s, c):
    """三根实心递增柱（业务验证）。设计尺寸 32.5。"""
    P, L = _xf(cx, cy, s, 1319.75, 148.75, 32.5)
    for x, top in ((1303.5, 153), (1315, 143), (1326.5, 132.5)):
        rect(sh, *P(x, top), L(9.5), L(165 - top), c, None)

def ic_org_tree(sh, cx, cy, s, c, accent=None, lw=2.25):
    """分工树：红色主节点 + 三个子节点。设计尺寸 88（高）。"""
    P, L = _xf(cx, cy, s, 175, 626, 88)
    seg(sh, *P(175, 612), *P(175, 645), c, lw)
    pl(sh, [P(132, 645), P(132, 636), P(175, 620), P(218, 636), P(218, 645)], c, lw)
    for dx in (-43.5, 0, 43.5):
        oval(sh, *P(175 + dx - 12.5, 645), L(25), L(25), None, c, lw)
    oval(sh, *P(160, 582.5), L(30), L(30), accent or ACCENT, None)

def ic_doc_shield(sh, cx, cy, s, c, accent=None, bg=PANEL, lw=2.4):
    """文档 + 盾牌对勾 + 回退箭头（改动先校验再生效）。bg 填卡片底色，用来挖出盾牌外的留白。设计尺寸 90。"""
    P, L = _xf(cx, cy, s, 527.5, 625, 90)
    a = accent or ACCENT
    rrect(sh, *P(460, 580), L(77), L(90), None, c, lw, radius=L(7))
    for y, x2 in ((602, 505), (620, 499), (638, 499)):
        seg(sh, *P(474, y), *P(x2, y), c, lw)
    pl(sh, shield_pts(*P(501, 596), L(66), L(74)), None, 0, close=True, fill=bg)
    pl(sh, shield_pts(*P(507, 602), L(54), L(61)), c, lw, close=True, fill=bg)
    pl(sh, [P(522, 630), P(531, 639), P(546, 621)], a, 2.6)
    pl(sh, [P(573, 668)] + [P(x, y) for x, y in arc_pts(583, 657, 11, 90, -90, 16)] + [P(571, 646)], c, lw)
    pl(sh, [P(577, 640), P(571, 646), P(577, 652)], c, lw)

def ic_expert_chat(sh, cx, cy, s, c, accent=None, lw=2.4):
    """人像 + 红色对话气泡（专家把关）。设计尺寸 89。"""
    P, L = _xf(cx, cy, s, 845, 624.5, 89)
    a = accent or ACCENT
    oval(sh, *P(798, 596), L(38), L(38), None, c, lw)
    pts = [P(x, y) for x, y in arc_pts(817, 669, 33, 180, 360, 20, ry=28)]
    pl(sh, pts + [pts[0]], c, lw)
    rrect(sh, *P(849, 580), L(57), L(40), WHITE, a, 2.4, radius=L(8))
    pl(sh, [P(858, 619), P(859, 632), P(871, 619)], a, 2.4, fill=WHITE)
    seg(sh, *P(856, 618.5), *P(874, 618.5), WHITE, 2.6)
    for x in (865, 877.5, 890):
        oval(sh, *P(x - 3.5, 596.5), L(7), L(7), a, None)

def ic_cycle_search(sh, cx, cy, s, c, accent=None, lw=2.4):
    """四段循环箭头 + 红色放大镜（测试—诊断—改进闭环）。设计尺寸 104（环直径）。"""
    P, L = _xf(cx, cy, s, 1165, 626, 104)
    a = accent or ACCENT
    R0 = 52
    for head in (-75, 15, 105, 195):
        pl(sh, [P(x, y) for x, y in arc_pts(1165, 626, R0, head - 68, head, 16)], c, lw)
        r = math.radians(head)
        tx, ty = 1165 + R0 * math.cos(r), 626 + R0 * math.sin(r)
        ux, uy = -math.sin(r), math.cos(r)          # 顺时针切向
        nx, ny = math.cos(r), math.sin(r)
        k = 9
        pl(sh, [P(tx - ux * k + nx * k, ty - uy * k + ny * k), P(tx, ty),
                P(tx - ux * k - nx * k, ty - uy * k - ny * k)], c, lw)
    oval(sh, *P(1143, 603), L(39), L(39), None, a, 2.8)
    seg(sh, *P(1177, 637), *P(1188, 649), a, 3.2)

def ic_toggle_docs(sh, cx, cy, s, c, accent=None, lw=2.4):
    """两份文档中间一个红色开关（双引擎切换）。设计尺寸 70（高）。"""
    P, L = _xf(cx, cy, s, 1498.5, 622, 70)
    for x0, xl in ((1407, 1422), (1532, 1546)):
        rrect(sh, *P(x0, 587), L(58), L(70), None, c, 2.6, radius=L(4))
        for y, ln in ((605, 30), (622, 30), (638, 22)):
            seg(sh, *P(xl, y), *P(xl + ln, y), c, lw)
    rrect(sh, *P(1471, 607), L(54), L(30), accent or ACCENT, None, radius=L(15))
    oval(sh, *P(1500, 612), L(20), L(20), WHITE, None)

def ic_signpost(sh, cx, cy, s, c, accent=None, lw=2.2):
    """路标：红色指向牌 + 描边反向牌（AI 带路）。设计尺寸 66（高）。"""
    P, L = _xf(cx, cy, s, 185, 627, 66)
    pl(sh, [P(191, 600), P(219, 600), P(228.5, 609), P(219, 618), P(191, 618)], None, 0, True, accent or ACCENT)
    pl(sh, [P(181, 626), P(150, 626), P(142, 635), P(150, 644), P(181, 644)], c, lw, True, WHITE)
    rect(sh, *P(181, 594.5), L(10), L(65.5), WHITE, c, lw)

def ic_eye(sh, cx, cy, s, c, accent=None, lw=2.4):
    """眼睛，红色瞳孔（看得清）。设计尺寸 86（宽）。"""
    P, L = _xf(cx, cy, s, 510, 627.5, 86)
    top = cubic(P(467, 627.5), P(486, 597), P(534, 597), P(553, 627.5), 20)
    bot = cubic(P(553, 627.5), P(534, 658), P(486, 658), P(467, 627.5), 20)
    pl(sh, top + bot[1:], c, lw, True, WHITE)
    oval(sh, *P(499.5, 617.5), L(20), L(20), accent or ACCENT, None)
    oval(sh, *P(506, 624), L(7), L(7), WHITE, None)

def ic_puzzle(sh, cx, cy, s, c, accent=None, lw=2.4):
    """拼图：描边主块 + 红色补块（增量建模）。设计尺寸 82（宽）。"""
    P, L = _xf(cx, cy, s, 839.5, 627, 82)
    a = accent or ACCENT
    pts = [(812.5, 609), (832.9, 609)]
    pts += arc_pts(838.3, 603, 8, 131.5, 408.5, 20)
    pts += [(865, 609), (865, 659), (843.6, 659)]
    pts += arc_pts(838.3, 653, 8, 48.5, -228.5, 20)
    pts += [(812.5, 659), (812.5, 639.3)]
    pts += arc_pts(806.5, 634, 8, 41.5, 318.5, 20)
    pl(sh, [P(x, y) for x, y in pts], c, lw, True, WHITE)
    oval(sh, *P(847.5, 627), L(13.5), L(13.5), a, None)
    rrect(sh, *P(859.5, 618), L(21), L(35.5), a, None, radius=L(2))

def ic_replay(sh, cx, cy, s, c, accent=None, lw=2.4):
    """顺时针重播环 + 红色播放三角（断点续跑）。设计尺寸 64（环直径）。"""
    P, L = _xf(cx, cy, s, 1165.5, 627, 64)
    R0 = 32
    pl(sh, [P(x, y) for x, y in arc_pts(1165.5, 627, R0, 5, 338, 40)], c, lw)
    r = math.radians(338)
    tx, ty = 1165.5 + R0 * math.cos(r), 627 + R0 * math.sin(r)
    ux, uy = -math.sin(r), math.cos(r)
    nx, ny = math.cos(r), math.sin(r)
    k = 9
    pl(sh, [P(tx - ux * k + nx * k, ty - uy * k + ny * k), P(tx, ty),
            P(tx - ux * k - nx * k, ty - uy * k - ny * k)], c, lw)
    pl(sh, [P(1157.5, 615.5), P(1179, 628), P(1157.5, 640.5)], None, 0, True, accent or ACCENT)

def ic_chat_dots(sh, cx, cy, s, c, accent=None, lw=2.4):
    """方角对话气泡 + 三个红点（说人话）。设计尺寸 74（宽）。"""
    P, L = _xf(cx, cy, s, 1493.75, 627.5, 74)
    x0, x1, y0, y1, rr = 1456.7, 1530.8, 596, 643.5, 7
    pts = arc_pts(x0 + rr, y0 + rr, rr, 180, 270, 6) + arc_pts(x1 - rr, y0 + rr, rr, 270, 360, 6)
    pts += arc_pts(x1 - rr, y1 - rr, rr, 0, 90, 6)
    pts += [(1493.7, y1), (1474, 659), (1474, y1)]
    pts += arc_pts(x0 + rr, y1 - rr, rr, 90, 180, 6)
    pl(sh, [P(x, y) for x, y in pts], c, lw, True, WHITE)
    for x in (1475.4, 1493, 1510.5):
        oval(sh, *P(x - 4.7, 615.3), L(9.4), L(9.4), accent or ACCENT, None)
