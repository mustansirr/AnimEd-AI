# SceneJSON Architecture

This document details the complete architecture of **SceneJSON**, the intermediate representation (IR) connecting the Storyboard Agent to the deterministic Code Generator within the Manima platform.

---

## 1. High-Level Purpose

**SceneJSON** (also referred to as Semantic Scene Specification v2) exists to decouple educational storytelling from physical rendering.

- **Why a Semantic IR?** Large Language Models are highly capable of writing educational scripts, but they struggle severely with spatial reasoning, pixel math, and complex 2D geometry coordinate systems. Generating raw Manim Python code directly from an LLM results in high hallucination rates, intersecting objects, and syntax errors.
- **The Solution:** Instead of telling the renderer *how* to draw (e.g., `Circle(radius=2).move_to(UP)`), the LLM outputs a SceneJSON describing *what* to draw semantically (e.g., `TreeDiagram` with `root_label: 50`). The deterministic `Code Agent` then translates this JSON into flawless Manim code using a predefined component library.

---

## 2. Schema

The SceneJSON structure is defined via TypedDicts in `app/agents/state.py`.

### `SceneJSON`

| Name | Type | Purpose | Example |
|------|------|---------|---------|
| `schema_version` | `str` | Specifies IR versioning for backwards compatibility. | `"v2"` |
| `scene_type` | `str` | The high-level topic domain. | `"binary_search_tree"` |
| `learning_goal` | `str` | The educational objective of the scene. | `"Understand BST ordering"` |
| `visual_metaphor` | `str` | Instructs the renderer on the thematic approach. | `"A tree with root branching..."` |
| `title` | `str` | The large header text to display on screen. | `"Binary Search Tree"` |
| `caption` | `str` | Subtitle or explanatory text for the bottom of the screen. | `"Smaller values go left"` |
| `components` | `List[str]` | The specific Python classes to instantiate from the sandbox. | `["TreeDiagram"]` |
| `component_data` | `dict` | Key-value pairs containing the semantic data to feed the component. | `{"root_label": "50", "children_labels": ["30", "70"]}` |
| `animation_sequence` | `List[str]` | Abstract intents defining what actions occur. | `["intro", "highlight"]` |
| `duration` | `int` | Time in seconds the scene should remain on screen. | `10` |

### `PositionedJSON` (Nested extension)
After the Layout Agent runs, `SceneJSON` is extended into `PositionedJSON` by appending:
| Name | Type | Purpose | Example |
|------|------|---------|---------|
| `layout_zones` | `dict` | Maps content to abstract spatial zones (Top, Middle, Bottom). | `{"title": "TitleZone", "visualization": "VisualizationZone"}` |

---

## 3. Component System

Components are identified strictly by their **class name string** (e.g., `"GraphPlot"`, `"ArrayDiagram"`, `"MoleculeDiagram"`). The `scene_json_generator.py` enforces a rigid allowlist against the `SUPPORTED_COMPONENTS` registry. 

**Component-Specific Data Storage:**
The `component_data` dictionary acts as a flexible kwargs payload passed directly to the component's Python constructor.
- **ArrayDiagram:** `{"elements": [1, 5, 10, 20]}`
- **TreeDiagram:** `{"root_label": "A", "children_labels": ["B", "C"]}`
- **NetworkDiagram:** `{"layers": [["Input1", "Input2"], ["Hidden1"], ["Output"]]}`

If the LLM hallucinates a component (e.g., `"MagicWand"`), the node throws a `ValueError` and falls back.

---

## 4. Animation Representation

SceneJSON intentionally **does not** represent low-level Manim animations. It cannot represent specific `Zoom`, `Rotation`, `TransformFromCopy`, or specific camera pan coordinates.

Instead, animations are represented as an array of **Semantic Intents**. The strict allowlist includes:
- `"intro"`
- `"highlight"`
- `"transform"`
- `"explain"`
- `"focus"`

**Sequencing vs Parallel:**
Currently, animations in the `animation_sequence` list are executed **sequentially**. The deterministic Code Agent maps each string to a component method (e.g., `"intro"` -> `main_comp.get_intro_animations()`) and executes them sequentially with `self.play()`, inserting wait times in between. Parallel animations are not natively supported by the JSON structure unless handled internally by the component's specific method.

---

## 5. Layout Representation

Before the Layout Agent runs, SceneJSON contains **no spatial information**. There are no coordinates, anchors, constraints, or alignments.

Once passed to the Layout Agent, it assigns layout information using **Zones**. It evaluates the existing JSON keys:
- If `title` exists -> Assigned to `"TitleZone"` (Top of screen)
- If `components` exist -> Assigned to `"VisualizationZone"` (Center of screen)
- If `caption` exists -> Assigned to `"ExplanationZone"` (Bottom of screen)

This zone mapping (`layout_zones` dict) ensures the deterministic Code Agent places objects without overlapping text.

---

## 6. Educational Information

