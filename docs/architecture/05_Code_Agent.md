# Code Agent Documentation

This document details the complete implementation of the Code Agent (implemented as the **Manim Generator** and **Reflector**) within the Manima platform.

---

## 1. High-Level Purpose

The Code Agent is responsible for translating declarative, semantic scene specifications into executable Python code for the **Manim** animation engine.

- **Role in Pipeline:** It acts as the bridge between abstract layout planning and physical rendering. 
- **Input Provider:** It receives its primary input from the `Layout Agent` (which provides `positioned_jsons`).
- **Output Consumer:** Its output is consumed first by the `Static Analyzer` (for syntax checking) and then by the `Sandbox Renderer` (which executes the code).

---

## 2. Inputs

The Code Agent (in `coder.py`) reads the following from the `AgentState`:

- **`positioned_jsons` (List[PositionedJSON]):** The semantic blueprint of the scene, complete with selected components (e.g., `GraphPlot`), text strings, and layout zone coordinates. Originated from the `scene_json` and `layout` nodes.
- **`current_scene_index` (int):** The index of the scene currently being generated.
- **`storyboards` (List[StoryboardScene]):** Used strictly to identify the correct `scene_number` for database saving.
- **`video_id` (str):** Used for database updates.

**External Static Inputs:**
- **`components.py`:** The raw text of the visual component library is read from disk and injected directly into the preamble of the generated script.
- **`SUPPORTED_COMPONENTS`:** A registry of allowed classes.

---

## 3. Prompt Construction & Model Configuration

### Primary Generation (Deterministic)
The most critical architectural detail of the current Code Agent is that **it does not use an LLM for primary code generation.** 

Previous iterations likely used LLMs to write Manim code directly, resulting in high hallucination rates and syntax errors. The current implementation in `coder.py` is entirely deterministic. It uses string interpolation to map semantic JSON directly to a predefined Manim component library. 

*Therefore, there is no system prompt, user prompt, or model configuration for the initial code generation phase.*

### Self-Correction (Reflector Node)
If the deterministically generated code fails during Sandbox Execution (e.g., a Manim-specific runtime error), the workflow routes to the **Reflector Agent** (`reflector.py`), which *does* use an LLM.

- **System Prompt:** `REFLECTOR_SYSTEM_PROMPT` provides rules for fixing common Manim errors (e.g., `NameError`, `AttributeError`, missing `Scene` inheritance).
- **User Prompt:** 
  ```text
  BROKEN CODE:
  ```python
  [code]
  ```
  ERROR MESSAGE:
  [error string]
  Fix the code to resolve this error. Return only the corrected Python code.
  ```
- **Model Configuration:** Configured via `llm_factory.py` under the `"reflector"` role. Defaults to temperature `0.1` (highly deterministic) using the Groq/OpenRouter provider.
- **Dynamic Truncation:** If the broken code and error exceed 5000 tokens, the prompt dynamically truncates the code (last 2000 chars) and error (last 1000 chars).

---

## 4. Code Output

The output of the Code Agent updates the `AgentState` with:

- **`generated_codes` (List[str]):** A list containing the raw Python script strings. Each string is a complete, standalone Python file capable of being executed by Manim.
- **`current_scene_index` (int):** Incremented by 1 after successful generation.
- **`last_render_error` (str | None):** Cleared to `None` so the renderer knows it has a fresh script.

---

## 5. Code Generation Strategy

**Scene-by-Scene Generation:**
The video is *not* generated as one massive Python file. The Code Agent runs in a loop, generating one scene at a time (indexed by `current_scene_index`). Each scene is always named `class Scene1(Scene):`.

**Preamble & Setup:**
Every generated script starts with:
1. `from manim import *`
2. An `EducationalBackground` class (draws a subtle teal grid).
3. The entire injected source code of `components.py`.
4. The instantiation of `Scene1`.

**Component Instantiation:**
The agent reads `scene_spec.get("components")`. It explicitly checks this against a hardcoded `if/elif` block (e.g., `if comp_name == "GraphPlot": main_comp = GraphPlot(...)`). 

**Layout Determination:**
Layout logic is handled by passing components to a predefined helper: `LayoutZones.arrange_zones(title_zone, visualization_zone)`. 

**Animation Translation:**
Semantic animation intents (e.g., `"show_diagram"`, `"highlight"`) are mapped to component methods using `generate_animation_code()`. 
For example, `"highlight"` translates to calling `main_comp.get_highlight_animations()` inside a `self.play()` call. If the component lacks the method, it falls back to a default Manim primitive like `Indicate(main_comp)`.

**Timing Synchronization:**
The agent calculates wait times by taking the total `duration` from the JSON (minimum 5 seconds) and dividing it equally among the number of requested animations. `self.wait(wait_per_anim)` is inserted between each animation.

---

## 6. Scene Independence

**The Code Agent has absolutely no knowledge of previous scenes.**

