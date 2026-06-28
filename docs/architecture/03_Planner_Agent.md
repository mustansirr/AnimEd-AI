# Planner Agent Documentation

This document details the complete implementation of the Planner Agent in the Manima platform.

---

## 1. High-Level Purpose

The **Planner Agent** acts as the curriculum director within the LangGraph workflow.

- **Problem Solved:** When users request a video (e.g., "Explain Neural Networks"), an LLM cannot directly write accurate, multi-minute Manim code in a single shot. The Planner breaks down broad topics into a structured, pedagogical sequence of distinct teaching scenes.
- **Why it Exists:** It enforces educational quality standards. It ensures videos follow a logical flow (Introduction → Concept → Demonstration → Example → Summary) rather than presenting a single overwhelming wall of text or an unstructured animation.
- **Consumers:** The output is immediately consumed by the `Concept Classifier` (which uses the title) and the `Storyboard Agent` (which expands the scene outlines into full narration scripts).

---

## 2. Inputs

The Planner Agent reads the following state variables from the `AgentState`:

- **`video_id` (str):** The database UUID of the video being generated (used for logging and database status updates).
- **`user_prompt` (str):** The original request supplied by the user on the frontend.
- **`syllabus_context` (str):** The RAG-retrieved text context chunks (if the user uploaded a PDF). Sourced from the `retrieve_info` node prior to the planner.

**Static Inputs:**
- **`PLANNER_SYSTEM_PROMPT`:** The strict instructional prompt governing educational boundaries.

---

## 3. Prompt Construction

The LLM prompt is assembled dynamically in `app/agents/prompts/planner_prompts.py` using `create_planner_prompt()`.

**System Prompt:**
The system prompt strictly commands the LLM to behave as a curriculum expert. It enforces:
- A specific 5-step educational progression.
- Exact JSON output formatting.
- Strict limits (maximum of 5 scenes, concise titles).

**User Prompt:**
The user prompt interpolates the retrieved RAG context and the user's initial request.
```text
Syllabus Context (use this to guide your planning):
---
[RAG Content Here]
---

User Request: [User Prompt Here]

Create a detailed video plan following the system instructions.
Return ONLY valid JSON, no additional text or markdown formatting.
```

**Dynamic Token Management:**
Before calling the LLM, the node estimates the token count of the combined prompt using `tiktoken`. If the total estimated tokens exceed **5,000**, the `syllabus_context` is actively truncated and replaced with `[TRUNCATED DUE TO LENGTH LIMITS]` to prevent context window overflow errors.

---

## 4. Model Configuration

The Planner LLM is instantiated via `create_llm("planner", temperature=0.7)` from `app/services/llm_factory.py`.

