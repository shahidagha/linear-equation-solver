from sqlalchemy.orm import Session
from models.equation_models import EquationSystem
from models.solution_methods import SolutionMethod
from utils.hash_utils import generate_equation_hash, generate_system_hash
from utils.canonical_encoder import canonicalize_equation


def save_equation_system(db: Session, payload: dict):
    """Save an equation system with duplicate detection."""

    var1 = payload["variables"]["var1"]
    var2 = payload["variables"]["var2"]

    eq1 = payload["equation1"]
    eq2 = payload["equation2"]

    eq1_canonical = canonicalize_equation(eq1)
    eq2_canonical = canonicalize_equation(eq2)

    if eq1_canonical == eq2_canonical:
        return {
            "status": "invalid",
            "message": "Both equations are identical. A valid system requires two different equations."
        }

    equation_hash = generate_equation_hash(eq1, eq2)
    system_hash = generate_system_hash(var1, var2, eq1, eq2)

    existing_system = db.query(EquationSystem).filter(EquationSystem.system_hash == system_hash).first()

    if existing_system:
        return {
            "status": "duplicate",
            "message": "This equation system already exists.",
            "id": existing_system.id,
        }

    existing_equation = db.query(EquationSystem).filter(EquationSystem.equation_hash == equation_hash).first()

    if existing_equation:
        old_vars = existing_equation.variables
        return {
            "status": "variable_conflict",
            "message": "Same equations exist but variables are different.",
            "existing_variables": old_vars
        }

    new_system = EquationSystem(
        variables=payload["variables"],
        equation1=payload["equation1"],
        equation2=payload["equation2"],
        equation_hash=equation_hash,
        system_hash=system_hash
    )

    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    return {"status": "saved", "id": new_system.id}


def get_saved_systems(db: Session):
    """Return saved systems with solution availability and stored method payloads."""

    systems = db.query(EquationSystem).order_by(EquationSystem.id.desc()).all()
    methods = db.query(SolutionMethod).all()

    methods_by_system = {}
    for method in methods:
        methods_by_system.setdefault(method.system_id, {})[method.method_name] = method

    result = []
    for s in systems:
        per_system = methods_by_system.get(s.id, {})
        elimination = per_system.get("elimination")
        graphical = per_system.get("graphical")

        stored_response = None
        if elimination and graphical:
            stored_response = {
                "solution": elimination.solution,
                "methods": {
                    "elimination": elimination.steps,
                    "graphical_steps": graphical.steps,
                },
                "graph": graphical.graph_data,
            }

        result.append(
            {
                "id": s.id,
                "variables": s.variables,
                "equation1": s.equation1,
                "equation2": s.equation2,
                "has_solution": stored_response is not None,
                "stored_response": stored_response,
            }
        )

    return result