- **Independence:** Every generated Python script is 100% self-contained. It defines `Scene1` and runs independently.
- **No Persistence:** Variables, objects, and camera states are not preserved between scenes. 
- **Reasoning:** Because LLMs struggle with maintaining global state across thousands of lines of coordinate math, the architecture forces strict encapsulation. Continuity is achieved by having the `Storyboard` enforce consistent themes, and the `Stitcher` (FFmpeg) seamlessly concatenates the independent MP4s at the end of the pipeline.

---

## 7. Visual Intelligence

The Code Agent possesses **no visual intelligence**.

- It does not reason about scene composition, camera movement, or object hierarchy.
- It acts purely as a dumb translator, mapping JSON strings to Python class constructors.
- **Automated Critic:** Visual intelligence is entirely delegated downstream to the `video_quality_evaluator` node (Vision LLM), which grades the output *after* it is rendered.

---

## 8. Manim Usage

- **Abstraction Layer:** The code heavily relies on a custom abstraction layer (`app/sandbox/components.py`). Instead of writing raw `Circle()`, `Line()`, or `Tex()`, the generator writes `BinarySearchDiagram(...)` or `FunctionPlot(...)`.
- **Primitives:** Raw primitives like `FadeIn`, `FadeOut`, `Wiggle`, and `Circumscribe` are used for fallback animations.
- **Backgrounds:** A custom `EducationalBackground` `NumberPlane` is used across all scenes for visual consistency.

---

## 9. Generated Files

- **State Storage:** The generated code exists purely as a string in `AgentState["generated_codes"]`.
- **Database Storage:** The code string is pushed to Supabase (`update_scene_code`) for observability.
- **Temporary Files:** The Code Agent itself creates no physical files. The downstream `Sandbox Renderer` takes the string, writes it to a temporary `.py` file inside the Docker volume, and executes it.

---

## 10. Validation & Relationship with Reviewer

**Validation Pipeline:**
1. **Syntax (`static_analyzer`):** Uses the Python `ast` module to ensure the generated string is valid Python and blocks forbidden imports (like `os` or `sys`) to prevent sandbox escapes.
2. **Execution (`renderer`):** Docker runs the code. If `stderr` contains errors, it fails.
3. **Recovery (`reflector`):** The LLM analyzes the `stderr` and rewrites the script.

**Relationship with Reviewers:**
- **Human Reviewer:** The Human Reviewer does *not* see the generated code. The human approves the *storyboard* before code is even written.
- **Vision Reviewer (`video_quality_evaluator`):** If the Vision LLM grades the rendered MP4 poorly (Score < 8), the graph routes to the `fix_agent`. The `fix_agent` decrements the `current_scene_index` and increments the `retry_count`. The graph routes back to the Code Agent, forcing it to regenerate the scene from scratch.

---

## 11. Important Files

- **`backend/app/agents/nodes/coder.py`**: Contains the deterministic `build_deterministic_scene()` string-builder and the LangGraph `generate_code` node.
- **`backend/app/agents/nodes/reflector.py`**: Contains the LLM fallback logic for repairing broken Manim scripts based on Python tracebacks.
- **`backend/app/sandbox/shared_animation_registry.py`**: Defines the `SUPPORTED_COMPONENTS` list that the coder is permitted to instantiate.

---

## 12. End-to-End Example

1. **Input:** `positioned_jsons` contains:
   ```json
   {
     "components": ["GraphPlot"],
     "component_data": {"learning_goal": "Linear growth"},
     "animation_sequence": ["show_diagram", "highlight"],
     "duration": 6
   }
   ```
2. **Generation (Deterministic):** `coder.py` reads `GraphPlot`. It appends the string `main_comp = GraphPlot(learning_goal='Linear growth')`.
3. **Animation Mapping:** It maps `"show_diagram"` to `FadeIn(main_comp)` and `"highlight"` to `main_comp.get_highlight_animations()`.
4. **Generated Python:**
   ```python
   from manim import *
   [EducationalBackground Class]
   [components.py Source]
   class Scene1(Scene):
       def construct(self):
           self.add(EducationalBackground())
           main_comp = GraphPlot(learning_goal='Linear growth')
           self.play(FadeIn(main_comp))
           self.wait(3.0)
           self.play(*main_comp.get_highlight_animations())
           self.wait(3.0)
   ```
5. **Execution:** Sent to Docker. If successful, state updates to `current_scene_index += 1`.
6. **Failure (Hypothetical):** If Docker returns `AttributeError: 'GraphPlot' has no attribute 'get_highlight_animations'`, the graph routes to `reflector.py`.
7. **Reflector LLM Prompt:** "BROKEN CODE: [code] ERROR: AttributeError... Fix the code."
8. **Reflector Output:** The LLM rewrites the highlight line to the fallback `self.play(Indicate(main_comp))` and overwrites the code in state. The graph loops back to the Renderer.
