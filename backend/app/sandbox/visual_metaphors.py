"""
Visual Metaphor Library

Maps STEM topics to concrete, understandable visual metaphors.
This ensures storyboards and animations are grounded in engaging real-world concepts.
"""

VISUAL_METAPHOR_LIBRARY = {
    # Physics
    "physics_surface_tension": "People pulling a rope inward, creating a tight outer layer",
    "physics_electric_field": "Gravity wells affecting nearby objects",
    "physics_particle": "Billiard balls colliding and transferring energy",
    "physics_force": "A tug-of-war where the strongest side wins",
    "physics_forces_multiple": "A tug-of-war where the strongest side wins",
    "physics_wave": "Ripples spreading out from a pebble dropped in a pond",
    "physics_droplet": "A balloon filled with water bulging under gravity",
    "physics_motion": "A car speeding up and slowing down on a track",
    
    # Mathematics
    "mathematics_theorem_law": "Building blocks fitting perfectly together to form a larger shape",
    "mathematics_area_proof": "Rearranging square areas like puzzle pieces",
    "geometry": "Drawing paths on a map to find the shortest route",
    "function_plot": "A roller coaster track mapping height over time",
    "linear_algebra": "Transforming a grid of streets into a new perspective",
    "statistics": "Sorting marbles into jars to see which is most full",

    # Computer Science
    "algorithm_search": "Looking up a word in a physical dictionary by splitting it in half",
    "algorithm_sort": "Organizing books on a shelf by height",
    "data_structure_tree": "A family tree showing ancestors and descendants",
    "data_structure_graph": "A map of cities connected by highways",
    "neural_network": "A group of experts voting on a decision based on their specialties",

    # Chemistry/Biology
    "chemistry_molecule": "Magnets snapping together to form a stable structure",
    "chemistry_atom": "A solar system with planets orbiting a central sun",
    "chemistry_reaction": "Baking a cake from raw ingredients to a new solid",
    "biology_process": "An assembly line in a factory building a product step-by-step",

    # General
    "process_flow": "Water flowing through pipes with different valves",
    "summary": "A highlight reel of the most important moments",
    "definition": "Opening a treasure chest to reveal the core meaning",
}

def get_visual_metaphor(topic: str) -> str:
    """Returns the visual metaphor for a given topic, or a generic fallback."""
    return VISUAL_METAPHOR_LIBRARY.get(topic, "A simple, clear visual explanation connecting the parts together")
