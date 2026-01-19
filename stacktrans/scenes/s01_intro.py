"""场景1: 开场与摘要"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class IntroScene(StackTransScene):
    """开场场景：标题、作者、摘要"""

    def construct(self):
        self.next_normal("Title")
        
        title = styled_title("StackTrans")
        subtitle = styled_text(
            "From Large Language Model\nto Large Pushdown Automata Model",
            font_size=32
        ).next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title), run_time=WRITE_TIME)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait()

        self.next_normal("Authors")
        
        authors = styled_text(
            "Kechi Zhang, Ge Li, Jia Li, et al.",
            font_size=28
        ).next_to(subtitle, DOWN, buff=0.8)
        
        self.play(FadeIn(authors))
        self.wait()

        self.next_normal("Abstract")
        
        self.fade_out_all()
        
        abstract_title = styled_text("Abstract", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(abstract_title))

        key_points = VGroup(
            styled_text("Transformer 无法有效捕捉乔姆斯基层级", font_size=24),
            styled_text("StackTrans: 在 Transformer 层间引入隐状态栈", font_size=24),
            styled_text("可微分栈操作，支持端到端学习", font_size=24),
            styled_text("360M 参数超越 2-3x 更大的 LLMs", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(abstract_title, DOWN, buff=0.8)

        for point in key_points:
            bullet = Dot(radius=0.05, color=HIGHLIGHT_COLOR).next_to(point, LEFT, buff=0.2)
            self.play(FadeIn(bullet), Write(point), run_time=0.8)
        
        self.wait()
