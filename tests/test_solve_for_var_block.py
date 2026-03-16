"""
Tests for the unified solve-for-variable block (equation → isolate → divide → simplify → result).
Covers: coeff 1 (3x+y=10), coeff 2 (3x+2y=10), and surds (3√2 x + 2√3 y = 5√7).
"""

import pytest
import sympy as sp

from backend.utils.solve_for_var_block import (
    get_visible_steps,
    solve_coeff_var_equals_constant,
    solve_linear_for_var,
)


def test_case_1_coeff_one_3x_plus_y_equals_10():
    """3x + y = 10, solve for y. Divide and result are hidden (result would repeat isolate)."""
    steps = solve_linear_for_var(3, 1, 10, "y", "x")
    types = [s["type"] for s in steps]
    assert types == ["equation", "isolate", "divide", "result"]
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is False
    result_step = next(s for s in steps if s["type"] == "result")
    assert result_step["visible"] is False
    visible = get_visible_steps(steps)
    visible_types = [s["type"] for s in visible]
    assert visible_types == ["equation", "isolate"]
    isolate_step = next(s for s in steps if s["type"] == "isolate")
    assert "y" in isolate_step["latex"] and "10" in isolate_step["latex"] and "3" in isolate_step["latex"]


def test_case_2_coeff_two_3x_plus_2y_equals_10():
    """3x + 2y = 10, solve for y. Equation, isolate, divide visible; result only if different from divide."""
    steps = solve_linear_for_var(3, 2, 10, "y", "x")
    types = [s["type"] for s in steps]
    assert types == ["equation", "isolate", "divide", "result"]
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is True
    visible = get_visible_steps(steps)
    assert len(visible) >= 3  # at least equation, isolate, divide; result only if not duplicate
    assert visible[0]["type"] == "equation" and visible[1]["type"] == "isolate" and visible[2]["type"] == "divide"
    result_step = next(s for s in steps if s["type"] == "result")
    assert "y" in result_step["latex"]


def test_case_3_surds_3sqrt2_x_plus_2sqrt3_y_equals_5sqrt7():
    """3√2 x + 2√3 y = 5√7, solve for y. Same structure: equation, isolate, divide (visible), result."""
    a = 3 * sp.sqrt(2)
    b = 2 * sp.sqrt(3)
    c = 5 * sp.sqrt(7)
    steps = solve_linear_for_var(a, b, c, "y", "x")
    types = [s["type"] for s in steps]
    assert types == ["equation", "isolate", "divide", "result"]
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is True
    # Equation step should contain sqrt
    eq_step = next(s for s in steps if s["type"] == "equation")
    assert "sqrt" in eq_step["latex"] or "\\\\sqrt" in eq_step["latex"]
    result_step = next(s for s in steps if s["type"] == "result")
    assert "y" in result_step["latex"]


def test_solve_for_x_instead():
    """2x + 4y = 8, solve for x. chosen_var=x, other_var=y; a=4, b=2, c=8."""
    steps = solve_linear_for_var(4, 2, 8, "x", "y")
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is True
    result_step = next(s for s in steps if s["type"] == "result")
    assert "x" in result_step["latex"]


def test_coeff_minus_one_flip_signs_no_divide():
    """2x - y = 5: isolate, then flip signs (y = 2x - 5); no divide by -1."""
    steps = solve_linear_for_var(2, -1, 5, "y", "x")
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is False
    visible = get_visible_steps(steps)
    types = [s["type"] for s in visible]
    assert "flip_signs" in types
    assert "equation" in types and "isolate" in types


def test_solve_coeff_var_equals_constant_fixed_path():
    """solve_coeff_var_equals_constant: equation → flip_signs → divide → simplify_result → result."""
    steps = solve_coeff_var_equals_constant(18, 90, "x")
    types = [s["type"] for s in steps]
    assert types == ["equation", "flip_signs", "divide", "simplify_result", "result"]
    eq = next(s for s in steps if s["type"] == "equation")
    assert "18" in eq["latex"] and "90" in eq["latex"]
    div = next(s for s in steps if s["type"] == "divide")
    assert div["visible"] is True
    res = next(s for s in steps if s["type"] == "result")
    assert "x" in res["latex"] and "5" in res["latex"]


def test_solve_coeff_var_equals_constant_divide_hidden_when_coeff_one():
    """When coeff is 1 (e.g. x = 5), divide step is hidden."""
    steps = solve_coeff_var_equals_constant(1, 5, "x")
    div = next(s for s in steps if s["type"] == "divide")
    assert div["visible"] is False
    visible = get_visible_steps(steps)
    assert any(s["type"] == "result" for s in visible)


def test_negative_coeff_flip_then_divide_by_positive():
    """5x - 3y = 10: isolate, flip signs (3y = 5x - 10), then divide by 3 (never by -3)."""
    steps = solve_linear_for_var(5, -3, 10, "y", "x")
    visible = get_visible_steps(steps)
    types = [s["type"] for s in visible]
    assert types == ["equation", "isolate", "flip_signs", "divide"]
    flip = next(s for s in steps if s["type"] == "flip_signs")
    assert "3 y" in flip["latex"] or "3y" in flip["latex"].replace(" ", "")
    div = next(s for s in steps if s["type"] == "divide")
    assert "y" in div["latex"] and ("3" in div["latex"] or "\\frac" in div["latex"])
