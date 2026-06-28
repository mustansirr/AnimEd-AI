STEM_BLUEPRINTS = {
    "mathematics_theorem_law": {
        "components": ["RightTriangleDiagram"],
        "required_visual_elements": ["shape", "equation_label", "angle_markers"],
        "use_mathtex": True
    },
    "mathematics_area_proof": {
        "components": ["AreaProofDiagram"],
        "required_visual_elements": ["geometric_shape", "area_subdivisions", "area_formula"],
        "use_mathtex": True
    },
    "chemistry_molecule": {
        "components": ["MoleculeDiagram"],
        "required_visual_elements": ["atoms", "bonds"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "physics_particle": {
        "components": ["ParticleDiagram"],
        "required_visual_elements": ["particles", "interaction_vectors"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "physics_forces_multiple": {
        "components": ["ForceVectorDiagram"],
        "required_visual_elements": ["center_mass", "force_vectors", "vector_labels"],
        "use_mathtex": True
    },
    "physics_surface_tension": {
        "components": ["MoleculeDiagram", "ForceVectorDiagram", "LiquidSurfaceDiagram"],
        "required_visual_elements": ["water_surface", "bulk_molecules", "surface_molecules", "force_vectors"],
        "use_mathtex": False,
        "disable_axes": True
    },
    "computer_science_graph": {
        "components": ["GraphDiagram"],
        "required_visual_elements": ["nodes", "edges", "labels"],
        "use_mathtex": False
    },
    "computer_science_tree": {
        "components": ["TreeDiagram"],
        "required_visual_elements": ["root", "children", "hierarchy_edges"],
        "use_mathtex": False
    },
    "mathematics_coordinate_geometry": {
        "components": ["CoordinateGeometryDiagram"],
        "required_visual_elements": ["axes", "points", "line_or_shape"],
        "use_mathtex": True
    },
    "physics_electric_field": {
        "components": ["ElectricFieldDiagram"],
        "required_visual_elements": ["charges", "field_lines", "force_vectors"],
        "use_mathtex": True
    },
    "physics_wave": {
        "components": ["WaveDiagram"],
        "required_visual_elements": ["axes", "sine_wave", "amplitude_marker", "wavelength_marker"],
        "use_mathtex": True
    },
    "chemistry_atom": {
        "components": ["AtomDiagram"],
        "required_visual_elements": ["nucleus", "electron_orbits", "electrons"],
        "use_mathtex": False
    },
    "chemistry_reaction": {
        "components": ["ReactionDiagram"],
        "required_visual_elements": ["reactants", "products", "yield_arrow"],
        "use_mathtex": True
    }
}
