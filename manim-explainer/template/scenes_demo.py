from common import *


class Intro(Narrated):
    def construct(self):
        d = self.narrate("s1_1")
        q = T("一条请求经过了哪些地方？", 40)
        self.play(Write(q), run_time=1.5)
        self.wait(max(d - 1.5, 0))

        d = self.narrate("s1_2")
        a = VGroup(RoundedRectangle(width=3, height=1.6, color=BLUE), T("客户端", 30)).move_to(LEFT * 3.5)
        b = VGroup(RoundedRectangle(width=3, height=1.6, color=GREEN), T("服务端", 30)).move_to(RIGHT * 3.5)
        self.play(q.animate.scale(0.7).to_edge(UP), FadeIn(a), FadeIn(b), run_time=1)
        req = Arrow(a.get_right() + UP * 0.3, b.get_left() + UP * 0.3, color=BLUE)
        res = Arrow(b.get_left() + DOWN * 0.3, a.get_right() + DOWN * 0.3, color=MUTED)
        self.play(GrowArrow(req), run_time=0.8)
        self.play(GrowArrow(res), run_time=0.8)
        self.wait(max(d - 2.6, 0))

        d = self.narrate("s1_3")
        self.play(Indicate(VGroup(a, b), color=YELLOW), run_time=1)
        self.wait(max(d - 1, 0))
