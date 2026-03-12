from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.equation_service import (
    save_equation_system,
    get_saved_systems,
    delete_system_by_id,
    get_cached_solution_response,
)
from backend.services.solver_service import solve_system

router = APIRouter()


@router.post('/save-system')
def save_system(payload: dict, db: Session = Depends(get_db)):
    """
    API endpoint to save equation systems.
    """

    result = save_equation_system(db, payload)

    return result


@router.post('/solve-system')
def solve_equation_system(payload: dict, db: Session = Depends(get_db)):

    save_result = save_equation_system(db, payload)

    if save_result['status'] in ('saved', 'duplicate'):
        system_id = save_result['id']
    else:
        return save_result

    cached_result = get_cached_solution_response(db, system_id)

    if cached_result is not None:
        return cached_result

    result = solve_system(db, system_id, payload)

    return result


@router.get('/systems')
def get_systems(db: Session = Depends(get_db)):

    systems = get_saved_systems(db)

    return systems


@router.delete('/system/{system_id}')
def delete_system(system_id: int, db: Session = Depends(get_db)):

    return delete_system_by_id(db, system_id)
