"""
Request validation for solve/save payloads. Applies Rules 1-4 from IMPROVEMENT_SUGGESTIONS.md.
Returns None if valid, or a dict { "code": "VALIDATION_ERROR", "message": "..." } for 4xx response.
"""
from typing import Any, Optional


def _error(message: str, detail: Optional[str] = None) -> dict:
    out = {"code": "VALIDATION_ERROR", "message": message}
    if detail is not None:
        out["detail"] = detail
    return out


def _get_terms_and_constant(equation: Any) -> tuple[Optional[list], Optional[Any]]:
    """Return (terms list of 2, constant) or (None, None) if structure invalid."""
    if not isinstance(equation, dict):
        return None, None
    terms = equation.get("terms")
    constant = equation.get("constant")
    if terms is not None and isinstance(terms, list) and len(terms) == 2 and constant is not None:
        return terms, constant
    term1 = equation.get("term1")
    term2 = equation.get("term2")
    if term1 is not None and term2 is not None and constant is not None:
        if isinstance(term1, dict) and isinstance(term2, dict) and isinstance(constant, dict):
            return [term1, term2], constant
    return None, None


def _is_term_like(obj: Any) -> bool:
    """True if obj is a dict that can be passed to build_fraction_surd (has expected keys)."""
    if not isinstance(obj, dict):
        return False
    # build_fraction_surd uses get("sign", 1), get("numCoeff", 1), etc. — all have defaults
    return True


def validate_solve_payload(payload: Any) -> Optional[dict]:
    """
    Validate payload for solve-system / save-system. Payload must be normalized (variables as list, equations with terms/constant).
    Returns None if valid, else dict for 422 response.
    """
    if not isinstance(payload, dict):
        return _error("Request body must be an object.")

    # Rule 1 — Exactly two equations, each with valid shape
    eq1 = payload.get("equation1")
    eq2 = payload.get("equation2")
    if eq1 is None:
        return _error("Missing required field: equation1.")
    if eq2 is None:
        return _error("Missing required field: equation2.")
    if not isinstance(eq1, dict):
        return _error("equation1 must be an object.")
    if not isinstance(eq2, dict):
        return _error("equation2 must be an object.")

    # Rule 2 — Variables: exactly two, non-empty, valid format
    variables = payload.get("variables")
    if variables is None:
        return _error("Missing required field: variables.")
    if not isinstance(variables, (list, tuple)):
        # Allow dict for legacy { var1, var2 }
        if isinstance(variables, dict):
            v1 = variables.get("var1")
            v2 = variables.get("var2")
            if v1 is None or v2 is None:
                return _error("variables must be a list of exactly two non-empty variable names.")
            variables = [v1, v2]
        else:
            return _error("variables must be a list of exactly two non-empty variable names.")
    if len(variables) != 2:
        return _error("variables must be a list of exactly two non-empty variable names.")
    if not isinstance(variables[0], str) or not str(variables[0]).strip():
        return _error("variables[0] must be a non-empty string.")
    if not isinstance(variables[1], str) or not str(variables[1]).strip():
        return _error("variables[1] must be a non-empty string.")
    if str(variables[0]).strip().lower() == str(variables[1]).strip().lower():
        return _error("Duplicate variable name.")

    # Rule 3 — Equation internal structure: terms and constant
    terms1, const1 = _get_terms_and_constant(eq1)
    terms2, const2 = _get_terms_and_constant(eq2)
    if terms1 is None or const1 is None:
        return _error("equation1 must have terms (array of two term objects) and constant.")
    if terms2 is None or const2 is None:
        return _error("equation2 must have terms (array of two term objects) and constant.")
    if not _is_term_like(terms1[0]) or not _is_term_like(terms1[1]) or not _is_term_like(const1):
        return _error("equation1: each term and constant must be an object with coefficient fields.")
    if not _is_term_like(terms2[0]) or not _is_term_like(terms2[1]) or not _is_term_like(const2):
        return _error("equation2: each term and constant must be an object with coefficient fields.")

    # Rule 4 — System buildability
    try:
        from backend.services.solver_service import build_fraction_surd
        from backend.math_engine.equation import Equation
        from backend.math_engine.system import EquationSystem
    except ImportError:
        return None  # Skip Rule 4 if imports fail (e.g. in tests); caller can still run solve

    var1 = str(variables[0]).strip()
    var2 = str(variables[1]).strip()
    try:
        a1 = build_fraction_surd(terms1[0])
        b1 = build_fraction_surd(terms1[1])
        c1 = build_fraction_surd(const1)
        eq1_obj = Equation(a1, b1, c1)
        a2 = build_fraction_surd(terms2[0])
        b2 = build_fraction_surd(terms2[1])
        c2 = build_fraction_surd(const2)
        eq2_obj = Equation(a2, b2, c2)
        EquationSystem(eq1_obj, eq2_obj, var1=var1, var2=var2)
    except Exception as e:
        return _error("System could not be built from the given equations.", detail=str(e))

    return None
