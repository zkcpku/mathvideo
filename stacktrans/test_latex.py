"""测试 LaTeX 公式渲染"""
from manim import *

class MathTest(Scene):
    def construct(self):
        self.camera.background_color = "#1e1e2e"
        
        title = Text("StackTrans", font_size=72, color=WHITE)
        self.play(Write(title))
        self.wait(0.5)
        self.play(title.animate.to_edge(UP))
        
        formula = MathTex(
            r"\mathcal{L} = -\sum_{t=1}^{T} \log p(y_t | y_{<t}, x, s_t)",
            font_size=48
        )
        self.play(Write(formula))
        self.wait()
        
        note = Text("可微分栈操作", font_size=32, color=YELLOW)
        note.next_to(formula, DOWN, buff=0.8)
        self.play(FadeIn(note))
        self.wait()
