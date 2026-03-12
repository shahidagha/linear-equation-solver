import json


def _canonicalize_term(term: dict | None) -> dict:
    """Return a stable dictionary representation for a term payload."""

    return dict(term or {})


def canonicalize_equation(eq_data: dict) -> str:
    """
    Convert raw equation JSON data into a canonical string while preserving
    user-entered structure (no algebraic normalization).

    Supports both payload styles:
    - current:  {"terms": [...], "constant": {...}}
    - legacy:   {"term1": {...}, "term2": {...}, "constant": {...}}
    """

    canonical: dict = {}

    if "positions" in eq_data:
        canonical["positions"] = dict(eq_data.get("positions") or {})

    if "terms" in eq_data and isinstance(eq_data.get("terms"), list):
        canonical["terms"] = [_canonicalize_term(term) for term in eq_data.get("terms", [])]
    else:
        canonical["term1"] = _canonicalize_term(eq_data.get("term1"))
        canonical["term2"] = _canonicalize_term(eq_data.get("term2"))

    canonical["constant"] = _canonicalize_term(eq_data.get("constant"))

    return json.dumps(canonical, sort_keys=True, separators=(",", ":"))
