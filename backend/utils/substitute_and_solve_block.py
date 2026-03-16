"""
Unified "substitute into the other equation and solve for the remaining variable" block.

Logical path (always the same):
  1. intro          : "Substituting y = expr into Equation (2):"
  2. substitute_raw : a*x + b*expr = c (raw substitution, no expand)
  3. expand         : distribute b*expr (e.g. 5x - 4(7-2x)/3 = 10 → terms shown separately)
  4. clear_denominator : multiply by LCM to remove fractions (visible only when denominators present)
  5. arrange        : variable terms on one side, constants on the other
  6. simplify_lhs   : collect like terms (e.g. 23x = 58)
  7. flip_signs     : multiply by -1 when coefficient of var is negative (visible only then)
  8. divide         : var = constant/coeff (visible when |coeff| != 1)
  9. simplify_result: simplify the fraction (visible only when it actually simplifies)
 10. result         : var = final value (hidden when duplicate of divide or simplify_result)

Rendering uses visibility so the number of *shown* steps varies (e.g. no clear_denominator when
no fractions, no flip_signs when coeff > 0) without changing the design.
"""

from __future__ import annotations

from math import gcd
from typing import Any, Dict, List, Optional, Union

import sympy as sp


def _expr_latex(expr: sp.Expr) -> str:
    return sp.latex(sp.simplify(expr))


def _get_denominators(expr: sp.Expr) -> List[int]:
    """Collect all rational denominators (q != 1) from expr."""
    denoms = []
    for atom in expr.atoms(sp.Rational):
        if atom.q != 1:
            denoms.append(atom.q)
    return denoms


def _lcm_of_denominators(expr: sp.Expr) -> int:
    """LCM of all rational denominators in expr; 1 if none."""
    denoms = _get_denominators(expr)
    if not denoms:
        return 1
    mult = denoms[0]
    for d in denoms[1:]:
        mult = mult * d // gcd(mult, d)
    return mult


