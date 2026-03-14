"""
Degenerate system result: no solution (inconsistent) or infinitely many (dependent).
Each solver returns one of these when it detects degeneracy at the natural point in its steps.
"""
from typing import Any, Dict

# Keys used in degenerate return dict
SOLUTION_TYPE = "solution_type"
MESSAGE = "message"

NONE = "none"
INFINITE = "infinite"
ABOVE_GRADE = "above_grade"

MSG_NONE = "The system has no solution (the equations are inconsistent; the lines are parallel)."
MSG_INFINITE = "The system has infinitely many solutions (the two equations represent the same line)."
MSG_ABOVE_GRADE = (
    "At this step we would add or subtract expressions involving surds with different radicands, "
    "which is beyond the scope of the current grade."
)


def degenerate_none(message: str = MSG_NONE) -> Dict[str, Any]:
    return {SOLUTION_TYPE: NONE, MESSAGE: message}


def degenerate_infinite(message: str = MSG_INFINITE) -> Dict[str, Any]:
    return {SOLUTION_TYPE: INFINITE, MESSAGE: message}


def above_grade(message: str = MSG_ABOVE_GRADE) -> Dict[str, Any]:
    return {SOLUTION_TYPE: ABOVE_GRADE, MESSAGE: message}


def is_degenerate(raw_solution: Any) -> bool:
    """True if the solver returned a non-unique result (none, infinite, or above_grade)."""
    return isinstance(raw_solution, dict) and SOLUTION_TYPE in raw_solution
