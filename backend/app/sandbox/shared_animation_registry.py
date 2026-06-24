SUPPORTED_ANIMATIONS = {
    "draw_axes",
    "show_points",
    "fit_line",
    "show_prediction",
    "fade_in_title",
    "grow_tree",
    "highlight_node",
    "fade_in_array",
    "highlight_element",
    "fade_in_flowchart",
    "highlight_step",
    "show_diagram",
    "fade_in_summary_diagram",
    "highlight_key_takeaways",
    "animate_flow",
    "gradient_descent_step",
    "binary_search_step"
}

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

# Provide a backwards-compatible way to get supported keys
SUPPORTED_COMPONENTS = set(COMPONENT_REGISTRY.keys())

SCENE_COMPONENT_RULES = {
    "coordinate_plot": ["GraphPlot", "FunctionPlot", "VectorArrow"],
    "hierarchical_structure": ["HierarchyDiagram"],
    "network_structure": ["NetworkDiagram"],
    "layered_network": ["NetworkDiagram"],
    "sequence_flow": ["ArrayDiagram", "FlowChart"],
    "process_flow": ["FlowChart"],
    "timeline": ["TimelineDiagram"],
    "algorithm_execution": ["ArrayDiagram", "FlowChart", "GraphPlot", "NetworkDiagram"],
    "generic_concept": [] # We will handle generic_concept in get_allowed_components
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

def get_allowed_components(scene_type: str) -> list[str]:
    """Return the allowed components for a given scene type / visualization strategy."""
    allowed = set(["TitleCard", "SummaryDiagram"]) # Ubiquitous components
    if scene_type == "generic_concept":
        allowed.update(SUPPORTED_COMPONENTS)
    elif scene_type in SCENE_COMPONENT_RULES:
        allowed.update(SCENE_COMPONENT_RULES[scene_type])
    else:
        allowed.update(SUPPORTED_COMPONENTS) # Fallback to all if unknown strategy
    return sorted(list(allowed))

