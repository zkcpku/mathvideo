"""自定义动画效果"""
from manim import *


class StackPush(Animation):
    """栈 Push 操作动画"""
    
    def __init__(self, stack_group: VGroup, element: VMobject, **kwargs):
        self.stack_group = stack_group
        self.element = element
        super().__init__(element, **kwargs)

    def interpolate_mobject(self, alpha: float):
        pass


class StackPop(Animation):
    """栈 Pop 操作动画"""
    
    def __init__(self, stack_group: VGroup, **kwargs):
        self.stack_group = stack_group
        if len(stack_group) > 0:
            super().__init__(stack_group[-1], **kwargs)
        else:
            super().__init__(VMobject(), **kwargs)

    def interpolate_mobject(self, alpha: float):
        pass


def create_stack_visual(height: float = 3, width: float = 2) -> VGroup:
    """创建栈的视觉表示"""
    base = Rectangle(width=width, height=0.1, fill_opacity=0.8, color=TEAL)
    left_wall = Line(start=[-width/2, 0, 0], end=[-width/2, height, 0], color=TEAL, stroke_width=4)
    right_wall = Line(start=[width/2, 0, 0], end=[width/2, height, 0], color=TEAL, stroke_width=4)
    
    stack = VGroup(base, left_wall, right_wall)
    stack.move_to(ORIGIN)
    return stack


def create_stack_element(label: str, width: float = 1.8, height: float = 0.5, color=BLUE) -> VGroup:
    """创建栈元素"""
    rect = Rectangle(width=width, height=height, fill_opacity=0.8, color=color)
    text = MathTex(label, color=WHITE).scale(0.6)
    text.move_to(rect)
    return VGroup(rect, text)


def highlight_box(mobject: VMobject, color=YELLOW, buff: float = 0.1) -> SurroundingRectangle:
    """为对象添加高亮框"""
    return SurroundingRectangle(mobject, color=color, buff=buff, stroke_width=3)
