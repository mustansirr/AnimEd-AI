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

SUPPORTED_COMPONENTS = {
    "TitleCard",
    "FlowChart",
    "GraphPlot",
    "HierarchyDiagram",
    "NetworkDiagram",
    "TimelineDiagram",
    "ArrayDiagram",
    "SummaryDiagram",
    "NumberLineDiagram",
    "FunctionPlot",
    "VectorArrow",
    "MatrixDisplay",
    "GeometryDiagram",
    "BarChartDiagram",
    "BinarySearchDiagram",
    "GradientDescentPlot",
    "SurfaceTensionDiagram",
    "NeuralNetworkDiagram"
}

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

