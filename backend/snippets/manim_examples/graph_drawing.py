"""
Example: Drawing mathematical graphs
Use case: Functions, data visualization, coordinate systems
"""
from manim import *


class GraphExample(Scene):
    def construct(self):
        # Create coordinate axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 5, 1],
            x_length=6,
            y_length=5,
            axis_config={"include_tip": True, "include_numbers": True}
        )

        # Plot a quadratic function
        graph = axes.plot(lambda x: x**2, color=BLUE)
        label = axes.get_graph_label(graph, label="x^2")

        # Animate creation
        self.play(Create(axes))
        self.play(Create(graph), Write(label))
        self.wait(2)


class MultipleGraphs(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": True}
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        # Multiple functions
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)

        sin_label = axes.get_graph_label(
            sin_graph, label="\\sin(x)", x_val=2, direction=UP
        )
        cos_label = axes.get_graph_label(
            cos_graph, label="\\cos(x)", x_val=2, direction=DOWN
        )

        # Build up the visualization
        self.play(Create(axes), Write(axes_labels))
        self.wait(0.5)
        self.play(Create(sin_graph), Write(sin_label))
        self.wait(0.5)
        self.play(Create(cos_graph), Write(cos_label))
        self.wait(2)


class AreaUnderCurve(Scene):
    def construct(self):
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 10, 2],
            x_length=6,
            y_length=4
        )

        # Plot function
        graph = axes.plot(lambda x: 0.5 * x**2, color=YELLOW)

        # Show area under curve
        area = axes.get_area(
            graph,
            x_range=[1, 3],
            color=[BLUE, GREEN],
            opacity=0.5
        )

        # Labels
        graph_label = axes.get_graph_label(graph, label="f(x) = \\frac{x^2}{2}")
        area_label = MathTex("\\int_1^3 f(x) dx").next_to(area, UP)

        self.play(Create(axes))
        self.play(Create(graph), Write(graph_label))
        self.wait(1)
        self.play(FadeIn(area), Write(area_label))
        self.wait(2)
