from sqlalchemy.orm import Session
from models.equation_models import EquationSystem
from utils.hash_utils import generate_equation_hash, generate_system_hash


def save_equation_system(db: Session, payload: dict):
    """
    Save an equation system with duplicate detection.
    """

    var1 = payload["variables"]["var1"]
    var2 = payload["variables"]["var2"]

    eq1 = payload["equation1"]
    eq2 = payload["equation2"]

    # Generate hashes
    equation_hash = generate_equation_hash(eq1, eq2)
    system_hash = generate_system_hash(var1, var2, eq1, eq2)

    # ---------------------------------------------------
    # Check for exact duplicate
    # ---------------------------------------------------

    existing_system = (
        db.query(EquationSystem)
        .filter(EquationSystem.system_hash == system_hash)
        .first()
    )

    if existing_system:
        return {
            "status": "duplicate",
            "message": "This equation system already exists."
        }

    # ---------------------------------------------------
    # Check same equations but different variables
    # ---------------------------------------------------

    existing_equation = (
        db.query(EquationSystem)
        .filter(EquationSystem.equation_hash == equation_hash)
        .first()
    )

    if existing_equation:

        old_vars = existing_equation.variables

        return {
            "status": "variable_conflict",
            "message": "Same equations exist but variables are different.",
            "existing_variables": old_vars
        }

    # ---------------------------------------------------
    # Save new system
    # ---------------------------------------------------

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

    return {
        "status": "saved",
        "id": new_system.id
    }