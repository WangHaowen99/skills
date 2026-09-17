#!/usr/bin/env python3
"""给录制帧叠加：聚光高亮 + 标注气泡 + 底部字幕。

坐标一律用 0~1 的相对值，因为录制帧在 1600x900 和 2400x1644 两种分辨率之间变过，
写死像素会在换分辨率时整体错位。
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def _rgb(text, fallback):
    """接受 #2a78d6 或 42,120,214 两种写法。"""
    if not text:
        return fallback
    text = text.strip().lstrip('#')
    if ',' in text:
        return tuple(int(v) for v in text.split(',')[:3])
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def _lift(rgb, amount=48):
    """亮一档：外圈辉光和气泡描边用，在压暗的底子上仍然跳得出来。"""
    return tuple(min(255, v + amount) for v in rgb)


# 高亮与标注的主色。默认是一支中性蓝；和界面同色系会更协调，用 DEMO_VIDEO_ACCENT 换。
ACCENT = _rgb(os.environ.get('DEMO_VIDEO_ACCENT'), (42, 120, 214))
ACCENT_SOFT = _lift(ACCENT)
NOTE_BG = (24, 30, 40)
DIM_ALPHA = 168                  # 非重点区域压暗程度
SUB_BG = (12, 16, 22, 214)

# 字体按候选顺序找第一个存在的：环境变量 → macOS → 常见 Linux 中文字体。
# 找不到就明确报错——落到 PIL 默认位图字体的话，中文会整片变成方块，
# 而且是在成片渲染到一半时才显形，比启动就失败难查得多。
FONT_CANDIDATES_MAIN = [
    os.environ.get('DEMO_VIDEO_FONT'),
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Medium.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
]
FONT_CANDIDATES_SUB = [
    os.environ.get('DEMO_VIDEO_FONT_SUB'),
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
]


def _pick(candidates, label):
    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise SystemExit(
        f'找不到{label}字体。装一个中文字体，或用 DEMO_VIDEO_FONT / DEMO_VIDEO_FONT_SUB 指定路径。\n'
        f'试过：{[c for c in candidates if c]}')


FONT_MAIN = _pick(FONT_CANDIDATES_MAIN, '正文')
FONT_SUB = _pick(FONT_CANDIDATES_SUB, '字幕')


def font(path, size):
    return ImageFont.truetype(path, size)


HL_PAD_X = 0.012                 # 高亮框相对画面宽度的外扩
HL_PAD_Y = 0.016                 # 纵向外扩给得多一点，元素一般比较扁


def _px(rect, size, pad=True):
    """量到的包围盒贴着元素边缘，框上去显得局促；统一往外放一圈再画。"""
    w, h = size
    x, y, rw, rh = rect
    px = HL_PAD_X * w if pad else 0
    py = HL_PAD_Y * h if pad else 0
    return [
        int(max(0, x * w - px)),
        int(max(0, y * h - py)),
        int(min(w, (x + rw) * w + px)),
        int(min(h, (y + rh) * h + py)),
    ]


TRAILING_PUNCT = '。，、；：！？）】》」”’·—,.;:!?)]}'


LEADING_PUNCT = '（(【「《“‘'


def _wrap(draw, text, fnt, max_width):
    """按字断行。收尾标点不甩到行首，开引号开括号不留在行尾——中文字幕里两种都很难看。"""
    lines, line = [], ''
    for ch in text:
        if ch == '\n':
            lines.append(line)
            line = ''
            continue
        probe = line + ch
        if draw.textlength(probe, font=fnt) <= max_width:
            line = probe
        elif ch in TRAILING_PUNCT and line:
            line += ch          # 宁可略微超宽，也不把标点甩到行首
        elif line and line[-1] in LEADING_PUNCT:
            lines.append(line[:-1])   # 开括号跟着后面的字一起换行
            line = line[-1] + ch
        else:
            lines.append(line)
            line = ch
    if line:
        lines.append(line)
    return lines


def _balance(draw, lines, fnt):
    """两行时如果第二行过短，把第一行末尾挪一些下去，视觉上更稳。"""
    if len(lines) != 2:
        return lines
    first, second = lines
    while len(second) < len(first) - 4 and len(first) > 6:
        first, second = first[:-1], first[-1] + second
    return [first, second]


REDACT_BLUR = 0.022              # 模糊半径相对画面短边，够把文字糊成完全读不出


