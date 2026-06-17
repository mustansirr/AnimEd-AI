# Changelog & Recent Architecture Updates

This document summarizes the recent architectural changes, new AI agents, and pipeline enhancements we've implemented. It's written in plain English so all team members can quickly get up to speed!

## 1. 🤖 New AI Agents Added

We moved away from a single monolithic LLM prompt to a multi-agent workflow using LangGraph. Each step of the video creation process is now handled by a specialized agent:

* **Concept Classifier**: Looks at the video topic and assigns the best pre-built "Visual Metaphor". For example, if the topic is "Surface Tension," it knows to use the `SurfaceTensionDiagram`.
* **Storyboard Agent**: Acts as the director. It breaks the topic down into logical, timed scenes (e.g., Intro, Core Explanation, Summary) and writes the narration script.
* **Scene JSON Generator**: Translates the storyboard into strict JSON data. It explicitly lists which Manim components are needed on screen for each scene.
* **Layout Agent**: Acts as the set designer. It takes the requested components and calculates exactly where they should be placed on the screen (X, Y coordinates) so they don't overlap.
* **Fix Agent (Auto-Healer)**: If the Coder agent writes bad Python/Manim code that fails our static analysis, the Fix Agent automatically steps in to rewrite and fix the code *before* we waste time rendering it.
* **Validators**: A suite of quality-control checkpoints (Schema, Layout, Diagram, Domain, Educational, and Video Quality). They review the output of the agents at every step to ensure the video makes sense and won't crash.

## 2. 🏗️ Core Pipeline Enhancements

* **Visual Metaphor Flow**: The pipeline now strictly follows a `Topic -> Visual Metaphor -> Component -> Animation -> Video` flow. This ensures that videos actually visualize concepts rather than just printing text on the screen.
* **Development Mode Bypasses**: We added a `DEVELOPMENT_MODE` toggle to the `workflow.py`. Previously, if a validator didn't perfectly like a scene, the entire pipeline would crash. Now, in development mode, it logs a warning but continues generating the video so you can actually see the output.
* **Docker Error Handling**: Fixed an issue where Manim crashes inside Docker would output weird characters, causing the Windows terminal to crash. Docker errors are now safely caught and dumped to local log files.

## 3. 🎨 Manim Component Upgrades

* **The `AnimatableComponent` Base Class**: We introduced a base class for all UI components. Now, every component automatically inherits fallback animation methods (like `get_intro_animations()`). If the LLM forgets to animate a component, it won't crash Manim anymore—it will just use the default fallback animation!
* **New Pre-Built Diagrams**: Added `SurfaceTensionDiagram` and `NeuralNetworkDiagram` to our `components.py` library.
* **Strict Argument Parsing**: Fixed a bug where the LLM would invent fake arguments (like `summary_diagram={...}`) and pass them into Manim classes, causing fatal `TypeError`s.

## 4. 🧪 Testing & Tooling

* **End-to-End Test Script**: Created `test_generation.py` in the root folder. You can run this script to trigger a full generation pipeline (from topic to final stitched `.mp4`) locally without needing to spin up the FastAPI server or hit the frontend. 

---

**Summary for GitHub**: We have successfully stabilized the video generation pipeline. By breaking the workload into specialized agents, adding graceful fallbacks for animations, and bypassing strict validation errors in dev mode, the system now successfully generates, renders, and stitches complete MP4 educational videos!
