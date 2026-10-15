"""3b1b 风格讲解视频的公共库：配色、文字、字幕、配音同步、常用图形部件。

同步模型：每段旁白一个 `with self.voice("段id"):` 块。进入时挂上该段音频和字幕，
块内动画随意编排，退出时自动补足等待到音频结束，并把 [段id, 起, 止] 记到 logs/timing_<场景>.json。
动画总时长超过音频，就会造成冷场（用 scripts/check_timing.py 检查）。
"""
import json
import math
import os
import sys

from manim import *
from manim.animation.animation import prepare_animation

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from narration import SEGMENTS  # noqa: E402

# ---------- 配色：颜色只表达含义，全片保持一致 ----------
# THEME=light（或 white）切白底：强调色换成同色系的深色版，否则黄、浅蓝、青在白底上看不清
THEME = os.environ.get("THEME", "dark")
if THEME in ("light", "white"):
    BG = "#FFFFFF"
    INK = "#1F2328"      # 正文
    MUTED = "#6B7280"    # 次要说明
    DIM = "#D0D5DD"      # 分隔线、弱边框
    CARD_BG = "#F5F7FA"  # 卡片底色
    BLUE = "#1C7ED6"
    GREEN = "#2F9E44"    # 正确、通过
    YELLOW = "#B07800"   # 强调、建议
    RED = "#E03131"      # 错误、风险
    PURPLE = "#7048E8"
    TEAL = "#0C8599"
    ORANGE = "#E8590C"
    SALMON = "#A0522D"
    PINK = "#D6336C"
else:
    BG = "#0F1117"
    INK = "#ECEFF4"
    MUTED = "#8B93A1"
    DIM = "#3A404C"
    CARD_BG = "#161A22"
    BLUE = "#58C4DD"
    GREEN = "#83C167"
    YELLOW = "#F7D96F"
    RED = "#FC6255"
    PURPLE = "#B794D6"
    TEAL = "#5CD0B3"
    ORANGE = "#FF9F5A"
    SALMON = "#E8A87C"
    PINK = "#E07A9F"
FONT = "LXGW WenKai"
MONO = "JetBrains Mono"
NBSP = " "  # Text 会吞掉前导空格，缩进用它

config.background_color = BG

DUR = json.load(open(os.path.join(HERE, "audio", "durations.json"), encoding="utf-8"))
SUB = {seg_id: text for seg_id, text, _ in SEGMENTS}

