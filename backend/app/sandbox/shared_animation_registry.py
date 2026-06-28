"""
Canonical Component & Animation Registry.

This module is the SINGLE SOURCE OF TRUTH for:
  - Which visualization components exist and can be instantiated
  - Which concept types map to which components
  - Which components are allowed for each visualization strategy
  - Which animation actions are supported

All other modules (classifier, coder, static_analyzer, scene_json_generator)
MUST import their component knowledge from here.

To add a new component:
  1. Define the class in components.py (must extend AnimatableComponent)
  2. Add it to SUPPORTED_COMPONENTS below
  3. (Optional) Map a concept_type to it in CONCEPT_TO_COMPONENT
  Nothing else needs to change.
"""

COMPONENT_REGISTRY = {
    "TitleCard": "TitleCard",
    "ImageLabelCard": "ImageLabelCard",
    "FlowChart": "FlowChart",
    "GraphPlot": "GraphPlot",
    "FunctionPlot": "FunctionPlot",
    "HierarchyDiagram": "TreeDiagram",
    "NetworkDiagram": "NetworkDiagram",
    "TimelineDiagram": "TimelineDiagram",
    "ArrayDiagram": "ArrayDiagram",
    "SummaryDiagram": "SummaryDiagram",
    "NumberLineDiagram": "NumberLineDiagram",
    "VectorArrow": "VectorArrow",
    "MatrixDisplay": "MatrixDisplay",
    "GeometryDiagram": "GeometryDiagram",
    "BarChartDiagram": "BarChartDiagram",
    "BinarySearchDiagram": "BinarySearchDiagram",
    "GradientDescentPlot": "GradientDescentPlot",
    "MoleculeDiagram": "MoleculeDiagram",
    "LiquidSurfaceDiagram": "LiquidSurfaceDiagram",
    "ForceVectorDiagram": "ForceVectorDiagram",
    "DropletDiagram": "DropletDiagram",
    "RightTriangleDiagram": "RightTriangleDiagram",
    "AreaProofDiagram": "AreaProofDiagram",
    "ParticleDiagram": "ParticleDiagram",
    "CoordinateGeometryDiagram": "CoordinateGeometryDiagram",
    "ElectricFieldDiagram": "ElectricFieldDiagram",
    "WaveDiagram": "WaveDiagram",
    "AtomDiagram": "AtomDiagram",
    "ReactionDiagram": "ReactionDiagram",
    "SurfaceTensionDiagram": "SurfaceTensionDiagram",
    "NeuralNetworkDiagram": "NeuralNetworkDiagram"
}

COMPONENT_ALIASES = {
    "TreeDiagram": "HierarchyDiagram",
    "FunctionPlotDiagram": "FunctionPlot",
    "SquareAreaProofDiagram": "AreaProofDiagram",
}

def validate_component_implementations():
    """Verify that every component registered actually exists and is an AnimatableComponent."""
    # We must import components dynamically to avoid circular imports 
    # since components.py imports SUPPORTED_COMPONENTS from here.
    import app.sandbox.components as components_module
    
    for registry_name, impl_name in COMPONENT_REGISTRY.items():
        if impl_name in ["LayoutZones", "EducationalBackground"]:
            continue
            
        comp_class = getattr(components_module, impl_name, None)
        if not comp_class:
            raise ValueError(f"Startup Validation Error: Component implementation '{impl_name}' not found for registry key '{registry_name}'.")
        
        if not issubclass(comp_class, components_module.AnimatableComponent):
            raise ValueError(f"Startup Validation Error: Component '{impl_name}' does not implement AnimatableComponent interface.")

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. SUPPORTED_COMPONENTS
#    The canonical set of ALL visualization component class names that exist
#    in components.py and can be instantiated by the deterministic coder.
#    Phantom entries (class names with no implementation) must NOT appear here.
# ---------------------------------------------------------------------------
SUPPORTED_COMPONENTS = {
    # Computer Science
    "ArrayDiagram",
    "TreeDiagram",
    "GraphDiagram",
    "NetworkDiagram",
    "NeuralNetworkDiagram",
    "BinarySearchDiagram",
    # Mathematics
    "RightTriangleDiagram",
    "AreaProofDiagram",
    "CoordinateGeometryDiagram",
    "GeometryDiagram",
    "FunctionPlot",
    "GraphPlot",
    "GradientDescentPlot",
    "NumberLineDiagram",
    "BarChartDiagram",
    "MatrixDisplay",
    "VectorArrow",
    # Physics
    "ForceVectorDiagram",
    "SurfaceTensionDiagram",
    "LiquidSurfaceDiagram",
    "DropletDiagram",
    "ElectricFieldDiagram",
    "ParticleDiagram",
    "WaveDiagram",
    # Chemistry / Biology
    "MoleculeDiagram",
    "AtomDiagram",
    "ReactionDiagram",
    # General / Layout
    "FlowChart",
    "TimelineDiagram",
    "SummaryDiagram",
    "TitleCard",
}

