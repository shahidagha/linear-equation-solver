from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.equation_service import save_equation_system
from services.solver_service import solve_system
from services.equation_service import get_saved_systems
from models.equation_models import EquationSystem
from utils.hash_utils import generate_system_hash
router = APIRouter()


@router.post("/save-system")
def save_system(payload: dict, db: Session = Depends(get_db)):
    """
    API endpoint to save equation systems.
    """

    result = save_equation_system(db, payload)

    return result

@router.post("/solve-system")
def solve_equation_system(payload: dict, db: Session = Depends(get_db)):

    save_result = save_equation_system(db, payload)

    if save_result["status"] == "saved":
        system_id = save_result["id"]

    elif save_result["status"] == "duplicate":
        # fetch existing system id
        existing = db.query(EquationSystem)\
            .filter(EquationSystem.system_hash == generate_system_hash(
                payload["variables"]["var1"],
                payload["variables"]["var2"],
                payload["equation1"],
                payload["equation2"]
            )).first()

        system_id = existing.id

    else:
        return save_result

    result = solve_system(db, system_id, payload)

    return result

@router.get("/systems")
def get_systems(db: Session = Depends(get_db)):

    systems = get_saved_systems(db)

    return systems