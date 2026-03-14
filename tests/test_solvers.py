"""Unit tests for elimination, substitution, Cramer, and graphical solvers."""
import pytest
import sympy as sp

from backend.math_engine.equation import Equation
from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.system import EquationSystem
from backend.normalization.equation_standardizer import EquationStandardizer
from backend.solver.elimination_solver import EliminationSolver
from backend.solver.substitution_solver import SubstitutionSolver
from backend.solver.cramer_solver import CramerSolver
from backend.solver.graphical_solver import GraphicalSolver
from backend.utils.degenerate import is_degenerate


def _standardized_system(sample_system):
    """Return standardized system for solvers."""
    raw = ["2x + y = 7", "4x - 7y = 41"]
    result = EquationStandardizer().standardize(sample_system, raw_equations=raw)
    return result["system"]


def _solution_values(raw):
    """Extract (x, y) from solver result; raw may have Symbol or string keys."""
    if not isinstance(raw, dict) or len(raw) < 2:
        return (None, None)
    vals = [sp.simplify(v) for v in raw.values()]
    if len(vals) == 2:
        return (int(vals[0]), int(vals[1]))
    return (None, None)


def test_elimination_solver_unique_solution(sample_system):
    """Elimination solver returns x=5, y=-3 for 2x+y=7, 4x-7y=41."""
    sys = _standardized_system(sample_system)
    solver = EliminationSolver(sys)
    raw = solver.solve()
    assert not is_degenerate(raw)
    x_val, y_val = _solution_values(raw)
    assert x_val == 5 and y_val == -3


def test_elimination_solver_records_steps(sample_system):
    """Elimination solver records steps (equation, vertical_elimination, etc.)."""
    sys = _standardized_system(sample_system)
    solver = EliminationSolver(sys)
    solver.solve()
    steps = solver.recorder.get_steps()
    assert len(steps) >= 1
    types = [getattr(s, "type", None) for s in steps]
    assert "equation" in types or "vertical_elimination" in types or "operation" in types or "text" in types


def test_substitution_solver_unique_solution(sample_system):
    """Substitution solver returns x=5, y=-3 for 2x+y=7, 4x-7y=41."""
    sys = _standardized_system(sample_system)
    solver = SubstitutionSolver(sys)
    raw = solver.solve()
    assert not is_degenerate(raw)
    x_val, y_val = _solution_values(raw)
    assert x_val == 5 and y_val == -3


def test_cramer_solver_unique_solution(sample_system):
    """Cramer solver returns x=5, y=-3 for 2x+y=7, 4x-7y=41."""
    sys = _standardized_system(sample_system)
    solver = CramerSolver(sys)
    raw = solver.solve()
    assert not is_degenerate(raw)
    x_val, y_val = _solution_values(raw)
    assert x_val == 5 and y_val == -3


def test_graphical_solver_returns_points(sample_system):
    """Graphical solver generate_tables returns two point lists."""
    sys = _standardized_system(sample_system)
    solver = GraphicalSolver(sys)
    p1, p2 = solver.generate_tables()
    assert isinstance(p1, list) and isinstance(p2, list)
    assert len(p1) >= 2 and len(p2) >= 2


def test_graphical_solver_classify_unique(sample_system):
    """Graphical solver classifies unique solution system as 'unique'."""
    sys = _standardized_system(sample_system)
    solver = GraphicalSolver(sys)
    assert solver.classify() == "unique"


def test_elimination_degenerate_infinite():
    """Elimination detects dependent equations (infinitely many solutions)."""
    # Same line: x + y = 1 and 2x + 2y = 2
    eq1 = Equation(
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(1, 1, 1, 1, 1),
    )
    eq2 = Equation(
        FractionSurd(2, 1, 1, 1, 1),
        FractionSurd(2, 1, 1, 1, 1),
        FractionSurd(2, 1, 1, 1, 1),
    )
    system = EquationSystem(eq1, eq2, var1="x", var2="y")
    std = EquationStandardizer().standardize(system, raw_equations=["x + y = 1", "2x + 2y = 2"])
    solver = EliminationSolver(std["system"])
    raw = solver.solve()
    assert is_degenerate(raw)
    assert raw.get("solution_type") == "infinite"


def test_elimination_degenerate_none():
    """Elimination detects inconsistent system (no solution)."""
    # Parallel: x + y = 1 and x + y = 2
    eq1 = Equation(
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(1, 1, 1, 1, 1),
    )
    eq2 = Equation(
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(1, 1, 1, 1, 1),
        FractionSurd(2, 1, 1, 1, 1),
    )
    system = EquationSystem(eq1, eq2, var1="x", var2="y")
    std = EquationStandardizer().standardize(system, raw_equations=["x + y = 1", "x + y = 2"])
    solver = EliminationSolver(std["system"])
    raw = solver.solve()
    assert is_degenerate(raw)
    assert raw.get("solution_type") == "none"
