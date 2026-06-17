import json
import logging
import re
from typing import Dict

from app.services.llm_factory import create_llm
from app.agents.state import AgentState
from app.agents.prompts.classifier_prompts import (
    CLASSIFIER_SYSTEM_PROMPT,
    create_classifier_prompt,
)
from app.sandbox.visual_metaphors import get_visual_metaphor

logger = logging.getLogger(__name__)

CONCEPT_TO_COMPONENT = {
    # Computer Science
    "algorithm_search": "ArrayDiagram",
    "algorithm_sort": "ArrayDiagram",
    "data_structure_tree": "TreeDiagram",
    "data_structure_graph": "GraphDiagram",
    "neural_network": "NeuralNetworkDiagram",
    # Mathematics
    "geometry": "CoordinateGeometryDiagram",
    "mathematics_theorem_law": "RightTriangleDiagram",
    "mathematics_area_proof": "AreaProofDiagram",
    "function_plot": "FunctionPlotDiagram",
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
    # Biology/Chemistry
    "biology_process": "FlowChart",
    "chemistry_molecule": "MoleculeDiagram",
    "chemistry_atom": "AtomDiagram",
    "chemistry_reaction": "ReactionDiagram",
    # General
    "process_flow": "FlowChart",
    "summary": "SummaryDiagram",
    "definition": "SummaryDiagram",
}

async def classify_concept(state: AgentState) -> dict:
    """
    Classifies the user's topic into a predefined STEM category.
    """
    logger.info("--- ENTERING CONCEPT_CLASSIFIER NODE ---")
    video_id = state["video_id"]
    user_prompt = state["user_prompt"]
    video_title = state.get("video_title", "Unknown")

    logger.info(f"Classifying concept for video {video_id}...")

    llm = create_llm("planner", temperature=0.0) # Use planner model, it's cheap and smart enough
    prompt = create_classifier_prompt(user_prompt, video_title)

    try:
        response = await llm.ainvoke([
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ])
        
        content = response.content.strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
            
        data = json.loads(content)
        topic = data.get("topic", video_title)
        concept_type = data.get("concept_type", "generic_concept")
        confidence = data.get("confidence", 1.0)
        
        if confidence < 0.7:
            logger.warning(f"Low confidence ({confidence}) for video {video_id}. Attempting multi-pass classification with smarter model.")
            # Use a smarter model for the second pass
            smart_llm = create_llm("scripter", temperature=0.2)
            smart_response = await smart_llm.ainvoke([
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt + "\n\nCRITICAL: Your previous attempt yielded low confidence. Think deeply about the underlying structural framework of this concept."},
            ])
            smart_content = smart_response.content.strip()
            smart_match = re.search(r'\{.*\}', smart_content, re.DOTALL)
            if smart_match:
                smart_content = smart_match.group(0)
            smart_data = json.loads(smart_content)
            
            smart_confidence = smart_data.get("confidence", 0.0)
            if smart_confidence > confidence:
                concept_type = smart_data.get("concept_type", "generic_concept")
                topic = smart_data.get("topic", topic)
                logger.info(f"Second pass succeeded with confidence {smart_confidence}: Strategy -> {concept_type}")
            else:
                logger.info("Second pass failed to improve confidence. Falling back to generic_concept.")
                concept_type = "generic_concept"
        
        component_suggestion = CONCEPT_TO_COMPONENT.get(concept_type, "SummaryDiagram")
        metaphor = get_visual_metaphor(concept_type)
        
        # Component Coverage Tracking
        from app.sandbox.shared_animation_registry import SUPPORTED_COMPONENTS
        # Simple heuristic: if we suggested a specific class that isn't SummaryDiagram, and it's a known string.
        # But we also have components.py. Let's just track based on if it's generic.
        coverage = "YES" if component_suggestion != "SummaryDiagram" else "NO"
        
        logger.info(f"\n--- COMPONENT COVERAGE TRACKING ---")
        logger.info(f"Topic: {topic}")
        logger.info(f"Required Component: {component_suggestion}")
        logger.info(f"Available: {coverage}")
        logger.info(f"-----------------------------------\n")
        
        logger.info(f"Classified video {video_id} -> Concept: {concept_type}, Suggested Component: {component_suggestion}")
        
        # END-TO-END VERIFICATION LOG
        logger.info(f"Classifier Component: {component_suggestion}")
        
        logger.info("--- EXITING CONCEPT_CLASSIFIER NODE ---")
        return {
            "concept_topic": topic,
            "concept_type": concept_type,
            "suggested_component": component_suggestion,
            "visual_metaphor": metaphor,
            "visualization_strategy": concept_type # Keep this for backwards compatibility
        }
        
    except Exception as e:
        logger.warning(f"Concept classification failed: {e}. Defaulting to 'generic_concept'.")
        logger.info("--- EXITING CONCEPT_CLASSIFIER NODE ---")
        return {
            "concept_topic": video_title,
            "concept_type": "generic_concept",
            "suggested_component": "SummaryDiagram",
            "visual_metaphor": "A simple, clear visual explanation",
            "visualization_strategy": "generic_concept"
        }
