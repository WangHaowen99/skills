import json
import os

from manim import *

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.environ.get("FONT", "Noto Sans SC")

config.background_color = "#14171C"
INK, MUTED = "#ECEFF4", "#8B93A1"
BLUE, GREEN, YELLOW, RED = "#58C4DD", "#83C167", "#F7D96F", "#FC6255"


def T(text, size=36, color=INK):
    return Text(text, font=FONT, font_size=size, color=color)


def durations():
    with open(os.path.join(HERE, "audio", "durations.json")) as f:
        return json.load(f)


class Narrated(Scene):
    """带字幕和配音的场景基类。"""

    def setup(self):
        from narration import SEGMENTS
        self.subs = dict(SEGMENTS)
        self.durs = durations()
        self.sub = None

    def narrate(self, seg_id):
        if self.sub is not None:
            self.remove(self.sub)
        self.sub = T(self.subs[seg_id], 26).to_edge(DOWN, buff=0.4)
        self.add(self.sub)
        self.add_sound(os.path.join(HERE, "audio", f"{seg_id}.mp3"))
        return self.durs[seg_id]
