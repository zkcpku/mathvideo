# arXiv 论文讲解视频制作完整指南

本文档详细记录了从 arXiv 论文到 3Blue1Brown 风格动画视频的完整制作流程，包含环境部署、项目结构、代码示例和常见问题解决方案。

---

## 目录

1. [项目概述](#1-项目概述)
2. [环境部署](#2-环境部署)
3. [项目结构](#3-项目结构)
4. [论文素材准备](#4-论文素材准备)
5. [场景开发](#5-场景开发)
6. [渲染与导出](#6-渲染与导出)
7. [Manim Editor 使用](#7-manim-editor-使用)
8. [常见问题与解决方案](#8-常见问题与解决方案)
9. [完整示例：StackTrans 论文](#9-完整示例stacktrans-论文)

---

## 1. 项目概述

### 1.1 目标

将 arXiv 论文转换为 3Blue1Brown 风格的动画讲解视频，支持：
- 论文摘要和动机介绍
- 核心方法动画演示
- 数学公式推导动画
- 实验结果图表展示
- 代码/伪代码展示
- 交互式 Web 演示

### 1.2 技术栈

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| Manim | 0.19.2 | 数学动画引擎 |
| Manim Editor | 0.3.8 | Web 编辑器和演示工具 |
| LaTeX | BasicTeX/MacTeX | 公式渲染 |
| ffmpeg | 8.0+ | 视频编码 |
| uv | latest | Python 包管理 |

### 1.3 工作流程

```
arXiv 论文 → 下载 TeX 源码 → 提取公式/图片 → 编写 Manim 场景 → 渲染视频 → Manim Editor 编辑 → 导出演示
```

---

## 2. 环境部署

### 2.1 系统依赖安装 (macOS)

```bash
# 1. 安装 Homebrew (如果没有)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装 ffmpeg
brew install ffmpeg

# 3. 安装 LaTeX (二选一)
# 选项 A: BasicTeX (约 100MB，推荐)
brew install --cask basictex

# 选项 B: MacTeX-No-GUI (约 4GB，完整版)
brew install --cask mactex-no-gui

# 4. 配置 LaTeX PATH
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 5. 安装 Manim 需要的 LaTeX 包 (BasicTeX 用户必须)
sudo tlmgr update --self
sudo tlmgr install standalone preview doublestroke relsize fundus-calligra \
    wasysym physics dvisvgm rsfs jknapltx wasy cm-super amsmath amscls

# 6. 安装 Node.js (用于 manim_editor 前端)
brew install node

# 7. 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 8. 安装 cairo 和 pkg-config (Manim 依赖)
brew install cairo pkg-config
```

### 2.2 验证系统依赖

```bash
# 验证各组件
ffmpeg -version | head -1
latex --version | head -1
dvisvgm --version | head -1
node --version
uv --version
```

### 2.3 Python 环境配置

```bash
# 进入项目目录
cd /path/to/your/project

# 创建虚拟环境 (Python 3.11+)
uv venv .venv --python 3.11

# 激活环境
source .venv/bin/activate

# 安装 Manim (从 submodule 或 PyPI)
# 方式 A: 从本地 submodule
uv pip install -e ./manim

# 方式 B: 从 PyPI
uv pip install manim

# 安装 Manim Editor
# 方式 A: 从本地 submodule
uv pip install -e ./manim_editor

# 方式 B: 从 PyPI
uv pip install manim-editor
```

### 2.4 构建 Manim Editor 前端

```bash
cd manim_editor

# 安装 npm 依赖
npm ci

# 构建前端 (需要设置 legacy provider 兼容新版 Node.js)
NODE_OPTIONS=--openssl-legacy-provider npm run build_release

cd ..
```

### 2.5 验证安装

```bash
# 确保 PATH 包含 LaTeX
export PATH="/Library/TeX/texbin:$PATH"

# 激活环境
source .venv/bin/activate

# 验证 Manim
manim --version
manim checkhealth

# 验证 Manim Editor
manedit --help
```

**预期输出：**
- `manim --version`: Manim Community v0.19.2
- `manim checkhealth`: 所有检查通过 (特别是 latex 和 dvisvgm)
- `manedit --help`: 显示帮助信息

---

## 3. 项目结构

### 3.1 推荐目录结构

```
your_project/
├── .venv/                          # Python 虚拟环境
├── manim/                          # Manim 源码 (可选，作为 submodule)
├── manim_editor/                   # Manim Editor 源码 (可选，作为 submodule)
├── your_paper/                     # 论文视频项目
│   ├── __init__.py
│   ├── config.py                   # 3B1B 风格配置
│   ├── manim.cfg                   # Manim 渲染配置
│   ├── render_all.py               # 批量渲染脚本
│   ├── assets/
│   │   ├── paper_src/              # 论文 TeX 源码
│   │   ├── images/                 # 提取的图片
│   │   └── tex/                    # 公式宏定义
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── s01_intro.py            # 场景 1: 开场
│   │   ├── s02_xxx.py              # 场景 2: ...
│   │   └── ...
│   └── utils/
│       ├── __init__.py
│       └── animations.py           # 自定义动画
├── media/                          # 渲染输出 (自动生成)
│   ├── videos/
│   ├── images/
│   └── Tex/
├── docs/
│   └── workflow.md                 # 工作流程文档
├── start_editor.sh                 # 启动编辑器脚本
├── render_all.sh                   # 批量渲染脚本
└── AGENTS.md                       # 开发指南
```

### 3.2 添加 Git Submodules (可选)

如果需要修改 Manim 或 Manim Editor 源码：

```bash
git submodule add https://github.com/ManimCommunity/manim.git
git submodule add https://github.com/ManimCommunity/manim_editor.git
```

---

## 4. 论文素材准备

### 4.1 下载 arXiv TeX 源码

```bash
# 创建目录
mkdir -p your_paper/assets/paper_src
cd your_paper/assets/paper_src

# 下载源码 (替换 ARXIV_ID)
curl -L -o source.tar.gz https://arxiv.org/src/ARXIV_ID

# 解压
tar -xzf source.tar.gz
rm source.tar.gz

# 查看内容
ls -la
```

### 4.2 提取关键素材

**公式提取：**
1. 打开 `.tex` 文件
2. 找到关键公式 (通常在 `\begin{equation}` 或 `$$` 中)
3. 复制到场景代码的 `MathTex()` 中

**图片提取：**
1. 论文图片通常是 PDF 或 PNG 格式
2. 复制到 `assets/images/` 目录
3. 使用 `ImageMobject` 或 `SVGMobject` 加载

```bash
# 复制图片
cp *.pdf *.png ../images/

# PDF 转 PNG (如果需要)
magick figure1.pdf figure1.png
```

---

## 5. 场景开发

### 5.1 配置文件

**`manim.cfg`:**

```ini
[CLI]
media_dir = ../media
save_sections = True

[quality]
default_quality = low_quality

[output]
background_color = #1e1e2e
```

**`config.py` (3B1B 风格配置):**

```python
"""3Blue1Brown 风格配置"""
from manim import *

# 颜色方案
BACKGROUND_COLOR = "#1e1e2e"
TEXT_COLOR = "#ffffff"
HIGHLIGHT_COLOR = YELLOW
PRIMARY_COLOR = BLUE
SECONDARY_COLOR = GREEN
ACCENT_COLOR = RED

# 字体大小
TITLE_FONT_SIZE = 72
HEADING_FONT_SIZE = 48
BODY_FONT_SIZE = 36
FORMULA_FONT_SIZE = 42

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


class BaseScene(Scene):
    """场景基类"""

    def setup(self):
        self.camera.background_color = BACKGROUND_COLOR

    def next_normal(self, name: str = None):
        from manim_editor import PresentationSectionType
        self.next_section(name, PresentationSectionType.NORMAL)

    def next_skip(self, name: str = None):
        from manim_editor import PresentationSectionType
        self.next_section(name, PresentationSectionType.SKIP)

    def fade_out_all(self):
        self.play(*[FadeOut(mob) for mob in self.mobjects])
```

### 5.2 场景文件模板

**`scenes/s01_intro.py`:**

```python
"""场景1: 开场与摘要"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from manim import *
from your_paper.config import *


class IntroScene(BaseScene):
    """开场场景"""

    def construct(self):
        # Section 1: 标题
        self.next_normal("Title")
        
        title = styled_title("Your Paper Title")
        subtitle = styled_text("Subtitle or Authors", font_size=32)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        self.play(Write(title), run_time=WRITE_TIME)
        self.play(FadeIn(subtitle, shift=UP * 0.3))
        self.wait()

        # Section 2: 摘要
        self.next_normal("Abstract")
        
        self.fade_out_all()
        
        abstract_title = styled_text("Abstract", font_size=HEADING_FONT_SIZE)
        abstract_title.to_edge(UP)
        self.play(Write(abstract_title))

        # 添加关键点
        key_points = VGroup(
            styled_text("Key point 1", font_size=24),
            styled_text("Key point 2", font_size=24),
            styled_text("Key point 3", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        key_points.next_to(abstract_title, DOWN, buff=0.8)

        for point in key_points:
            bullet = Dot(radius=0.05, color=HIGHLIGHT_COLOR)
            bullet.next_to(point, LEFT, buff=0.2)
            self.play(FadeIn(bullet), Write(point), run_time=0.8)
        
        self.wait()
```

### 5.3 公式场景示例

```python
class FormulaScene(BaseScene):
    """公式推导场景"""

    def construct(self):
        self.next_normal("Formula_Intro")
        
        title = styled_text("Key Formula", font_size=HEADING_FONT_SIZE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # 显示公式
        formula = MathTex(
            r"\mathcal{L} = -\sum_{t=1}^{T} \log p(y_t | y_{<t}, x)",
            font_size=FORMULA_FONT_SIZE
        )
        self.play(Write(formula))
        self.wait()

        # 公式变换
        self.next_normal("Formula_Transform")
        
        formula2 = MathTex(
            r"\mathcal{L} = -\sum_{t=1}^{T} \log \frac{e^{s_t}}{\sum_j e^{s_j}}",
            font_size=FORMULA_FONT_SIZE
        )
        
        self.play(TransformMatchingTex(formula, formula2))
        self.wait()
```

### 5.4 代码展示场景示例

```python
class CodeScene(BaseScene):
    """代码展示场景"""

    def construct(self):
        self.next_normal("Pseudocode")
        
        title = styled_text("Implementation", font_size=HEADING_FONT_SIZE)
        title.to_edge(UP)
        self.play(Write(title))
        
        code = Code(
            code_string='''def forward(x):
    for token in x:
        h = encode(token)
        output = decode(h)
    return output''',
            language="python",
            background="window",
        ).scale(0.7).shift(DOWN * 0.3)
        
        self.play(FadeIn(code))
        self.wait()
```

### 5.5 批量渲染脚本

**`render_all.py`:**

```python
"""批量渲染所有场景"""
import subprocess
import sys
from pathlib import Path

SCENES = [
    ("scenes/s01_intro.py", ["IntroScene"]),
    ("scenes/s02_method.py", ["MethodScene"]),
    ("scenes/s03_formula.py", ["FormulaScene"]),
    # 添加更多场景...
]


def render_all(quality: str = "-ql"):
    """渲染所有场景
    
    Args:
        quality: -ql (低质量), -qm (中等), -qh (高质量), -qk (4K)
    """
    project_dir = Path(__file__).parent
    
    for scene_file, scene_names in SCENES:
        scene_path = project_dir / scene_file
        for scene_name in scene_names:
            cmd = [
                "manim", "render",
                quality,
                "--save_sections",
                str(scene_path),
                scene_name
            ]
            print(f"Rendering {scene_name}...")
            try:
                subprocess.run(cmd, check=True)
                print(f"  Done: {scene_name}")
            except subprocess.CalledProcessError as e:
                print(f"  Failed: {scene_name} - {e}")


if __name__ == "__main__":
    quality = sys.argv[1] if len(sys.argv) > 1 else "-ql"
    render_all(quality)
```

---

## 6. 渲染与导出

### 6.1 渲染命令

```bash
# 确保 PATH 正确
export PATH="/Library/TeX/texbin:$PATH"
source .venv/bin/activate

# 渲染单个场景 (低质量预览)
manim render -ql --save_sections your_paper/scenes/s01_intro.py IntroScene

# 渲染单个场景 (高质量)
manim render -qh --save_sections your_paper/scenes/s01_intro.py IntroScene

# 批量渲染
python your_paper/render_all.py -ql   # 低质量
python your_paper/render_all.py -qh   # 高质量
```

### 6.2 质量选项

| 选项 | 分辨率 | FPS | 用途 |
|------|--------|-----|------|
| `-ql` | 480p | 15 | 快速预览 |
| `-qm` | 720p | 30 | 中等质量 |
| `-qh` | 1080p | 60 | 高质量 |
| `-qk` | 4K | 60 | 最高质量 |

### 6.3 输出目录

```
media/
├── videos/
│   └── s01_intro/
│       └── 480p15/
│           ├── IntroScene.mp4           # 完整视频
│           ├── partial_movie_files/     # 分段视频
│           └── sections/
│               └── IntroScene.json      # Section 索引
├── images/                              # 图片输出
└── Tex/                                 # LaTeX 缓存
```

---

## 7. Manim Editor 使用

### 7.1 启动编辑器

```bash
export PATH="/Library/TeX/texbin:$PATH"
source .venv/bin/activate
manedit
```

浏览器打开显示的地址 (通常是 `http://127.0.0.1:5000`)

### 7.2 创建项目

1. 点击 "Create New Project"
2. 选择要包含的场景
3. 设置场景顺序 (priority)
4. 保存项目

### 7.3 编辑演示

1. 选择已创建的项目
2. 在时间线上拖动、重排 sections
3. 设置 section 类型:
   - **NORMAL**: 需要手动点击切换
   - **SKIP**: 自动播放
   - **LOOP**: 循环播放
4. 预览效果

### 7.4 导出演示

```bash
# 命令行导出
manedit --quick_present_export

# 或在 Web 界面点击 "Export Presenter"
```

导出后得到可部署的静态网页目录。

### 7.5 便捷脚本

**`start_editor.sh`:**

```bash
#!/bin/bash
export PATH="/Library/TeX/texbin:$PATH"
cd "$(dirname "$0")"
source .venv/bin/activate
manedit
```

**`render_all.sh`:**

```bash
#!/bin/bash
export PATH="/Library/TeX/texbin:$PATH"
cd "$(dirname "$0")"
source .venv/bin/activate

QUALITY="${1:--ql}"
echo "Rendering with quality: $QUALITY"
python your_paper/render_all.py "$QUALITY"
```

```bash
# 设置可执行权限
chmod +x start_editor.sh render_all.sh
```

---

## 8. 常见问题与解决方案

### 8.1 LaTeX 相关

**问题：`latex` 或 `dvisvgm` 命令找不到**

```bash
# 解决：添加 PATH
export PATH="/Library/TeX/texbin:$PATH"
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
```

**问题：LaTeX 包缺失**

```bash
# 解决：安装缺失的包
sudo tlmgr install <package_name>
```

**问题：中文字符在 MathTex 中报错**

```python
# 错误
MathTex(r"\text{中文}")

# 解决：使用 Text 代替
Text("中文")
```

### 8.2 Manim 相关

**问题：cairo 编译失败**

```bash
# 解决：安装依赖
brew install cairo pkg-config
```

**问题：模块导入错误**

```python
# 解决：在场景文件顶部添加
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

**问题：Code 组件参数错误**

```python
# 旧版 API (已废弃)
Code(code="...", font="Menlo", font_size=18)

# 新版 API
Code(code_string="...", language="python", background="window")
```

### 8.3 Manim Editor 相关

**问题：前端构建失败 (OpenSSL 错误)**

```bash
# 解决：使用 legacy provider
NODE_OPTIONS=--openssl-legacy-provider npm run build_release
```

**问题：Section 文件未生成**

```bash
# 解决：确保使用 --save_sections 参数
manim render -ql --save_sections scene.py SceneName
```

### 8.4 Homebrew 相关

**问题：缓存文件损坏**

```bash
# 解决：清理缓存并重新安装
brew cleanup --prune=all
brew install --cask basictex
```

---

## 9. 完整示例：StackTrans 论文

### 9.1 项目信息

- **论文**: StackTrans (arXiv:2507.15343)
- **主题**: 将 Transformer 扩展为下推自动机模型
- **视频风格**: 3Blue1Brown 教学风格

### 9.2 场景列表

| 场景 | 文件 | 内容 | Sections |
|------|------|------|----------|
| 1 | `s01_intro.py` | 标题、作者、摘要 | Title, Authors, Abstract |
| 2 | `s02_motivation.py` | Transformer 局限性、PDA 方案 | Transformer_Limitation, PDA_Solution |
| 3 | `s03_stack_mechanics.py` | 栈结构、Push/Pop 动画 | Stack_Structure, Push_Operation, Pop_Operation, Differentiable_Stack |
| 4 | `s04_derivation.py` | 训练目标、栈状态更新 | Loss_Function, Stack_State, Stack_Update |
| 5 | `s05_experiments.py` | 性能对比、扩展性 | Results_Overview, Highlight_Best, Scaling |
| 6 | `s06_code.py` | 伪代码实现 | Pseudocode, Key_Lines, Integration |
| 7 | `s07_conclusion.py` | 贡献总结、未来工作 | Summary, Future, Thanks |

### 9.3 使用命令

```bash
# 进入项目目录
cd /path/to/math_video

# 启动编辑器
./start_editor.sh

# 批量渲染 (低质量)
./render_all.sh -ql

# 批量渲染 (高质量)
./render_all.sh -qh

# 渲染单个场景
export PATH="/Library/TeX/texbin:$PATH"
source .venv/bin/activate
manim render -ql --save_sections stacktrans/scenes/s03_stack_mechanics.py StackMechanicsScene
```

### 9.4 项目文件

```
math_video/
├── .venv/                          # Python 环境
├── manim/                          # Manim 源码 (submodule)
├── manim_editor/                   # Editor 源码 (submodule)
├── stacktrans/                     # StackTrans 视频项目
│   ├── config.py                   # 3B1B 风格配置
│   ├── manim.cfg                   # Manim 配置
│   ├── render_all.py               # 批量渲染
│   ├── assets/paper_src/           # 论文 TeX 源码
│   ├── scenes/                     # 7 个场景文件
│   └── utils/animations.py         # 动画工具
├── media/videos/                   # 渲染输出
├── docs/                           # 文档
├── start_editor.sh                 # 启动脚本
└── render_all.sh                   # 渲染脚本
```

---

## 附录 A: 快速命令参考

```bash
# 环境激活
export PATH="/Library/TeX/texbin:$PATH"
source .venv/bin/activate

# 验证环境
manim checkhealth

# 渲染场景
manim render -ql --save_sections <file.py> <SceneName>

# 启动编辑器
manedit

# 查看帮助
manim --help
manedit --help
```

---

## 附录 B: 资源链接

- [Manim 官方文档](https://docs.manim.community/)
- [Manim Editor 文档](https://docs.editor.manim.community/)
- [3Blue1Brown YouTube](https://www.youtube.com/c/3blue1brown)
- [arXiv](https://arxiv.org/)
- [LaTeX 数学符号](https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols)

---

*文档版本: 1.0*
*最后更新: 2026-01-19*
*作者: 基于 StackTrans 论文视频制作经验整理*