# ---------------------------------------------------------------------------
# 2. CONCEPT_TO_COMPONENT
#    Maps classifier concept-type strings to their primary visualization
#    component.  Every value MUST be a member of SUPPORTED_COMPONENTS.
#    Validated at import time by validate_registry_integrity().
# ---------------------------------------------------------------------------
CONCEPT_TO_COMPONENT = {
    # Computer Science
    "algorithm_search": "BinarySearchDiagram",
    "algorithm_sort": "ArrayDiagram",
    "data_structure_tree": "TreeDiagram",
    "data_structure_graph": "GraphDiagram",
    "neural_network": "NeuralNetworkDiagram",
    # Mathematics
    "geometry": "GeometryDiagram",
    "mathematics_theorem_law": "GeometryDiagram",
    "mathematics_area_proof": "AreaProofDiagram",
    "function_plot": "FunctionPlot",
    "statistics": "BarChartDiagram",
    "linear_algebra": "MatrixDisplay",
    # Physics
    "physics_motion": "FunctionPlot",
    "physics_force": "ForceVectorDiagram",
    "physics_forces_multiple": "ForceVectorDiagram",
    "physics_surface_tension": "SurfaceTensionDiagram",
    "physics_droplet": "DropletDiagram",
    "physics_electric_field": "ElectricFieldDiagram",
    "physics_particle": "ParticleDiagram",
    "physics_wave": "WaveDiagram",
    # Biology / Chemistry
    "biology_process": "FlowChart",
    "chemistry_molecule": "MoleculeDiagram",
    "chemistry_atom": "AtomDiagram",
    "chemistry_reaction": "ReactionDiagram",
    # General
    "process_flow": "FlowChart",
    "summary": "SummaryDiagram",
    "definition": "SummaryDiagram",
}

# ---------------------------------------------------------------------------
# 3. SUPPORTED_ANIMATIONS
# ---------------------------------------------------------------------------
SUPPORTED_ANIMATIONS = {
    # Canonical semantic actions (used by the new dict-based format)
    "intro", "highlight", "transform", "explain", "focus",
    # Legacy string aliases (mapped to canonical actions by generate_animation_code)
    "draw_axes", "show_points", "fit_line", "show_prediction",
    "fade_in_title", "grow_tree", "highlight_node", "fade_in_array",
    "highlight_element", "fade_in_flowchart", "highlight_step",
    "show_diagram", "fade_in_summary_diagram", "highlight_key_takeaways",
    "animate_flow", "gradient_descent_step", "binary_search_step",
}

# ---------------------------------------------------------------------------
# 4. SCENE_COMPONENT_RULES  (auto-derived from CONCEPT_TO_COMPONENT)
#    Maps each concept_type to the set of components that the SceneJSON
#    generator is allowed to use for that concept.
# ---------------------------------------------------------------------------
def _build_scene_component_rules():
    """Derive per-category component rules from CONCEPT_TO_COMPONENT."""
    rules: dict[str, set[str]] = {}
    for concept_type, component in CONCEPT_TO_COMPONENT.items():
        rules.setdefault(concept_type, set()).add(component)
    # Convert sets to sorted lists for determinism
    return {k: sorted(v) for k, v in rules.items()}

SCENE_COMPONENT_RULES = _build_scene_component_rules()

# Components available in every scene regardless of concept type
UBIQUITOUS_COMPONENTS = {"TitleCard", "SummaryDiagram"}

