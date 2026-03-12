from sqlalchemy.orm import Session
from backend.models.equation_models import EquationSystem
from backend.models.solution_methods import SolutionMethod
from backend.utils.hash_utils import generate_equation_hash, generate_system_hash
from backend.utils.canonical_encoder import canonicalize_equation


REQUIRED_SOLUTION_METHODS = {"elimination", "substitution", "cramer", "graphical"}


def _normalize_variable_name(value: str) -> str:
    """Normalize variable labels for stable duplicate detection."""

    return str(value or "").strip().lower()


def _system_signature(variables: list[str], eq1: dict, eq2: dict) -> tuple:
    """Build a canonical signature that ignores equation order."""

    canonical_equations = sorted([canonicalize_equation(eq1), canonicalize_equation(eq2)])
    canonical_variables = tuple(_normalize_variable_name(var) for var in variables[:2])
    return (canonical_variables, tuple(canonical_equations))


def save_equation_system(db: Session, payload: dict):
    """Save an equation system with duplicate detection."""

    var1 = _normalize_variable_name(payload["variables"][0])
    var2 = _normalize_variable_name(payload["variables"][1])
    variables = [var1, var2]

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

    # Fallback duplicate check for legacy rows created before hash/canonical updates.
    incoming_signature = _system_signature(variables, eq1, eq2)
    all_systems = db.query(EquationSystem).all()
    for saved_system in all_systems:
        saved_signature = _system_signature(
            list(saved_system.variables or []),
            saved_system.equation1,
            saved_system.equation2,
        )
        if saved_signature != incoming_signature:
            continue

        # Backfill missing hashes on legacy rows so future lookups stay fast.
        if not saved_system.equation_hash:
            saved_system.equation_hash = equation_hash
        if not saved_system.system_hash:
            saved_system.system_hash = system_hash
        db.commit()

        return {
            "status": "duplicate",
            "message": "This equation system already exists.",
            "id": saved_system.id,
        }

    existing_equation = db.query(EquationSystem).filter(EquationSystem.equation_hash == equation_hash).first()

    if existing_equation and [_normalize_variable_name(var) for var in (existing_equation.variables or [])[:2]] != variables:
        return {
            "status": "variable_conflict",
            "message": "Same equations exist but variables are different.",
            "existing_variables": existing_equation.variables
        }

    new_system = EquationSystem(
        variables=variables,
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


def get_cached_solution_response(db: Session, system_id: int):
    """Return a solve-system response from cached method records if all methods exist."""

    method_rows = db.query(SolutionMethod).filter(SolutionMethod.system_id == system_id).all()
    method_map = {row.method_name: row for row in method_rows}

    if not REQUIRED_SOLUTION_METHODS.issubset(method_map.keys()):
        return None

    elimination = method_map["elimination"]
    substitution = method_map["substitution"]
    cramer = method_map["cramer"]
    graphical = method_map["graphical"]

    return {
        "solution": elimination.solution_json,
        "methods": {
            "elimination_latex": {
                "latex_detailed": elimination.latex_detailed,
                "latex_medium": elimination.latex_medium,
                "latex_short": elimination.latex_short,
            },
            "substitution_latex": {
                "latex_detailed": substitution.latex_detailed,
                "latex_medium": substitution.latex_medium,
                "latex_short": substitution.latex_short,
            },
            "cramer_latex": {
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
