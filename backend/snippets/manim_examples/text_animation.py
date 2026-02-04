"""
Example: Text appearing and transforming
Use case: Introducing concepts, showing definitions
"""
from manim import *


class TextIntro(Scene):
    def construct(self):
        # Title appears with write animation
        title = Text("Pythagorean Theorem", font_size=48)
        self.play(Write(title))
        self.wait(1)

        # Transform title to equation
        equation = MathTex("a^2 + b^2 = c^2")
        self.play(Transform(title, equation))
        self.wait(2)


class MultipleTextStyles(Scene):
    def construct(self):
        # Different text styles
        heading = Text("Key Concept", font_size=42, color=BLUE)
        heading.to_edge(UP)

        definition = Text(
            "A function maps inputs to outputs",
            font_size=28
        )
        definition.next_to(heading, DOWN, buff=0.5)

        # Animate sequentially
        self.play(FadeIn(heading, shift=DOWN))
        self.play(Write(definition))
        self.wait(1)

        # Highlight with color change
        self.play(definition.animate.set_color(YELLOW))
        self.wait(1)


class EquationReveal(Scene):
    def construct(self):
        # Reveal equation part by part
        eq_parts = VGroup(
            MathTex("E"),
            MathTex("="),
            MathTex("m"),
            MathTex("c^2")
        ).arrange(RIGHT, buff=0.1)

        for part in eq_parts:
            self.play(Write(part), run_time=0.5)
            self.wait(0.3)

        self.wait(1)

        # Group and transform
        full_eq = MathTex("E = mc^2", font_size=72)
        self.play(Transform(eq_parts, full_eq))
        self.wait(2)
