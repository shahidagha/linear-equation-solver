"""Unit tests for EquationStandardizer."""
import pytest
import sympy as sp

from backend.math_engine.equation import Equation
from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.system import EquationSystem
from backend.normalization.equation_standardizer import EquationStandardizer


def test_standardize_produces_system_and_steps(sample_system):
    """Standardizer returns system and steps for both equations."""
    raw = [
        "2x + y = 7",
        "4x - 7y = 41",
    ]
    result = EquationStandardizer().standardize(sample_system, raw_equations=raw)
    assert "system" in result
    assert "steps_eq1" in result
    assert "steps_eq2" in result
    assert isinstance(result["system"], EquationSystem)
    assert result["system"].var1 == "x" and result["system"].var2 == "y"
    assert len(result["steps_eq1"]) >= 1
    assert len(result["steps_eq2"]) >= 1


def test_standardize_steps_contain_expected_types(sample_system):
    """Standardization steps include write_equation, rearrange_standard_form, remove_denominator, etc."""
    result = EquationStandardizer().standardize(sample_system, raw_equations=["2x + y = 7", "4x - 7y = 41"])
    types_eq1 = {s.get("type") for s in result["steps_eq1"]}
    assert "write_equation" in types_eq1
    assert "rearrange_standard_form" in types_eq1
    assert "make_leading_positive" in types_eq1
    assert "remove_denominator" in types_eq1 or "reduce_equation" in types_eq1
    assert "assign_equation_number" in types_eq1


def test_standardized_system_solves_correctly(sample_system):
    """Standardized system has same solution as original (e.g. x=5, y=-3)."""
    result = EquationStandardizer().standardize(sample_system, raw_equations=["2x + y = 7", "4x - 7y = 41"])
    sys = result["system"]
    eq1 = sys.eq1.sympy_equation(sys.var1, sys.var2)
    eq2 = sys.eq2.sympy_equation(sys.var1, sys.var2)
    sol = sp.solve([eq1, eq2], [sp.Symbol(sys.var1), sp.Symbol(sys.var2)])
    assert sol is not None
    assert sol[sp.Symbol("x")] == 5
    assert sol[sp.Symbol("y")] == -3


def test_standardize_leading_positive():
    """Equation with negative leading coefficient gets sign flip step."""
    a = FractionSurd(-2, 1, 1, 1, 1)
    b = FractionSurd(1, 1, 1, 1, 1)
    c = FractionSurd(-7, 1, 1, 1, 1)
    eq = Equation(a, b, c)
    eq2 = Equation(FractionSurd(4, 1, 1, 1, 1), FractionSurd(-7, 1, 1, 1, 1), FractionSurd(41, 1, 1, 1, 1))
    system = EquationSystem(eq, eq2, var1="x", var2="y")
    result = EquationStandardizer().standardize(system, raw_equations=["-2x + y = -7", "4x - 7y = 41"])
    types_eq1 = [s.get("type") for s in result["steps_eq1"]]
    assert "make_leading_positive" in types_eq1
