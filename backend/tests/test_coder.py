import asyncio
import sys
from pathlib import Path

# Add backend dir to path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from app.agents.nodes.coder import build_deterministic_scene

scene_spec = {
    "scene_type": "linear_regression",
    "learning_goal": "Understand best fit line",
    "visual_metaphor": "Scatter points aligning to trend",
    "title": "Linear Regression",
    "caption": "Finding the line of best fit",
    "components": ["GraphPlot"],
    "animation_sequence": ["draw_axes", "show_points", "fit_line"],
    "duration": 5,
    "layout_zones": {
        "title": "TitleZone",
        "visualization": "VisualizationZone"
    }
}

code = build_deterministic_scene(scene_spec)
print("--- GENERATED CODE ---")
print(code[:500] + "\n...\n" + code[-500:])

try:
    # Try to compile it to catch basic python syntax errors
    compile(code, "<string>", "exec")
    print("\n[OK] Code compiled successfully without syntax errors.")
except Exception as e:
    print(f"\n[ERROR] Syntax error in generated code: {e}")
