"""StackTrans 视频项目配置 - 3Blue1Brown 风格"""
from manim import *

# 颜色方案 (3B1B 风格)
BACKGROUND_COLOR = "#1e1e2e"
TEXT_COLOR = "#ffffff"
HIGHLIGHT_COLOR = YELLOW
PRIMARY_COLOR = BLUE
SECONDARY_COLOR = GREEN
ACCENT_COLOR = RED
STACK_COLOR = TEAL

# 字体大小
TITLE_FONT_SIZE = 72
HEADING_FONT_SIZE = 48
BODY_FONT_SIZE = 36
FORMULA_FONT_SIZE = 42
CODE_FONT_SIZE = 24

# 动画时长
FADE_TIME = 0.5
WRITE_TIME = 1.5
TRANSFORM_TIME = 1.0


def styled_text(text: str, **kwargs) -> Text:
    defaults = {"color": TEXT_COLOR, "font_size": BODY_FONT_SIZE}
    defaults.update(kwargs)
    return Text(text, **defaults)


def styled_math(tex: str, **kwargs) -> MathTex:
    defaults = {"color": TEXT_COLOR, "font_size": FORMULA_FONT_SIZE}
    defaults.update(kwargs)
    return MathTex(tex, **defaults)


def styled_title(text: str, **kwargs) -> Text:
    defaults = {"color": TEXT_COLOR, "font_size": TITLE_FONT_SIZE, "weight": BOLD}
    defaults.update(kwargs)
    return Text(text, **defaults)


class StackTransScene(Scene):
    """StackTrans 视频场景基类"""

    def setup(self):
        self.camera.background_color = BACKGROUND_COLOR

    def next_normal(self, name: str = None):
        from manim_editor import PresentationSectionType
        self.next_section(name, PresentationSectionType.NORMAL)

    def next_skip(self, name: str = None):
        from manim_editor import PresentationSectionType
        self.next_section(name, PresentationSectionType.SKIP)

    def next_loop(self, name: str = None):
        from manim_editor import PresentationSectionType
        self.next_section(name, PresentationSectionType.LOOP)

    def fade_out_all(self):
        self.play(*[FadeOut(mob) for mob in self.mobjects])
