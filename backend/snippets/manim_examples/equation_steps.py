"""
Example: Step-by-step equation solving
Use case: Algebra tutorials, derivations, mathematical proofs
"""
from manim import *


class SolveLinearEquation(Scene):
    def construct(self):
        # Step-by-step linear equation solving
        title = Text("Solve for x", font_size=36).to_edge(UP)
        self.play(Write(title))

        # Initial equation
        eq1 = MathTex("2x + 5 = 13")
        self.play(Write(eq1))
        self.wait(1)

        # Step 1: Subtract 5
        step1_text = Text("Subtract 5 from both sides", font_size=24)
        step1_text.to_edge(DOWN)
        eq2 = MathTex("2x + 5 - 5 = 13 - 5")
        eq3 = MathTex("2x = 8")

        self.play(Write(step1_text))
        self.play(Transform(eq1, eq2))
        self.wait(0.5)
        self.play(Transform(eq1, eq3))
        self.play(FadeOut(step1_text))
        self.wait(1)

        # Step 2: Divide by 2
        step2_text = Text("Divide both sides by 2", font_size=24)
        step2_text.to_edge(DOWN)
        eq4 = MathTex("\\frac{2x}{2} = \\frac{8}{2}")
        eq5 = MathTex("x = 4", color=GREEN, font_size=48)

        self.play(Write(step2_text))
        self.play(Transform(eq1, eq4))
        self.wait(0.5)
        self.play(Transform(eq1, eq5))
        self.wait(2)


class QuadraticFormula(Scene):
    def construct(self):
        # Show quadratic formula derivation
        title = Text("Quadratic Formula", font_size=40).to_edge(UP)
        self.play(Write(title))

        equations = [
            MathTex("ax^2 + bx + c = 0"),
            MathTex("x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0"),
            MathTex("x^2 + \\frac{b}{a}x = -\\frac{c}{a}"),
            MathTex(
                "x^2 + \\frac{b}{a}x + \\frac{b^2}{4a^2} = "
                "\\frac{b^2}{4a^2} - \\frac{c}{a}"
            ),
            MathTex(
                "\\left(x + \\frac{b}{2a}\\right)^2 = "
                "\\frac{b^2 - 4ac}{4a^2}"
            ),
            MathTex("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")
        ]

        # Show first equation
        current = equations[0]
        self.play(Write(current))
        self.wait(1)

        # Transform through each step
        for next_eq in equations[1:]:
            self.play(Transform(current, next_eq), run_time=1.5)
            self.wait(1)

        # Highlight final result
        box = SurroundingRectangle(current, color=YELLOW, buff=0.2)
        self.play(Create(box))
        self.wait(2)


class HighlightTerms(Scene):
    def construct(self):
        # Demonstrate highlighting specific terms
        equation = MathTex(
            "f(x)", "=", "a", "x^2", "+", "b", "x", "+", "c"
        )
        equation.scale(1.5)
        self.play(Write(equation))
        self.wait(1)

        # Highlight quadratic term
        self.play(equation[2:4].animate.set_color(RED))
        label_a = Text("quadratic term", font_size=20, color=RED)
        label_a.next_to(equation[2:4], UP)
        self.play(FadeIn(label_a))
        self.wait(1)

        # Highlight linear term
        self.play(equation[5:7].animate.set_color(BLUE))
        label_b = Text("linear term", font_size=20, color=BLUE)
        label_b.next_to(equation[5:7], DOWN)
        self.play(FadeIn(label_b))
        self.wait(1)

        # Highlight constant term
        self.play(equation[8].animate.set_color(GREEN))
        label_c = Text("constant", font_size=20, color=GREEN)
        label_c.next_to(equation[8], UP)
        self.play(FadeIn(label_c))
        self.wait(2)