def _redact(base, rects):
    """把指定区域糊掉。

    演示环境里混着真实工单号和客户名，这些不能出现在汇报视频里。
    先像素化再高斯模糊：单用模糊时，笔画粗的汉字放大了还能猜出来。
    """
    if not rects:
        return base
    size = base.size
    radius = max(6, int(min(size) * REDACT_BLUR))
    out = base.copy()
    for rect in rects:
        box = _px(rect, size, pad=False)
        if box[2] <= box[0] or box[3] <= box[1]:
            continue
        patch = out.crop(box)
        small = patch.resize((max(1, patch.width // 24), max(1, patch.height // 24)), Image.BILINEAR)
        patch = small.resize(patch.size, Image.NEAREST).filter(ImageFilter.GaussianBlur(radius))
        out.paste(patch, box)
    return out


def _spotlight(base, rects):
    """压暗全图，只把高亮矩形按原亮度还原——观众视线自然被带到该看的地方。"""
    if not rects:
        return base
    size = base.size
    mask = Image.new('L', size, DIM_ALPHA)
    md = ImageDraw.Draw(mask)
    radius = int(min(size) * 0.012)
    for rect in rects:
        box = _px(rect, size)
        md.rounded_rectangle(box, radius=radius, fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(int(min(size) * 0.006)))
    dim = Image.new('RGB', size, (6, 10, 16))
    return Image.composite(dim, base, mask)


def _glow_border(layer, box, radius, width, color):
    draw = ImageDraw.Draw(layer)
    for step in range(6, 0, -1):
        alpha = int(16 + (6 - step) * 9)
        pad = step * 3
        draw.rounded_rectangle(
            [box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad],
            radius=radius + pad, outline=(*color, alpha), width=3,
        )
    draw.rounded_rectangle(box, radius=radius, outline=(*color, 255), width=width)


def _note(layer, size, anchor, text, point_to=None, align='left', attach_box=None):
    """标注气泡：深底白字 + 投影，带一条指向高亮区的引线。"""
    draw = ImageDraw.Draw(layer)
    fnt = font(FONT_MAIN, int(size[1] * 0.0255))
    pad_x, pad_y = int(size[0] * 0.011), int(size[1] * 0.011)
    max_w = int(size[0] * 0.30)
    lines = _wrap(draw, text, fnt, max_w)
    line_h = int(fnt.size * 1.42)
    box_w = int(max(draw.textlength(l, font=fnt) for l in lines)) + pad_x * 2
    box_h = line_h * len(lines) + pad_y * 2 - int(line_h - fnt.size)
    ax, ay = int(anchor[0] * size[0]), int(anchor[1] * size[1])
    if align == 'right':
        ax -= box_w
    box = [ax, ay, ax + box_w, ay + box_h]

    target = None
    cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
    if attach_box:
        # 吸附到高亮框边界上离气泡最近的点，避免端点压在被强调的文字上
        target = (min(max(cx, attach_box[0]), attach_box[2]),
                  min(max(cy, attach_box[1]), attach_box[3]))
        if attach_box[0] < target[0] < attach_box[2] and attach_box[1] < target[1] < attach_box[3]:
            target = (target[0], attach_box[3] if cy > attach_box[3] else attach_box[1])
    elif point_to:
        target = (int(point_to[0] * size[0]), int(point_to[1] * size[1]))
    if target:
        draw.line([cx, cy, target[0], target[1]], fill=(*ACCENT, 235), width=4)
        r = int(size[1] * 0.007)
        draw.ellipse([target[0] - r, target[1] - r, target[0] + r, target[1] + r], fill=(*ACCENT, 255))

    shadow = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [box[0] + 5, box[1] + 7, box[2] + 5, box[3] + 7],
        radius=int(size[1] * 0.012), fill=(0, 0, 0, 130))
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(9)))

    draw.rounded_rectangle(box, radius=int(size[1] * 0.012), fill=(*NOTE_BG, 242))
    draw.rounded_rectangle(box, radius=int(size[1] * 0.012), outline=(*ACCENT_SOFT, 230), width=3)
    for index, line in enumerate(lines):
        draw.text((box[0] + pad_x, box[1] + pad_y + index * line_h), line,
                  font=fnt, fill=(255, 255, 255, 255))


