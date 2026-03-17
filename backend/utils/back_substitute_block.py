"""
Unified "back-substitute" block: substitute a known value into one equation a*x + b*y = c
and solve for the remaining variable.

Used at the end of elimination (and potentially elsewhere): we have one variable's value
(e.g. x = 5), substitute into one of the original equations to find the other (e.g. y).

Logical path (always the same):
  1. intro               : "Substitute x = value in equation (1)"
  2. substitute_raw      : show a*value + b*var = c (nice formatting: hide coeff 1 for a)
  3. simplify_substituted: lhs_known + b*var = c (visible only when different from raw)
  4. isolate             : b*var = c - lhs_known
  5. simplify_rhs        : simplify RHS (visible only when it changes display)
  6. flip_signs          : when b < 0 (visible only then)
  7. divide              : var = (c - lhs_known)/b (visible when |b| != 1)
  8. simplify_result      : when fraction simplifies (visible only then)
  9. result               : var = final value (hidden when duplicate)

Rendering uses visibility so the number of *shown* steps varies without changing the design.
"""

from __future__ import annotations

from typing import Any, Dict, List, Union

import sympy as sp


def _expr_latex(expr: sp.Expr) -> str:
    return sp.latex(sp.simplify(expr))


def _term(coeff: sp.Expr, var: str) -> str:
    """Format coeff*var for display; hide coefficient when 1 or -1."""
    coeff = sp.simplify(coeff)
    if coeff == 1:
        return var
    if coeff == -1:
        return f"-{var}"
    return f"{sp.latex(coeff)}{var}"


def back_substitute(
    a: Union[sp.Expr, int, float],
    b: Union[sp.Expr, int, float],
    c: Union[sp.Expr, int, float],
    known_var: str,
    known_value: sp.Expr,
    solve_for_var: str,
    eq_num: int = 1,
) -> List[Dict[str, Any]]:
    """
    Produce the unified step sequence for: substitute known_var = known_value into
    a*known_var + b*solve_for_var = c (with equation number eq_num) and solve for solve_for_var.

    Parameters
    ----------
    a, b, c : coefficients and RHS of the equation we substitute into (a*known + b*other = c)
    known_var : name of variable we already have (e.g. 'x')
    known_value : its value (SymPy expression, e.g. 5 or 3/2)
    solve_for_var : name of variable we solve for (e.g. 'y')
    eq_num : equation number for intro text (e.g. 1)

    Returns
    -------
    List of step dicts with type, latex, visible; optional description.
    """
    a, b, c = sp.simplify(sp.S(a)), sp.simplify(sp.S(b)), sp.simplify(sp.S(c))
    known_value = sp.simplify(known_value)
    var_sym = sp.Symbol(solve_for_var)

    steps: List[Dict[str, Any]] = []

    # 1. Intro
    steps.append({
        "type": "intro",
        "latex": (
            f"\\text{{Substitute }} {known_var} = {_expr_latex(known_value)} "
            f"\\text{{ in equation ({eq_num})}}"
        ),
        "visible": True,
    })

    # 2. Substitute raw: a*known_value + b*var = c (hide coeff 1/-1 for a)
    b_term = _term(b, solve_for_var)
    if a == 1:
        subst_raw = f"{_expr_latex(known_value)} + {b_term} = {_expr_latex(c)}"
    elif a == -1:
        subst_raw = f"-{_expr_latex(known_value)} + {b_term} = {_expr_latex(c)}"
    else:
        subst_raw = f"{_expr_latex(a)}({_expr_latex(known_value)}) + {b_term} = {_expr_latex(c)}"
    steps.append({
        "type": "substitute_raw",
        "latex": subst_raw,
        "visible": True,
    })

    # 3. Simplify substituted term: lhs_known + b*var = c
    lhs_known = sp.simplify(a * known_value)
    simplify_sub_visible = _expr_latex(lhs_known) != _expr_latex(a * known_value) or (a != 1 and a != -1)
    # Show when the next line would differ (e.g. 3(5) → 15)
    next_line = f"{_expr_latex(lhs_known)} + {b_term} = {_expr_latex(c)}"
    simplify_sub_visible = simplify_sub_visible or (next_line != subst_raw)
    steps.append({
        "type": "simplify_substituted",
        "latex": next_line,
        "visible": simplify_sub_visible,
    })

    # 4. Isolate: b*var = c - lhs_known
    rhs_isolate = sp.simplify(c - lhs_known)
    lhs_isolate = _term(b, solve_for_var)
    steps.append({
        "type": "isolate",
        "latex": f"\\therefore {lhs_isolate} = {_expr_latex(c)} - {_expr_latex(lhs_known)}",
        "visible": True,
    })

    # 5. Simplify RHS (e.g. 9 - 15 → -6) — visible only when it changes display
    rhs_simple = sp.simplify(rhs_isolate)
    simplify_rhs_visible = _expr_latex(rhs_simple) != _expr_latex(rhs_isolate)
    steps.append({
        "type": "simplify_rhs",
        "latex": f"\\therefore {lhs_isolate} = {_expr_latex(rhs_simple)}",
        "visible": simplify_rhs_visible,
    })

    coeff = b
    const_side = sp.simplify(rhs_simple)

    # 6. Flip signs when b < 0
    coeff_negative = sp.simplify(coeff).is_negative or (sp.simplify(coeff).is_Number and coeff < 0)
    if coeff_negative:
        coeff = sp.simplify(-coeff)
        const_side = sp.simplify(-const_side)
        steps.append({
            "type": "flip_signs",
            "latex": f"\\therefore {_term(coeff, solve_for_var)} = {_expr_latex(const_side)}",
            "visible": True,
        })
    else:
        steps.append({"type": "flip_signs", "latex": "", "visible": False})

    # 7. Divide (symbolic division so fractions like 1/2 are preserved; do not use int() — int(S(1)/2)==0)
    value_frac = sp.simplify(const_side / coeff)
    value_simple = sp.simplify(value_frac)
    divide_visible = not (sp.simplify(coeff) == 1 or sp.simplify(coeff) == -1)
    divide_latex = f"\\therefore {solve_for_var} = {_expr_latex(value_frac)}"
    steps.append({
        "type": "divide",
        "latex": divide_latex,
        "visible": divide_visible,
    })

    # 8. Simplify result
    simplify_result_visible = value_simple != value_frac
    steps.append({
        "type": "simplify_result",
        "latex": f"\\therefore {solve_for_var} = {_expr_latex(value_simple)}",
        "visible": simplify_result_visible,
    })

    # 9. Result
    result_latex = f"\\therefore {solve_for_var} = {_expr_latex(value_simple)}"
    if not divide_visible:
        result_visible = True
    elif simplify_result_visible:
        result_visible = False
    else:
        result_visible = result_latex != divide_latex
    steps.append({
        "type": "result",
        "latex": result_latex,
        "visible": result_visible,
    })

    return steps


def get_visible_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only steps where visible is True."""
    return [s for s in steps if s.get("visible", True)]
