from manim import *
# Explicit color imports to satisfy IDE static analysis:
from manim import YELLOW, BLUE, GREEN, WHITE, RED, GRAY, BLACK, TEAL, BLUE_D, GREEN_C, BLUE_E
# Explicit symbol imports to satisfy IDE static analysis:
from manim import (
    AnimationGroup, ArcBetweenPoints, Arrow, Axes, BarChart, Circle,
    Circumscribe, Create, DL, DOWN, DR, Dot, DoubleArrow, Ellipse,
    FadeIn, FadeOut, Flash, GrowArrow, GrowFromCenter, Indicate,
    LEFT, Line, MathTex, Matrix, MoveAlongPath, NumberLine, ORIGIN,
    PI, Polygon, RIGHT, Rectangle, ReplacementTransform, RightAngle,
    Square, Succession, Text, Transform, UL, UP, UR, UpdateFromFunc,
    VGroup, Wiggle, Write
)
import numpy as np

class VisualGrammar:
    max_objects_per_scene = 8
    max_text_lines = 2
    min_spacing = 0.3
    title_zone_reserved = True
    subtitle_zone_reserved = True
    colors = {
        "primary": YELLOW,
        "secondary": BLUE,
        "accent": GREEN,
        "background": "#0F0F0F",
        "text": WHITE
    }

def filter_manim_kwargs(kwargs):
    manim_keys = {"color", "fill_opacity", "stroke_width", "stroke_color", "fill_color", "z_index", "opacity"}
    return {k: v for k, v in kwargs.items() if k in manim_keys}

STEM_BLUEPRINTS = {
    "mathematics_theorem_law": {
        "components": ["RightTriangleDiagram"],
        "required_visual_elements": ["shape", "equation_label", "angle_markers"],
        "use_mathtex": True
    },
    "mathematics_area_proof": {
        "components": ["AreaProofDiagram"],
        "required_visual_elements": ["geometric_shape", "area_subdivisions", "area_formula"],
        "use_mathtex": True
    },
    "chemistry_molecule": {
        "components": ["MoleculeDiagram"],
        "required_visual_elements": ["atoms", "bonds"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "physics_particle": {
        "components": ["ParticleDiagram"],
        "required_visual_elements": ["particles", "interaction_vectors"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "physics_forces_multiple": {
        "components": ["ForceVectorDiagram"],
        "required_visual_elements": ["center_mass", "force_vectors", "vector_labels"],
        "use_mathtex": True
    },
    "physics_surface_tension": {
        "components": ["MoleculeDiagram", "ForceVectorDiagram", "LiquidSurfaceDiagram"],
        "required_visual_elements": ["water_surface", "bulk_molecules", "surface_molecules", "force_vectors"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "computer_science_graph": {
        "components": ["GraphDiagram"],
        "required_visual_elements": ["nodes", "edges", "labels"],
        "use_mathtex": False
    },
    "computer_science_tree": {
        "components": ["TreeDiagram"],
        "required_visual_elements": ["root", "children", "hierarchy_edges"],
        "use_mathtex": False
    },
    "mathematics_coordinate_geometry": {
        "components": ["CoordinateGeometryDiagram"],
        "required_visual_elements": ["axes", "points", "line_or_shape"],
        "use_mathtex": True
    },
    "physics_electric_field": {
        "components": ["ElectricFieldDiagram"],
        "required_visual_elements": ["charges", "field_lines", "force_vectors"],
        "use_mathtex": True
    },
    "physics_wave": {
        "components": ["WaveDiagram"],
        "required_visual_elements": ["axes", "sine_wave", "amplitude_marker", "wavelength_marker"],
        "use_mathtex": True
    },
    "chemistry_atom": {
        "components": ["AtomDiagram"],
        "required_visual_elements": ["nucleus", "electron_orbits", "electrons"],
        "use_mathtex": False
    },
    "chemistry_reaction": {
        "components": ["ReactionDiagram"],
        "required_visual_elements": ["reactants", "products", "yield_arrow"],
        "use_mathtex": True
    }
}

class GlobalTransitionEngine:
    """
    Forces all generative assets to utilize Manim's native smooth interpolation
    instead of hard visual cuts.
    """
    @staticmethod
    def apply_global_entry_logic(mobject, entry_style="smooth"):
        if entry_style == "smooth":
            return FadeIn(mobject, shift=UP*0.2, scale=0.8)
        return FadeIn(mobject)

    @staticmethod
    def transition_between_states(old_group, new_group):
        # Automatically handles morphing between abstract concepts and real-world examples
        return ReplacementTransform(old_group, new_group, run_time=1.5)

class AnimatableComponent(VGroup):
    def get_intro_animations(self, *args, **kwargs):
        if not self.submobjects:
            return [GlobalTransitionEngine.apply_global_entry_logic(self)]
        animations = [GlobalTransitionEngine.apply_global_entry_logic(obj) for obj in self.submobjects]
        return [AnimationGroup(*animations, lag_ratio=0.1)]

    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self)]

    def get_transformation_animations(self, *args, **kwargs):
        return [Wiggle(self)]

    def get_explanation_animations(self, *args, **kwargs):
        return [Circumscribe(self)]

    def get_focus_animations(self, *args, **kwargs):
        return [Flash(self.get_center())]

class ImageLabelCard(AnimatableComponent):
    def __init__(self, image_path: str = "", label: str = "", **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.image_path = image_path
        self.label_text = label
        
        self.group = VGroup()
        
        try:
            if not image_path:
                raise ValueError("No image path provided")
            import os
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found at {image_path}")
            
            self.img = ImageMobject(image_path)
            self.img.scale_to_fit_height(3.0)
        except Exception as e:
            # Fallback to textured square placeholder
            base_sq = Square(side_length=3.0, fill_color=VisualGrammar.colors["surface"], fill_opacity=0.8, stroke_color=RED, stroke_width=4)
            warning_text = SmartText("Image Missing", font_size=20, color=RED).move_to(base_sq.get_center())
            self.img = VGroup(base_sq, warning_text)
            
        self.group.add(self.img)
        
        if label:
            lbl = SmartText(str(label), font_size=24).next_to(self.img, DOWN, buff=0.5)
            self.group.add(lbl)
            
        self.add(self.group)
        
    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.group, shift=UP*0.2)]
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self)]
    def get_transformation_animations(self, *args, **kwargs):
        return [AnimationGroup(self.animate.scale(1.05), self.animate.scale(1/1.05), lag_ratio=1)]
    def get_explanation_animations(self, *args, **kwargs):
        return [Circumscribe(self)]
    def get_focus_animations(self, *args, **kwargs):
        return [Flash(self.get_center())]

class SmartText(AnimatableComponent):
    def __init__(self, text, blueprint_context=None, **kwargs):
        super().__init__()
        text_str = str(text)
        use_mathtex = False
        
        if blueprint_context and blueprint_context in STEM_BLUEPRINTS:
            use_mathtex = STEM_BLUEPRINTS[blueprint_context].get("use_mathtex", False)
            
        if use_mathtex:
            self.t = MathTex(text_str, color=kwargs.get('color', WHITE))
        else:
            font_size = kwargs.pop('font_size', 24)
            self.t = Text(text_str, font_size=font_size, **kwargs)
            
        self.add(self.t)

class TitleCard(AnimatableComponent):
    def __init__(self, title_text="Title", subtitle_text=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.title = SmartText(str(title_text)[:50], font_size=48, color=VisualGrammar.colors["primary"])
        self.add(self.title)
        if subtitle_text:
            self.subtitle = SmartText(str(subtitle_text)[:80], font_size=32, color=VisualGrammar.colors["text"])
            self.add(self.subtitle)
            self.arrange(DOWN, buff=VisualGrammar.min_spacing)

class FlowChart(AnimatableComponent):
    def __init__(self, steps=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not steps:
            steps = ["Step 1", "Step 2", "Step 3"]
                
        self.nodes = VGroup(*[
            SmartText(str(step)[:30], font_size=24, color=BLACK).add_background_rectangle(color=VisualGrammar.colors["secondary"], opacity=0.8, buff=0.2)
            for step in steps[:VisualGrammar.max_objects_per_scene]
        ])
        self.nodes.arrange(DOWN, buff=0.8)
        self.edges = VGroup()
        for i in range(len(self.nodes)-1):
            arrow = Arrow(self.nodes[i].get_bottom(), self.nodes[i+1].get_top(), buff=0.1, color=WHITE)
            self.edges.add(arrow)
        self.add(self.nodes, self.edges)

class GraphPlot(AnimatableComponent):
    def __init__(self, x_range=[0,10,1], y_range=[0,10,1], function=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not function:
            function = "x**2"
        self.axes = Axes(x_range=x_range, y_range=y_range, x_length=6, y_length=4)
        self.add(self.axes)
        def safe_eval(x):
            try: return eval(function, {"__builtins__": {}}, {"x": x, "np": np, "math": np})
            except: return x**2
        self.plot = self.axes.plot(safe_eval, color=VisualGrammar.colors["accent"])
        self.add(self.plot)
        self.points = VGroup()
        self.line = VGroup()

class TreeDiagram(AnimatableComponent):
    def __init__(self, root_label=None, children_labels=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not root_label:
            root_label = "Root"
        if not children_labels:
            children_labels = ["Child A", "Child B"]
            
        self.root = SmartText(str(root_label)[:30], font_size=32, color=BLACK).add_background_rectangle(color=VisualGrammar.colors["primary"])
        self.children_nodes = VGroup(*[SmartText(str(label)[:20], font_size=24, color=BLACK).add_background_rectangle(color=VisualGrammar.colors["secondary"]) for label in children_labels[:VisualGrammar.max_objects_per_scene]])
        self.children_nodes.arrange(RIGHT, buff=0.5)
        self.children_nodes.next_to(self.root, DOWN, buff=1.5)
        self.edges = VGroup()
        for child in self.children_nodes:
            self.edges.add(Line(self.root.get_bottom(), child.get_top(), color=WHITE))
            
        # Hide children and edges initially for progressive insertion
        for child in self.children_nodes:
            child.target_pos = child.get_center()
            child.move_to(self.root.get_center())
            child.set_opacity(0)
            
        self.edges.set_opacity(0)
        self.add(self.root, self.children_nodes, self.edges)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.root, shift=DOWN)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.root)]
        
    def get_transformation_animations(self, *args, **kwargs):
        # Enforce Animation Chaining: Travel down the tree sequentially via intermediate points
        animations = []
        for child, edge in zip(self.children_nodes, self.edges):
            midpoint = (self.root.get_center() + child.target_pos) / 2
            node_travel = Succession(
                child.animate.set_opacity(1).move_to(midpoint),
                child.animate.move_to(child.target_pos)
            )
            edge_reveal = Create(edge)
            animations.append(AnimationGroup(node_travel, edge_reveal, lag_ratio=0.5))
            
        return [AnimationGroup(*animations, lag_ratio=0.8)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.edges)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.children_nodes[0] if self.children_nodes else self)]

