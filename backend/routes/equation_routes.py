from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.utils.request_validator import validate_solve_payload
from backend.schemas.equation_schema import (
    SolveRequestSchema,
    SolveResponseSchema,
    SaveResponseSchema,
)
from backend.services.equation_service import (
    save_equation_system,
    update_equation_system,
    get_saved_systems,
    delete_system_by_id,
    get_cached_solution_response,
)
from backend.services.solver_service import solve_system

router = APIRouter()


def _normalize_payload(payload: SolveRequestSchema | dict) -> dict:
    """Normalize request payload to the service contract."""

    if isinstance(payload, SolveRequestSchema):
        data = payload.model_dump()
    else:
        data = payload

    variables = data.get("variables")
    if isinstance(variables, dict):
        data["variables"] = [variables.get("var1"), variables.get("var2")]

    for key in ("equation1", "equation2"):
        equation = data.get(key, {})
        if "terms" not in equation and "term1" in equation and "term2" in equation:
            equation["terms"] = [equation["term1"], equation["term2"]]

    return data


@router.post(
    "/save-system",
    response_model=None,
    responses={200: {"description": "Save result", "model": SaveResponseSchema}, 422: {"description": "Validation error"}},
)
def save_system(payload: SolveRequestSchema, db: Session = Depends(get_db)):
    """Save equation system. Returns status (saved | duplicate | invalid | variable_conflict)."""
    normalized_payload = _normalize_payload(payload)
    validation_error = validate_solve_payload(normalized_payload)
    if validation_error is not None:
        return JSONResponse(status_code=422, content=validation_error)
    result = save_equation_system(db, normalized_payload)
    return result


@router.post(
    "/solve-system",
    response_model=None,
    responses={200: {"description": "Solution and LaTeX per method", "model": SolveResponseSchema}, 422: {"description": "Validation error"}},
)
def solve_equation_system(payload: SolveRequestSchema, db: Session = Depends(get_db)):
    payload_dict = _normalize_payload(payload)
    validation_error = validate_solve_payload(payload_dict)
    if validation_error is not None:
        return JSONResponse(status_code=422, content=validation_error)

    incoming_system_id = payload_dict.get("system_id")
    if incoming_system_id is not None:
        save_result = update_equation_system(db, incoming_system_id, payload_dict)
    else:
        save_result = save_equation_system(db, payload_dict)

    if save_result['status'] in ('saved', 'duplicate', 'updated'):
        system_id = save_result['id']
    else:
        return save_result

    cached_result = get_cached_solution_response(db, system_id)

    if cached_result is not None:
        cached_result["system_id"] = system_id
        return cached_result

    result = solve_system(db, system_id, payload_dict)
    result["system_id"] = system_id

    return result


@router.get('/systems')
def get_systems(db: Session = Depends(get_db)):

    systems = get_saved_systems(db)

    return systems


@router.delete('/system/{system_id}')
def delete_system(system_id: int, db: Session = Depends(get_db)):

    return delete_system_by_id(db, system_id)
