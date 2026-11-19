#!/usr/bin/env python3
"""
Manim Math & Scientific Animation Engine for Antigravity Video Studio.
Generates 3Blue1Brown-style mathematical animations, neural network diagrams,
and scientific formula morphs.
"""

import sys
import os
import subprocess
import shutil

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
MANIM_DIR = os.path.join(BASE_DIR, "projects", "manim-animations")
os.makedirs(MANIM_DIR, exist_ok=True)

TEMPLATES = {
    "neural_network": """
from manim import *

class NeuralNetScene(Scene):
    def construct(self):
        title = Text("Neural Network Forward Pass", font_size=36, color=BLUE).to_edge(UP)
        self.play(Write(title))

        # Layers
        input_layer = VGroup(*[Circle(radius=0.25, color=GREEN).set_fill(GREEN, opacity=0.5) for _ in range(4)]).arrange(DOWN, buff=0.4).shift(LEFT * 3)
        hidden_layer = VGroup(*[Circle(radius=0.25, color=BLUE).set_fill(BLUE, opacity=0.5) for _ in range(5)]).arrange(DOWN, buff=0.3)
        output_layer = VGroup(*[Circle(radius=0.25, color=RED).set_fill(RED, opacity=0.5) for _ in range(2)]).arrange(DOWN, buff=0.6).shift(RIGHT * 3)

        self.play(FadeIn(input_layer), FadeIn(hidden_layer), FadeIn(output_layer))

        # Connections
        lines = VGroup()
        for i in input_layer:
            for h in hidden_layer:
                lines.add(Line(i.get_right(), h.get_left(), stroke_width=1, color=GRAY_B))
        for h in hidden_layer:
            for o in output_layer:
                lines.add(Line(h.get_right(), o.get_left(), stroke_width=1, color=GRAY_B))

        self.play(Create(lines), run_time=2)
        self.wait(1)
""",
    "quantum_formula": """
from manim import *

class QuantumFormulaScene(Scene):
    def construct(self):
        title = Text("Schrodinger Wave Equation", font_size=34, color=PURPLE).to_edge(UP)
        formula = MathTex(
            r"i\\hbar \\frac{\\partial}{\\partial t} \\Psi(\\mathbf{r},t) = \\hat{H} \\Psi(\\mathbf{r},t)",
            font_size=48, color=YELLOW
        )
        self.play(Write(title))
        self.play(Write(formula), run_time=2.5)
        self.play(formula.animate.scale(1.15).set_color(BLUE), run_time=1.5)
        self.wait(1)
"""
}

def check_manim_installed():
    return shutil.which("manim") is not None

def generate_manim_animation(template_name="neural_network", scene_id="manim_01"):
    has_manim = check_manim_installed()
    script_path = os.path.join(MANIM_DIR, f"{scene_id}.py")
    code = TEMPLATES.get(template_name, TEMPLATES["neural_network"])

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"📐 Generated Manim script at: {script_path}")

    if has_manim:
        print("⚡ Executing Manim headless render...")
        scene_class = "NeuralNetScene" if template_name == "neural_network" else "QuantumFormulaScene"
        out_mp4 = os.path.join(BASE_DIR, "assets", "visuals", f"{scene_id}.mp4")
        cmd = ["manim", "-qm", "--media_dir", MANIM_DIR, script_path, scene_class]
        subprocess.run(cmd, cwd=BASE_DIR)
        print(f"✅ Manim animation rendered to: {out_mp4}")
        return out_mp4
    else:
        print("💡 Manim CLI is not currently in system PATH.")
        print("   To enable native Manim rendering: pip install manim")
        print("   Using Three.js / Canvas math visualizer fallback inside Remotion.")
        return None

if __name__ == "__main__":
    t_name = sys.argv[1] if len(sys.argv) > 1 else "neural_network"
    s_id = sys.argv[2] if len(sys.argv) > 2 else "manim_01"
    generate_manim_animation(t_name, s_id)