class NetworkDiagram(AnimatableComponent):
    def __init__(self, layers=None, layer_labels=None, animate_flow=False, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        print(f"NetworkDiagram received kwargs: {kwargs}")
        if layers is None:
            layers = [["x1", "x2"], ["h1", "h2", "h3"], ["y1"]]
            
        # Always default to proper 3-layer network if data is wrong
        if len(layers) < 2 or max(len(l) for l in layers) < 2:
            layers = [["x1","x2","x3"], ["h1","h2","h3"], ["out"]]
            layer_labels = ["Input", "Hidden", "Output"]
            
        self.layer_groups = VGroup()
        self.all_nodes = []
        for layer_nodes in layers:
            col = VGroup()
            for node_name in layer_nodes:
                circ = Circle(radius=0.4, color=VisualGrammar.colors["primary"], fill_opacity=0.8)
                label = SmartText(str(node_name)[:10], font_size=20, color=BLACK)
                col.add(VGroup(circ, label))
            col.arrange(DOWN, buff=0.5)
            self.layer_groups.add(col)
            self.all_nodes.append(col)
            
        self.layer_groups.arrange(RIGHT, buff=2.0)
        
        self.edges = VGroup()
        import random
        # Parse weights if provided: list of lists corresponding to layers
        weights_data = kwargs.get("weights", None)
        
        for i in range(len(self.all_nodes)-1):
            src_layer = self.all_nodes[i]
            tgt_layer = self.all_nodes[i+1]
            for s_idx, src in enumerate(src_layer):
                for t_idx, tgt in enumerate(tgt_layer):
                    try:
                        weight = weights_data[i][s_idx][t_idx] if weights_data else random.randint(1, 5)
                    except (IndexError, TypeError):
                        weight = random.randint(1, 5)
                    self.edges.add(Line(src.get_center(), tgt.get_center(), stroke_width=weight, stroke_opacity=0.4, z_index=-1))
                    
        self.add(self.edges, self.layer_groups)
        
        layer_labels = layer_labels or []
        while len(layer_labels) < len(layers):
            layer_labels.append(f"Layer {len(layer_labels)+1}")
        layer_labels = layer_labels[:len(layers)]
        
        labels_group = VGroup()
        for i, lab in enumerate(layer_labels):
            t = SmartText(str(lab), font_size=24, color=VisualGrammar.colors["secondary"]).next_to(self.layer_groups[i], DOWN, buff=0.5)
            labels_group.add(t)
        self.add(labels_group)
            
        print(f"NetworkDiagram created with layers: {layers}")
        print(f"Total mobjects: {len(self.submobjects)}")

    def get_transformation_animations(self, *args, **kwargs):
        # Pulse data signals physically through connections layer by layer
        anims = []
        for i in range(len(self.all_nodes) - 1):
            layer_pulses = []
            for src in self.all_nodes[i]:
                for tgt in self.all_nodes[i+1]:
                    pulse = Dot(src.get_center(), radius=0.08, color=YELLOW)
                    travel = Succession(
                        FadeIn(pulse, run_time=0.1),
                        pulse.animate(run_time=0.6).move_to(tgt.get_center()),
                        FadeOut(pulse, run_time=0.1)
                    )
                    layer_pulses.append(travel)
            anims.append(AnimationGroup(*layer_pulses))
        return anims

class GraphDiagram(AnimatableComponent):
    def __init__(self, nodes=None, edges=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        blueprint = "computer_science_graph"
        if not nodes:
            nodes = ["A", "B", "C", "D"]
        if not edges:
            edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
            
        self.node_mobjects = {}
        self.nodes_group = VGroup()
        
        import math
        radius = 2.0
        for i, node in enumerate(nodes[:VisualGrammar.max_objects_per_scene]):
            angle = i * (2 * math.pi / min(len(nodes), VisualGrammar.max_objects_per_scene))
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            
            circ = Circle(radius=0.4, color=VisualGrammar.colors["primary"]).set_fill(VisualGrammar.colors["primary"], opacity=0.8).move_to(RIGHT*x + UP*y)
            label = SmartText(str(node)[:5], font_size=20, color=BLACK, blueprint_context=blueprint).move_to(circ.get_center())
            node_grp = VGroup(circ, label)
            self.node_mobjects[str(node)] = node_grp
            self.nodes_group.add(node_grp)
            
        self.edges_group = VGroup()
        for src, tgt in edges:
            if str(src) in self.node_mobjects and str(tgt) in self.node_mobjects:
                line = Line(self.node_mobjects[str(src)].get_center(), self.node_mobjects[str(tgt)].get_center(), stroke_width=2, color=WHITE, z_index=-1)
                self.edges_group.add(line)
                
        self.add(self.edges_group, self.nodes_group)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.nodes_group, scale=0.5), Create(self.edges_group)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.nodes_group)]
        
    def get_transformation_animations(self, *args, **kwargs):
        return [Wiggle(self.nodes_group)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.edges_group)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.nodes_group[0] if self.nodes_group else self)]

