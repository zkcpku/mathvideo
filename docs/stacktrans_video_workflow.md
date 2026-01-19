# StackTrans 论文讲解视频工作流程

本文档描述从论文到动画视频的完整制作流程。

## 1. 项目目标与受众

- **视频目标**: 以 3Blue1Brown 风格讲解 StackTrans 论文
- **受众**: 课程教学 + 学术研究者
- **风格原则**:
  - 动画为主，配合旁白
  - 逐步构造，循序渐进
  - 重点高亮，清晰标注

## 2. 环境与工具准备

### 系统依赖

```bash
# LaTeX (必需，用于公式渲染)
brew install --cask mactex-no-gui
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc

# ffmpeg (必需，用于视频编码)
brew install ffmpeg

# Node.js (manim_editor 前端构建)
brew install node
```

### Python 环境

```bash
cd /path/to/math_video

# 创建虚拟环境
uv venv .venv --python 3.11
source .venv/bin/activate

# 安装依赖
uv pip install -e ./manim
uv pip install -e ./manim_editor

# 构建 Editor 前端
cd manim_editor && npm ci && npm run build_release && cd ..

# 验证
manim checkhealth
manedit --help
```

## 3. 论文素材准备

### 下载 TeX 源码

```bash
cd stacktrans/assets/paper_src
curl -L -o source.tar.gz https://arxiv.org/src/2507.15343
tar -xzf source.tar.gz
rm source.tar.gz
```

### 提取关键素材

- **公式**: 从 `.tex` 文件中复制关键公式到场景代码
- **图表**: 将论文图片复制到 `stacktrans/assets/images/`
- **结构**: 梳理论文结构，对应到视频章节

## 4. 视频结构设计

| 章节 | 场景文件 | 内容 |
|------|----------|------|
| 开场 | s01_intro.py | 标题、作者、摘要 |
| 动机 | s02_motivation.py | Transformer 局限性、PDA 方案 |
| 核心方法 | s03_stack_mechanics.py | 栈结构、Push/Pop 动画 |
| 公式推导 | s04_derivation.py | 训练目标、栈状态更新 |
| 实验结果 | s05_experiments.py | 性能对比、扩展性 |
| 代码展示 | s06_code.py | 伪代码实现 |
| 总结 | s07_conclusion.py | 贡献、未来工作 |

## 5. Manim 场景开发

### 基类使用

```python
from stacktrans.config import StackTransScene, styled_text, styled_math

class MyScene(StackTransScene):
    def construct(self):
        self.next_normal("Section_Name")  # 创建演示章节
        # ... 动画代码
```

### Section API

- `next_normal(name)`: 普通章节，演示时需要手动点击
- `next_skip(name)`: 跳过章节，自动播放
- `next_loop(name)`: 循环章节

### 调试单个场景

```bash
source .venv/bin/activate
manim render -pql stacktrans/scenes/s03_stack_mechanics.py StackMechanicsScene
```

## 6. 渲染与导出

### 开发阶段 (快速预览)

```bash
source .venv/bin/activate
manim render -ql --save_sections stacktrans/scenes/s01_intro.py IntroScene
```

### 批量渲染

```bash
source .venv/bin/activate
python stacktrans/render_all.py -ql   # 低质量
python stacktrans/render_all.py -qh   # 高质量
```

### 输出目录

```
media/
├── videos/stacktrans/       # 视频文件
├── images/stacktrans/       # 图片
└── sections/                # Section 索引 (供 Editor 使用)
```

## 7. Manim Editor 使用

### 启动编辑器

```bash
source .venv/bin/activate
manedit
# 浏览器访问 http://127.0.0.1:5000
```

### 编辑流程

1. 创建新项目
2. 导入 `media/sections/*.json`
3. 在时间线上排布 sections
4. 预览效果
5. 导出演示

### 命令行导出

```bash
manedit --quick_present_export
```

## 8. 质量检查

- [ ] 公式渲染正确
- [ ] 动画流畅，无卡顿
- [ ] Section 划分合理
- [ ] 颜色风格统一
- [ ] 旁白节奏匹配动画

## 常用命令速查

```bash
# 激活环境
source .venv/bin/activate

# 渲染单场景 (快速预览)
manim render -pql stacktrans/scenes/s01_intro.py IntroScene

# 渲染单场景 (高质量 + section)
manim render -qh --save_sections stacktrans/scenes/s01_intro.py IntroScene

# 批量渲染
python stacktrans/render_all.py -qh

# 启动编辑器
manedit

# 健康检查
manim checkhealth
```
