from sqlalchemy.orm import Session
from backend.models.equation_models import EquationSystem
from backend.models.solution_methods import SolutionMethod
from backend.utils.hash_utils import generate_equation_hash, generate_system_hash
from backend.utils.canonical_encoder import canonicalize_equation


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
        substitution = per_system.get("substitution")
        cramer = per_system.get("cramer")
        graphical = per_system.get("graphical")

        stored_response = None
        if elimination and graphical:
            stored_response = {
                "solution": elimination.solution_json,
                "methods": {
                    "elimination_latex": {
                        "latex_detailed": elimination.latex_detailed,
                        "latex_medium": elimination.latex_medium,
                        "latex_short": elimination.latex_short,
                    },
                    "substitution_latex": None if substitution is None else {
                        "latex_detailed": substitution.latex_detailed,
                        "latex_medium": substitution.latex_medium,
                        "latex_short": substitution.latex_short,
                    },
                    "cramer_latex": None if cramer is None else {
                        "latex_detailed": cramer.latex_detailed,
                        "latex_medium": cramer.latex_medium,
                        "latex_short": cramer.latex_short,
                    },
                    "graphical_latex": {
                        "latex_detailed": graphical.latex_detailed,
                        "latex_medium": graphical.latex_medium,
                        "latex_short": graphical.latex_short,
                    },
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


def delete_system_by_id(db: Session, system_id: int):
    """Delete solution methods for a system and then delete the system itself."""

    db.query(SolutionMethod).filter(SolutionMethod.system_id == system_id).delete(synchronize_session=False)
    db.query(EquationSystem).filter(EquationSystem.id == system_id).delete(synchronize_session=False)
    db.commit()

    return {"status": "deleted"}
