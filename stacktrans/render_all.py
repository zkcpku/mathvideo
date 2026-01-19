"""批量渲染所有场景"""
import subprocess
import sys
from pathlib import Path

SCENES = [
    ("scenes/s01_intro.py", ["IntroScene"]),
    ("scenes/s02_motivation.py", ["MotivationScene"]),
    ("scenes/s03_stack_mechanics.py", ["StackMechanicsScene"]),
    ("scenes/s04_derivation.py", ["DerivationScene"]),
    ("scenes/s05_experiments.py", ["ExperimentsScene"]),
    ("scenes/s06_code.py", ["CodeScene"]),
    ("scenes/s07_conclusion.py", ["ConclusionScene"]),
]


def render_all(quality: str = "-ql"):
    """渲染所有场景
    
    Args:
        quality: -ql (低质量快速), -qm (中等), -qh (高质量), -qk (4K)
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
            print(f"Rendering {scene_name} from {scene_file}...")
            try:
                subprocess.run(cmd, check=True)
                print(f"  Done: {scene_name}")
            except subprocess.CalledProcessError as e:
                print(f"  Failed: {scene_name} - {e}")


if __name__ == "__main__":
    quality = sys.argv[1] if len(sys.argv) > 1 else "-ql"
    render_all(quality)
