from dkit import *


class S0Demo(Base):
    def construct(self):
        with self.voice("s0_1"):
            q = T("一条请求经过了哪些地方？", 40).move_to(UP * 0.5)
            self.play(Write(q), run_time=1.2)
        a = container("客户端", BLUE, 3.0, 2.0).move_to(LEFT * 3.6)
        b = container("服务端", GREEN, 3.0, 2.0).move_to(RIGHT * 3.6)
        with self.voice("s0_2"):
            self.play(q.animate.scale(0.7).to_edge(UP, buff=0.5), FadeIn(a), FadeIn(b), run_time=0.9)
            req = arrow(a.box.get_right() + UP * 0.3, b.box.get_left() + UP * 0.3, BLUE, sw=5)
            res = darrow(b.box.get_left() + DOWN * 0.3, a.box.get_right() + DOWN * 0.3, MUTED)
            self.play(GrowArrow(req), run_time=0.7)
            self.play(Create(res), run_time=0.7)
        with self.voice("s0_3"):
            self.play(Indicate(VGroup(a, b), color=YELLOW, scale_factor=1.05), run_time=1.0)
        self.fade_all()


class D1Demo(Decision):
    NUM, TITLE, COLOR, META = 1, "缓存放在哪一层", PURPLE, "负责：示例 · P1"

    def construct(self):
        with self.voice("d1_1"):
            self.header()
            self.step(0, clear=False)
        cards = self.options(["d1_2", "d1_3"], [
            ("A", "客户端缓存", [("+", "最快"), ("-", "各端不一致")]),
            ("B", "服务端缓存", [("+", "一致性好"), ("-", "多一次往返")]),
        ])
        with self.voice("d1_4"):
            self.recommend(cards, {1: "建议"})
            self.note("热点数据 5 分钟过期", YELLOW)
        self.fade_all()
