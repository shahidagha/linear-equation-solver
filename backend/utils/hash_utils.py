import hashlib
import json

from backend.utils.canonical_encoder import canonicalize_equation


def _hash_parts(parts: list[str]) -> str:
    """Create a stable SHA-256 hash from ordered string parts."""

    payload = json.dumps(parts, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def generate_equation_hash(eq1_data: dict, eq2_data: dict) -> str:
    """
    Generate a hash from canonical raw equations only (variables excluded).

    Equation order is ignored.
    """

    canonical_equations = sorted(
        [
            canonicalize_equation(eq1_data),
            canonicalize_equation(eq2_data),
        ]
    )
    return _hash_parts(canonical_equations)


def generate_system_hash(var1: str, var2: str, eq1_data: dict, eq2_data: dict) -> str:
    """
    Generate a hash from canonical raw equations and the variable tuple.

    Equation order is ignored, variable order is preserved.
    """

    canonical_equations = sorted(
        [
            canonicalize_equation(eq1_data),
            canonicalize_equation(eq2_data),
        ]
    )

    return _hash_parts(canonical_equations + [var1, var2])
