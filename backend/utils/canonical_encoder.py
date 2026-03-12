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


def canonicalize_equation(eq_data: dict) -> str:
    """
    Convert equation JSON into a canonical string for duplicate detection.

    Important behaviors:
    - ignores presentation-only metadata (e.g. frame positions)
    - supports both legacy (term1/term2) and current (terms[]) payloads
    - normalizes numeric fields to deterministic integers
    """

    terms = eq_data.get("terms") if isinstance(eq_data.get("terms"), list) else None

    if terms is None:
        terms = [eq_data.get("term1"), eq_data.get("term2")]

    canonical = {
        "terms": [_canonicalize_term(term) for term in terms[:2]],
        "constant": _canonicalize_term(eq_data.get("constant")),
    }

    return json.dumps(canonical, sort_keys=True, separators=(",", ":"))