SceneJSON is capable of representing:
- **`learning_goal`**: Top-level string explaining what must be understood.
- **`visual_metaphor` / `visual_intent`**: Thematic instructions.
- **`title` & `caption`**: Explicit visual hierarchy (Main topic vs subtext).

**What it CANNOT represent:**
- Misconceptions.
- Frame-perfect narration synchronization (narration text is stripped out entirely before reaching the Code Agent).
- Specific emphasis on sub-parts of an equation (unless handled internally by a highly specialized component).

---

## 7. Scene Relationships

**SceneJSON represents scenes entirely independently. There are no relationships between scenes.**

- **Previous Scene References:** None.
- **Persistent Objects / Reused Objects:** Not supported. Every scene instantiates its objects entirely from scratch.
- **Shared Camera / Object IDs:** No global state exists.
- **Transitions / Morphing:** You cannot morph an object from Scene 1 into Scene 2. 

*Why?* The prompt explicitly instructs the LLM: *"When transitioning between scenes, maintain visual continuity by reusing the same components... To show progression, modify `component_data` rather than switching components."* Continuity is faked by drawing an identical `ArrayDiagram` in Scene 2 but with updated array values in `component_data`.

---

## 8. Conversion Process

When the **Scene JSON Generator** converts the Storyboard to SceneJSON:
- **Information that Survives:** The learning objective (`goal` -> `learning_goal`), the visual concepts (`visuals` -> `components` & `component_data`), abstract actions (`animations` -> `animation_sequence`), and `duration`.
- **Information Discarded:** The `narration` text is completely discarded from the JSON. The English conversational prose is thrown away, leaving only the mechanical instructions.

---

## 9. Validation

Validation is handled in multiple discrete steps:
1. **Node Logic (Generation):** The generation node ensures the output component is in the `allowed_components` list. If the Concept Classifier specifically mandated a component (e.g., `ForceVectorDiagram`), the node forcefully overrides the LLM to guarantee adherence.
2. **`schema_validator.py`:** A deterministic check ensuring `components`, `scene_type`, and `animation_sequence` fields exist and are of type `List`.
3. **`domain_validator.py` & `educational_validator.py`:** These nodes act as semantic checks in the LangGraph, capable of failing the graph if the semantic intent is fundamentally flawed (though they rely on downstream pipeline robustness to handle edge cases).

---

## 10. Examples

### Example 1: Binary Search Tree
```json
{
  "schema_version": "v2",
  "scene_type": "data_structure_tree",
  "learning_goal": "Understand tree hierarchy",
  "visual_metaphor": "Nodes branching downward",
  "title": "Binary Tree",
  "caption": "Root node has two children",
  "components": ["TreeDiagram"],
  "component_data": {
    "root_label": "50",
    "children_labels": ["30", "70"]
  },
  "animation_sequence": ["intro", "highlight"],
  "duration": 6
}
```

### Example 2: Physics Motion / Graph
```json
{
  "schema_version": "v2",
  "scene_type": "physics_motion",
  "learning_goal": "Visualize constant acceleration",
  "visual_metaphor": "An upward curving parabola",
  "title": "Velocity over Time",
  "caption": "Speed increases steadily",
  "components": ["FunctionPlot"],
  "component_data": {
    "function_type": "quadratic",
    "x_label": "Time (s)",
    "y_label": "Velocity (m/s)"
  },
  "animation_sequence": ["intro", "explain"],
  "duration": 8
}
```

### Example 3: Array Sorting
```json
{
  "schema_version": "v2",
  "scene_type": "algorithm_sort",
  "learning_goal": "Show elements swapping",
  "visual_metaphor": "Boxes containing numbers",
  "title": "Bubble Sort Step 1",
  "caption": "Comparing the first two elements",
  "components": ["ArrayDiagram"],
  "component_data": {
    "elements": [5, 2, 8, 1]
  },
  "animation_sequence": ["intro", "highlight", "transform"],
  "duration": 7
}
```

---

## 11. Important Files

- **`backend/app/agents/state.py`**: Defines the TypedDict schema for `SceneJSON` and `PositionedJSON`.
- **`backend/app/agents/prompts/scene_json_prompts.py`**: Contains the system prompts enforcing the JSON schema and mapping Storyboard concepts to allowable components.
- **`backend/app/agents/nodes/scene_json_generator.py`**: The node that calls the LLM and executes the strict component allowlist validation.
- **`backend/app/agents/nodes/layout_agent.py`**: The node that upgrades `SceneJSON` into `PositionedJSON` by adding spatial zones.
- **`backend/app/agents/nodes/schema_validator.py`**: Intercepts the JSON to guarantee structural integrity before it reaches layout or code generation.

---

## 12. Notes

- **The Enforcer:** SceneJSON is the primary defense against LLM hallucination. By reducing the LLM's output space from "Turing-complete Python geometry" to "5 allowed animations and 10 allowed classes", the system dramatically increases render success rates.
- **Simulated Animation State:** Because components are instantiated fresh every scene, "transform" animations typically involve the component internally managing an initial state and an end state (based on its `component_data`) rather than a true continuous Manim `Transform` between two separate scenes.
