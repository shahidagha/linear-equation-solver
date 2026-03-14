"""Pytest fixtures for linear equation solver tests."""
import pytest

from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.equation import Equation
from backend.math_engine.system import EquationSystem


@pytest.fixture
def fraction_surd():
    """Basic FractionSurd: 1 * sqrt(1) / (1 * sqrt(1)) = 1."""
    return FractionSurd(1, 1, 1, 1, 1)


@pytest.fixture
def sample_system():
    """System: 2x + y = 7, 4x - 7y = 41. Solution x=5, y=-3."""
    # eq1: 2x + 1y = 7
    a1 = FractionSurd(2, 1, 1, 1, 1)
    b1 = FractionSurd(1, 1, 1, 1, 1)
    c1 = FractionSurd(7, 1, 1, 1, 1)
    eq1 = Equation(a1, b1, c1)
    # eq2: 4x - 7y = 41
    a2 = FractionSurd(4, 1, 1, 1, 1)
    b2 = FractionSurd(-7, 1, 1, 1, 1)
    c2 = FractionSurd(41, 1, 1, 1, 1)
    eq2 = Equation(a2, b2, c2)
    return EquationSystem(eq1, eq2, var1="x", var2="y")


@pytest.fixture
def valid_solve_payload():
    """Minimal valid payload for solve-system / save-system."""
    return {
        "variables": ["x", "y"],
        "equation1": {
            "terms": [
                {"sign": 1, "numCoeff": 2, "numRad": 1, "denCoeff": 1, "denRad": 1},
                {"sign": 1, "numCoeff": 1, "numRad": 1, "denCoeff": 1, "denRad": 1},
            ],
            "constant": {"sign": 1, "numCoeff": 7, "numRad": 1, "denCoeff": 1, "denRad": 1},
        },
        "equation2": {
            "terms": [
                {"sign": 1, "numCoeff": 4, "numRad": 1, "denCoeff": 1, "denRad": 1},
                {"sign": -1, "numCoeff": 7, "numRad": 1, "denCoeff": 1, "denRad": 1},
            ],
            "constant": {"sign": 1, "numCoeff": 41, "numRad": 1, "denCoeff": 1, "denRad": 1},
        },
    }