class TimelineDiagram(AnimatableComponent):
    def __init__(self, events=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if events is None:
            lists = [v for k, v in kwargs.items() if isinstance(v, (list, tuple))]
            events = lists[0] if lists else ["Event 1", "Event 2"]
            
        max_events = min(len(events), VisualGrammar.max_objects_per_scene)
        self.line = NumberLine(x_range=[0, max_events+1, 1], length=10)
        self.events_group = VGroup()
        for i, ev in enumerate(events[:max_events]):
            dot = Dot(self.line.number_to_point(i+1), color=VisualGrammar.colors["accent"])
            label = SmartText(str(ev)[:15], font_size=20).next_to(dot, UP)
            self.events_group.add(dot, label)
        self.add(self.line, self.events_group)

class ArrayDiagram(AnimatableComponent):
    def __init__(self, elements=None, highlight_index=None, target=None, found_index=None, label=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not elements:
            elements = [1, 2, 3, 4, 5]
            
        self.cells = VGroup()
        self.labels = VGroup()
        for i, el in enumerate(elements[:12]):
            color = VisualGrammar.colors["secondary"]
            if found_index is not None and i == found_index:
                color = VisualGrammar.colors["accent"]
            elif highlight_index is not None and i == highlight_index:
                color = VisualGrammar.colors["primary"]
                
            rect = Square(side_length=1.0, color=WHITE).set_fill(color, opacity=0.5)
            text = SmartText(str(el)[:10], font_size=32, color=BLACK)
            idx = SmartText(str(i), font_size=20, color=GRAY)
            cell = VGroup(rect, text)
            self.cells.add(cell)
            self.labels.add(idx)
        self.cells.arrange(RIGHT, buff=0)
        
        # Re-align indices after arrangement
        for i, cell in enumerate(self.cells):
            self.labels[i].next_to(cell, DOWN, buff=0.1)
            
        self.add(self.cells, self.labels)
        if label:
            lbl_text = SmartText(str(label), font_size=24, color=WHITE).next_to(self, UP, buff=0.5)
            self.add(lbl_text)

class SummaryDiagram(AnimatableComponent):
    def __init__(self, points=None, learning_goal=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if points is None:
            key_takeaways = kwargs.get("key_takeaways")
            if key_takeaways:
                points = key_takeaways
            else:
                lists = [v for k, v in kwargs.items() if isinstance(v, (list, tuple))]
                points = lists[0] if lists else []
                
        if not points:
            learning_goal = learning_goal or kwargs.get("learning_goal", "Understand the concept")
            points = [
                f"Key concept: {learning_goal}",
                "See caption for details"
            ]
                    
        self.takeaways_group = VGroup()
        for i, point in enumerate(points[:VisualGrammar.max_objects_per_scene]):
            bullet = SmartText("•", font_size=32, color=VisualGrammar.colors["accent"])
            text = SmartText(str(point)[:50], font_size=28, color=VisualGrammar.colors["text"])
            row = VGroup(bullet, text).arrange(RIGHT, buff=0.2)
            self.takeaways_group.add(row)
        self.takeaways_group.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        self.add(self.takeaways_group)

class NumberLineDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        ranges = [v for k, v in kwargs.items() if isinstance(v, (list, tuple)) and len(v) == 3]
        x_range = ranges[0] if ranges else [-5, 5, 1]
        self.line = NumberLine(x_range=x_range, length=8)
        self.add(self.line)

class FunctionPlot(AnimatableComponent):
    def __init__(self, function="x**2", **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 25, 5], x_length=6, y_length=4)
        
        def safe_eval(x):
            try:
                allowed = {"x": x, "sin": np.sin, "cos": np.cos, "np": np, "math": np}
                return eval(function, {"__builtins__": {}}, allowed)
            except:
                return x**2
                
        self.plot = self.axes.plot(safe_eval, color=VisualGrammar.colors["accent"])
        self.add(self.axes, self.plot)

class VectorArrow(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1], x_length=6, y_length=6)
        coords = [v for k, v in kwargs.items() if isinstance(v, (list, tuple)) and len(v) == 2]
        direction = coords[0] if coords else [2, 3]
        self.vector = Arrow(self.axes.c2p(0, 0), self.axes.c2p(direction[0], direction[1]), buff=0, color=VisualGrammar.colors["primary"])
        self.add(self.axes, self.vector)

class MatrixDisplay(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        matrices = [v for k, v in kwargs.items() if isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], (list, tuple))]
        matrix_data = matrices[0] if matrices else [[1, 2], [3, 4]]
        self.matrix = Matrix(matrix_data)
        self.add(self.matrix)

