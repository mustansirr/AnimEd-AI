"""
Example: Building diagrams piece by piece
Use case: Flowcharts, system diagrams, concept maps
"""
from manim import *


class SimpleFlowchart(Scene):
    def construct(self):
        # Create flowchart nodes
        start = Rectangle(width=2, height=1, color=GREEN)
        start_text = Text("Start", font_size=24)
        start_node = VGroup(start, start_text)
        start_node.to_edge(UP, buff=1)

        process1 = Rectangle(width=3, height=1, color=BLUE)
        process1_text = Text("Input Data", font_size=24)
        process1_node = VGroup(process1, process1_text)
        process1_node.next_to(start_node, DOWN, buff=1)

        process2 = Rectangle(width=3, height=1, color=BLUE)
        process2_text = Text("Process", font_size=24)
        process2_node = VGroup(process2, process2_text)
        process2_node.next_to(process1_node, DOWN, buff=1)

        end = Rectangle(width=2, height=1, color=RED)
        end_text = Text("End", font_size=24)
        end_node = VGroup(end, end_text)
        end_node.next_to(process2_node, DOWN, buff=1)

        # Create arrows
        arrow1 = Arrow(start_node.get_bottom(), process1_node.get_top())
        arrow2 = Arrow(process1_node.get_bottom(), process2_node.get_top())
        arrow3 = Arrow(process2_node.get_bottom(), end_node.get_top())

        # Animate building the flowchart
        self.play(Create(start_node))
        self.play(GrowArrow(arrow1))
        self.play(Create(process1_node))
        self.play(GrowArrow(arrow2))
        self.play(Create(process2_node))
        self.play(GrowArrow(arrow3))
        self.play(Create(end_node))
        self.wait(2)


class ConceptMap(Scene):
    def construct(self):
        # Central concept
        center = Circle(radius=1, color=YELLOW, fill_opacity=0.3)
        center_text = Text("Main\nConcept", font_size=20)
        center_node = VGroup(center, center_text)

        # Related concepts
        concepts = ["Idea A", "Idea B", "Idea C", "Idea D"]
        colors = [RED, BLUE, GREEN, PURPLE]
        nodes = []
        arrows = []

        for i, (concept, color) in enumerate(zip(concepts, colors)):
            angle = i * PI / 2 + PI / 4
            pos = 3 * np.array([np.cos(angle), np.sin(angle), 0])

            node_circle = Circle(radius=0.7, color=color, fill_opacity=0.3)
            node_text = Text(concept, font_size=18)
            node = VGroup(node_circle, node_text)
            node.move_to(pos)
            nodes.append(node)

            arrow = Arrow(
                center_node.get_center(),
                node.get_center(),
                buff=1,
                color=color
            )
            arrows.append(arrow)

        # Animate
        self.play(Create(center_node))
        self.wait(0.5)

        for arrow, node in zip(arrows, nodes):
            self.play(GrowArrow(arrow), Create(node), run_time=0.7)

        self.wait(2)


class LayeredDiagram(Scene):
    def construct(self):
        # Build a layered architecture diagram
        title = Text("System Architecture", font_size=32).to_edge(UP)
        self.play(Write(title))

        # Create layers
        layers = []
        layer_names = ["Presentation", "Business Logic", "Data Access", "Database"]
        colors = [BLUE, GREEN, ORANGE, RED]

        for i, (name, color) in enumerate(zip(layer_names, colors)):
            rect = Rectangle(width=6, height=1, color=color, fill_opacity=0.5)
            text = Text(name, font_size=24)
            layer = VGroup(rect, text)
            layer.shift(DOWN * i * 1.3 + UP * 1)
            layers.append(layer)

        # Animate layers from top to bottom
        for layer in layers:
            self.play(FadeIn(layer, shift=DOWN), run_time=0.5)
            self.wait(0.3)

        # Add connecting arrows
        arrows = []
        for i in range(len(layers) - 1):
            arrow = Arrow(
                layers[i].get_bottom(),
                layers[i + 1].get_top(),
                buff=0.1,
                color=WHITE
            )
            arrows.append(arrow)

        self.play(*[GrowArrow(a) for a in arrows])
        self.wait(2)


class TreeDiagram(Scene):
    def construct(self):
        # Create a tree structure
        root = Circle(radius=0.4, color=GOLD, fill_opacity=0.7)
        root_text = Text("Root", font_size=16)
        root_node = VGroup(root, root_text)
        root_node.to_edge(UP, buff=1)

        # Level 1 children
        level1 = []
        for i, pos in enumerate([LEFT * 3, ORIGIN, RIGHT * 3]):
            node = Circle(radius=0.35, color=BLUE, fill_opacity=0.7)
            text = Text(f"L1-{i+1}", font_size=14)
            group = VGroup(node, text)
            group.move_to(pos + UP * 0.5)
            level1.append(group)

        # Level 2 children (under first level 1 node)
        level2 = []
        for i, x_offset in enumerate([LEFT * 1, RIGHT * 1]):
            node = Circle(radius=0.3, color=GREEN, fill_opacity=0.7)
            text = Text(f"L2-{i+1}", font_size=12)
            group = VGroup(node, text)
            group.move_to(LEFT * 3 + x_offset + DOWN * 1.5)
            level2.append(group)

        # Animate tree construction
        self.play(Create(root_node))

        # Connect root to level 1
        arrows_l1 = []
        for child in level1:
            arrow = Arrow(
                root_node.get_bottom(),
                child.get_top(),
                buff=0.2,
                stroke_width=2
            )
            arrows_l1.append(arrow)

        self.play(
            *[GrowArrow(a) for a in arrows_l1],
            *[Create(c) for c in level1]
        )

        # Connect first level1 to level 2
        arrows_l2 = []
        for child in level2:
            arrow = Arrow(
                level1[0].get_bottom(),
                child.get_top(),
                buff=0.2,
                stroke_width=2
            )
            arrows_l2.append(arrow)

        self.play(
            *[GrowArrow(a) for a in arrows_l2],
            *[Create(c) for c in level2]
        )

        self.wait(2)
