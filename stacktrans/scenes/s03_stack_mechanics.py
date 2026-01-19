"""场景3: 栈操作核心动画"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *
from stacktrans.utils.animations import create_stack_visual, create_stack_element, highlight_box


class StackMechanicsScene(StackTransScene):
    """核心场景：栈操作动画演示"""

    def construct(self):
        self.next_normal("Stack_Structure")
        
        title = styled_text("StackTrans 核心：隐状态栈", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))
        
        stack_frame = create_stack_visual(height=3.5, width=2.5)
        stack_frame.shift(DOWN * 0.5)
        
        stack_label = styled_text("Hidden State Stack", font_size=24).next_to(stack_frame, DOWN)
        
        self.play(Create(stack_frame), Write(stack_label))
        self.wait()

        self.next_normal("Push_Operation")
        
        push_title = styled_text("Push 操作", font_size=32, color=GREEN).to_corner(UL).shift(DOWN)
        self.play(Write(push_title))
        
        elements = []
        labels = ["h_1", "h_2", "h_3"]
        colors = [BLUE, TEAL, PURPLE]
        
        base_y = stack_frame[0].get_top()[1] + 0.3
        
        for i, (label, color) in enumerate(zip(labels, colors)):
            elem = create_stack_element(label, color=color)
            elem.move_to([0, base_y + i * 0.6, 0])
            
            elem_start = elem.copy().shift(UP * 2 + RIGHT * 3)
            self.play(elem_start.animate.move_to(elem), run_time=0.8)
            elements.append(elem_start)
            
            self.wait(0.3)

        self.next_normal("Pop_Operation")
        
        pop_title = styled_text("Pop 操作", font_size=32, color=RED).next_to(push_title, DOWN, aligned_edge=LEFT)
        self.play(Write(pop_title))
        
        if elements:
            top_elem = elements[-1]
            box = highlight_box(top_elem)
            self.play(Create(box))
            self.wait(0.3)
            
            self.play(
                top_elem.animate.shift(RIGHT * 4),
                FadeOut(box),
                run_time=0.8
            )
            elements.pop()
        
        self.wait()

        self.next_normal("Differentiable_Stack")
        
        self.fade_out_all()
        
        diff_title = styled_text("可微分栈操作", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(diff_title))
        
        formula = MathTex(
            r"\text{push}(s_t, h_t)", r"=", r"[h_t; s_t]",
            font_size=FORMULA_FONT_SIZE
        ).shift(UP)
        
        formula2 = MathTex(
            r"\text{pop}(s_t)", r"=", r"s_t[1:]",
            font_size=FORMULA_FONT_SIZE
        ).next_to(formula, DOWN, buff=0.8)
        
        self.play(Write(formula))
        self.wait(0.5)
        self.play(Write(formula2))
        
        note = styled_text("端到端可训练，与 Flash-Attention 兼容", font_size=24, color=HIGHLIGHT_COLOR)
        note.to_edge(DOWN)
        self.play(FadeIn(note))
        
        self.wait()
