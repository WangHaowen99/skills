#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""体检生成的 pptx：字体槽位、拼写检查开关、预置几何。

    python3 verify.py out.pptx [--font 微软雅黑]

退出码非 0 表示有不合规项。这是交付前的完成判据，不要靠肉眼。
"""
import sys, re, zipfile, collections
from lxml import etree

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
# 这几个预置几何 macOS QuickLook / 预览不渲染，命中说明该改手绘 poly()
RISKY = {"lightningBolt", "gear6", "gear9", "cloud", "sun", "moon", "smileyFace", "heart"}

def main(path, font="微软雅黑"):
    z = zipfile.ZipFile(path)
    names = sorted((n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
                   key=lambda n: int(re.search(r'\d+', n.split('/')[-1]).group()))
    tot = badf = badp = 0
    langs, fonts, geo = set(), set(), collections.Counter()
    bad_samples = []
    for n in names:
        raw = z.read(n); s = etree.fromstring(raw)
        for r in s.findall('.//' + A + 'r'):
            tot += 1
            rPr = r.find(A + 'rPr'); t = r.find(A + 't')
            txt = (t.text or '')[:18] if t is not None else ''
            if rPr is None:
                badf += 4; bad_samples.append((n, txt, 'no rPr')); continue
            for k in ('latin', 'ea', 'cs', 'sym'):
                e = rPr.find(A + k)
                if e is None or e.get('typeface') != font:
                    badf += 1
                    if len(bad_samples) < 6: bad_samples.append((n, txt, k))
            if rPr.get('noProof') != '1':
                badp += 1
                if len(bad_samples) < 6: bad_samples.append((n, txt, 'noProof'))
            langs.add(rPr.get('lang'))
        fonts |= set(re.findall(r'typeface="([^"]+)"', raw.decode('utf8')))
        geo.update(re.findall(r'<a:prstGeom prst="([a-zA-Z0-9]+)"', raw.decode('utf8')))
    risky = {g: c for g, c in geo.items() if g in RISKY}
    print("页数 %d ｜ run %d ｜ 非%s槽位 %d ｜ 缺 noProof %d ｜ lang %s"
          % (len(names), tot, font, badf, badp, langs or {'-'}))
    print("字体集合:", fonts)
    print("预置几何:", dict(geo))
    ok = True
    if badf or badp:
        ok = False
        print("!! 不合规样本:", bad_samples)
    if risky:
        ok = False
        print("!! 这些预置几何 QuickLook 不渲染，改手绘 poly():", risky)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    f = sys.argv[sys.argv.index("--font") + 1] if "--font" in sys.argv else "微软雅黑"
    sys.exit(main(sys.argv[1], f))
