"""简单测试场景 - 不使用 LaTeX"""
from manim import *

class SimpleTest(Scene):
    def construct(self):
        self.camera.background_color = "#1e1e2e"
        
        circle = Circle(color=BLUE, fill_opacity=0.5)
        square = Square(color=RED, fill_opacity=0.5)
        
        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.play(FadeOut(circle))
        
        text = Text("StackTrans", font_size=72, color=WHITE)
        self.play(Write(text))
        self.wait()
