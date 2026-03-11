from sqlalchemy.orm import Session

from math_engine.equation import Equation
from math_engine.fraction_surd import FractionSurd
from math_engine.system import EquationSystem
from models.solution_methods import SolutionMethod
from solver.elimination_solver import EliminationSolver
from solver.graphical_solver import GraphicalSolver


def build_fraction_surd(term: dict):
    """Convert frontend term JSON into FractionSurd object."""

    sign = term["sign"]
    num_coeff = term["numCoeff"]
    num_rad = term["numRad"]
    den_coeff = term["denCoeff"]
    den_rad = term["denRad"]

    num_coeff = sign * num_coeff

    return FractionSurd(num_coeff, num_rad, den_coeff, den_rad, 1)


def to_python_number(value):
    """Convert SymPy numbers to JSON-safe values without float conversion."""

    try:
        return int(value)
    except Exception:
        return str(value)


def convert_points(points):
    """Convert graph points to JSON-safe numbers."""

    clean = []

    for p in points:
        x = to_python_number(p[0])
        y = to_python_number(p[1])
        clean.append([x, y])

    return clean


def solve_system(db: Session, system_id: int, payload: dict):
    var1 = payload["variables"]["var1"]
    var2 = payload["variables"]["var2"]

    eq1_data = payload["equation1"]
    eq2_data = payload["equation2"]

    a1 = build_fraction_surd(eq1_data["term1"])
    b1 = build_fraction_surd(eq1_data["term2"])
    c1 = build_fraction_surd(eq1_data["constant"])
    eq1 = Equation(a1, b1, c1)

    a2 = build_fraction_surd(eq2_data["term1"])
    b2 = build_fraction_surd(eq2_data["term2"])
    c2 = build_fraction_surd(eq2_data["constant"])
    eq2 = Equation(a2, b2, c2)

    methods = {}

    system = EquationSystem(eq1, eq2)

    solver = EliminationSolver(system)
    raw_solution = solver.solve()
    values = list(raw_solution.values())

    solution = {
        var1: to_python_number(values[0]),
        var2: to_python_number(values[1])
    }

    steps = []
    for step in solver.recorder.get_steps():
        if step.type == "vertical_elimination":
            data = step.content
            steps.append(
                {
                    "type": "vertical_elimination",
                    "eq1": data["eq1"],
                    "eq2": data["eq2"],
                    "result": data["result"]
                }
            )
        else:
            steps.append({"type": step.type, "content": step.content})

    methods["elimination"] = steps

    graph_solver = GraphicalSolver(system)
    points1, points2 = graph_solver.generate_tables()

    graph = {
        "equation1_points": convert_points(points1),
        "equation2_points": convert_points(points2),
        "intersection": solution
    }

    methods["graphical_steps"] = [
        "Generated value table for equation 1",
        "Generated value table for equation 2",
        "Plotted both equations",
        "Intersection point found"
    ]

    elimination_record = SolutionMethod(
        system_id=system_id,
        method_name="elimination",
        solution=solution,
        steps=methods["elimination"],
        graph_data=None
    )
    db.add(elimination_record)

    graphical_record = SolutionMethod(
        system_id=system_id,
        method_name="graphical",
        solution=solution,
        steps=methods["graphical_steps"],
        graph_data=graph
    )
    db.add(graphical_record)

    db.commit()

    return {
        "solution": solution,
        "methods": methods,
        "graph": graph
    }
