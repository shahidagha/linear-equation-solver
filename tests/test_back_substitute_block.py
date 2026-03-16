"""
Tests for the unified back-substitute block (intro → substitute_raw → ... → result).
"""

import pytest
import sympy as sp

from backend.utils.back_substitute_block import (
    back_substitute,
    get_visible_steps,
)


def test_fixed_step_types():
    """Block returns a fixed logical sequence of step types."""
    steps = back_substitute(3, 4, 29, "x", sp.S(5), "y", eq_num=1)
    types = [s["type"] for s in steps]
    expected = [
        "intro", "substitute_raw", "simplify_substituted", "isolate",
        "simplify_rhs", "flip_signs", "divide", "simplify_result", "result",
    ]
    assert types == expected


def test_simple_substitute_x_5_into_3x_plus_4y_29():
    """Substitute x=5 into 3x+4y=29 → y = 7/2 (or 3.5); divide visible."""
    steps = back_substitute(3, 4, 29, "x", sp.S(5), "y", eq_num=1)
    visible = get_visible_steps(steps)
    raw = next(s for s in steps if s["type"] == "substitute_raw")
    assert "5" in raw["latex"] and "4" in raw["latex"] and "29" in raw["latex"]
    result_step = next(s for s in steps if s["type"] == "result")
    assert "y" in result_step["latex"]


def test_divide_hidden_when_coeff_one():
    """Equation 1*x + 2*y = 10, substitute x=4 → 2y=6 → y=3; divide visible. For b=1 we hide divide."""
    steps = back_substitute(1, 1, 5, "x", sp.S(3), "y", eq_num=1)
    # 1*3 + 1*y = 5 → y = 2
    divide_step = next(s for s in steps if s["type"] == "divide")
    assert divide_step["visible"] is False
    result_step = next(s for s in steps if s["type"] == "result")
    assert result_step["visible"] is True


def test_intro_contains_equation_number():
    """Intro step mentions equation number."""
    steps = back_substitute(2, 3, 10, "x", sp.S(1), "y", eq_num=2)
    intro = next(s for s in steps if s["type"] == "intro")
    assert "equation (2)" in intro["latex"]
