import json


_TERM_KEYS = ("sign", "numCoeff", "numRad", "denCoeff", "denRad")


def _to_int(value, default: int) -> int:
    """Convert arbitrary input into a deterministic integer."""

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_sign(value) -> int:
    """Normalize signs to backend-stable +1 / -1 values."""

    return -1 if _to_int(value, 1) < 0 else 1


def _normalize_positive(value, default: int = 1) -> int:
    """Normalize positive integer fields used in coefficients/radicals."""

    normalized = abs(_to_int(value, default))
    return normalized if normalized > 0 else default


def _normalize_non_negative(value, default: int = 1) -> int:
    """Normalize non-negative integer fields (numerator coefficient can be 0)."""

    normalized = abs(_to_int(value, default))
    return normalized if normalized >= 0 else default


def _canonicalize_term(term: dict | None) -> dict:
    """Return a stable schema-only representation for a term payload."""

    payload = dict(term or {})

    canonical = {key: payload.get(key) for key in _TERM_KEYS}

    return {
        "sign": _normalize_sign(canonical.get("sign")),
        "numCoeff": _normalize_non_negative(canonical.get("numCoeff"), 1),
        "numRad": _normalize_positive(canonical.get("numRad"), 1),
        "denCoeff": _normalize_positive(canonical.get("denCoeff"), 1),
        "denRad": _normalize_positive(canonical.get("denRad"), 1),
    }


def _equation_terms_and_constant(eq_data: dict) -> tuple[list, dict]:
    """Get terms list (length 2) and constant from equation payload (terms[] or term1/term2)."""
    terms = eq_data.get("terms") if isinstance(eq_data.get("terms"), list) else None
    if terms is None:
        terms = [eq_data.get("term1"), eq_data.get("term2")]
    return terms[:2], eq_data.get("constant")


def to_canonical_equation_dict(eq_data: dict) -> dict:
    """
    Return the canonical equation shape for storage and hashing: only "terms" and "constant".
    Accepts both legacy (term1/term2) and current (terms[]) payloads.
    """
    terms, constant = _equation_terms_and_constant(eq_data)
    return {
        "terms": [_canonicalize_term(t) for t in terms],
        "constant": _canonicalize_term(constant),
    }


def to_frontend_equation_dict(canonical_eq: dict) -> dict:
    """
    Expand canonical equation { terms, constant } for API responses so the frontend
    receives term1/term2 (used when loading saved systems for edit).
    """
    terms = list(canonical_eq.get("terms") or [])[:2]
    constant = canonical_eq.get("constant")
    out = {"terms": terms, "constant": constant}
    if len(terms) >= 2:
        out["term1"] = terms[0]
        out["term2"] = terms[1]
    return out


def canonicalize_equation(eq_data: dict) -> str:
    """
    Convert equation JSON into a canonical string for duplicate detection.

    Important behaviors:
    - ignores presentation-only metadata (e.g. frame positions)
    - supports both legacy (term1/term2) and current (terms[]) payloads
    - normalizes numeric fields to deterministic integers
    """
    canonical = to_canonical_equation_dict(eq_data)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"))
