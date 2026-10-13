"""“待决策项”讲解模板：标题条 + 背景/分析/选项/建议四步进度 + 选项卡片 + 建议高亮。

用法（场景里）：
    class D1Foo(Decision):
        NUM, TITLE, COLOR, META = 1, "工具上下文怎么注入", PURPLE, "负责：xx · P0 · 10/15 前"
        def construct(self):
            with self.voice("d1_1"):
                self.header(); self.step(0, clear=False)
            ...背景、分析段落自己画（分析开始时 self.step(1)）...
            cards = self.options(["d1_6", "d1_7", "d1_8"], [("A", "标题", [("+", "优点"), ("-", "缺点"), (".", "备注")]), ...])
            with self.voice("d1_9"):
                self.recommend(cards, {1: "建议"})
                self.note("条件或理由", YELLOW)
            self.fade_all()
"""
from common import *

STEPS = ("背景", "分析", "选项", "建议")


class Decision(Base):
    NUM, TITLE, COLOR, META = 0, "", INK, ""

    def setup(self):
        super().setup()
        self.keep = []
        self.note_y = -0.85

    def header(self):
        head = chip(self.NUM, self.TITLE, self.COLOR, 28).to_corner(UL, buff=0.35)
        meta = T(self.META, 20, MUTED).next_to(head, DOWN, buff=0.14).align_to(head, LEFT)
        steps = VGroup(*[pill(n, MUTED, 20, fill=0.0, stroke=1.5) for n in STEPS]).arrange(RIGHT, buff=0.12)
        steps.to_corner(UR, buff=0.4)
        self.keep = [head, meta, steps]
        self.steps = steps
        self.play(FadeIn(head, shift=DOWN * 0.15), FadeIn(meta), FadeIn(steps), run_time=0.7)

    def content(self, keep=()):
        return [m for m in self.mobjects if m not in self.subs and m not in self.keep and m not in keep]

    def clear(self, keep=(), rt=0.5):
        mobs = self.content(keep)
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=rt)

    def step(self, i, clear=True, keep=()):
        """切到第 i 步（0 背景 / 1 分析 / 2 选项 / 3 建议）；clear=True 时同时清掉正文。"""
        anims = [FadeOut(m) for m in self.content(keep)] if clear else []
        for j, s in enumerate(self.steps):
            col = YELLOW if j == i else (INK if j < i else MUTED)
            anims += [s.box.animate.set_stroke(col, 2.5 if j == i else 1.5).set_fill(col, 0.22 if j == i else 0.0),
                      s.label.animate.set_color(col)]
        self.play(*anims, run_time=0.5)

    def show_card(self, card, budget):
        budget = max(budget, 1.0)
        self.play(FadeIn(card.box), FadeIn(card.head, shift=UP * 0.1), run_time=min(0.6, budget * 0.4))
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in card.rows], lag_ratio=0.35),
                  run_time=min(1.6, budget * 0.55))

    def options(self, segs, specs, y=0.85):
        """每段旁白亮出一张选项卡；第一段自动切到“选项”步。"""
        cards = opt_row(specs, y)
        for k, (seg, card) in enumerate(zip(segs, cards)):
            with self.voice(seg):
                if k == 0:
                    self.step(2)
                self.show_card(card, DUR[seg] - (0.9 if k == 0 else 0.3))
        return cards

    def recommend(self, cards, picks):
        """picks = {卡片下标: 标签文字}，可多选（如 {0: "现在", 1: "目标"}）；其余卡片变暗。"""
        self.step(3, clear=False)
        self.note_y = -0.85
        anims, tags = [], VGroup()
        for i, c in enumerate(cards):
            anims.append(c.box.animate.set_stroke(YELLOW, 4) if i in picks else c.animate.set_opacity(0.28))
        for i, lab in picks.items():
            tag = tagged(lab, YELLOW, 21)
            tags.add(tag.move_to(cards[i].box.get_corner(UR) + LEFT * (tag.width / 2 + 0.25)))
        self.play(*anims, LaggedStart(*[FadeIn(t, scale=1.4) for t in tags], lag_ratio=0.3), run_time=1.0)
        return tags

    def note(self, text, color=INK, size=22, rt=0.8):
        """卡片下方逐行追加理由/条件（最多 3 行，避开字幕）。"""
        g = note_line(text, color, size)
        g.move_to([0, self.note_y, 0]).align_to([-5.9, 0, 0], LEFT)
        self.note_y -= 0.52
        self.play(FadeIn(g, shift=UP * 0.1), run_time=rt)
        return g


def note_line(text, color=INK, size=22):
    bullet = Square(0.13).set_stroke(width=0).set_fill(color, 1)
    g = VGroup(bullet, T(text, size, color)).arrange(RIGHT, buff=0.18)
    if g.width > 11.8:
        g.scale_to_fit_width(11.8)
    return g


def opt_card(letter, title, lines, w, h):
    box = RoundedRectangle(corner_radius=0.18, width=w, height=h).set_stroke(MUTED, 2).set_fill(CARD_BG, 1)
    badge = Circle(radius=0.22).set_stroke(width=0).set_fill(INK, 1)
    head = VGroup(VGroup(badge, T(letter, 22, BG).move_to(badge)), T(title, 23, INK)).arrange(RIGHT, buff=0.18)
    if head.width > w - 0.4:
        head.scale_to_fit_width(w - 0.4)
    rows = VGroup()
    for sign, text in lines:
        mark = {"+": check(GREEN, 0.17, 4), "-": xmark(RED, 0.1, 4)}.get(sign) or Dot(radius=0.05, color=MUTED)
        rows.add(VGroup(mark, T(text, 20, INK if sign in "+-" else MUTED)).arrange(RIGHT, buff=0.16))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    for r in rows:
        if r.width > w - 0.55:
            r.scale_to_fit_width(w - 0.55)
    head.move_to(box.get_top() + DOWN * 0.45).align_to(box, LEFT).shift(RIGHT * 0.25)
    rows.next_to(head, DOWN, buff=0.32).align_to(box, LEFT).shift(RIGHT * 0.32)
    card = VGroup(box, head, rows)
    card.box, card.head, card.rows = box, head, rows
    return card


def opt_row(specs, y=0.85, h=2.45):
    n = len(specs)
    w = {2: 5.6, 3: 3.85}[n]
    cards = VGroup(*[opt_card(l, t, ls, w, h) for l, t, ls in specs]).arrange(RIGHT, buff=0.2 if n == 3 else 0.5)
    return cards.move_to([0, y, 0])


def dashed_pill(label, color=MUTED, size=22, w=None, h=None):
    p = pill(label, color, size, w=w, h=h, fill=0.0)
    return VGroup(DashedVMobject(p.box, num_dashes=40), p.label)


def item_card(num, text, color, w=2.8):
    """总览网格用的小卡片（编号圆 + 短标题）。"""
    r = RoundedRectangle(corner_radius=0.12, width=w, height=0.66).set_stroke(color, 2).set_fill(color, 0.1)
    c = Circle(radius=0.19).set_stroke(width=0).set_fill(color, 1)
    n = T(str(num), 19, BG)
    if n.width > 0.28:
        n.scale_to_fit_width(0.28)
    row = VGroup(VGroup(c, n.move_to(c)), T(text, 20, INK)).arrange(RIGHT, buff=0.14)
    row.move_to(r).align_to(r, LEFT).shift(RIGHT * 0.15)
    g = VGroup(r, row)
    g.box = r
    return g
