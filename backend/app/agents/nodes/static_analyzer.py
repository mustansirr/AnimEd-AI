"""
Static Analyzer Node.

Intercepts the generated Python code before it is passed to the Sandbox Renderer.
Uses `ast` and `compile()` to detect SyntaxErrors, undefined variables,
undefined attributes, and invalid Manim API calls.
"""

import ast
import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

import builtins
from manim import *

def get_dynamic_whitelist():
    symbols = {name for name in globals()} # Pulls in all from manim import *
    symbols.update({name for name in dir(builtins)})
    
    project_symbols = {
        "EducationalBackground", "Scene1", "filter_manim_kwargs",
        "NumberLineDiagram", "FunctionPlot", "VectorArrow", "MatrixDisplay", "GeometryDiagram", "BarChartDiagram",
        "Matrix", "BarChart", "SmartText", "TitleCard", "LayoutZones",
        "FlowChart", "GraphPlot", "TreeDiagram", "NetworkDiagram", "TimelineDiagram",
        "SummaryDiagram", "MoleculeDiagram", "LiquidSurfaceDiagram", "ForceVectorDiagram",
        "DropletDiagram", "RightTriangleDiagram", "AreaProofDiagram", "ParticleDiagram",
        "CoordinateGeometryDiagram", "ElectricFieldDiagram", "WaveDiagram", "AtomDiagram", "ReactionDiagram"
    }
    symbols.update(project_symbols)
    
    # Common dummy variables
    symbols.update({"step", "label", "el", "point", "k", "v", "x", "y", "z"})
    return symbols

MANIM_WHITELIST = get_dynamic_whitelist()

ALLOWED_ATTRIBUTES = {
    # Mobject methods
    "add", "remove", "clear", "play", "wait", "add_sound",
    "move_to", "shift", "scale", "rotate", "flip", "stretch", "set_color", "set_opacity",
    "set_stroke", "set_fill", "align_to", "next_to", "arrange", "arrange_in_grid",
    "get_center", "get_top", "get_bottom", "get_left", "get_right",
    "get_width", "get_height", "scale_to_fit_width", "scale_to_fit_height",
    "copy", "generate_target", "move_to_target", "save_state", "restore",
    "set_z_index", "match_color", "match_style", "match_width", "match_height",
    "match_x", "match_y",
    
    # Group indexing
    "submobjects", "add_to_back",
    
    # Special attributes
    "camera", "frame_width", "frame_height", "frame_center",
    
    # Python generic
    "append", "extend", "pop", "get", "keys", "values", "items"
}

