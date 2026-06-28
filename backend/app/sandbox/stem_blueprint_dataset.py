"""
stem_blueprint_dataset.py
==========================================================================
STEM Blueprint Dataset — Knowledge Base for Curriculum-Aligned
Educational Video Generation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from collections import defaultdict


class BlueprintCategory(str, Enum):
    MATHEMATICS_THEOREM = "mathematics_theorem"
    MATHEMATICS_GEOMETRY = "mathematics_geometry"
    MATHEMATICS_CALCULUS = "mathematics_calculus"
    MATHEMATICS_ALGEBRA = "mathematics_algebra"
    MATHEMATICS_STATISTICS = "mathematics_statistics"
    MATHEMATICS_LINEAR_ALGEBRA = "mathematics_linear_algebra"
    PHYSICS_FORCES = "physics_forces"
    PHYSICS_ELECTRICITY = "physics_electricity"
    PHYSICS_WAVES = "physics_waves"
    PHYSICS_MECHANICS = "physics_mechanics"
    PHYSICS_OPTICS = "physics_optics"
    PHYSICS_MAGNETISM = "physics_magnetism"
    PHYSICS_SURFACE_TENSION = "physics_surface_tension"
    CHEMISTRY_ATOMIC_STRUCTURE = "chemistry_atomic_structure"
    CHEMISTRY_REACTION = "chemistry_reaction"
    CHEMISTRY_BONDING = "chemistry_bonding"
    CHEMISTRY_EQUILIBRIUM = "chemistry_equilibrium"
    CHEMISTRY_ELECTROCHEMISTRY = "chemistry_electrochemistry"
    COMPUTER_SCIENCE_ALGORITHMS = "computer_science_algorithms"
    COMPUTER_SCIENCE_DATA_STRUCTURES = "computer_science_data_structures"
    COMPUTER_SCIENCE_GRAPH_THEORY = "computer_science_graph_theory"
    COMPUTER_SCIENCE_THEORY = "computer_science_theory"
    COMPUTER_SCIENCE_NETWORKS = "computer_science_networks"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"
    ENGINEERING_MECHANICAL = "engineering_mechanical"
    ENGINEERING_CIVIL = "engineering_civil"
    ENGINEERING_ELECTRICAL = "engineering_electrical"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class VisualElementType(str, Enum):
    SHAPE = "shape"
    LABEL = "label"
    EQUATION = "equation"
    AXIS = "axis"
    VECTOR = "vector"
    NODE = "node"
    EDGE = "edge"
    PLOT = "plot"
    ARRAY_CELL = "array_cell"
    ANNOTATION = "annotation"
    ICON = "icon"
    HIGHLIGHT = "highlight"
    TABLE_CELL = "table_cell"
    PATH = "path"
    REGION = "region"

class ValidationSeverity(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class VisualElement:
    element_id: str
    name: str
    element_type: VisualElementType
    description: str
    is_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "name": self.name,
            "element_type": self.element_type.value,
            "description": self.description,
            "is_required": self.is_required,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VisualElement":
        return cls(
            element_id=data["element_id"],
            name=data["name"],
            element_type=VisualElementType(data["element_type"]),
            description=data["description"],
            is_required=bool(data.get("is_required", True)),
        )

@dataclass(frozen=True)
class AnimationTemplate:
    template_id: str
    name: str
    description: str
    sequence_order: int
    duration_seconds: float = 2.0
    easing: str = "smooth"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "sequence_order": self.sequence_order,
            "duration_seconds": self.duration_seconds,
            "easing": self.easing,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnimationTemplate":
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            sequence_order=int(data["sequence_order"]),
            duration_seconds=float(data.get("duration_seconds", 2.0)),
            easing=data.get("easing", "smooth"),
        )

@dataclass(frozen=True)
class CameraBehavior:
    initial_framing: str
    movements: List[str] = field(default_factory=list)
    focus_points: List[str] = field(default_factory=list)
    zoom_strategy: str = "static"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_framing": self.initial_framing,
            "movements": list(self.movements),
            "focus_points": list(self.focus_points),
            "zoom_strategy": self.zoom_strategy,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CameraBehavior":
        return cls(
            initial_framing=data["initial_framing"],
            movements=list(data.get("movements", [])),
            focus_points=list(data.get("focus_points", [])),
            zoom_strategy=data.get("zoom_strategy", "static"),
        )

@dataclass(frozen=True)
class ValidationRule:
    rule_id: str
    description: str
    severity: ValidationSeverity
    check_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity.value,
            "check_type": self.check_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationRule":
        return cls(
            rule_id=data["rule_id"],
            description=data["description"],
            severity=ValidationSeverity(data["severity"]),
            check_type=data["check_type"],
        )

@dataclass
class STEMBlueprint:
    blueprint_id: str
    topic: str
    category: BlueprintCategory
    learning_objective: str
    visual_metaphor: str
    primary_component: str
    supporting_components: List[str]
    required_visual_elements: List[VisualElement]
    animation_templates: List[AnimationTemplate]
    camera_behavior: CameraBehavior
    difficulty_level: DifficultyLevel
    keywords: List[str]
    validation_rules: List[ValidationRule]
    version: str = "1.0.0"
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("STEMBlueprint.topic must not be empty")
        if not self.blueprint_id.strip():
            raise ValueError("STEMBlueprint.blueprint_id must not be empty")
        if not self.primary_component.strip():
            raise ValueError(f"'{self.topic}': primary_component must not be empty")
        if not self.required_visual_elements:
            raise ValueError(f"'{self.topic}': at least one required_visual_element must be defined")
        if not self.animation_templates:
            raise ValueError(f"'{self.topic}': at least one animation_template must be defined")
        self.keywords = sorted({kw.strip().lower() for kw in self.keywords if kw.strip()})
        orders = sorted(t.sequence_order for t in self.animation_templates)
        if orders != list(range(1, len(orders) + 1)):
            raise ValueError(f"'{self.topic}': animation_templates.sequence_order must be a contiguous 1..N sequence")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "topic": self.topic,
            "category": self.category.value,
            "learning_objective": self.learning_objective,
            "visual_metaphor": self.visual_metaphor,
            "primary_component": self.primary_component,
            "supporting_components": list(self.supporting_components),
            "required_visual_elements": [ve.to_dict() for ve in self.required_visual_elements],
            "animation_templates": [at.to_dict() for at in self.animation_templates],
            "camera_behavior": self.camera_behavior.to_dict(),
            "difficulty_level": self.difficulty_level.value,
            "keywords": list(self.keywords),
            "validation_rules": [vr.to_dict() for vr in self.validation_rules],
            "version": self.version,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "STEMBlueprint":
        return cls(
            blueprint_id=data["blueprint_id"],
            topic=data["topic"],
            category=BlueprintCategory(data["category"]),
            learning_objective=data["learning_objective"],
            visual_metaphor=data["visual_metaphor"],
            primary_component=data["primary_component"],
            supporting_components=list(data.get("supporting_components", [])),
            required_visual_elements=[VisualElement.from_dict(ve) for ve in data["required_visual_elements"]],
            animation_templates=[AnimationTemplate.from_dict(at) for at in data["animation_templates"]],
            camera_behavior=CameraBehavior.from_dict(data["camera_behavior"]),
            difficulty_level=DifficultyLevel(data["difficulty_level"]),
            keywords=list(data.get("keywords", [])),
            validation_rules=[ValidationRule.from_dict(vr) for vr in data["validation_rules"]],
            version=data.get("version", "1.0.0"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )

class BlueprintRegistryError(Exception):
    pass

class DuplicateBlueprintError(BlueprintRegistryError):
    pass

class BlueprintNotFoundError(BlueprintRegistryError):
    pass


class STEMBlueprintRegistry:
    def __init__(self) -> None:
        self._blueprints: Dict[str, STEMBlueprint] = {}
        self._topic_to_id: Dict[str, str] = {}
        self._category_index: Dict[BlueprintCategory, Set[str]] = defaultdict(set)
        self._keyword_index: Dict[str, Set[str]] = defaultdict(set)
        self._component_index: Dict[str, Set[str]] = defaultdict(set)
        self._difficulty_index: Dict[DifficultyLevel, Set[str]] = defaultdict(set)

    def register_blueprint(self, blueprint: STEMBlueprint, overwrite: bool = False) -> None:
        if blueprint.blueprint_id in self._blueprints and not overwrite:
            raise DuplicateBlueprintError(f"Blueprint '{blueprint.blueprint_id}' is already registered.")
        if blueprint.blueprint_id in self._blueprints:
            self._deindex(self._blueprints[blueprint.blueprint_id])
        self._blueprints[blueprint.blueprint_id] = blueprint
        self._topic_to_id[blueprint.topic.strip().lower()] = blueprint.blueprint_id
        self._category_index[blueprint.category].add(blueprint.blueprint_id)
        self._difficulty_index[blueprint.difficulty_level].add(blueprint.blueprint_id)
        for keyword in blueprint.keywords:
            self._keyword_index[keyword].add(blueprint.blueprint_id)
        for component in [blueprint.primary_component, *blueprint.supporting_components]:
            self._component_index[component].add(blueprint.blueprint_id)

    def _deindex(self, blueprint: STEMBlueprint) -> None:
        self._topic_to_id.pop(blueprint.topic.strip().lower(), None)
        self._category_index[blueprint.category].discard(blueprint.blueprint_id)
        self._difficulty_index[blueprint.difficulty_level].discard(blueprint.blueprint_id)
        for keyword in blueprint.keywords:
            self._keyword_index[keyword].discard(blueprint.blueprint_id)
        for component in [blueprint.primary_component, *blueprint.supporting_components]:
            self._component_index[component].discard(blueprint.blueprint_id)

    def remove_blueprint(self, topic_or_id: str) -> None:
        blueprint = self.get_blueprint(topic_or_id)
        if blueprint is None: return
        self._deindex(blueprint)
        self._blueprints.pop(blueprint.blueprint_id, None)

    def get_blueprint(self, topic_or_id: str) -> Optional[STEMBlueprint]:
        key = topic_or_id.strip()
        if key in self._blueprints: return self._blueprints[key]
        blueprint_id = self._topic_to_id.get(key.lower())
        return self._blueprints.get(blueprint_id) if blueprint_id else None

    def require_blueprint(self, learning_goal: str) -> Optional[STEMBlueprint]:
        if not learning_goal:
            return None
        learning_goal_lower = learning_goal.lower()
        
        # 1. Exact or substring match in topic
        for bp in self.all_blueprints():
            if bp.topic.lower() in learning_goal_lower or learning_goal_lower in bp.topic.lower():
                return bp
                
        # 2. Check if keywords match
        for bp in self.all_blueprints():
            for kw in bp.keywords:
                if kw.lower() in learning_goal_lower:
                    return bp
                    
        # 3. Match learning objective similarity
        for bp in self.all_blueprints():
            if bp.learning_objective.lower() in learning_goal_lower or learning_goal_lower in bp.learning_objective.lower():
                return bp
                
        return None

    def search_by_category(self, category: BlueprintCategory) -> List[STEMBlueprint]:
        ids = self._category_index.get(category, set())
        return sorted((self._blueprints[i] for i in ids), key=lambda bp: bp.topic)

    def all_blueprints(self) -> List[STEMBlueprint]:
        return sorted(self._blueprints.values(), key=lambda bp: bp.topic)

    def count(self) -> int:
        return len(self._blueprints)

    async def _initialize_embeddings(self) -> None:
        """Fetch and cache embeddings for all registered blueprints."""
        if hasattr(self, '_embeddings_initialized') and self._embeddings_initialized:
            return
            
        self._blueprint_embeddings: Dict[str, List[float]] = {}
        
        bps = self.all_blueprints()
        if not bps:
            self._embeddings_initialized = True
            return
            
        texts = []
        for bp in bps:
            text = f"Topic: {bp.topic}\nCategory: {bp.category.value}\nKeywords: {', '.join(bp.keywords)}\nLearning Objective: {bp.learning_objective}\nVisual Metaphor: {bp.visual_metaphor}"
            texts.append(text)
            
        from app.services.rag_service import generate_embeddings_batch
        embeddings = await generate_embeddings_batch(texts)
        
        for bp, emb in zip(bps, embeddings):
            self._blueprint_embeddings[bp.blueprint_id] = emb
            
        self._embeddings_initialized = True

    async def semantic_search(self, query: str, top_k: int = 1, threshold: float = 0.65) -> List[tuple[float, STEMBlueprint]]:
        """Return the best matching blueprints based on cosine similarity."""
        if not hasattr(self, '_embeddings_initialized') or not self._embeddings_initialized:
            await self._initialize_embeddings()
            
        if not hasattr(self, '_blueprint_embeddings') or not self._blueprint_embeddings:
            return []
            
        from app.services.rag_service import generate_embedding
        import numpy as np
        
        try:
            query_emb = await generate_embedding(query)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to generate query embedding: {e}")
            return []
            
        q_vec = np.array(query_emb)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
            
        scores = []
        for bp_id, emb in self._blueprint_embeddings.items():
            emb_vec = np.array(emb)
            e_norm = np.linalg.norm(emb_vec)
            if e_norm == 0:
                continue
            sim = np.dot(q_vec, emb_vec) / (q_norm * e_norm)
            if sim >= threshold:
                scores.append((float(sim), self._blueprints[bp_id]))
                
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[:top_k]

    async def get_blueprint_hybrid(self, query: str) -> Optional[tuple[str, float, STEMBlueprint]]:
        """
        Hybrid retrieval:
        1. Exact Topic Match
        2. Alias / Keyword Match
        3. Semantic Search
        
        Returns: (match_type, similarity_score, blueprint)
        """
        # 1. Exact Topic Match
        bp = self.get_blueprint(query)
        if bp:
            return ("Exact Topic Match", 1.0, bp)
            
        # 2. Alias / Keyword Match
        query_lower = query.strip().lower()
        if query_lower in self._keyword_index:
            bp_ids = list(self._keyword_index[query_lower])
            if bp_ids:
                # Return the first match if multiple exist
                return ("Alias Match", 1.0, self._blueprints[bp_ids[0]])
                
        # 3. Semantic Search
        semantic_matches = await self.semantic_search(query, top_k=1, threshold=0.65)
        if semantic_matches:
            score, bp = semantic_matches[0]
            return ("Semantic Search", score, bp)
            
        return None


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug

def _ve(name: Any, element_type: Any, description: str, required: bool = True) -> Dict[str, Any]:
    if isinstance(name, VisualElementType) and isinstance(element_type, str):
        name, element_type = element_type, name
    return {"name": name, "type": element_type, "description": description, "required": required}

def _anim(name: str, description: str, duration: float = 2.0, easing: str = "smooth") -> Dict[str, Any]:
    return {"name": name, "description": description, "duration": duration, "easing": easing}

def _rule(description: str, severity: ValidationSeverity, check_type: str) -> Dict[str, Any]:
    return {"description": description, "severity": severity, "check_type": check_type}

def _build_blueprint(spec: Dict[str, Any]) -> STEMBlueprint:
    from app.sandbox.shared_animation_registry import COMPONENT_ALIASES
    
    topic_slug = _slugify(spec["topic"])
    blueprint_id = f"bp_{topic_slug}"
    visual_elements = [
        VisualElement(
            element_id=f"VE-{topic_slug}-{idx:02d}",
            name=ve_spec["name"],
            element_type=ve_spec["type"],
            description=ve_spec["description"],
            is_required=ve_spec["required"],
        )
        for idx, ve_spec in enumerate(spec.get("visual_elements", []), start=1)
    ]
    animation_templates = [
        AnimationTemplate(
            template_id=f"ANIM-{topic_slug}-{idx:02d}",
            name=anim_spec["name"],
            description=anim_spec["description"],
            sequence_order=idx,
            duration_seconds=anim_spec["duration"],
            easing=anim_spec["easing"],
        )
        for idx, anim_spec in enumerate(spec.get("animation_templates", []), start=1)
    ]
    camera = CameraBehavior(
        initial_framing=spec["camera"]["initial_framing"],
        movements=list(spec["camera"]["movements"]),
        focus_points=list(spec["camera"]["focus_points"]),
        zoom_strategy=spec["camera"].get("zoom_strategy", "static"),
    )
    validation_rules = [
        ValidationRule(
            rule_id=f"VR-{topic_slug}-{idx:02d}",
            description=rule_spec["description"],
            severity=rule_spec["severity"],
            check_type=rule_spec["check_type"],
        )
        for idx, rule_spec in enumerate(spec.get("validation_rules", []), start=1)
    ]
    
    primary_comp = str(spec.get("primary_component", "SummaryDiagram"))
    primary_comp = str(COMPONENT_ALIASES.get(primary_comp, primary_comp))
    
    supporting_comps = []
    for comp in spec.get("supporting_components", []):
        supporting_comps.append(str(COMPONENT_ALIASES.get(comp, comp)))
        
    return STEMBlueprint(
        blueprint_id=blueprint_id,
        topic=spec["topic"],
        category=spec["category"],
        learning_objective=spec["learning_objective"],
        visual_metaphor=spec["visual_metaphor"],
        primary_component=primary_comp,
        supporting_components=supporting_comps,
        required_visual_elements=visual_elements,
        animation_templates=animation_templates,
        camera_behavior=camera,
        difficulty_level=spec["difficulty"],
        keywords=list(spec.get("keywords", [])),
        validation_rules=validation_rules,
    )

_BLUEPRINT_SPECS: List[Dict[str, Any]] = [
    {
        "topic": "Pythagorean Theorem",
        "category": BlueprintCategory.MATHEMATICS_THEOREM,
        "difficulty": DifficultyLevel.BEGINNER,
        "learning_objective": "Demonstrate that the sum of the squares of a right triangle's legs equals the square of the hypotenuse using an area-based geometric proof.",
        "visual_metaphor": "Three squares grown outward from each side of a right triangle, where the areas of the two smaller squares visually recombine to fill the largest square.",
        "primary_component": "RightTriangleDiagram",
        "supporting_components": ["SquareAreaProofDiagram", "CoordinateGeometryDiagram"],
        "visual_elements": [
            _ve("right_triangle", VisualElementType.SHAPE, "Right triangle with legs labeled a and b and hypotenuse labeled c"),
            _ve("right_angle_marker", VisualElementType.ANNOTATION, "Small square marker at the vertex indicating the 90-degree angle"),
            _ve("square_on_a", VisualElementType.SHAPE, "Square constructed outward on side a representing area a^2"),
            _ve("square_on_b", VisualElementType.SHAPE, "Square constructed outward on side b representing area b^2"),
            _ve("square_on_c", VisualElementType.SHAPE, "Square constructed outward on hypotenuse c representing area c^2"),
            _ve("area_equation", VisualElementType.EQUATION, "Equation a^2 + b^2 = c^2 displayed and built up term by term"),
        ],
        "animation_templates": [
            _anim("draw_triangle", "Draw the right triangle and label each side", 2.0),
            _anim("construct_squares", "Grow each square outward from its corresponding side", 3.0),
            _anim("decompose_recombine", "Decompose the two smaller squares and animate their pieces sliding into the larger square", 4.0),
            _anim("reveal_equation", "Reveal the algebraic identity a^2 + b^2 = c^2 beneath the diagram", 1.5),
        ],
        "camera": {
            "initial_framing": "Centered medium shot on the right triangle",
            "movements": ["Slow zoom out as squares are constructed", "Pan to follow the decomposition pieces"],
            "focus_points": ["right angle vertex", "hypotenuse square"],
            "zoom_strategy": "progressive_reveal",
        },
        "validation_rules": [
            _rule("Diagram must include exactly one right-angle marker", ValidationSeverity.ERROR, "element_presence"),
            _rule("All three squares must show their computed area labels", ValidationSeverity.ERROR, "label_consistency"),
            _rule("The sum a^2 + b^2 must equal c^2 within floating-point tolerance", ValidationSeverity.CRITICAL, "mathematical_correctness"),
        ],
        "keywords": ["pythagorean theorem", "right triangle", "hypotenuse", "geometry", "a^2+b^2=c^2", "area proof"],
    },
    {
        "topic": "Surface Tension",
        "category": BlueprintCategory.PHYSICS_SURFACE_TENSION,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "learning_objective": "Explain how cohesive forces between liquid molecules create a surface tension barrier.",
        "visual_metaphor": "People pulling a rope inward",
        "primary_component": "SurfaceTensionDiagram",
        "supporting_components": ["DropletDiagram"],
        "visual_elements": [
            _ve("surface_molecules", VisualElementType.NODE, "Molecules at the surface of the liquid"),
            _ve("force_arrows", VisualElementType.VECTOR, "Inward pulling cohesive forces"),
            _ve("meniscus", VisualElementType.SHAPE, "Curved surface of the liquid"),
        ],
        "animation_templates": [
            _anim("draw_molecules", "Draw the bulk and surface molecules", 2.0),
            _anim("show_forces", "Animate the force vectors pulling inward", 2.0),
        ],
        "camera": {
            "initial_framing": "Close up on surface",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Forces must point inward", ValidationSeverity.ERROR, "physical_accuracy"),
        ],
        "keywords": ["surface tension", "cohesion", "forces", "physics"],
    },
    {
        "blueprint_id": "eng_elec_ohms_law",
        "topic": "Ohm's Law",
        "category": BlueprintCategory.ENGINEERING_ELECTRICAL,
        "learning_objective": "Understand the relationship between voltage, current, and resistance.",
        "visual_metaphor": "Water flowing through a pipe: voltage is pressure, current is flow, resistance is a pipe constriction.",
        "primary_component": "NetworkDiagram",
        "supporting_components": ["GraphPlot"],
        "difficulty": DifficultyLevel.BEGINNER,
        "visual_elements": [
            _ve(VisualElementType.NODE, "Battery/Voltage Source", "Source of electrical pressure"),
            _ve(VisualElementType.EDGE, "Wire/Current", "Path of electron flow"),
            _ve(VisualElementType.NODE, "Resistor", "Constriction in the path"),
        ],
        "animation_templates": [
            _anim("fade_in_summary_diagram", "Draw the circuit components", 2.0),
            _anim("animate_flow", "Animate electrons flowing through the circuit", 3.0),
        ],
        "camera": {
            "initial_framing": "Wide shot of circuit",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Current must decrease if resistance increases", ValidationSeverity.ERROR, "physical_accuracy"),
        ],
        "keywords": ["ohm's law", "electricity", "voltage", "current", "resistance", "engineering", "electrical"],
    },
    {
        "blueprint_id": "eng_civil_truss",
        "topic": "Truss Bridge Forces",
        "category": BlueprintCategory.ENGINEERING_CIVIL,
        "learning_objective": "Understand how a truss distributes load into compression and tension members.",
        "visual_metaphor": "A skeleton of triangles: arrows pointing towards joints (compression) and away from joints (tension).",
        "primary_component": "NetworkDiagram",
        "supporting_components": ["ForceVectorDiagram"],
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "visual_elements": [
            _ve(VisualElementType.NODE, "Joints", "Connection points"),
            _ve(VisualElementType.EDGE, "Truss Members", "Beams connecting joints"),
            _ve(VisualElementType.VECTOR, "Load Force", "Downward force on the bridge"),
            _ve(VisualElementType.VECTOR, "Reaction Forces", "Upward forces from supports"),
        ],
        "animation_templates": [
            _anim("show_diagram", "Draw the triangular truss structure", 2.0),
            _anim("highlight_element", "Highlight members in compression vs tension", 3.0),
        ],
        "camera": {
            "initial_framing": "Full view of bridge",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Trusses must form triangles", ValidationSeverity.ERROR, "structural_integrity"),
        ],
        "keywords": ["truss", "bridge", "civil engineering", "forces", "tension", "compression", "engineering"],
    },
    {
        "blueprint_id": "cs_algo_binary_search",
        "topic": "Binary Search Algorithm",
        "category": BlueprintCategory.COMPUTER_SCIENCE_ALGORITHMS,
        "learning_objective": "Understand how dividing a sorted array in half logarithmically reduces search time.",
        "visual_metaphor": "Looking up a word in a dictionary by continually opening to the middle page.",
        "primary_component": "BinarySearchDiagram",
        "supporting_components": ["ArrayDiagram"],
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "visual_elements": [
            _ve(VisualElementType.ARRAY_CELL, "Sorted Array", "A sequence of ordered numbers"),
            _ve(VisualElementType.LABEL, "Target", "The number we are looking for"),
            _ve(VisualElementType.LABEL, "Pointers", "Left, Right, and Mid indices"),
        ],
        "animation_templates": [
            _anim("fade_in_array", "Display the initial sorted array", 1.0),
            _anim("binary_search_step", "Highlight mid and discard half the array", 2.0),
        ],
        "camera": {
            "initial_framing": "Full view of array",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Array must be sorted before searching", ValidationSeverity.ERROR, "logical_accuracy"),
        ],
        "keywords": ["binary search", "algorithm", "divide and conquer", "log n", "computer science"],
    },
    {
        "blueprint_id": "cs_theory_turing_machine",
        "topic": "Turing Machine",
        "category": BlueprintCategory.COMPUTER_SCIENCE_THEORY,
        "learning_objective": "Understand the abstract machine that forms the foundation of all computation.",
        "visual_metaphor": "A robotic read/write head moving back and forth along an infinite paper tape.",
        "primary_component": "ArrayDiagram",
        "supporting_components": ["NetworkDiagram"],
        "difficulty": DifficultyLevel.ADVANCED,
        "visual_elements": [
            _ve(VisualElementType.ARRAY_CELL, "Infinite Tape", "Memory cells holding symbols"),
            _ve(VisualElementType.LABEL, "Read/Write Head", "The active position on the tape"),
            _ve(VisualElementType.NODE, "State Machine", "The current internal state"),
        ],
        "animation_templates": [
            _anim("fade_in_array", "Show the tape and head", 1.0),
            _anim("highlight_element", "Head reads, writes, and moves", 2.0),
        ],
        "camera": {
            "initial_framing": "View of tape and state",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Head must only move one cell at a time", ValidationSeverity.WARNING, "logical_accuracy"),
        ],
        "keywords": ["turing machine", "computation", "tape", "automata", "computer science", "theory"],
    },
    {
        "blueprint_id": "cs_ds_arrays",
        "topic": "Arrays in Memory",
        "category": BlueprintCategory.COMPUTER_SCIENCE_DATA_STRUCTURES,
        "learning_objective": "Understand contiguous memory allocation and O(1) index access.",
        "visual_metaphor": "A row of numbered post office boxes next to each other.",
        "primary_component": "ArrayDiagram",
        "supporting_components": ["SummaryDiagram"],
        "difficulty": DifficultyLevel.BEGINNER,
        "visual_elements": [
            _ve(VisualElementType.ARRAY_CELL, "Memory Blocks", "Contiguous cells"),
            _ve(VisualElementType.LABEL, "Indices", "0-based indexing"),
        ],
        "animation_templates": [
            _anim("fade_in_array", "Draw the contiguous blocks", 1.0),
            _anim("highlight_element", "Access a specific index directly", 2.0),
        ],
        "camera": {
            "initial_framing": "Full view of array",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Indices must start at 0", ValidationSeverity.ERROR, "syntax_accuracy"),
        ],
        "keywords": ["array", "data structure", "memory", "indexing", "computer science"],
    },
    {
        "blueprint_id": "cs_networks_routing",
        "topic": "Packet Routing",
        "category": BlueprintCategory.COMPUTER_SCIENCE_NETWORKS,
        "learning_objective": "Understand how data packets navigate through a network of routers.",
        "visual_metaphor": "Mail being sorted and passed between post offices to reach a destination.",
        "primary_component": "NetworkDiagram",
        "supporting_components": ["FlowChart"],
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "visual_elements": [
            _ve(VisualElementType.NODE, "Routers", "Network nodes"),
            _ve(VisualElementType.EDGE, "Links", "Connections between routers"),
            _ve(VisualElementType.SHAPE, "Packet", "Data moving along edges"),
        ],
        "animation_templates": [
            _anim("show_diagram", "Draw the network topology", 1.0),
            _anim("animate_flow", "Animate a packet traversing the shortest path", 2.0),
        ],
        "camera": {
            "initial_framing": "Wide view of network",
            "movements": [],
            "focus_points": [],
            "zoom_strategy": "static",
        },
        "validation_rules": [
            _rule("Packets must travel along defined edges", ValidationSeverity.ERROR, "logical_accuracy"),
        ],
        "keywords": ["network", "routing", "packets", "internet", "topology", "computer science"],
    }
]

# Global instance for easy importing
registry = STEMBlueprintRegistry()
for spec in _BLUEPRINT_SPECS:
    registry.register_blueprint(_build_blueprint(spec))

STEM_BLUEPRINT_REGISTRY = registry

def validate_blueprints_against_registry():
    from app.sandbox.shared_animation_registry import COMPONENT_REGISTRY
    for bp in registry.all_blueprints():
        if bp.primary_component not in COMPONENT_REGISTRY:
            raise ValueError(f"Startup Validation Error: Blueprint '{bp.topic}' uses unknown primary_component: '{bp.primary_component}'")
        for comp in bp.supporting_components:
            if comp not in COMPONENT_REGISTRY:
                raise ValueError(f"Startup Validation Error: Blueprint '{bp.topic}' uses unknown supporting_component: '{comp}'")

