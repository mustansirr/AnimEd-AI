import asyncio
import sys
from pathlib import Path

# Add backend dir to path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from app.agents.nodes.coder import build_deterministic_scene

# Test 1: Linear Regression
scene1 = {
    "scene_type": "linear_regression",
    "learning_goal": "Understand best fit line",
    "visual_metaphor": "Scatter points aligning to trend",
    "title": "Linear Regression",
    "caption": "Finding the line of best fit",
    "components": ["GraphPlot"],
    "component_data": {
        "x_range": [0, 10, 1],
        "y_range": [0, 10, 1]
    },
    "animation_sequence": ["draw_axes", "show_points", "fit_line"],
    "duration": 5,
    "layout_zones": {"title": "TitleZone", "visualization": "VisualizationZone"}
}

# Test 2: Binary Search Tree
scene2 = {
    "scene_type": "binary_search_tree",
    "learning_goal": "Understand BST ordering",
    "visual_metaphor": "A tree with the root branching into smaller left nodes and larger right nodes",
    "title": "Binary Search Tree",
    "caption": "Smaller values go left, larger go right",
    "components": ["HierarchyDiagram"],
    "component_data": {
        "root_label": "50",
        "children_labels": ["30", "70"]
    },
    "animation_sequence": ["grow_tree", "highlight_node"],
    "duration": 5,
    "layout_zones": {"title": "TitleZone", "visualization": "VisualizationZone"}
}

# Test 3: Linear Search
scene3 = {
    "scene_type": "linear_search",
    "learning_goal": "Understand linear search array traversal",
    "visual_metaphor": "An array of elements scanned from left to right",
    "title": "Linear Search",
    "caption": "Scanning elements one by one",
    "components": ["ArrayDiagram"],
    "component_data": {
        "elements": [12, 45, 7, 89, 23]
    },
    "animation_sequence": ["grow_tree", "highlight_node"], # Reusing abstract animations for test
    "duration": 5,
    "layout_zones": {"title": "TitleZone", "visualization": "VisualizationZone"}
}

for i, scene in enumerate([scene1, scene2, scene3]):
    print(f"\n==================== TEST {i+1}: {scene['scene_type']} ====================")
    code = build_deterministic_scene(scene)
    print("... Generated Code Snippet ...")
    lines = [line for line in code.split("\n") if "main_comp =" in line or "title_card =" in line]
    for line in lines:
        print(line)
        
    try:
        compile(code, "<string>", "exec")
        print("[OK] Code compiled successfully without syntax errors.")
    except Exception as e:
        print(f"[ERROR] Syntax error in generated code: {e}")