class GeometryDiagram(AnimatableComponent):
    def __init__(self, shape=None, labels=None, equation=None, show_squares=False, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not shape:
            shape = "right_triangle"
            labels = {"a": 3, "b": 4, "c": 5}
        shape_type = str(shape).lower()
        self.diagram_group = VGroup()
        
        if shape_type == "right_triangle":
            vertices = [ORIGIN, RIGHT * 3, UP * 4]
            self.shape = Polygon(*vertices, color=VisualGrammar.colors["primary"])
            self.diagram_group.add(self.shape)
            
            if labels and isinstance(labels, dict):
                a_lab = labels.get("a", "a")
                b_lab = labels.get("b", "b")
                c_lab = labels.get("c", "c")
                l_a = SmartText(str(a_lab), font_size=24).next_to(self.shape, DOWN)
                l_b = SmartText(str(b_lab), font_size=24).next_to(self.shape, LEFT)
                l_c = SmartText(str(c_lab), font_size=24).move_to(self.shape.get_center() + RIGHT * 1.5 + UP * 2)
                self.diagram_group.add(l_a, l_b, l_c)
                
            if show_squares:
                sq_a = Square(side_length=3, color=BLUE).set_fill(BLUE, 0.3).next_to(self.shape, DOWN, buff=0)
                sq_b = Square(side_length=4, color=GREEN).set_fill(GREEN, 0.3).next_to(self.shape, LEFT, buff=0)
                angle = np.arctan2(4, -3)
                sq_c = Square(side_length=5, color=RED).set_fill(RED, 0.3)
                sq_c.rotate(angle)
                sq_c.move_to(self.shape.get_center() + RIGHT*2.5 + UP*2)
                self.diagram_group.add(sq_a, sq_b, sq_c)
        elif shape_type == "square":
            self.shape = Square(side_length=3, color=VisualGrammar.colors["primary"])
            self.diagram_group.add(self.shape)
        elif shape_type == "circle":
            self.shape = Circle(radius=2, color=VisualGrammar.colors["primary"])
            self.diagram_group.add(self.shape)
        else:
            self.shape = Polygon(LEFT*2+DOWN, RIGHT*2+DOWN, UP*2, color=VisualGrammar.colors["primary"])
            self.diagram_group.add(self.shape)
            
        self.add(self.diagram_group)
        
        if equation:
            eq = MathTex(str(equation)).next_to(self.diagram_group, DOWN, buff=1.0)
            self.add(eq)

class BarChartDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        values_lists = [v for k, v in kwargs.items() if isinstance(v, (list, tuple)) and len(v) > 0 and isinstance(v[0], (int, float))]
        values = values_lists[0] if values_lists else [2, 4, 8, 6]
        labels_lists = [v for k, v in kwargs.items() if isinstance(v, (list, tuple)) and len(v) == len(values) and isinstance(v[0], str)]
        labels = labels_lists[0] if labels_lists else [f"Bar {i+1}" for i in range(len(values))]
        self.chart = BarChart(values, bar_names=labels, max_value=max(values)+1)
        self.add(self.chart)

class BinarySearchDiagram(AnimatableComponent):
    def __init__(self, elements=None, low=None, high=None, mid=None, target=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not elements:
            elements = [1, 3, 5, 7, 9, 11, 13]
            
        self.cells = VGroup()
        for i, el in enumerate(elements[:12]):
            color = VisualGrammar.colors["secondary"]
            opacity = 0.5
            
            if low is not None and i < low:
                color = GRAY
                opacity = 0.2
            if high is not None and i > high:
                color = GRAY
                opacity = 0.2
                
            if mid is not None and i == mid:
                color = VisualGrammar.colors["primary"]
                
            rect = Square(side_length=1.0, color=WHITE).set_fill(color, opacity=opacity)
            text = SmartText(str(el)[:10], font_size=32, color=BLACK)
            cell = VGroup(rect, text)
            self.cells.add(cell)
            
        self.cells.arrange(RIGHT, buff=0)
        self.add(self.cells)
        
        if low is not None and 0 <= low < len(self.cells):
            t_low = SmartText("low", font_size=20, color=BLUE).next_to(self.cells[low], DOWN)
            self.add(t_low)
        if high is not None and 0 <= high < len(self.cells):
            t_high = SmartText("high", font_size=20, color=RED).next_to(self.cells[high], DOWN)
            self.add(t_high)
            
        self.eval_node = self.cells
        if mid is not None and 0 <= mid < len(self.cells):
            t_mid = SmartText("mid", font_size=20, color=YELLOW).next_to(self.cells[mid], UP)
            self.add(t_mid)
            self.eval_node = self.cells[mid]
        elif target is not None and 0 <= target < len(self.cells):
            self.eval_node = self.cells[target]

    def get_highlight_animations(self, *args, **kwargs):
        # Logic Highlight States: Explicitly indicate the node evaluating the condition
        return [Indicate(self.eval_node, scale_factor=1.2, color=RED)]

class GradientDescentPlot(AnimatableComponent):
    def __init__(self, function="x**2", start_x=3, learning_rate=0.3, steps=5, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 25, 5], x_length=6, y_length=4)
        
        def f(x):
            try:
                allowed = {"x": x, "sin": np.sin, "cos": np.cos, "np": np}
                return eval(function, {"__builtins__": {}}, allowed)
            except:
                return x**2
                
        self.plot = self.axes.plot(f, color=VisualGrammar.colors["secondary"])
        self.add(self.axes, self.plot)
        
        self.dots = VGroup()
        self.lines = VGroup()
        curr_x = start_x
        
        def df(x):
            h = 1e-5
            return (f(x+h) - f(x-h)) / (2*h)
            
        for _ in range(steps):
            dot = Dot(self.axes.c2p(curr_x, f(curr_x)), color=VisualGrammar.colors["primary"])
            self.dots.add(dot)
            next_x = curr_x - learning_rate * df(curr_x)
            if _ > 0:
                line = Line(self.dots[-2].get_center(), dot.get_center(), color=VisualGrammar.colors["accent"])
                self.lines.add(line)
            curr_x = next_x
            
        self.add(self.lines, self.dots)

class MoleculeDiagram(AnimatableComponent):
    def __init__(self, molecules=None, bonds=None, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if not molecules: molecules = [("O", 0, 0), ("H", -1, -1), ("H", 1, -1)]
        
        self.nodes = VGroup()
        for label, x, y in molecules[:VisualGrammar.max_objects_per_scene]:
            circ = Circle(radius=0.4, color=VisualGrammar.colors["primary"]).set_fill(VisualGrammar.colors["primary"], opacity=0.3).move_to(RIGHT*x + UP*y)
            t = SmartText(str(label)[:5], font_size=24, color=BLACK).move_to(circ.get_center())
            self.nodes.add(VGroup(circ, t))
            
        self.edges = VGroup()
        if not bonds: bonds = [(0, 1), (0, 2)]
        for i, j in bonds:
            if i < len(self.nodes) and j < len(self.nodes):
                self.edges.add(Line(self.nodes[i][0].get_center(), self.nodes[j][0].get_center(), stroke_width=4, color=WHITE, z_index=-1))
                
        self.add(self.edges, self.nodes)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.nodes, shift=UP), Create(self.edges)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.nodes)]
        
    def get_transformation_animations(self, *args, **kwargs):
        return [Wiggle(self.nodes)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.edges)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.nodes[0] if self.nodes else self)]

class LiquidSurfaceDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        # Dense particle array representing bulk fluid instead of a static container
        self.particles = VGroup()
        for x in np.linspace(-3.5, 3.5, 12):
            for y in np.linspace(-1.5, 0.7, 5):
                offset_x = 0.05 * np.sin(x*y)
                dot = Dot(RIGHT*(x + offset_x) + UP*y, radius=0.08, color=BLUE, fill_opacity=0.6)
                self.particles.add(dot)
                
        # Surface boundary represented by connected surface particles
        self.surface_particles = VGroup(*[
            Dot(RIGHT*x + UP*0.9, radius=0.1, color=BLUE_D)
            for x in np.linspace(-3.5, 3.5, 10)
        ])
        self.surface_links = VGroup(*[
            Line(self.surface_particles[i].get_center(), self.surface_particles[i+1].get_center(), stroke_width=3, color=BLUE)
            for i in range(len(self.surface_particles)-1)
        ])
        
        self.molecules = VGroup()
        # Inward forces on surface molecules
        for m in self.surface_particles[2:-2]:
            self.molecules.add(Arrow(m.get_center(), m.get_center() + DOWN*0.6, buff=0.1, color=RED, max_tip_length_to_length_ratio=0.3))
            
        # Highlighted bulk molecule showing symmetrical forces
        bulk_m = Dot(DOWN*0.5, radius=0.15, color=GREEN_C)
        self.molecules.add(bulk_m)
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            self.molecules.add(Arrow(bulk_m.get_center(), bulk_m.get_center() + RIGHT*0.6*dx + UP*0.6*dy, buff=0.1, color=GREEN, max_tip_length_to_length_ratio=0.3))
            
        self.add(self.particles, self.surface_links, self.surface_particles, self.molecules)

    def get_transformation_animations(self, *args, **kwargs):
        # Surface deforms downward into a meniscus curve under cohesive force
        anims = []
        for i, dot in enumerate(self.surface_particles):
            dist_from_center = abs(i - len(self.surface_particles)/2)
            pull_down = max(0, 0.45 * (1 - (dist_from_center / (len(self.surface_particles)/2))))
            anims.append(dot.animate.shift(DOWN * pull_down))
            
        for i, line in enumerate(self.surface_links):
            anims.append(UpdateFromFunc(line, lambda l, idx=i: l.put_start_and_end_on(
                self.surface_particles[idx].get_center(),
                self.surface_particles[idx+1].get_center()
            )))
            
        # Shift bulk particles down slightly to follow the meniscus deformation
        for p in self.particles:
            pos = p.get_center()
            dist_x = abs(pos[0])
            if pos[1] > 0.0:
                pull = max(0, 0.3 * (1 - (dist_x / 4.0)))
                anims.append(p.animate.shift(DOWN * pull))
                
        return [AnimationGroup(*anims, lag_ratio=0.01)]

class ForceVectorDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        
        # Two competing blocks (Small vs Large)
        self.small_block = Square(side_length=1.0, color=BLUE, fill_opacity=0.5).move_to(LEFT * 3)
        self.small_label = SmartText("m", font_size=24).move_to(self.small_block.get_center())
        
        self.large_block = Square(side_length=2.5, color=GREEN, fill_opacity=0.5).move_to(RIGHT * 3)
        self.large_label = SmartText("M", font_size=36).move_to(self.large_block.get_center())
        
        self.blocks = VGroup(self.small_block, self.small_label, self.large_block, self.large_label)
        
        # Identical force arrows applied to both blocks
        self.force_arrow_small = Arrow(self.small_block.get_right(), self.small_block.get_right() + RIGHT*2, buff=0.1, color=RED)
        self.force_arrow_large = Arrow(self.large_block.get_right(), self.large_block.get_right() + RIGHT*2, buff=0.1, color=RED)
        self.arrows = VGroup(self.force_arrow_small, self.force_arrow_large)
        
        # Acceleration vectors (Small block has large acceleration, Large block has small acceleration)
        self.accel_arrow_small = Arrow(self.small_block.get_top(), self.small_block.get_top() + UP*1.5 + RIGHT*0.5, buff=0.1, color=YELLOW)
        self.accel_arrow_large = Arrow(self.large_block.get_top(), self.large_block.get_top() + UP*0.5 + RIGHT*0.1, buff=0.1, color=YELLOW)
        self.accels = VGroup(self.accel_arrow_small, self.accel_arrow_large)
        
        self.add(self.blocks, self.arrows, self.accels)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.blocks, shift=UP), GrowArrow(self.force_arrow_small), GrowArrow(self.force_arrow_large)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.arrows)]
        
    def get_transformation_animations(self, *args, **kwargs):
        return [GrowArrow(self.accel_arrow_small), GrowArrow(self.accel_arrow_large)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Circumscribe(self.large_block)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Indicate(self.accels)]

class DropletDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        # Droplet outer surface as particle ring
        self.surface_particles = VGroup()
        self.num_particles = 16
        for i in range(self.num_particles):
            angle = i * (2 * np.pi / self.num_particles)
            dot = Dot(RIGHT*1.5*np.cos(angle) + UP*1.5*np.sin(angle), radius=0.08, color=BLUE)
            self.surface_particles.add(dot)
            
        # Droplet inner bulk particles
        self.bulk_particles = VGroup()
        for r in np.linspace(0.3, 1.2, 3):
            num_inner = int(r * 10)
            for i in range(num_inner):
                angle = i * (2 * np.pi / num_inner)
                dot = Dot(RIGHT*r*np.cos(angle) + UP*r*np.sin(angle), radius=0.06, color=BLUE, fill_opacity=0.4)
                self.bulk_particles.add(dot)
                
        self.droplet = VGroup(self.surface_particles, self.bulk_particles)
        
        self.arrows = VGroup()
        for p in self.surface_particles:
            v = -p.get_center() / np.linalg.norm(p.get_center())
            self.arrows.add(Arrow(p.get_center(), p.get_center() + v*0.5, buff=0.05, color=RED))
            
        self.label = SmartText("Minimizing Surface Area", font_size=24).next_to(self.droplet, DOWN, buff=0.5)
        self.add(self.droplet, self.arrows, self.label)

    def get_transformation_animations(self, *args, **kwargs):
        anims = []
        # Pulse contraction to show surface tension action
        for p in self.surface_particles:
            v = -p.get_center() / np.linalg.norm(p.get_center())
            anims.append(p.animate.shift(v * 0.15))
        for p in self.bulk_particles:
            v = -p.get_center() / np.linalg.norm(p.get_center()) if np.linalg.norm(p.get_center()) > 0 else ORIGIN
            anims.append(p.animate.shift(v * 0.1))
        return [AnimationGroup(*anims)]

class RightTriangleDiagram(AnimatableComponent):
    def __init__(self, a=3, b=4, c=5, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        blueprint = "mathematics_theorem_law"
        
        # Base Shape
        vertices = [ORIGIN, RIGHT * a, UP * b]
        self.shape = Polygon(*vertices, color=VisualGrammar.colors["primary"])
        
        # Labels bound relatively
        self.l_a = SmartText(str(a), blueprint_context=blueprint).next_to(self.shape, DOWN)
        self.l_b = SmartText(str(b), blueprint_context=blueprint).next_to(self.shape, LEFT)
        self.l_c = SmartText(str(c), blueprint_context=blueprint).next_to(self.shape.get_center(), UR, buff=0.5)
        
        # Angle marker
        self.angle_marker = RightAngle(Line(ORIGIN, RIGHT), Line(ORIGIN, UP), length=0.4, color=RED)
        self.angle_marker.move_to(self.shape.get_vertices()[0], aligned_edge=DL)
        
        # Equation bound relatively
        self.equation_label = SmartText(f"{a}^2 + {b}^2 = {c}^2", blueprint_context=blueprint).next_to(self.shape, DOWN, buff=1.5)
        
        self.add(self.shape, self.l_a, self.l_b, self.l_c, self.angle_marker, self.equation_label)

    def get_intro_animations(self, *args, **kwargs):
        return [Create(self.shape), Write(self.l_a), Write(self.l_b), Write(self.l_c), Create(self.angle_marker), Write(self.equation_label)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.shape)]
        
    def get_transformation_animations(self, *args, **kwargs):
        return [Indicate(self.l_c)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.equation_label)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.angle_marker)]

class AreaProofDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        blueprint = "mathematics_area_proof"
        
        self.geometric_shape = Square(side_length=4, color=VisualGrammar.colors["primary"])
        
        self.area_subdivisions = VGroup(
            Square(side_length=2, color=BLUE).set_fill(BLUE, 0.3).move_to(self.geometric_shape.get_center() + DL),
            Square(side_length=2, color=GREEN).set_fill(GREEN, 0.3).move_to(self.geometric_shape.get_center() + UR),
            Rectangle(width=2, height=2, color=YELLOW).set_fill(YELLOW, 0.3).move_to(self.geometric_shape.get_center() + UL),
            Rectangle(width=2, height=2, color=YELLOW).set_fill(YELLOW, 0.3).move_to(self.geometric_shape.get_center() + DR)
        )
        
        self.area_formula = SmartText("(a+b)^2 = a^2 + 2ab + b^2", blueprint_context=blueprint).next_to(self.geometric_shape, DOWN, buff=1)
        
        self.add(self.geometric_shape, self.area_subdivisions, self.area_formula)

class ParticleDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        blueprint = "physics_particle"
        
        self.particles = VGroup(
            Circle(radius=0.3, color=RED).set_fill(RED, 0.8).move_to(LEFT * 2),
            Circle(radius=0.3, color=BLUE).set_fill(BLUE, 0.8).move_to(RIGHT * 2)
        )
        
        # Interaction vector bound relative to particles
        self.interaction_vectors = VGroup(
            Arrow(self.particles[0].get_right(), self.particles[1].get_left(), buff=0.1, color=YELLOW),
            Arrow(self.particles[1].get_left(), self.particles[0].get_right(), buff=0.1, color=YELLOW)
        )
        
        self.add(self.particles, self.interaction_vectors)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.particles, scale=0.5), Create(self.interaction_vectors)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.particles)]
        
    def get_transformation_animations(self, *args, **kwargs):
        return [Wiggle(self.interaction_vectors)]
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.interaction_vectors)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.particles)]

class CoordinateGeometryDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.axes = Axes(x_range=[-5, 5, 1], y_range=[-5, 5, 1], x_length=6, y_length=6)
        self.points = VGroup(Dot(self.axes.coords_to_point(-2, -2), color=RED), Dot(self.axes.coords_to_point(3, 4), color=BLUE))
        self.line_or_shape = Line(self.points[0].get_center(), self.points[1].get_center(), color=YELLOW)
        self.add(self.axes, self.points, self.line_or_shape)

    def get_intro_animations(self, *args, **kwargs):
        return [Create(self.axes), FadeIn(self.points), Create(self.line_or_shape)]
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.points)]
    def get_transformation_animations(self, *args, **kwargs):
        return [self.points[1].animate.move_to(self.axes.coords_to_point(4, 1)), UpdateFromFunc(self.line_or_shape, lambda l: l.put_start_and_end_on(self.points[0].get_center(), self.points[1].get_center()))]
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.line_or_shape)]
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.line_or_shape)]

class ElectricFieldDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.charges = VGroup(
            Circle(radius=0.4, color=RED).set_fill(RED, 0.8).move_to(LEFT*2),
            Circle(radius=0.4, color=BLUE).set_fill(BLUE, 0.8).move_to(RIGHT*2)
        )
        self.charges.add(SmartText("+", font_size=36).move_to(self.charges[0]), SmartText("-", font_size=36).move_to(self.charges[1]))
        
        self.field_lines = VGroup()
        for i in range(5):
            arc = ArcBetweenPoints(self.charges[0].get_right(), self.charges[1].get_left(), angle=np.pi/4 * (i-2), color=YELLOW, stroke_width=2).set_opacity(0.5)
            self.field_lines.add(arc)
            
        self.force_vectors = VGroup(
            Arrow(self.charges[0].get_right(), self.charges[0].get_right() + RIGHT*1, buff=0, color=WHITE),
            Arrow(self.charges[1].get_left(), self.charges[1].get_left() + LEFT*1, buff=0, color=WHITE)
        )
        self.add(self.charges, self.field_lines, self.force_vectors)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.charges, scale=0.5), Create(self.field_lines), GrowArrow(self.force_vectors[0]), GrowArrow(self.force_vectors[1])]
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.charges)]
    def get_transformation_animations(self, *args, **kwargs):
        return [Wiggle(self.field_lines)]
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.force_vectors)]
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.charges)]

class WaveDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.axes = Axes(x_range=[0, 4*np.pi, np.pi/2], y_range=[-2, 2, 1], x_length=8, y_length=4)
        self.sine_wave = self.axes.plot(lambda x: np.sin(x), color=BLUE)
        self.amplitude_marker = DoubleArrow(self.axes.coords_to_point(np.pi/2, 0), self.axes.coords_to_point(np.pi/2, 1), buff=0, color=YELLOW)
        self.wavelength_marker = DoubleArrow(self.axes.coords_to_point(np.pi/2, 1.2), self.axes.coords_to_point(5*np.pi/2, 1.2), buff=0, color=RED)
        self.add(self.axes, self.sine_wave, self.amplitude_marker, self.wavelength_marker)

    def get_intro_animations(self, *args, **kwargs):
        return [Create(self.axes), Create(self.sine_wave)]
    def get_highlight_animations(self, *args, **kwargs):
        return [Create(self.amplitude_marker), Create(self.wavelength_marker)]
    def get_transformation_animations(self, *args, **kwargs):
        return [self.sine_wave.animate.set_color(RED)]
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.amplitude_marker)]
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.wavelength_marker)]

class AtomDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        # Nucleus as particle cluster (protons/neutrons) instead of a static circle
        self.nucleus_particles = VGroup(*[
            Dot(
                RIGHT * (0.15 * np.cos(angle)) + UP * (0.15 * np.sin(angle)),
                radius=0.1,
                color=RED if i % 2 == 0 else GRAY
            )
            for i, angle in enumerate(np.linspace(0, 2*np.pi, 7, endpoint=False))
        ])
        self.nucleus_particles.add(Dot(ORIGIN, radius=0.1, color=RED))
        self.nucleus = self.nucleus_particles
        
        self.electron_orbits = VGroup(
            Ellipse(width=4, height=1.5, color=WHITE).set_opacity(0.3).rotate(np.pi/4),
            Ellipse(width=4, height=1.5, color=WHITE).set_opacity(0.3).rotate(-np.pi/4)
        )
        self.electrons = VGroup(
            Dot(self.electron_orbits[0].point_from_proportion(0.2), color=BLUE),
            Dot(self.electron_orbits[1].point_from_proportion(0.7), color=BLUE)
        )
        self.add(self.nucleus, self.electron_orbits, self.electrons)

    def get_intro_animations(self, *args, **kwargs):
        return [GrowFromCenter(self.nucleus), Create(self.electron_orbits), FadeIn(self.electrons)]
        
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.electrons)]
        
    def get_transformation_animations(self, *args, **kwargs):
        anims = [
            MoveAlongPath(self.electrons[0], self.electron_orbits[0]),
            MoveAlongPath(self.electrons[1], self.electron_orbits[1])
        ]
        # Nucleus vibration to show dynamic energy state
        for particle in self.nucleus:
            random_offset = np.array([np.random.uniform(-0.15, 0.15), np.random.uniform(-0.15, 0.15), 0])
            anims.append(particle.animate.shift(random_offset))
        return anims
        
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.nucleus)]
        
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.nucleus)]

class ReactionDiagram(AnimatableComponent):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.reactants = VGroup(
            Circle(radius=0.4, color=BLUE).set_fill(BLUE, 0.5),
            Circle(radius=0.4, color=BLUE).set_fill(BLUE, 0.5).next_to(RIGHT*0.5, buff=0.1)
        ).move_to(LEFT*3)
        self.products = VGroup(
            Circle(radius=0.5, color=GREEN).set_fill(GREEN, 0.5).move_to(RIGHT*3)
        )
        self.yield_arrow = Arrow(LEFT*1, RIGHT*1, buff=0.2, color=WHITE)
        self.add(self.reactants, self.yield_arrow, self.products)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.reactants, shift=RIGHT), GrowArrow(self.yield_arrow), FadeIn(self.products, shift=LEFT)]
    def get_highlight_animations(self, *args, **kwargs):
        return [Indicate(self.reactants), Indicate(self.products)]
    def get_transformation_animations(self, *args, **kwargs):
        return [Transform(self.reactants.copy(), self.products)]
    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.yield_arrow)]
    def get_focus_animations(self, *args, **kwargs):
        return [Circumscribe(self.products)]

