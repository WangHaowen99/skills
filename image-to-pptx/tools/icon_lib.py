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
