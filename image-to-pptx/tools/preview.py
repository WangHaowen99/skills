#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某一页单独构建出来渲染成 PNG。

qlmanage 只渲染 pptx 的第一页，多页 deck 要看第 N 页必须单独构建。

    python3 preview.py p3                    # 渲染 p3.py 整页
    python3 preview.py p3 --crop 1240,180,1660,760   # 只截源图坐标下的这块
    python3 preview.py p3 p5 p7              # 一次多页

页模块约定：定义 build(sh)，并用 CANVAS 声明源图尺寸，见 page_template.py。
"""
import sys, os, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.getcwd()); sys.path.insert(0, HERE)
import deck_kit as K

def render(modname, crop=None, outdir="_preview"):
    mod = __import__(modname)
    if hasattr(mod, "CANVAS"):
        K.canvas(*mod.CANVAS)
    prs = K.new_deck()
    # 约定 build(sh)；模块置 TAKES_PRS=True 时改传 prs。
    # 不用 try/except 猜签名——那会把 build 内部真正的 TypeError 一起吞掉。
    if getattr(mod, "TAKES_PRS", False):
        mod.build(prs)
    else:
        mod.build(K.add_slide(prs))
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "_%s.pptx" % modname)
    K.save(prs, tmp)
    subprocess.run(["qlmanage", "-t", "-s", "1673", "-o", outdir, tmp],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    png = os.path.join(outdir, os.path.basename(tmp) + ".png")
    final = os.path.join(outdir, "%s.png" % modname)
    if os.path.exists(png): shutil.move(png, final)
    os.remove(tmp)
    if crop and os.path.exists(final):
        from PIL import Image
        im = Image.open(final).convert("RGB")
        sx, sy = im.width / K._C["w"], im.height / K._C["h"]
        x0, y0, x1, y1 = crop
        b = im.crop((int(x0*sx), int(y0*sy), int(x1*sx), int(y1*sy)))
        b = b.resize((int(b.width*2), int(b.height*2)), Image.LANCZOS)
        final = os.path.join(outdir, "%s_crop.png" % modname)
        b.save(final)
    print(final)
    return final

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    crop = None
    if "--crop" in sys.argv:
        crop = tuple(float(v) for v in sys.argv[sys.argv.index("--crop") + 1].split(","))
    if not args:
        print(__doc__); sys.exit(1)
    for m in args:
        render(m.replace(".py", ""), crop)
