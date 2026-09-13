# -*- coding: utf-8 -*-
"""单页模板。一页一个文件，复制改名成 p1.py / p2.py …

坐标全部写源图像素，和图逐块对照。
"""
from deck_kit import *
from icon_lib import *

CANVAS = (1673, 951)          # 源图像素尺寸，preview.py 会读它

def build(sh):
    label(sh, 40, 20, 1560, 46, "这里是标题", 22, True, INK, align=PP_ALIGN.LEFT)

    # 面板：先底后头，再用一个方块压平头部下方圆角
    rrect(sh, 40, 100, 400, 300, WHITE, BLUE_B, 1.2, radius=10)
    rrect(sh, 40, 100, 400, 45, BLUE, None, radius=10)
    rect(sh, 40, 122.5, 400, 22.5, BLUE, None)
    label(sh, 40, 100, 400, 45, "面板标题", 13, True, WHITE)

    # 正文：宽度按 wpx() 估，留 10% 给回落字体
    label(sh, 60, 170, 360, 30, "一行正文", 11, False, BODY, align=PP_ALIGN.LEFT)

    # 图标一律不编组
    ic_target(sh, 80, 240, 28, BLUE)

    # 面板之间的箭头最后画，否则会被后画的面板盖住
    line(sh, 450, 250, 520, 250, BLUE, 1.5, arrow=True)
