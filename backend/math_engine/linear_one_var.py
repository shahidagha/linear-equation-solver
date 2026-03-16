"""
Step-by-step solver for linear equations in one variable: a*x + b = c.

Supports a, b, c as integers, surds (SymPy sqrt/rationals), or mixed.
Returns a list of steps (each with description and equation/latex) so they can be displayed.
"""

from typing import Any, List, Optional, Union

import sympy as sp


def _ensure_sympy(expr: Any) -> sp.Expr:
    """Convert int, float, or existing Expr to SymPy expression."""
    if isinstance(expr, (sp.Expr, sp.Basic)):
        return sp.sympify(expr)
    return sp.sympify(expr)


def solve_linear_one_variable_steps(
    a: Union[int, float, sp.Expr, Any],
    b: Union[int, float, sp.Expr, Any],
    c: Union[int, float, sp.Expr, Any],
    variable: str = "x",
    simplify_steps: bool = True,
) -> List[dict]:
    """
    Solve a*x + b = c and return all calculation steps.

    a, b, c can be integers, surds (e.g. sp.sqrt(2)), or mixed.
    Each step is a dict with:
      - "description": short text (e.g. "Subtract b from both sides")
      - "lhs": SymPy expression for left-hand side
      - "rhs": SymPy expression for right-hand side
      - "latex": optional "lhs = rhs" as LaTeX string (if requested)

    Parameters
    ----------
    a, b, c : coefficient and constant terms (ax + b = c)
    variable : name of the variable (default "x")
    simplify_steps : if True, simplify and rationalize at each step (default True)

    Returns
    -------
    List of step dicts. Last step has lhs = Symbol(variable), rhs = solution.
    """
    a = _ensure_sympy(a)
    b = _ensure_sympy(b)
    c = _ensure_sympy(c)
    x = sp.Symbol(variable)

    steps: List[dict] = []

    # Step 0: Given equation  a*x + b = c
    lhs0 = a * x + b
    rhs0 = c
    steps.append({
        "description": "Given",
        "lhs": lhs0,
        "rhs": rhs0,
    })

    # Step 1: Subtract b from both sides  =>  a*x = c - b
    lhs1 = a * x
    rhs1 = c - b
    if simplify_steps:
        rhs1 = sp.simplify(rhs1)
        rhs1 = sp.radsimp(rhs1)  # rationalize / simplify surds
    steps.append({
        "description": "Subtract the constant from both sides",
        "lhs": lhs1,
        "rhs": rhs1,
    })

    # Step 2: Divide both sides by a  =>  x = (c - b) / a
    solution = (c - b) / a
    if simplify_steps:
        solution = sp.simplify(solution)
        solution = sp.radsimp(solution)
    steps.append({
        "description": "Divide both sides by the coefficient of the variable",
        "lhs": x,
        "rhs": solution,
    })

    return steps


def steps_to_latex(steps: List[dict], variable: str = "x") -> List[str]:
    """
    Convert a list of step dicts (from solve_linear_one_variable_steps) to LaTeX strings.

    Returns a list of strings, each of the form "lhs = rhs" in LaTeX.
    """
    lines = []
    for step in steps:
        lhs = step["lhs"]
        rhs = step["rhs"]
        lines.append(f"{sp.latex(lhs)} = {sp.latex(rhs)}")
    return lines


def solve_linear_one_variable(
    a: Union[int, float, sp.Expr, Any],
    b: Union[int, float, sp.Expr, Any],
    c: Union[int, float, sp.Expr, Any],
    variable: str = "x",
) -> sp.Expr:
    """
    Return the solution x of a*x + b = c as a SymPy expression.
    Convenience wrapper; use solve_linear_one_variable_steps for steps.
    """
    a = _ensure_sympy(a)
    b = _ensure_sympy(b)
    c = _ensure_sympy(c)
    x = sp.Symbol(variable)
    return sp.simplify(sp.radsimp((c - b) / a))


def solve_ax_eq_b_steps(
    a: Union[int, float, sp.Expr, Any],
    b: Union[int, float, sp.Expr, Any],
    variable: str = "x",
    simplify_steps: bool = True,
) -> List[dict]:
    """
    Solve a*x = b and return all calculation steps.

    One function handles all cases:
      - a and b can be 1, -1, any other integer, or a surd (e.g. sp.sqrt(2)).
    SymPy normalizes display (e.g. 1*x → x, -1*x → -x) and simplifies b/a.

    Parameters
    ----------
    a : coefficient of x (ax = b)
    b : right-hand side
    variable : name of the variable (default "x")
    simplify_steps : if True, simplify and rationalize the solution (default True)

    Returns
    -------
    List of step dicts with "description", "lhs", "rhs".
    Step 1: Given  a*x = b  (or  x = b  when a=1,  -x = b  when a=-1)
    Step 2: Divide by a  =>  x = b/a  (skipped only if a=1; when a=-1, x = -b).
    """
    a = _ensure_sympy(a)
    b = _ensure_sympy(b)
    x = sp.Symbol(variable)

    steps: List[dict] = []

    # Step 1: Given  a*x = b  (SymPy displays 1*x as x, -1*x as -x)
    lhs_given = a * x
    rhs_given = b
    steps.append({
        "description": "Given",
        "lhs": sp.simplify(lhs_given),
        "rhs": rhs_given,
    })

    # Step 2: Divide both sides by a  =>  x = b/a
    solution = b / a
    if simplify_steps:
        solution = sp.simplify(solution)
        solution = sp.radsimp(solution)
    steps.append({
        "description": "Divide both sides by the coefficient of the variable",
        "lhs": x,
        "rhs": solution,
    })

    return steps


def solve_ax_eq_b(
    a: Union[int, float, sp.Expr, Any],
    b: Union[int, float, sp.Expr, Any],
    variable: str = "x",
) -> sp.Expr:
    """Return the solution x of a*x = b as a SymPy expression."""
    a = _ensure_sympy(a)
    b = _ensure_sympy(b)
    return sp.simplify(sp.radsimp(b / a))
