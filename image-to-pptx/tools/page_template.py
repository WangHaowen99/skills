# -*- coding: utf-8 -*-
"""单页模板。一页一个文件，复制改名成 p1.py / p2.py …

坐标全部写画布像素（复刻时就是源图像素），和图逐块对照。
下面把常用组件各调一次，数据都是示意值；组件清单见 SKILL.md「组件」一节和 components.py 文件头。

页型 A（图表 + 指标卡 | 时间轴 + 统计条 / 特性卡）整页用 overview_page，参数是各组件的参数字典：

    overview_page(sh, title=dict(...), left=dict(...), chart=dict(...), metrics=[dict(...)],
                  right=dict(..., inner=(x, y, w, h, 边框色)), timeline=dict(...), stat=dict(...),
                  section=dict(...), features=dict(...), footer_spec=dict(...))
"""
from components import *

CANVAS = (1672, 941)          # 源图像素尺寸，preview.py 会读它
# use_theme(STYLE)            # 按 ppt-deck 规范新做页面时打开：直角、#C7000A


def build(sh):
    page_title(sh, "主题：一句有观点的标题，数字和判断都在本页找得到依据")

    # ---- 左栏（主）：推导条 + 分组表格 ----
    panel(sh, 14, 64, 1012, 762, "左栏标题", 17, title_box=(38, 70, 600, 38),
          fill=T.soft_panel, radius=10, accent_bar=(26, 77, 5, 24))
    S9 = lambda t: [txt(t, 9.5)]
    step_chain(sh, 30, 112, [
        ("第一步", [("7", 30, True, T.red), (" 个问题", 14, True, T.red)], [S9("说明第一行"), S9("说明第二行")]),
        ("第二步", [("10", 30, True, T.red), (" 个 issue", 14, True, T.red)], [S9("说明第一行"), S9("说明第二行")]),
        ("第三步", [("1", 30, True, T.red), (" 个修复", 14, True, T.red)], [S9("说明第一行"), S9("说明第二行")]),
    ])
    n = lambda t: txt(t, 8.5)
    rows = [[[n("现象 %d" % i)], [n("业务表现 %d" % i)], [n("#%d" % (100 + i))], [[n("已提交")]]] for i in range(1, 6)]
    # 表格用原生表格：用户要能在 PowerPoint 里增删行、拖列宽
    grouped_table(sh, 30, 362, [104, 420, 260, 90, 106], [32] + [40] * 5,
                  ["类别", "现象", "业务中的表现", "编号", "进展"], rows,
                  [(1, 3, [[("分组一", 10, True, T.ink)]], WHITE, 13),
                   (4, 5, [[("分组二", 10, True, T.red)]], RGBColor(0xFD, 0xF1, 0xF0), 13)],
                  header_border=RGBColor(0xD9, 0xDD, 0xE1), col_align=[L, L, C, C],
                  col_margin=[(12, 8), (12, 8), (0, 0), (0, 0)], spacing=11, highlight={4: T.pink_bg})

    # ---- 右栏（次）：架构层 + 编号要点 ----
    panel(sh, 1040, 64, 618, 762, "右栏标题", 13.5, title_box=(1056, 70, 590, 38), fill=T.soft_panel, radius=10)
    LY = dict(lab_w=74, name_size=10, pitch=20)
    arch_layer(sh, 1056, 112, 586, 60, "业务\n平台层", **LY)
    module_cell(sh, 1144, 120, 150, 44, "模块 A", icon=(ic_chat, 1170, 22, T.red), text_cx=1230)
    arch_layer(sh, 1056, 188, 586, 60, "协议层", fill=T.pink_bg, border=T.pink_border,
               lab=RGBColor(0xF8, 0xE4, 0xE4), **LY)
    arch_layer(sh, 1056, 272, 586, 60, "引擎\n实现层", **LY)
    rrect(sh, 1056, 360, 586, 300, WHITE, RGBColor(0xE6, 0xE9, 0xEC), 0.75, radius=8)
    tag_title(sh, 1072, 372, "下一步", "小标题")
    for i in range(3):
        y = 418 + i * 80
        numbered_item(sh, i + 1, (1086, y + 14), "要点 %d" % (i + 1), (1108, y, 300, 28),
                      [[txt("说明文字，一到两行", 10)]], (1108, y + 30, 520, 40),
                      sep=(1108, 1626, y + 72) if i < 2 else None)

    # ---- 箭头、连线最后画，否则会被后画的面板盖住 ----
    bi_arrow(sh, 1349, 173, 187)
    fanout(sh, 249, [(1209, 271), (1390, 271), (1571, 271)], label_text="按项目切换",
           label_box=(1235, 249, 130, 22), label_size=8.5, label_bg=None)

    flow_band(sh, 14, 836, 1644, 38, "闭环：", ["步骤一", "步骤二", "步骤三", "步骤四"])
    footer(sh, ["数据来源：……，统计至 ……"], size=8.2, box=(17, 882, 1640, 46), pitch=21)