POINTER_R = 0.011                # 光点半径，相对画面短边
POINTER_GLOW = 3.2               # 外圈光晕相对本体的倍数


def _pointer(layer, size, at):
    """激光笔光点：内芯亮、外圈渐隐，像真的激光落在屏幕上。

    讲解时观众不知道该看哪儿，一个会动的点比静态框更能带住视线；
    画在高亮框之上、字幕之下，不挡读字。
    """
    if not at:
        return
    cx, cy = int(at[0] * size[0]), int(at[1] * size[1])
    base = max(4, int(min(size) * POINTER_R))
    glow = ImageDraw.Draw(layer)
    for step in range(6, 0, -1):
        r = int(base * (1 + (POINTER_GLOW - 1) * step / 6))
        glow.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(*ACCENT_SOFT, int(10 + (6 - step) * 7)))
    glow.ellipse([cx - base, cy - base, cx + base, cy + base], fill=(255, 255, 255, 235))
    inner = int(base * 0.58)
    glow.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=(*ACCENT, 255))


def _subtitle(layer, size, text):
    """字幕贴近底部，深色半透明底衬保证任何画面上都读得清。"""
    draw = ImageDraw.Draw(layer)
    fnt = font(FONT_SUB, int(size[1] * 0.0315))
    max_w = int(size[0] * 0.80)
    lines = _balance(draw, _wrap(draw, text, fnt, max_w)[:2], fnt)
    line_h = int(fnt.size * 1.48)
    pad_x, pad_y = int(size[0] * 0.018), int(size[1] * 0.014)
    box_w = int(max(draw.textlength(l, font=fnt) for l in lines)) + pad_x * 2
    box_h = line_h * len(lines) + pad_y * 2 - int(line_h - fnt.size)
    bottom = size[1] - int(size[1] * 0.035)
    box = [(size[0] - box_w) // 2, bottom - box_h, (size[0] + box_w) // 2, bottom]
    draw.rounded_rectangle(box, radius=int(size[1] * 0.011), fill=SUB_BG)
    for index, line in enumerate(lines):
        lw = draw.textlength(line, font=fnt)
        draw.text(((size[0] - lw) // 2, box[1] + pad_y + index * line_h), line,
                  font=fnt, fill=(255, 255, 255, 255))
    return box


def _chip(layer, size, text, above=None):
    draw = ImageDraw.Draw(layer)
    fnt = font(FONT_MAIN, int(size[1] * 0.023))
    pad_x, pad_y = int(size[0] * 0.010), int(size[1] * 0.009)
    tw = draw.textlength(text, font=fnt)
    height = int(fnt.size + pad_y * 2)
    if above:
        x, y = above[0], above[1] - height - int(size[1] * 0.012)
    else:
        x, y = int(size[0] * 0.10), int(size[1] * 0.845)
    box = [x, y, int(x + tw + pad_x * 2), int(y + fnt.size + pad_y * 2)]
    draw.rounded_rectangle(box, radius=int(size[1] * 0.010), fill=(*ACCENT, 245))
    draw.text((box[0] + pad_x, box[1] + pad_y), text, font=fnt, fill=(255, 255, 255, 255))


def render(frame_path, out_path, spec):
    base = Image.open(frame_path).convert('RGB')
    base = _redact(base, spec.get('redact', []))
    size = base.size
    rects = [h['rect'] for h in spec.get('highlights', [])]
    canvas = _spotlight(base, rects).convert('RGBA')
    layer = Image.new('RGBA', size, (0, 0, 0, 0))

    radius = int(min(size) * 0.012)
    for item in spec.get('highlights', []):
        _glow_border(layer, _px(item['rect'], size), radius, 5, ACCENT)

    boxes = [_px(item['rect'], size) for item in spec.get('highlights', [])]
    for note in spec.get('notes', []):
        attach = boxes[note['attach']] if isinstance(note.get('attach'), int) and boxes else None
        _note(layer, size, note['at'], note['text'], point_to=note.get('to'),
              align=note.get('align', 'left'), attach_box=attach)
    _pointer(layer, size, spec.get('pointer'))
    sub_box = _subtitle(layer, size, spec['subtitle']) if spec.get('subtitle') else None
    if spec.get('chip'):
        _chip(layer, size, spec['chip'], above=sub_box)

    out = Image.alpha_composite(canvas, layer).convert('RGB')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out.save(out_path, quality=92)
    return out_path
