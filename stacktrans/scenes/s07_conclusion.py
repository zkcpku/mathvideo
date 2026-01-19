"""场景7: 总结"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class ConclusionScene(StackTransScene):
    """总结场景"""

    def construct(self):
        self.next_normal("Summary")
        
        title = styled_text("总结", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))
        
        contributions = VGroup(
            styled_text("StackTrans: 首个大规模下推自动机模型", font_size=28),
            styled_text("显式栈结构增强 Transformer 表达能力", font_size=28),
            styled_text("可微分设计，端到端训练", font_size=28),
            styled_text("360M 模型超越 2-3x 更大的 LLMs", font_size=28),
            styled_text("成功扩展至 7B 参数", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).shift(DOWN * 0.3)
        
        for i, contrib in enumerate(contributions):
            num = Text(f"{i+1}.", font_size=28, color=HIGHLIGHT_COLOR).next_to(contrib, LEFT, buff=0.3)
            self.play(FadeIn(num), Write(contrib), run_time=0.7)
        
        self.wait()

        self.next_normal("Future")
        
        future = styled_text(
            "未来方向: 更深层次的形式语言理论集成",
            font_size=24,
            color=SECONDARY_COLOR
        ).to_edge(DOWN, buff=1)
        
        self.play(FadeIn(future))
        self.wait()

        self.next_normal("Thanks")
        
        self.fade_out_all()
        
        thanks = styled_title("Thank You!").move_to(ORIGIN)
        self.play(Write(thanks))
        self.wait()
