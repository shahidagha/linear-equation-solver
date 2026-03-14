"""
Grade-scope check: at a step where we would add or subtract two expressions,
if they involve surds with different radicands (or mixed radicands), that step is "above grade".
Used by each solver at the concrete add/subtract step.
"""
import sympy as sp
from typing import Any, Optional


def radicand(expr: Any) -> Optional[Any]:
    """
    Inspect expr for square roots. Return:
    - None if no sqrt
    - The common base if a single kind of sqrt (e.g. sqrt(2) -> 2)
    - "MIXED" if more than one kind of sqrt in the same expression
    """
    expr = sp.simplify(expr)
    roots = [p.base for p in expr.atoms(sp.Pow) if p.exp == sp.Rational(1, 2)]
    if not roots:
        return None
    base0 = sp.simplify(roots[0])
    for r in roots[1:]:
        if sp.simplify(r - base0) != 0:
            return "MIXED"
    return base0


def would_add_subtract_unlike_surds(expr1: Any, expr2: Any) -> bool:
    """
    True if adding or subtracting expr1 and expr2 would involve surds with different
    radicands, mixed radicands, or one rational and one surd (e.g. 5 - √3). At such a step we declare "above grade".
    """
    r1 = radicand(expr1)
    r2 = radicand(expr2)
    if r1 == "MIXED" or r2 == "MIXED":
        return True
    # One has a surd, the other has none (rational ± surd, e.g. 5 - √3) → above grade
    if (r1 is None) != (r2 is None):
        return True
    if r1 is not None and r2 is not None and sp.simplify(r1 - r2) != 0:
        return True
    return False
