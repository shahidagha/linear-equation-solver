"""
Tests for the unified substitute-and-solve block (substitute → expand → clear_denom? → arrange → simplify → flip? → divide → result).
Covers: no fractions (y=x+2 into 3x+4y=29), with fractions (y=(7-2x)/3 into 5x-4y=10).
"""

import pytest
import sympy as sp

from backend.utils.substitute_and_solve_block import (
    get_visible_steps,
    substitute_and_solve_for_var,
)


def test_fixed_step_types():
    """Block always returns the same logical step types in order."""
    x = sp.Symbol("x")
    steps = substitute_and_solve_for_var(3, 4, 29, "y", x + 2, "x", target_eq_num=2)
    types = [s["type"] for s in steps]
    expected = [
        "intro", "substitute_raw", "expand", "clear_denominator", "arrange",
        "simplify_lhs", "flip_signs", "divide", "simplify_result", "result",
    ]
    assert types == expected


def test_simple_no_fractions_y_equals_x_plus_2():
    """Substitute y = x+2 into 3x+4y=29. No denominators → clear_denominator hidden."""
    x = sp.Symbol("x")
    steps = substitute_and_solve_for_var(3, 4, 29, "y", x + 2, "x", target_eq_num=2)
    clear_step = next(s for s in steps if s["type"] == "clear_denominator")
    assert clear_step["visible"] is False
    visible = get_visible_steps(steps)
    visible_types = [s["type"] for s in visible]
    assert "clear_denominator" not in visible_types
    result_step = next(s for s in steps if s["type"] == "result")
    assert "x" in result_step["latex"] and "3" in result_step["latex"]


def test_with_fractions_clear_denominator_visible():
    """Substitute y = (7-2x)/3 into 5x-4y=10. Has fractions → clear_denominator visible."""
    x = sp.Symbol("x")
    expr = (7 - 2 * x) / 3
    steps = substitute_and_solve_for_var(5, -4, 10, "y", expr, "x", target_eq_num=2)
    clear_step = next(s for s in steps if s["type"] == "clear_denominator")
    assert clear_step["visible"] is True
    visible = get_visible_steps(steps)
    visible_types = [s["type"] for s in visible]
    assert "clear_denominator" in visible_types
    result_step = next(s for s in steps if s["type"] == "result")
    assert "x" in result_step["latex"]


def test_flip_signs_when_coeff_negative():
    """When coefficient of remaining var is negative after simplify_lhs, flip_signs is visible."""
    # Target 2x - 3y = 0, substitute x = 5 → 10 - 3y = 0 → -3y = -10 → flip → 3y = 10.
    steps = substitute_and_solve_for_var(2, -3, 0, "x", sp.S(5), "y", target_eq_num=2)
    flip_step = next(s for s in steps if s["type"] == "flip_signs")
    assert flip_step["visible"] is True


def test_divide_hidden_when_coeff_one():
    """When coefficient of remaining variable is 1 after simplify, divide step is hidden."""
    # Target 0*x + 1*y = 5, substitute x=0 → y = 5 (coeff 1, so divide hidden).
    steps = substitute_and_solve_for_var(0, 1, 5, "x", sp.S(0), "y", target_eq_num=2)
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is False
    result_step = next(s for s in steps if s["type"] == "result")
    assert result_step["visible"] is True
    assert "y" in result_step["latex"] and "5" in result_step["latex"]


def test_intro_and_substitute_raw_content():
    """Intro and substitute_raw steps contain expected text/equation."""
    x = sp.Symbol("x")
    steps = substitute_and_solve_for_var(3, 4, 29, "y", x + 2, "x", target_eq_num=2)
    intro = next(s for s in steps if s["type"] == "intro")
    assert "Substituting" in intro["latex"] and "Equation (2)" in intro["latex"]
    raw = next(s for s in steps if s["type"] == "substitute_raw")
    assert "3" in raw["latex"] and "4" in raw["latex"] and "29" in raw["latex"]