# 换配音后：把旧音频目录的 durations.json 当参考（PACE_REF=旧目录名），
# 动画按每段“新/旧”时长之比整体加速（只加速不减速），不用改场景代码。
_REF_PATH = os.path.join(HERE, os.environ.get("PACE_REF", "audio_ref"), "durations.json")
REF = json.load(open(_REF_PATH, encoding="utf-8")) if os.path.exists(_REF_PATH) else {}
_ratios = sorted(DUR[k] / REF[k] for k in REF if k in DUR)
GAP_PACE = min(_ratios[len(_ratios) // 2], 1.0) if _ratios else 1.0
MIN_PACE = 0.55


def seg_pace(seg_id):
    if seg_id not in REF:
        return GAP_PACE
    return max(min(DUR[seg_id] / REF[seg_id], 1.0), MIN_PACE)


# ---------- 文本 ----------
def T(s, size=30, color=INK, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def M(s, size=22, color=INK, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


PUNCT = "，。；：？！、"


def wrap(text, maxc=33):
    text = text.rstrip("。；")
    if len(text) <= maxc:
        return [text]
    lines, rest = [], text
    while len(rest) > maxc:
        n_left = math.ceil(len(rest) / maxc)
        target = len(rest) / n_left
        cands = [i for i in range(1, min(maxc, len(rest)) + 1) if rest[i - 1] in PUNCT]
        if cands:
            cut = min(cands, key=lambda i: abs(i - target))
        else:
            cut = maxc
            while cut > 1 and rest[cut - 1].isascii() and rest[cut].isascii() and rest[cut] != " ":
                cut -= 1
        lines.append(rest[:cut])
        rest = rest[cut:].lstrip()
    lines.append(rest)
    return lines


def subtitle(text):
    g = VGroup(*[T(l, 28, INK) for l in wrap(text)]).arrange(DOWN, buff=0.1)
    g.to_edge(DOWN, buff=0.2)
    bg = BackgroundRectangle(g, color=BG, fill_opacity=0.82, buff=0.1)
    return VGroup(bg, g).set_z_index(100)


# ---------- 场景基类：配音与画面同步 ----------
class Voice:
    def __init__(self, scene, seg_id):
        self.scene, self.seg_id = scene, seg_id

    def __enter__(self):
        s = self.scene
        self.t0 = s.renderer.time
        s.pace = seg_pace(self.seg_id)
        s.add_sound(os.path.join(HERE, "audio", f"{self.seg_id}.wav"))
        self.sub = subtitle(SUB[self.seg_id])
        s.add(self.sub)
        s.subs.append(self.sub)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            return False
        s = self.scene
        s.pace = 1.0
        rest = DUR[self.seg_id] - (s.renderer.time - self.t0)
        if rest > 0.02:
            s.wait(rest)
        s.pace = GAP_PACE
        s.layout_issues += layout_check(s, self.seg_id, self.sub)
        s.remove(self.sub)
        s.subs.remove(self.sub)
        s.timing.append([self.seg_id, round(self.t0, 3), round(s.renderer.time, 3)])
        return False


class Base(Scene):
    def setup(self):
        self.subs, self.timing, self.pace, self.layout_issues = [], [], GAP_PACE, []

    def play(self, *args, **kwargs):
        if self.pace != 1.0:
            if "run_time" in kwargs:
                kwargs["run_time"] *= self.pace
            else:
                args = [prepare_animation(a) for a in args]
                for a in args:
                    a.run_time *= self.pace
        super().play(*args, **kwargs)

    def voice(self, seg_id):
        return Voice(self, seg_id)

    def fade_all(self, run_time=0.6, keep=()):
        mobs = [m for m in self.mobjects if m not in self.subs and m not in keep]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def tear_down(self):
        os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
        with open(os.path.join(HERE, "logs", f"timing_{type(self).__name__}.json"), "w") as f:
            json.dump(self.timing, f)
        with open(os.path.join(HERE, "logs", f"layout_{type(self).__name__}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(self.layout_issues) + ("\n" if self.layout_issues else ""))


# ---------- 自动排版检查：每段旁白结束的画面（与联系表同一时刻）写 logs/layout_<场景>.txt ----------
FRAME_X, FRAME_Y = config.frame_width / 2, config.frame_height / 2


def _visible(m):
    if len(m.points) == 0:
        return False
    try:
        return m.get_fill_opacity() > 0.05 or (m.get_stroke_opacity() > 0.05 and m.get_stroke_width() > 0)
    except Exception:
        return True


def _box(m):
    return m.get_left()[0], m.get_right()[0], m.get_bottom()[1], m.get_top()[1]


def _overlap(a, b):
    w = min(a[1], b[1]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[2], b[2])
    return w * h if w > 0 and h > 0 else 0.0


def layout_check(scene, seg_id, sub):
    """出界、压字幕、文字重叠（>20%）、字太小（正文 <18、代码 <16）。整屏底色（宽于 12）不算。"""
    issues = []
    sub_family = set(sub.get_family())
    texts, leaves = [], []
    for top in [m for m in scene.mobjects if m not in scene.subs]:
        for m in top.get_family():
            if m in sub_family:
                continue
            if isinstance(m, Text):
                if any(_visible(c) for c in m.get_family()):
                    texts.append(m)
            elif not m.submobjects and _visible(m) and m.width < 12:
                leaves.append(m)
    sx0, sx1, sy0, sy1 = _box(sub[1])
    for m in texts + leaves:
        x0, x1, y0, y1 = _box(m)
        name = f"“{m.text[:12]}”" if isinstance(m, Text) else type(m).__name__
        if x0 < -FRAME_X + 0.15 or x1 > FRAME_X - 0.15 or y1 > FRAME_Y - 0.1 or y0 < -FRAME_Y + 0.05:
            issues.append(f"{seg_id}\t出界\t{name} x[{x0:.2f},{x1:.2f}] y[{y0:.2f},{y1:.2f}]")
        elif y0 < sy1 + 0.05 and x1 > sx0 and x0 < sx1:
            issues.append(f"{seg_id}\t压字幕\t{name} 底边 {y0:.2f} < 字幕顶 {sy1:.2f}")
    for i, a in enumerate(texts):
        fs = getattr(a, "font_size", 99)
        if fs < (15.5 if getattr(a, "font", "") == MONO else 17.5):
            issues.append(f"{seg_id}\t字太小\t“{a.text[:12]}” {fs:.0f}")
        ba = _box(a)
        for b in texts[i + 1:]:
            bb = _box(b)
            ov = _overlap(ba, bb)
            small = min((ba[1] - ba[0]) * (ba[3] - ba[2]), (bb[1] - bb[0]) * (bb[3] - bb[2]))
            if small > 0 and ov / small > 0.2:
                issues.append(f"{seg_id}\t文字重叠\t“{a.text[:10]}” × “{b.text[:10]}” {ov / small:.0%}")
    return issues


def soft_indicate(m, color=YELLOW, scale_factor=1.06, **kw):
    """Indicate 的替代：不透明填充只换描边色。原版 Indicate 会把不透明底色整块染成实色、盖住文字（白底尤其明显）。"""
    target = m.copy().scale(scale_factor)
    text_parts = {id(x) for t in target.get_family() if isinstance(t, Text) for x in t.get_family()}
    for x in target.get_family():
        if not isinstance(x, VMobject) or len(x.points) == 0:
            continue
        if id(x) not in text_parts and x.get_fill_opacity() >= 0.5:
            x.set_stroke(color)
        else:
            x.set_color(color)
    return Transform(m, target, rate_func=there_and_back, **kw)


# ---------- 部件 ----------
def pill(label, color=INK, size=26, w=None, h=None, fill=0.14, mono=False, stroke=2.5, corner=0.14, text_color=None):
    t = (M if mono else T)(label, size, text_color or color)
    w = w or t.width + 0.5
    h = h or max(t.height + 0.32, 0.6)
    r = RoundedRectangle(corner_radius=corner, width=w, height=h).set_stroke(color, stroke).set_fill(color, fill)
    t.move_to(r)
    g = VGroup(r, t)
    g.box, g.label = r, t
    return g


def container(title, color, w, h, size=28, fill=0.05):
    r = RoundedRectangle(corner_radius=0.25, width=w, height=h).set_stroke(color, 3).set_fill(color, fill)
    t = T(title, size, color).next_to(r.get_top(), DOWN, buff=0.2)
    g = VGroup(r, t)
    g.box, g.title = r, t
    return g


def arrow(a, b, color=INK, sw=4, buff=0.1, ratio=0.12, **kw):
    return Arrow(a, b, buff=buff, stroke_width=sw, color=color, max_tip_length_to_length_ratio=ratio, **kw)


def darrow(a, b, color=INK, sw=3.5, buff=0.1, ratio=0.12, **kw):
    ar = Arrow(a, b, buff=buff, stroke_width=sw, color=color, max_tip_length_to_length_ratio=ratio, **kw)
    tips = ar.pop_tips()
    dashed = DashedVMobject(ar, num_dashes=max(int(ar.get_arc_length() / 0.2), 4))
    return VGroup(dashed, tips)


def _ray_box(m, d):
    """从 m 中心沿 d 射出与外接矩形的交点（圆角矩形上 get_boundary_point 会落到角上，水平线会歪）。"""
    tx = m.width / 2 / abs(d[0]) if abs(d[0]) > 1e-6 else np.inf
    ty = m.height / 2 / abs(d[1]) if abs(d[1]) > 1e-6 else np.inf
    return m.get_center() + d * min(tx, ty)


def edge_arrow(a, b, color=MUTED, sw=3, arc=0.0, buff=0.08):
    """从 a 的边界指向 b 的边界（流程图、环形图）；箭头尖固定约 0.22，不随线长放大。"""
    d = b.get_center() - a.get_center()
    d = d / np.linalg.norm(d)
    p0, p1 = _ray_box(a, d), _ray_box(b, -d)
    ratio = min(0.12, 0.22 / max(np.linalg.norm(p1 - p0), 0.1))
    return arrow(p0, p1, color, sw=sw, buff=buff, ratio=ratio, path_arc=arc)


def check(color=GREEN, s=0.35, sw=7):
    return VMobject().set_points_as_corners([[-0.5, 0, 0], [-0.12, -0.38, 0], [0.55, 0.42, 0]]).scale(s).set_stroke(color, sw)


def xmark(color=RED, s=0.3, sw=7):
    return VGroup(Line(UL, DR), Line(UR, DL)).scale(s).set_stroke(color, sw)


def strike(m, color=RED, sw=4):
    return Line(m.get_left(), m.get_right()).set_stroke(color, sw)


def file_icon(h=0.7, color=INK, fill=0.12):
    w, f = h * 0.78, h * 0.28
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - f, h / 2, 0], [w / 2, h / 2 - f, 0], [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0])
    body.set_stroke(color, 2.5).set_fill(color, fill)
    fold = VMobject().set_points_as_corners([[w / 2 - f, h / 2, 0], [w / 2 - f, h / 2 - f, 0], [w / 2, h / 2 - f, 0]]).set_stroke(color, 2.5)
    lines = VGroup(*[Line([-w * 0.3, y, 0], [w * 0.3, y, 0]) for y in (-h * 0.05, -h * 0.2, -h * 0.35)]).set_stroke(color, 2, opacity=0.7)
    return VGroup(body, fold, lines)


def folder_icon(w=1.0, h=0.7, color=INK, fill=0.14):
    tab = w * 0.38
    pts = [[-w / 2, -h / 2, 0], [-w / 2, h / 2, 0], [-w / 2 + tab, h / 2, 0], [-w / 2 + tab + 0.12, h / 2 - 0.12, 0],
           [w / 2, h / 2 - 0.12, 0], [w / 2, -h / 2, 0]]
    return Polygon(*pts).set_stroke(color, 2.5).set_fill(color, fill)


def db_icon(color=INK, w=1.1, h=0.9, fill=0.14):
    rx, ry = w / 2, h * 0.13
    body = Rectangle(width=w, height=h).set_stroke(width=0).set_fill(color, fill)
    top = Ellipse(width=w, height=2 * ry).shift(UP * h / 2).set_stroke(color, 2.5).set_fill(color, fill * 1.6)

    def lower(y):
        a = Arc(radius=1, start_angle=PI, angle=PI)
        a.stretch(rx, 0, about_point=ORIGIN).stretch(ry, 1, about_point=ORIGIN)
        return a.shift(UP * y).set_stroke(color, 2.5)
    sides = VGroup(Line([-rx, h / 2, 0], [-rx, -h / 2, 0]), Line([rx, h / 2, 0], [rx, -h / 2, 0])).set_stroke(color, 2.5)
    return VGroup(body, top, sides, lower(-h / 2), lower(h / 6).set_stroke(opacity=0.5))


def envelope(color=BLUE, w=0.7, h=0.46):
    r = Rectangle(width=w, height=h).set_stroke(color, 2.5).set_fill(color, 0.25)
    v = VMobject().set_points_as_corners([[-w / 2, h / 2, 0], [0, -h * 0.05, 0], [w / 2, h / 2, 0]]).set_stroke(color, 2.5)
    return VGroup(r, v)


def name_tag(label, color=YELLOW, size=22):
    t = T(label, size, BG)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.45, height=t.height + 0.25).set_stroke(color, 2).set_fill(color, 1)
    t.move_to(r).shift(RIGHT * 0.08)
    hole = Circle(radius=0.05).set_stroke(BG, 2).set_fill(BG, 1).move_to(r.get_left() + RIGHT * 0.14)
    return VGroup(r, t, hole)


def clock_icon(color=YELLOW, r=0.28):
    c = Circle(radius=r).set_stroke(color, 2.5)
    hands = VGroup(Line(ORIGIN, UP * r * 0.7), Line(ORIGIN, RIGHT * r * 0.5)).set_stroke(color, 2.5)
    return VGroup(c, hands)


def person_icon(color=INK, s=0.32):
    head = Circle(radius=s * 0.45).set_stroke(color, 2.5).shift(UP * s * 0.55)
    body = Arc(radius=s * 0.8, start_angle=0, angle=PI).set_stroke(color, 2.5).shift(DOWN * s * 0.6)
    return VGroup(head, body)


def browser_icon(w=2.2, h=1.5, color=INK):
    r = RoundedRectangle(corner_radius=0.12, width=w, height=h).set_stroke(color, 2.5).set_fill(color, 0.05)
    bar = Line(r.get_corner(UL) + DOWN * 0.3, r.get_corner(UR) + DOWN * 0.3).set_stroke(color, 2)
    dots = VGroup(*[Dot(radius=0.04, color=color) for _ in range(3)]).arrange(RIGHT, buff=0.08)
    dots.move_to(r.get_corner(UL) + DOWN * 0.15 + RIGHT * 0.3)
    return VGroup(r, bar, dots)


def cursor_icon(color=INK):
    p = Polygon([0, 0, 0], [0, -0.5, 0], [0.13, -0.38, 0], [0.24, -0.6, 0], [0.32, -0.56, 0], [0.21, -0.35, 0], [0.38, -0.35, 0])
    return p.set_stroke(BG, 2).set_fill(color, 1)


def image_icon(color=PINK, w=0.9, h=0.7):
    r = RoundedRectangle(corner_radius=0.06, width=w, height=h).set_stroke(color, 2.5).set_fill(color, 0.12)
    m = Polygon([-w * 0.38, -h * 0.32, 0], [-w * 0.08, h * 0.05, 0], [w * 0.1, -h * 0.12, 0], [w * 0.22, 0, 0],
                [w * 0.4, -h * 0.32, 0]).set_stroke(color, 2).set_fill(color, 0.4)
    s = Circle(radius=h * 0.1).set_stroke(width=0).set_fill(color, 0.9).move_to([w * 0.22, h * 0.22, 0])
    return VGroup(r, m, s)


def toggle(on=False, color=GREEN, w=0.9, h=0.44):
    track = RoundedRectangle(corner_radius=h / 2, width=w, height=h).set_stroke(color if on else MUTED, 2.5)
    track.set_fill(color if on else MUTED, 0.3 if on else 0.1)
    knob = Circle(radius=h * 0.36).set_stroke(width=0).set_fill(INK, 1)
    knob.move_to(track.get_right() + LEFT * h / 2 if on else track.get_left() + RIGHT * h / 2)
    return VGroup(track, knob)


def tagged(text, color, size=20):
    """实心小标签（例如“建议”“新问题”）。"""
    t = T(text, size, BG)
    bg = RoundedRectangle(corner_radius=0.1, width=t.width + 0.3, height=t.height + 0.18).set_stroke(width=0).set_fill(color, 1)
    return VGroup(bg, t.move_to(bg))


def chip(num, label, color, size=24):
    """带圆形编号的标题条；两位数编号会自动缩小以免溢出。"""
    n = T(str(num), size, BG)
    c = Circle(radius=0.2).set_stroke(width=0).set_fill(color, 1)
    if n.width > 0.3:
        n.scale_to_fit_width(0.3)
    n.move_to(c)
    row = VGroup(VGroup(c, n), T(label, size, INK)).arrange(RIGHT, buff=0.15)
    r = RoundedRectangle(corner_radius=0.12, width=row.width + 0.35, height=0.62).set_stroke(color, 2).set_fill(color, 0.12)
    row.move_to(r)
    g = VGroup(r, row)
    g.box = r
    return g


def flow_dot(path, color=INK, run_time=1.2, radius=0.07):
    """沿路径跑一个点，返回 (dot, 动画)。"""
    d = Dot(radius=radius, color=color).move_to(path.get_start())
    return d, Succession(FadeIn(d, run_time=0.1), MoveAlongPath(d, path, run_time=run_time, rate_func=smooth),
                         FadeOut(d, run_time=0.15))
