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


def get_allowed_components(scene_type: str) -> list[str]:
    """Return the allowed components for a given visualization strategy."""
    allowed = set(UBIQUITOUS_COMPONENTS)
    if scene_type == "generic_concept":
        # Generic concept — allow everything
        allowed.update(SUPPORTED_COMPONENTS)
    elif scene_type in SCENE_COMPONENT_RULES:
        allowed.update(SCENE_COMPONENT_RULES[scene_type])
    else:
        # Unknown scene type — allow all rather than silently restricting
        logger.warning(f"Unknown scene_type '{scene_type}' in get_allowed_components. Allowing all components.")
        allowed.update(SUPPORTED_COMPONENTS)
    return sorted(allowed)


# ---------------------------------------------------------------------------
# 5. STARTUP INTEGRITY VALIDATION
# ---------------------------------------------------------------------------
def validate_registry_integrity():
    """
    Verify that the component registry is internally consistent.
    Called at import time. Raises RuntimeError on mismatch so that broken
    deployments fail immediately with a clear diagnostic.
    """
    errors = []

    # Check 1: Every CONCEPT_TO_COMPONENT value must be in SUPPORTED_COMPONENTS
    for concept_type, component in CONCEPT_TO_COMPONENT.items():
        if component not in SUPPORTED_COMPONENTS:
            errors.append(
                f"CONCEPT_TO_COMPONENT['{concept_type}'] = '{component}' "
                f"is NOT in SUPPORTED_COMPONENTS"
            )

    # Check 2: Every SCENE_COMPONENT_RULES value must be in SUPPORTED_COMPONENTS
    for scene_type, components in SCENE_COMPONENT_RULES.items():
        for comp in components:
            if comp not in SUPPORTED_COMPONENTS:
                errors.append(
                    f"SCENE_COMPONENT_RULES['{scene_type}'] contains '{comp}' "
                    f"which is NOT in SUPPORTED_COMPONENTS"
                )

    if errors:
        error_msg = (
            "COMPONENT REGISTRY INTEGRITY CHECK FAILED:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info(
        f"Component registry integrity OK: "
        f"{len(SUPPORTED_COMPONENTS)} components, "
        f"{len(CONCEPT_TO_COMPONENT)} concept mappings."
    )


# Run validation at import time — fail fast on broken deployments
validate_registry_integrity()
