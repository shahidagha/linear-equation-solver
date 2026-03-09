import hashlib
from utils.canonical_encoder import canonicalize_equation


def generate_equation_hash(eq1_data: dict, eq2_data: dict) -> str:
    """
    Generate a hash based only on the equation structures.
    Variables are NOT included.
    """

    eq1 = canonicalize_equation(eq1_data)
    eq2 = canonicalize_equation(eq2_data)

    # Order equations consistently
    ordered = sorted([eq1, eq2])

    combined = "".join(ordered)

    return hashlib.sha256(combined.encode()).hexdigest()


def generate_system_hash(var1: str, var2: str, eq1_data: dict, eq2_data: dict) -> str:
    """
    Generate a hash including variables.
    Used for detecting exact duplicates.
    """

    eq1 = canonicalize_equation(eq1_data)
    eq2 = canonicalize_equation(eq2_data)

    ordered_eq = sorted([eq1, eq2])

    ordered_vars = sorted([var1, var2])

    combined = "".join(ordered_vars) + "".join(ordered_eq)

    return hashlib.sha256(combined.encode()).hexdigest()