"""场景4: 公式推导"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class DerivationScene(StackTransScene):
    """公式推导场景"""

    def construct(self):
        self.next_normal("Loss_Function")
        
        title = styled_text("训练目标", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))
        
        loss = MathTex(
            r"\mathcal{L}", r"=", r"-\sum_{t=1}^{T}", r"\log", r"p(y_t | y_{<t}, x)",
            font_size=FORMULA_FONT_SIZE
        )
        self.play(Write(loss))
        self.wait()

        self.next_normal("Stack_State")
        
        loss_with_stack = MathTex(
            r"\mathcal{L}", r"=", r"-\sum_{t=1}^{T}", r"\log", r"p(y_t | y_{<t}, x,", r"s_t", r")",
            font_size=FORMULA_FONT_SIZE
        )
        loss_with_stack[5].set_color(HIGHLIGHT_COLOR)
        
        self.play(TransformMatchingTex(loss, loss_with_stack))
        
        stack_note = styled_text("s_t: 时刻 t 的栈状态", font_size=24, color=HIGHLIGHT_COLOR)
        stack_note.next_to(loss_with_stack, DOWN, buff=0.8)
        self.play(FadeIn(stack_note))
        
        self.wait()

        self.next_normal("Stack_Update")
        
        self.fade_out_all()
        
        update_title = styled_text("栈状态更新", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(update_title))
        
        update_eq = MathTex(
            r"s_{t+1}", r"=", r"f(s_t, h_t, a_t)",
            font_size=FORMULA_FONT_SIZE
        ).shift(UP * 0.5)
        
        self.play(Write(update_eq))
        
        where = VGroup(
            styled_text("其中:", font_size=24),
            VGroup(MathTex(r"h_t", font_size=28), styled_text(": hidden state", font_size=24)).arrange(RIGHT, buff=0.2),
            MathTex(r"a_t \in \{\text{push}, \text{pop}, \text{no-op}\}", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(update_eq, DOWN, buff=0.8)
        
        for item in where:
            self.play(FadeIn(item), run_time=0.5)
        
        self.wait()
