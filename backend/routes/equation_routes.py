from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.equation_service import save_equation_system

router = APIRouter()


@router.post("/save-system")
def save_system(payload: dict, db: Session = Depends(get_db)):
    """
    API endpoint to save equation systems.
    """

    result = save_equation_system(db, payload)

    return result