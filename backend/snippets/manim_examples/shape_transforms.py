"""
Example: Geometric shape animations
Use case: Geometry lessons, transformations, visual proofs
"""
from manim import *


class BasicShapes(Scene):
    def construct(self):
        # Create basic shapes
        circle = Circle(radius=1, color=BLUE, fill_opacity=0.5)
        square = Square(side_length=2, color=RED, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)

        # Position them
        circle.shift(LEFT * 3)
        triangle.shift(RIGHT * 3)

        # Animate appearance
        self.play(Create(circle))
        self.play(DrawBorderThenFill(square))
        self.play(GrowFromCenter(triangle))
        self.wait(1)

        # Transform circle into square
        self.play(Transform(circle, square.copy().shift(LEFT * 3)))
        self.wait(2)


class ShapeGrouping(Scene):
    def construct(self):
        # Create a group of shapes
        shapes = VGroup(
            Circle(radius=0.5, color=RED),
            Square(side_length=1, color=GREEN),
            Triangle(color=BLUE)
        ).arrange(RIGHT, buff=0.5)

        # Animate the group together
        self.play(Create(shapes))
        self.wait(0.5)

        # Move entire group
        self.play(shapes.animate.shift(UP * 2))
        self.wait(0.5)

        # Scale the group
        self.play(shapes.animate.scale(1.5))
        self.wait(0.5)

        # Rotate the group
        self.play(Rotate(shapes, angle=PI / 2))
        self.wait(1)


class GeometricProof(Scene):
    def construct(self):
        # Pythagorean theorem visual proof
        # Create a right triangle
        triangle = Polygon(
            ORIGIN, RIGHT * 3, RIGHT * 3 + UP * 4,
            color=WHITE, fill_opacity=0.3
        )

        # Labels for sides
        a_label = MathTex("a").next_to(triangle, DOWN)
        b_label = MathTex("b").next_to(triangle, RIGHT)
        c_label = MathTex("c").move_to(
            (ORIGIN + RIGHT * 3 + UP * 4) / 2 + LEFT * 0.5 + UP * 0.3
        )

        # Squares on each side
        a_square = Square(side_length=3, color=RED, fill_opacity=0.3)
        a_square.next_to(triangle, DOWN, buff=0)

        b_square = Square(side_length=4, color=BLUE, fill_opacity=0.3)
        b_square.next_to(triangle, RIGHT, buff=0)

        # Build the proof
        self.play(Create(triangle))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(1)

        self.play(DrawBorderThenFill(a_square))
        self.play(DrawBorderThenFill(b_square))
        self.wait(1)

        # Show equation
        equation = MathTex("a^2 + b^2 = c^2").to_edge(UP)
        self.play(Write(equation))
        self.wait(2)


class MorphingShapes(Scene):
    def construct(self):
        # Demonstrate shape morphing
        circle = Circle(radius=1.5, color=PURPLE, fill_opacity=0.7)
        square = Square(side_length=3, color=ORANGE, fill_opacity=0.7)
        triangle = RegularPolygon(n=3, color=TEAL, fill_opacity=0.7)
        triangle.scale(2)

        self.play(Create(circle))
        self.wait(1)

        self.play(Transform(circle, square), run_time=1.5)
        self.wait(1)

        self.play(Transform(circle, triangle), run_time=1.5)
        self.wait(2)