- **Model Provider:** Configured via environment variables (defaults to Groq).
- **Model Name:** Recommended `llama-3.3-70b-versatile` (or similar high-capability instruction model).
- **Temperature:** `0.7` (allows creative but structured curriculum planning).
- **Response Format:** The prompt requests plain JSON. No strict Pydantic structured output (`response_format={"type": "json_object"}`) is used at the LangChain layer.
- **Parsing:** Responses are cleaned manually using `_parse_json_response()` which strips markdown code blocks (e.g., ` ```json `) and fixes unescaped backslashes (often generated when the LLM outputs LaTeX math strings).

---

## 5. Planner Output

The Planner node returns a dictionary that updates the following `AgentState` fields:

- **`video_title`** (Type: `str`): The overall title of the video. 
  - *Example:* `"Introduction to Neural Networks"`
- **`topic_breakdown`** (Type: `List[str]`): A list of high-level learning objectives.
  - *Example:* `["Understand perceptrons", "Learn backpropagation"]`
- **`scene_plans`** (Type: `List[ScenePlan]`): The core output. A list of TypedDict objects containing:
  - `scene_number` (`int`): Sequential ordering.
  - `title` (`str`): Short title for the scene.
  - `key_concepts` (`List[str]`): Brief conceptual tags.
  - `visual_type` (`str`): Suggested abstract visual style (e.g., `"text_animation"`, `"diagram"`, `"graph"`).
  - `duration_seconds` (`int`): Estimated time (usually defaults to `60`).

---

## 6. Planning Logic

The Planner Agent contains specific, hardcoded business logic to ensure quality:

- **Scene Boundaries:** Enforced by the system prompt, which mandates exactly one concept per scene.
- **Concept Ordering:** The system prompt dictates a rigid educational flow: `Introduction Scene -> Concept Scene -> Visual Demonstration Scene -> Example Scene -> Comparison Scene -> Summary Scene`.
- **Minimum Scene Enforcement:** After the LLM generates a response, the node counts the number of generated scenes. If there are fewer than **5 scenes**, it rejects the output, appends an error (`"ERROR: Your previous plan only had X scenes..."`), and regenerates the response.
- **Visual & Animation Planning:** The planner does *not* plan specific coordinates, objects, or animations. It only assigns a high-level `visual_type` (e.g., `graph` or `equation`) to guide the downstream Scripter.

---

## 7. Downstream Usage

The output of the Planner is consumed by the following nodes:

1. **`concept_classifier.py`**: Reads `AgentState["video_title"]` to help deduce the overall mathematical or scientific domain (e.g., determining if the video requires a `NeuralNetworkDiagram` or `FunctionPlot`).
2. **`storyboard_agent.py`**: Iterates through every item in `AgentState["scene_plans"]`. It expands the short `key_concepts` and `visual_type` into a detailed `StoryboardScene` containing a full narration script and a list of specific visual objects to be drawn on screen.

*Ignored Fields:* The `duration_seconds` field is currently carried forward but is mostly overridden by the text-to-speech timing later in the pipeline.

---

## 8. Error Handling

- **Parsing Resiliency:** `_parse_json_response()` aggressively scrubs markdown formatting and regex-replaces malformed LaTeX backslashes before attempting `json.loads(strict=False)`.
- **Validation Retries:** Implements a `max_attempts = 3` loop. It retries if `JSONDecodeError` occurs or if the scene count is `< 5`.
- **Hard Failure / Fatal Routing:**
  - If the LLM throws a `413 Payload Too Large` or Rate Limit error, the node immediately logs a `FATAL ERROR`, updates the database video status to `FAILED`, and sets `last_render_error`.
  - If 0 scenes are generated after 3 attempts, the workflow is aborted.

---

## 9. Important Files

- **`backend/app/agents/nodes/planner.py`**: The core execution node. Handles token counting, LLM invocation, JSON parsing, retry loops, and state updates.
- **`backend/app/agents/prompts/planner_prompts.py`**: Contains `PLANNER_SYSTEM_PROMPT` and the `create_planner_prompt()` function.

---

## 10. Execution Walkthrough

1. **Invocation:** LangGraph routes to `plan_scenes()`. The video status in Supabase is updated to `PLANNING`.
2. **Prompt Assembly:** `create_planner_prompt` is called with "What is a Binary Search Tree?" and the RAG context.
3. **Token Check:** `tiktoken` estimates 1,200 tokens. (Passes the < 5,000 threshold).
4. **Generation (Attempt 1):** `llm.ainvoke` is called. The LLM returns a markdown block: ` ```json { "title": "...", "scenes": [...] } ``` `.
5. **Parsing:** The node strips the markdown and parses the JSON.
6. **Validation:** The node counts the scenes. If the LLM returned 4 scenes, the code logs a warning, appends an error to the prompt, and loops to Attempt 2.
7. **Generation (Attempt 2):** The LLM returns 5 scenes.
8. **Return:** The node packages `video_title`, `topic_breakdown`, and `scene_plans` into a dict and returns it, updating the global `AgentState`. The graph routes to the next node.

---

## 11. Notes

- **Token Economy:** The active truncation of the `syllabus_context` based on a 5000-token limit is a critical stability feature. Since PDFs can be vast, and the embedding retriever might pull dense chunks, this prevents the Planner from crashing on strict API context limits.
- **Separation of Concerns:** The Planner intentionally avoids writing narration. This separation allows the Planner to focus purely on pedagogical structure (the "bones"), leaving the Scripter to focus on pacing and prose (the "meat").
