from manim import *
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

class NetworkDiagram(VGroup):
    def __init__(self, layers=None, layer_labels=None, animate_flow=False, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        if layers is None:
            layers = [["x1", "x2"], ["h1", "h2", "h3"], ["y1"]]
            
        print(f"NetworkDiagram created with layers: {layers}")
            
        self.layer_groups = VGroup()
        self.all_nodes = []
        for layer_nodes in layers:
            col = VGroup()
            for node_name in layer_nodes:
                circ = Circle(radius=0.4, color=VisualGrammar.colors["primary"], fill_opacity=0.8)
                label = Text(str(node_name)[:10], font_size=20)
                col.add(VGroup(circ, label))
            col.arrange(DOWN, buff=0.5)
            self.layer_groups.add(col)
            self.all_nodes.append(col)
            
        self.layer_groups.arrange(RIGHT, buff=2.0)
        
        self.edges = VGroup()
        for i in range(len(self.all_nodes)-1):
            for src in self.all_nodes[i]:
                for tgt in self.all_nodes[i+1]:
                    self.edges.add(Line(src.get_center(), tgt.get_center(), stroke_opacity=0.3, z_index=-1))
                    
        self.add(self.edges, self.layer_groups)
        
        if layer_labels and len(layer_labels) == len(layers):
            labels_group = VGroup()
            for i, lab in enumerate(layer_labels):
                t = Text(str(lab), font_size=24, color=VisualGrammar.colors["secondary"]).next_to(self.layer_groups[i], DOWN, buff=0.5)
                labels_group.add(t)
            self.add(labels_group)
            
        print(f"Total mobjects: {len(self.submobjects)}")

class NetworkScene(Scene):
    def construct(self):
        layers = [["x1","x2","x3"], ["h1","h2","h3"], ["out"]]
        layer_labels = ["Input","Hidden","Output"]
        net = NetworkDiagram(layers=layers, layer_labels=layer_labels)
        self.play(FadeIn(net))
        self.wait(1)