def substitute_and_solve_for_var(
    a_t: Union[sp.Expr, int, float],
    b_t: Union[sp.Expr, int, float],
    c_t: Union[sp.Expr, int, float],
    substituted_var: str,
    expr: sp.Expr,
    remaining_var: str,
    target_eq_num: int = 2,
) -> List[Dict[str, Any]]:
    """
    Produce the unified step sequence for substituting substituted_var = expr into
    a_t*substituted + b_t*remaining = c_t (target equation) and solving for remaining_var.
    So after substitution: a_t*expr + b_t*remaining = c_t.

    Parameters
    ----------
    a_t, b_t, c_t : coefficients and RHS of the target equation (the one we substitute into)
    substituted_var : name of variable we substitute (e.g. 'y')
    expr : SymPy expression for that variable in terms of remaining_var (e.g. (7-2*x)/3)
    remaining_var : name of the variable we solve for (e.g. 'x')
    target_eq_num : equation number for intro text (e.g. 2)

    Returns
    -------
    List of step dicts. Each step has:
      - type : "intro" | "substitute_raw" | "expand" | "clear_denominator" | "arrange" | "simplify_lhs" | "flip_signs" | "divide" | "simplify_result" | "result"
      - latex : LaTeX string (equation or text)
      - visible : whether to show this step
    Optional: description (short text for the step).
    """
    a_t = sp.simplify(sp.S(a_t))
    b_t = sp.simplify(sp.S(b_t))
    c_t = sp.simplify(sp.S(c_t))
    expr = sp.simplify(expr)
    var_sym = sp.Symbol(remaining_var)
    other_sym_t = sp.Symbol(substituted_var)

    steps: List[Dict[str, Any]] = []

    # Raw substitution: a_t*expr + b_t*var = c_t (substitute expr for the other variable)
    raw_lhs = sp.Add(
        sp.Mul(a_t, expr, evaluate=False),
        sp.Mul(b_t, var_sym, evaluate=False),
        evaluate=False,
    )

    # 1. Intro
    steps.append({
        "type": "intro",
        "latex": (
            f"\\text{{Substituting }} {substituted_var} = {sp.latex(expr)} "
            f"\\text{{ into Equation ({target_eq_num}):}}"
        ),
        "visible": True,
    })

    # 2. Substitute raw
    steps.append({
        "type": "substitute_raw",
        "latex": f"{sp.latex(raw_lhs)} = {_expr_latex(c_t)}",
        "visible": True,
    })

    # 3. Expand (distribute): show (a_t*expr expanded) + b_t*var = c_t
    expanded_lhs = sp.expand(raw_lhs)
    expanded_first = sp.expand(a_t * expr)
    const_first = expanded_first.subs(var_sym, 0)
    var_first = sp.simplify(expanded_first - const_first)
    expand_display = sp.Add(const_first, var_first, b_t * var_sym, evaluate=False)
    steps.append({
        "type": "expand",
        "latex": f"{sp.latex(expand_display)} = {_expr_latex(c_t)}",
        "visible": True,
    })

    # 4. Clear denominator (visible only when there are fractions; always emit step for fixed path)
    mult = _lcm_of_denominators(expanded_lhs)
    if mult != 1:
        cleared_lhs = sp.expand(expand_display * mult)
        cleared_rhs = sp.simplify(c_t * mult)
        cleared_lhs_display = sp.Add(
            *[sp.expand(t * mult) for t in sp.Add.make_args(expand_display)],
            evaluate=False,
        )
        clear_latex = (
            f"\\text{{Multiply the equation by }} {int(mult)} "
            f"\\text{{ to remove the denominator.}}"
        )
        steps.append({
            "type": "clear_denominator",
            "latex": f"{sp.latex(cleared_lhs_display)} = {_expr_latex(cleared_rhs)}",
            "visible": True,
            "description": clear_latex,
        })
    else:
        cleared_lhs = expanded_lhs
        cleared_rhs = c_t
        cleared_lhs_display = expanded_lhs
        steps.append({
            "type": "clear_denominator",
            "latex": f"{sp.latex(expand_display)} = {_expr_latex(c_t)}",
            "visible": False,
        })

    # 5. Arrange: variable terms = RHS (constants moved)
    var_terms = [t for t in sp.Add.make_args(cleared_lhs_display) if t.has(var_sym)]
    const_terms = [t for t in sp.Add.make_args(cleared_lhs) if not t.has(var_sym)]
    var_part = (
        sp.Add(*var_terms, evaluate=False)
        if len(var_terms) > 1
        else (var_terms[0] if var_terms else sp.S.Zero)
    )
    const_part = sp.Add(*const_terms) if const_terms else sp.S.Zero
    rhs_arranged = sp.Add(cleared_rhs, sp.Mul(-1, const_part, evaluate=False), evaluate=False)
    steps.append({
        "type": "arrange",
        "latex": f"{sp.latex(var_part)} = {_expr_latex(rhs_arranged)}",
        "visible": True,
    })

    # 6. Simplify LHS (collect like terms); hide when identical to arrange (avoid duplicate line)
    simplified_lhs = sp.simplify(var_part)
    const_side = sp.simplify(rhs_arranged)
    arrange_latex = f"{sp.latex(var_part)} = {_expr_latex(rhs_arranged)}"
    simplify_lhs_latex = f"{_expr_latex(simplified_lhs)} = {_expr_latex(const_side)}"
    steps.append({
        "type": "simplify_lhs",
        "latex": simplify_lhs_latex,
        "visible": simplify_lhs_latex != arrange_latex,
    })

    coeff = simplified_lhs.coeff(var_sym)

    # 7. Flip signs when coefficient is negative
    coeff_negative = sp.simplify(coeff).is_negative or (
        sp.simplify(coeff).is_Number and coeff < 0
    )
    if coeff_negative:
        lhs_flip = sp.simplify(-simplified_lhs)
        rhs_flip = sp.simplify(-const_side)
        steps.append({
            "type": "flip_signs",
            "latex": f"{_expr_latex(lhs_flip)} = {_expr_latex(rhs_flip)}",
            "visible": True,
        })
        coeff = sp.simplify(-coeff)
        const_side = rhs_flip
    else:
        steps.append({
            "type": "flip_signs",
            "latex": "",
            "visible": False,
        })

    # 8. Divide by coefficient
    try:
        c_num, c_den = int(const_side), int(coeff)
        value_frac = sp.Mul(c_num, sp.Pow(c_den, -1, evaluate=False), evaluate=False)
    except (TypeError, ValueError):
        value_frac = const_side / coeff
    value_simple = sp.simplify(value_frac)
    divide_visible = not (sp.simplify(coeff) == 1 or sp.simplify(coeff) == -1)
    divide_latex = f"{sp.latex(var_sym)} = {_expr_latex(value_frac)}"
    steps.append({
        "type": "divide",
        "latex": divide_latex,
        "visible": divide_visible,
    })

    # 9. Simplify result (when fraction simplifies)
    simplify_result_visible = value_simple != value_frac
    steps.append({
        "type": "simplify_result",
        "latex": f"{sp.latex(var_sym)} = {_expr_latex(value_simple)}",
        "visible": simplify_result_visible,
    })

    # 10. Result: hide when it would duplicate the last visible step; always show when divide was hidden
    result_latex = f"{sp.latex(var_sym)} = {_expr_latex(value_simple)}"
    if not divide_visible:
        result_visible = True  # need to show final answer (divide step was hidden)
    elif simplify_result_visible:
        result_visible = False  # already shown as simplify_result
    else:
        result_visible = result_latex != divide_latex
    steps.append({
        "type": "result",
        "latex": result_latex,
        "visible": result_visible,
    })

    return steps


def get_visible_steps(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only steps where visible is True (for rendering or tests)."""
    return [s for s in steps if s.get("visible", True)]
