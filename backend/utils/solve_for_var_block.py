"""
Unified "solve for variable" blocks.

1) solve_linear_for_var: for equations A*x + B*y = C, solve for one variable.
   Logical path: equation → isolate → flip_signs (if B<0) → divide → simplify_sub → result.

2) solve_coeff_var_equals_constant: for one-variable equations coeff*var = constant
   (e.g. after elimination we get 18x = 90 or 2x = 6). Used by DIRECT, LCM, and CROSS.
   Logical path: equation → flip_signs (if coeff<0) → divide → simplify_result → result.

Rendering hides duplicate or trivial steps (e.g. "divide by 1" when coeff = ±1).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

import sympy as sp


def _expr_latex(expr: sp.Expr) -> str:
    return sp.latex(sp.simplify(expr))


def _coefficient_is_one_or_minus_one(b: sp.Expr) -> bool:
    """True if b simplifies to 1 or -1 (so 'divide by b' step is redundant)."""
    b = sp.simplify(b)
    if b == 1 or b == -1:
        return True
    return False


def _coefficient_is_minus_one(b: sp.Expr) -> bool:
    """True if b simplifies to -1 (isolate shows '-y = ...'; we need result step for 'y = ...')."""
    return sp.simplify(b) == -1 or sp.simplify(b) == sp.S(-1)


def _term(coeff: sp.Expr, var: str) -> str:
    """Format coeff*var for display; hide coefficient when 1 or -1."""
    coeff = sp.simplify(coeff)
    if coeff == 1:
        return var
    if coeff == -1:
        return f"-{var}"
    return f"{sp.latex(coeff)}{var}"


def solve_coeff_var_equals_constant(
    coeff: Union[sp.Expr, int, float],
    constant: Union[sp.Expr, int, float],
    var_name: str,
) -> List[Dict[str, Any]]:
    """
    Produce the unified step sequence for solving coeff*var = constant (one variable).

    Used after elimination add/subtract when we have Ax = C or By = C.
    Logical path: equation → flip_signs (if coeff < 0) → divide → simplify_result → result.
    Same visibility rules as solve_linear_for_var (hide divide when |coeff| = 1, etc.).
    """
    coeff = sp.simplify(sp.S(coeff))
    constant = sp.simplify(sp.S(constant))
    steps: List[Dict[str, Any]] = []

    # 1. Equation: coeff*var = constant
    term_str = _term(coeff, var_name)
    steps.append({
        "type": "equation",
        "latex": f"{term_str} = {_expr_latex(constant)}",
        "visible": True,
    })

    # 2. Flip signs when coeff < 0
    coeff_negative = coeff.is_negative or (coeff.is_Number and coeff < 0)
    if coeff_negative:
        steps.append({
            "type": "flip_signs",
            "latex": f"{_term(-coeff, var_name)} = {_expr_latex(-constant)}",
            "visible": True,
        })
        coeff = -coeff
        constant = sp.simplify(-constant)
    else:
        steps.append({"type": "flip_signs", "latex": "", "visible": False})

    # 3. Divide (symbolic division so fractions are preserved; do not use int() — e.g. int(S(1)/2)==0)
    value_frac = sp.simplify(constant / coeff)
    value_simple = sp.simplify(value_frac)
    divide_visible = not _coefficient_is_one_or_minus_one(coeff)
    divide_latex = f"{var_name} = {_expr_latex(value_frac)}"
    steps.append({
        "type": "divide",
        "latex": divide_latex,
        "visible": divide_visible,
    })

    # 4. Simplify result
    simplify_visible = value_simple != value_frac
    steps.append({
        "type": "simplify_result",
        "latex": f"{var_name} = {_expr_latex(value_simple)}",
        "visible": simplify_visible,
    })

    # 5. Result
    result_latex = f"{var_name} = {_expr_latex(value_simple)}"
    if not divide_visible:
        result_visible = True
    elif simplify_visible:
        result_visible = False
    else:
        result_visible = result_latex != divide_latex
    steps.append({
        "type": "result",
        "latex": result_latex,
        "visible": result_visible,
    })

    return steps


def solve_linear_for_var(
    a: Union[sp.Expr, int, float],
    b: Union[sp.Expr, int, float],
    c: Union[sp.Expr, int, float],
    chosen_var: str,
    other_var: str,
) -> List[Dict[str, Any]]:
    """
    Produce the unified step sequence for solving a*x + b*y = c for the chosen variable.

    Parameters
    ----------
    a : coefficient of the *other* variable (e.g. 3 when we have 3x + ...)
    b : coefficient of the *chosen* variable (e.g. 1 or 2 or 2*sqrt(3))
    c : constant term
    chosen_var : name of variable we solve for (e.g. 'y')
    other_var : name of the other variable (e.g. 'x')

    Returns
    ----------
    List of step dicts. Each step has:
      - type : "equation" | "isolate" | "flip_signs" | "divide" | "simplify_sub" | "result"
      - latex : LaTeX string for the step
      - visible : whether to show this step in rendering (duplicate/trivial steps are hidden)
    Optional for simplify_sub: description (short text for the sub-step).
    """
    a, b, c = sp.simplify(sp.S(a)), sp.simplify(sp.S(b)), sp.simplify(sp.S(c))
    chosen_sym = sp.Symbol(chosen_var)
    other_sym = sp.Symbol(other_var)

    steps: List[Dict[str, Any]] = []

    # 1. Equation: a*other + b*chosen = c
    lhs_eq = a * other_sym + b * chosen_sym
    steps.append({
        "type": "equation",
        "latex": f"{_expr_latex(lhs_eq)} = {_expr_latex(c)}",
        "visible": True,
    })

    # 2. Isolate: b*chosen = c - a*other
    rhs_isolate = c - a * other_sym
    lhs_isolate = b * chosen_sym
    steps.append({
        "type": "isolate",
        "latex": f"{_expr_latex(lhs_isolate)} = {_expr_latex(rhs_isolate)}",
        "visible": True,
    })

    # 3. Flip signs: when b < 0, multiply both sides by -1 (so we never divide by a negative integer)
    b_negative = sp.simplify(b).is_negative or (sp.simplify(b).is_Number and b < 0)
    if b_negative:
        lhs_flip = (-b) * chosen_sym
        rhs_flip = sp.simplify(-rhs_isolate)
        steps.append({
            "type": "flip_signs",
            "latex": f"{_expr_latex(lhs_flip)} = {_expr_latex(rhs_flip)}",
            "visible": True,
        })
        # After flip, effective coefficient is -b (positive); quotient for display is rhs_flip / (-b)
        divisor = -b
        raw_quotient = rhs_flip / divisor
    else:
        raw_quotient = (c - a * other_sym) / b
        divisor = b
    result_expr = sp.simplify(raw_quotient)
    divide_visible = not _coefficient_is_one_or_minus_one(b)
    steps.append({
        "type": "divide",
        "latex": f"{chosen_var} = {_expr_latex(raw_quotient)}",
        "visible": divide_visible,
    })

    # 4. Simplify: one logical step that may expand into 0+ visible sub-steps
    # (rationalize, expand, cancel, etc.; each sub-step has its own visibility)
    simplify_sub_steps = _build_simplify_sub_steps(b, c, a, other_sym, chosen_var, result_expr)
    for sub in simplify_sub_steps:
        steps.append({
            "type": "simplify_sub",
            "latex": sub["latex"],
            "visible": sub["visible"],
            "description": sub.get("description", ""),
        })

    # 5. Result: chosen = final expression. Hide when it would repeat the previous visible step.
    if simplify_sub_steps and "expr" in simplify_sub_steps[-1]:
        final_expr = sp.simplify(simplify_sub_steps[-1]["expr"])
    else:
        final_expr = sp.simplify(result_expr)
    result_latex = f"{chosen_var} = {_expr_latex(final_expr)}"
    # Don't repeat: when divide hidden, isolate (b=1) or flip_signs (b=-1) already shows final line.
    # When divide visible, show result only if it differs from divide (e.g. simplified form).
    divide_latex = f"{chosen_var} = {_expr_latex(raw_quotient)}"
    result_visible = bool(simplify_sub_steps)
    if not result_visible:
        result_visible = divide_visible and (result_latex != divide_latex)
    steps.append({
        "type": "result",
        "latex": result_latex,
        "visible": result_visible,
    })

    return steps


def _build_simplify_sub_steps(
    b: sp.Expr,
    c: sp.Expr,
    a: sp.Expr,
    other_sym: sp.Symbol,
    chosen_var: str,
    result_expr: sp.Expr,
) -> List[Dict[str, Any]]:
    """
    Build 0 or more simplify sub-steps (e.g. rationalize denominator, expand).
    Each sub-step can set visible=False if it's a no-op for this case.
    """
    sub_steps: List[Dict[str, Any]] = []
    # Optional: if result_expr is a fraction with a surd in the denominator, add rationalize step.
    # For testing we keep it simple: no sub-steps by default.
    return sub_steps


def get_visible_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only steps where visible is True (for easier assertion in tests)."""
    return [s for s in steps if s.get("visible", True)]
