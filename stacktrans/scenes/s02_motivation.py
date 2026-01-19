"""场景2: 问题动机"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class MotivationScene(StackTransScene):
    """动机场景：Transformer 的局限性"""

    def construct(self):
        self.next_normal("Transformer_Limitation")
        
        title = styled_text("Transformer 的局限性", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))
        
        chomsky = VGroup(
            styled_text("乔姆斯基层级", font_size=32),
            styled_text("Type 3: 正则语言", font_size=24, color=GREEN),
            styled_text("Type 2: 上下文无关语言", font_size=24, color=BLUE),
            styled_text("Type 1: 上下文相关语言", font_size=24, color=ORANGE),
            styled_text("Type 0: 递归可枚举语言", font_size=24, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(LEFT * 3)
        
        self.play(Write(chomsky[0]))
        for item in chomsky[1:]:
            self.play(FadeIn(item, shift=RIGHT * 0.2), run_time=0.5)
        
        self.wait()

        self.next_normal("PDA_Solution")
        
        pda_box = VGroup(
            Rectangle(width=4, height=2, color=PRIMARY_COLOR),
            styled_text("下推自动机\n(PDA)", font_size=28)
        ).shift(RIGHT * 3)
        pda_box[1].move_to(pda_box[0])
        
        arrow = Arrow(chomsky.get_right(), pda_box.get_left(), color=HIGHLIGHT_COLOR)
        
        self.play(Create(arrow), Create(pda_box[0]), Write(pda_box[1]))
        
        stack_hint = styled_text("栈结构 → 处理嵌套", font_size=24, color=HIGHLIGHT_COLOR)
        stack_hint.next_to(pda_box, DOWN)
        self.play(FadeIn(stack_hint))
        
        self.wait()