class CodeValidator(ast.NodeVisitor):
    def __init__(self):
        self.defined_names = set(MANIM_WHITELIST)
        self.errors = []
        self.current_scope = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.defined_names.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == "*":
                # We assume wildcard imports are Manim, which is covered by whitelist
                pass
            else:
                self.defined_names.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.current_scope.add(target.id)
            elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.current_scope.add(elt.id)
        self.generic_visit(node)
        
    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.current_scope.add(node.target.id)
        elif isinstance(node.target, ast.Tuple) or isinstance(node.target, ast.List):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.current_scope.add(elt.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        # Add arguments to scope
        func_scope = set()
        for arg in node.args.args:
            func_scope.add(arg.arg)
        if node.args.vararg:
            func_scope.add(node.args.vararg.arg)
        if node.args.kwarg:
            func_scope.add(node.args.kwarg.arg)
            
        old_scope = self.current_scope
        self.current_scope = old_scope.union(func_scope)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        old_scope = self.current_scope.copy()
        for arg in node.args.args:
            self.current_scope.add(arg.arg)
        if node.args.vararg:
            self.current_scope.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.current_scope.add(node.args.kwarg.arg)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_With(self, node):
        old_scope = self.current_scope.copy()
        for item in node.items:
            if item.optional_vars:
                self._add_to_scope(item.optional_vars)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_Try(self, node):
        old_scope = self.current_scope.copy()
        for handler in node.handlers:
            if handler.name:
                self.current_scope.add(handler.name)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_ListComp(self, node):
        old_scope = self.current_scope.copy()
        for gen in node.generators:
            self._add_to_scope(gen.target)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_DictComp(self, node):
        old_scope = self.current_scope.copy()
        for gen in node.generators:
            self._add_to_scope(gen.target)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_SetComp(self, node):
        old_scope = self.current_scope.copy()
        for gen in node.generators:
            self._add_to_scope(gen.target)
        self.generic_visit(node)
        self.current_scope = old_scope

    def visit_GeneratorExp(self, node):
        old_scope = self.current_scope.copy()
        for gen in node.generators:
            self._add_to_scope(gen.target)
        self.generic_visit(node)
        self.current_scope = old_scope

    def _add_to_scope(self, target):
        if isinstance(target, ast.Name):
            self.current_scope.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._add_to_scope(elt)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self.defined_names and node.id not in self.current_scope:
                self.errors.append(f"Undefined variable or function referenced: '{node.id}'")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Specific Manim API typo check
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name.lower().startswith("fade") and func_name not in MANIM_WHITELIST:
                 self.errors.append(f"Invalid Manim API call: '{func_name}'")
            if func_name.lower().startswith("transform") and func_name not in MANIM_WHITELIST:
                 self.errors.append(f"Invalid Manim API call: '{func_name}'")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load):
            attr_name = node.attr
            if attr_name not in ALLOWED_ATTRIBUTES:
                # To prevent blocking valid python math operations (like math.cos), we only enforce loosely.
                # If it's a known hallucination, we catch it.
                if attr_name in ["position", "layout_zones", "title_scale", "caption_scale", "title_pos"]:
                    self.errors.append(f"Invalid attribute accessed: '.{attr_name}'. Use standard Manim coordinate geometry.")
        self.generic_visit(node)


def analyze_code(code: str) -> list[str]:
    """Runs compile check and AST analysis on the generated code."""
    errors = []
    
    # 1. Compile Check (SyntaxErrors)
    try:
        compile(code, "<generated>", "exec")
    except SyntaxError as e:
        return [f"SyntaxError on line {e.lineno}: {e.msg}\nCode snippet: {e.text}"]
    except Exception as e:
        return [f"Compilation failed: {e}"]

    # 2. AST Static Analysis
    try:
        tree = ast.parse(code)
        validator = CodeValidator()
        validator.visit(tree)
        
        STATIC_ANALYZER_DEBUG = True
        if STATIC_ANALYZER_DEBUG and validator.errors:
            logger.warning("--- STATIC ANALYZER DEBUG INFO ---")
            logger.warning(f"Defined Names count: {len(validator.defined_names)}")
            logger.warning(f"Current Scope: {validator.current_scope}")
            logger.warning(f"Validation Errors: {validator.errors}")
            logger.warning("----------------------------------")
            
        errors.extend(validator.errors)
    except Exception as e:
        errors.append(f"AST Parsing failed: {e}")
        
    # Deduplicate while preserving order
    seen = set()
    unique_errors = []
    for e in errors:
        if e not in seen:
            unique_errors.append(e)
            seen.add(e)
            
    return unique_errors

async def static_analysis_pass(state: AgentState) -> dict:
    generated_codes = state.get("generated_codes", [])
    if not generated_codes:
        return {}
        
    # We only check the most recently generated code (the current scene)
    current_code = generated_codes[-1]
    
    errors = analyze_code(current_code)
    
    if errors:
        error_msg = "[DIAGNOSTIC] FATAL ERROR: Static Analysis Failed:\n- " + "\n- ".join(errors)
        logger.error(error_msg)
        return {"last_render_error": error_msg}
        
    logger.info("Static analysis passed. Code is syntactically valid and identifiers resolve.")
    return {"last_render_error": None}
