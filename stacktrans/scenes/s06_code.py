"""场景6: 代码展示"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from stacktrans.config import *


class CodeScene(StackTransScene):
    """代码/伪代码展示"""

    def construct(self):
        self.next_normal("Pseudocode")
        
        title = styled_text("核心实现", font_size=HEADING_FONT_SIZE).to_edge(UP)
        self.play(Write(title))
        
        code = Code(
            code_string='''def stack_forward(x, stack):
    for t, token in enumerate(x):
        h_t = transformer_layer(token)
        action = predict_action(h_t, stack)
        
        if action == PUSH:
            stack = push(stack, h_t)
        elif action == POP:
            stack = pop(stack)
        
        output[t] = decode(h_t, stack.top())
    
    return output''',
            language="python",
            background="window",
        ).scale(0.7).shift(DOWN * 0.3)
        
        self.play(FadeIn(code))
        self.wait()

        self.next_normal("Key_Lines")
        
        note1 = styled_text("predict_action: 预测栈操作", font_size=20, color=HIGHLIGHT_COLOR)
        note1.next_to(code, DOWN, buff=0.3)
        
        self.play(Write(note1))
        self.wait()

        self.next_normal("Integration")
        
        note2 = styled_text("无缝集成现有 Transformer 代码库", font_size=24, color=GREEN)
        note2.next_to(note1, DOWN, buff=0.3)
        
        self.play(Write(note2))
        self.wait()