class LayoutZones:
    @staticmethod
    def arrange_zones(title_zone=None, visualization_zone=None, explanation_zone=None, subtitle_zone=None):
        zones = VGroup()
        if title_zone:
            zones.add(title_zone)
            
        if visualization_zone:
            zones.add(visualization_zone)
            
        caption = subtitle_zone if subtitle_zone else explanation_zone
        if caption:
            zones.add(caption)
            
        if len(zones) > 0:
            zones.arrange(DOWN, buff=0.5)
            zones.move_to(ORIGIN)
            
            # Dynamically scale to fit within camera bounds
            max_width = 13.0
            max_height = 7.0
            if zones.width > max_width:
                zones.scale_to_fit_width(max_width)
            if zones.height > max_height:
                zones.scale_to_fit_height(max_height)
                
        return zones

def validate_animation_interfaces():
    import logging
    try:
        from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY
    except ImportError:
        return
        
    missing = []
    required = [
        "get_intro_animations",
        "get_highlight_animations",
        "get_transformation_animations",
        "get_explanation_animations",
        "get_focus_animations",
    ]
    for registry_name, impl_name in COMPONENT_REGISTRY.items():
        comp_class = globals().get(impl_name)
        if comp_class and isinstance(comp_class, type) and issubclass(comp_class, AnimatableComponent):
            for method in required:
                if not hasattr(comp_class, method) or not callable(getattr(comp_class, method)):
                    missing.append(f"{impl_name}.{method}")
    if missing:
        logging.warning(f"Components missing animation interfaces: {missing}")


class SurfaceTensionDiagram(AnimatableComponent):
    """Diagram specifically for surface tension with surface molecules pulled inward."""
    def __init__(self, **kwargs):
        super().__init__()
        # Liquid particle grid
        self.particles = VGroup()
        for x in np.linspace(-3.0, 3.0, 10):
            for y in np.linspace(-3.0, 0.0, 6):
                dot = Dot(RIGHT*x + UP*y, radius=0.08, color=BLUE, fill_opacity=0.5)
                self.particles.add(dot)
                
        # Surface particles
        self.surface_particles = VGroup(*[
            Dot(RIGHT*x + UP*0.1, radius=0.12, color=BLUE_D)
            for x in np.linspace(-3.0, 3.0, 8)
        ])
        self.surface_line = VGroup(*[
            Line(self.surface_particles[i].get_center(), self.surface_particles[i+1].get_center(), stroke_width=3, color=BLUE)
            for i in range(len(self.surface_particles)-1)
        ])
        
        self.molecules = VGroup()
        # Pulling forces on surface
        self.surface_arrows = VGroup()
        for p in self.surface_particles:
            self.surface_arrows.add(Arrow(p.get_center(), p.get_center() + DOWN*0.6, buff=0.1, color=RED, max_tip_length_to_length_ratio=0.3))
            
        # Bulk molecule
        bulk = Dot(DOWN*1.5, radius=0.15, color=BLUE_E)
        bulk_arrows = VGroup(*[Arrow(bulk.get_center(), bulk.get_center() + UP*0.6).rotate(angle, about_point=bulk.get_center()) for angle in [0, PI/2, PI, 3*PI/2]])
        
        self.molecules.add(bulk, bulk_arrows, self.surface_particles, self.surface_arrows)
        self.add(self.particles, self.surface_line, self.molecules)

    def get_intro_animations(self, *args, **kwargs):
        return [FadeIn(self.particles), Create(self.surface_line), FadeIn(self.molecules)]

    def get_highlight_animations(self, *args, **kwargs):
        return [Wiggle(self.molecules)]

    def get_transformation_animations(self, *args, **kwargs):
        # Surface deforms downward under cohesive force pull (tension)
        anims = []
        for i, dot in enumerate(self.surface_particles):
            dist_from_center = abs(i - len(self.surface_particles)/2)
            pull_down = max(0, 0.5 * (1 - (dist_from_center / (len(self.surface_particles)/2))))
            anims.append(dot.animate.shift(DOWN * pull_down))
            
        for i, line in enumerate(self.surface_line):
            anims.append(UpdateFromFunc(line, lambda l, idx=i: l.put_start_and_end_on(
                self.surface_particles[idx].get_center(),
                self.surface_particles[idx+1].get_center()
            )))
        return [AnimationGroup(*anims)]

    def get_explanation_animations(self, *args, **kwargs):
        return [Indicate(self.surface_line)]

    def get_focus_animations(self, *args, **kwargs):
        return [self.animate.scale(1.1)]


class NeuralNetworkDiagram(AnimatableComponent):
    """Bespoke neural network layer drawing."""
    def __init__(self, **kwargs):
        super().__init__()
        layers = [3, 4, 4, 2]
        self.nodes = VGroup()
        self.edges = VGroup()
        
        # Create nodes
        for i, num_nodes in enumerate(layers):
            layer_nodes = VGroup()
            for j in range(num_nodes):
                node = Circle(radius=0.2, color=WHITE, fill_opacity=1)
                node.move_to(RIGHT * (i * 2 - 3) + UP * (j - num_nodes/2 + 0.5))
                layer_nodes.add(node)
            self.nodes.add(layer_nodes)
            
        # Create edges with random weight-based stroke scaling
        import random
        for i in range(len(layers) - 1):
            layer1 = self.nodes[i]
            layer2 = self.nodes[i+1]
            for n1 in layer1:
                for n2 in layer2:
                    weight = random.randint(1, 5)
                    self.edges.add(Line(n1.get_center(), n2.get_center(), stroke_width=weight, stroke_opacity=0.4))
                    
        self.add(self.edges, self.nodes)

    def get_intro_animations(self, *args, **kwargs):
        return [Create(self.nodes), Create(self.edges)]

    def get_highlight_animations(self, *args, **kwargs):
        return [Wiggle(self.nodes)]

    def get_transformation_animations(self, *args, **kwargs):
        # Pulse data signals physically through connections layer by layer
        anims = []
        for i in range(len(self.nodes) - 1):
            layer_pulses = []
            for n1 in self.nodes[i]:
                for n2 in self.nodes[i+1]:
                    pulse = Dot(n1.get_center(), radius=0.08, color=YELLOW)
                    travel = Succession(
                        FadeIn(pulse, run_time=0.1),
                        pulse.animate(run_time=0.6).move_to(n2.get_center()),
                        FadeOut(pulse, run_time=0.1)
                    )
                    layer_pulses.append(travel)
            anims.append(AnimationGroup(*layer_pulses))
        return anims

    def get_explanation_animations(self, *args, **kwargs):
        return [Flash(self.nodes[-1])]

    def get_focus_animations(self, *args, **kwargs):
        return [self.animate.scale(1.1)]


validate_animation_interfaces()
