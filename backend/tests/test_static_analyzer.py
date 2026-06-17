import pytest
from app.agents.nodes.static_analyzer import analyze_code

def test_manim_dynamic_symbols():
    """Verify that previously missing Manim symbols now pass via dynamic registry."""
    code = """
class TestScene(Scene):
    def construct(self):
        arrow = GrowArrow(Arrow(ORIGIN, UP))
        angle = RightAngle(Line(LEFT, ORIGIN), Line(ORIGIN, UP))
        arc = ArcBetweenPoints(LEFT, RIGHT, angle=PI/2)
        self.play(arrow, Create(angle), Create(arc))
"""
    errors = analyze_code(code)
    assert not errors, f"Expected no errors, got: {errors}"

def test_ast_lambda_scope():
    """Verify that lambda arguments are correctly tracked in scope."""
    code = """
class TestScene(Scene):
    def construct(self):
        dot1 = Dot(LEFT)
        dot2 = Dot(RIGHT)
        line = Line(dot1.get_center(), dot2.get_center())
        # The static analyzer should not flag 'l' as undefined
        anim = UpdateFromFunc(line, lambda l: l.put_start_and_end_on(dot1.get_center(), dot2.get_center()))
        self.play(anim)
"""
    errors = analyze_code(code)
    assert not errors, f"Expected no errors, got: {errors}"

def test_ast_with_scope():
    """Verify that variables bound in a 'with' statement are tracked."""
    code = """
from manim import tempconfig

class TestScene(Scene):
    def construct(self):
        with tempconfig({"quality": "low_quality"}) as config_var:
            print(config_var)
            dot = Dot()
            self.add(dot)
"""
    errors = analyze_code(code)
    assert not errors, f"Expected no errors, got: {errors}"

def test_ast_try_scope():
    """Verify that exception bindings in a 'try/except' are tracked."""
    code = """
class TestScene(Scene):
    def construct(self):
        try:
            x = 1 / 0
        except ZeroDivisionError as e:
            print(e)
"""
    errors = analyze_code(code)
    assert not errors, f"Expected no errors, got: {errors}"

def test_ast_class_def_scope():
    """Verify that dynamically defined classes within the code are added to scope."""
    code = """
class MyCustomDiagram(VGroup):
    def __init__(self, **kwargs):
        super().__init__(**filter_manim_kwargs(kwargs))
        self.dot = Dot()
        self.add(self.dot)

class TestScene(Scene):
    def construct(self):
        diagram = MyCustomDiagram()
        self.add(diagram)
"""
    errors = analyze_code(code)
    assert not errors, f"Expected no errors, got: {errors}"

def test_true_undefined_variable():
    """Verify that the analyzer still successfully catches actual undefined variables."""
    code = """
class TestScene(Scene):
    def construct(self):
        self.play(FadeIn(some_hallucinated_variable))
"""
    errors = analyze_code(code)
    assert len(errors) == 1
    assert "some_hallucinated_variable" in errors[0]
