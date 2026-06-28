"""
Transition Engine for Manima components.
"""
from typing import Any, Sequence
from manim import Animation, ReplacementTransform

class TransitionResult:
    def __init__(self, animations: Sequence[Animation], new_state: dict):
        self.animations = animations
        self.new_state = new_state

class TransitionEngine:
    """
    Computes differences between states and delegates animation generation
    to components, or falls back to generic transitions.
    """
    
    @staticmethod
    def compute_diff(old_state: dict, new_state: dict) -> dict:
        diff = {}
        # Collect changed or added keys
        for k, v in new_state.items():
            if k not in old_state or old_state[k] != v:
                diff[k] = (old_state.get(k), v)
        # Collect removed keys
        for k in old_state:
            if k not in new_state:
                diff[k] = (old_state[k], None)
        return diff

    @staticmethod
    def transition(component: Any, old_state: dict, new_state: dict, strategy: str = "morph") -> TransitionResult:
        """
        Transitions a component from old_state to new_state.
        Returns a TransitionResult containing the animations and updated state.
        """
        diff = TransitionEngine.compute_diff(old_state, new_state)
        
        # If no diff, no animations needed unless forced
        if not diff and strategy != "force":
            return TransitionResult([], new_state)
            
        # If component supports native transitions
        if hasattr(component, "transition_to"):
            try:
                result = component.transition_to(diff, old_state, new_state)
                # If the component returns a dict matching TransitionResult
                if isinstance(result, dict) and "animations" in result and "new_state" in result:
                    return TransitionResult(result["animations"], result["new_state"])
                # If it just returns animations
                return TransitionResult(result, new_state)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Component {component.__class__.__name__} failed transition_to: {e}. Falling back.")
                
        # Generic Fallback: Re-instantiate and ReplacementTransform
        try:
            new_comp = component.__class__(**new_state)
            try:
                new_comp.match_x(component).match_y(component)
            except Exception:
                pass
            return TransitionResult([ReplacementTransform(component, new_comp)], new_state)
        except Exception:
            return TransitionResult([], new_state)
