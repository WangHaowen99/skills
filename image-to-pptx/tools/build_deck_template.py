# -*- coding: utf-8 -*-
"""整本 deck 的入口。复制到工作目录，按页数增减。

    python3 build_deck.py
"""
import sys, os
TOOLS = os.environ.get("IMG2PPTX_TOOLS") or os.path.expanduser(
    "~/.claude/skills/image-to-pptx/tools")   # 装在别处时用 IMG2PPTX_TOOLS 指过去
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_kit import *
import p1, p2

PAGES = [p1, p2]
OUT = "deck.pptx"

canvas(*PAGES[0].CANVAS)
prs = new_deck()
for m in PAGES:
    m.build(add_slide(prs))
print("saved:", save(prs, OUT))
print("形状数:", [len(s.shapes) for s in prs.slides])
