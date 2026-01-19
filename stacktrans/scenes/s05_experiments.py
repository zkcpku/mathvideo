"""场景5: 实验结果"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class ExperimentsScene(StackTransScene):
    """实验结果展示"""

    def construct(self):
        self.next_normal("Results_Overview")
        
        title = styled_text("实验结果", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))

        table_data = [
            ["Model", "Params", "Score"],
            ["Transformer", "360M", "45.2"],
            ["RWKV", "430M", "47.8"],
            ["Mamba", "370M", "48.1"],
            ["StackTrans", "360M", "51.3"],
        ]
        
        table = Table(
            table_data[1:],
            col_labels=[Text(h, font_size=24) for h in table_data[0]],
            include_outer_lines=True,
        ).scale(0.7).shift(DOWN * 0.5)
        
        self.play(Create(table))
        self.wait()

        self.next_normal("Highlight_Best")
        
        best_row = table.get_rows()[-1]
        highlight = SurroundingRectangle(best_row, color=HIGHLIGHT_COLOR, buff=0.1)
        self.play(Create(highlight))
        
        better_note = styled_text(
            "360M 参数超越更大模型!",
            font_size=28,
            color=HIGHLIGHT_COLOR
        ).next_to(table, DOWN, buff=0.5)
        self.play(Write(better_note))
        
        self.wait()

        self.next_normal("Scaling")
        
        self.fade_out_all()
        
        scale_title = styled_text("规模扩展", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(scale_title))
        
        scale_points = VGroup(
            styled_text("成功扩展至 7B 参数", font_size=28),
            styled_text("保持与标准 Transformer 相同的训练效率", font_size=28),
            styled_text("推理时栈操作开销可忽略", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).shift(DOWN * 0.5)
        
        for point in scale_points:
            check = Text("✓", color=GREEN, font_size=32).next_to(point, LEFT, buff=0.3)
            self.play(FadeIn(check), Write(point), run_time=0.7)
        
        self.wait()
