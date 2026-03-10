from math_engine.fraction_surd import FractionSurd
from math_engine.equation import Equation
from math_engine.system import EquationSystem
from models.equation_models import EquationSystem as EquationSystemModel
from solver.elimination_solver import EliminationSolver
from solver.graphical_solver import GraphicalSolver
from utils.hash_utils import generate_equation_hash, generate_system_hash
from sqlalchemy.orm import Session
from models.solution_methods import SolutionMethod
def build_fraction_surd(term: dict):
    """
    Convert frontend term JSON into FractionSurd object
    """

    sign = term["sign"]
    numCoeff = term["numCoeff"]
    numRad = term["numRad"]
    denCoeff = term["denCoeff"]
    denRad = term["denRad"]

    numCoeff = sign * numCoeff

    return FractionSurd(
        numCoeff,
        numRad,
        denCoeff,
        denRad,
        1
    )


def to_python_number(value):
    """
    Convert SymPy numbers to Python numbers
    """
    try:
        return int(value)
    except:
        try:
            return float(value)
        except:
            return str(value)

def convert_points(points):
    """
    Convert graph points to JSON-safe numbers
    """

    clean = []

    for p in points:

        x = to_python_number(p[0])
        y = to_python_number(p[1])

        clean.append([x, y])

    return clean

def solve_system(db: Session, system_id: int, payload: dict):
    # -----------------------------
    # Extract data
    # -----------------------------
    print("SOLVER SERVICE STARTED")
    var1 = payload["variables"]["var1"]
    var2 = payload["variables"]["var2"]

    eq1_data = payload["equation1"]
    eq2_data = payload["equation2"]

    # -----------------------------
    # Generate hashes for duplicate detection
    # -----------------------------

    equation_hash = generate_equation_hash(eq1_data, eq2_data)
    system_hash = generate_system_hash(var1, var2, eq1_data, eq2_data)

    # -----------------------------
    # Check exact duplicate
    # -----------------------------


    # -----------------------------
    # Check same equations but different variables
    # -----------------------------

    
    # -----------------------------
    # Build Equation 1
    # -----------------------------

    a1 = build_fraction_surd(eq1_data["term1"])
    b1 = build_fraction_surd(eq1_data["term2"])
    c1 = build_fraction_surd(eq1_data["constant"])

    eq1 = Equation(a1, b1, c1)

    # -----------------------------
    # Build Equation 2
    # -----------------------------

    a2 = build_fraction_surd(eq2_data["term1"])
    b2 = build_fraction_surd(eq2_data["term2"])
    c2 = build_fraction_surd(eq2_data["constant"])

    eq2 = Equation(a2, b2, c2)

    # -----------------------------
    # Initialize containers
    # -----------------------------

    methods = {}
    graph = {}

    # -----------------------------
    # Build System
    # -----------------------------

    system = EquationSystem(eq1, eq2)

    # -----------------------------
    # Elimination Solver
    # -----------------------------

    solver = EliminationSolver(system)

    raw_solution = solver.solve()

    print("RAW SOLUTION:", raw_solution)

    values = list(raw_solution.values())

    solution = {
        var1: to_python_number(values[0]),
        var2: to_python_number(values[1])
    }

    # -----------------------------
    # Extract Steps
    # -----------------------------

    steps = []

    for step in solver.recorder.get_steps():

        if step.type == "vertical_elimination":

            data = step.content

            steps.append({
                "type": "vertical_elimination",
                "eq1": data["eq1"],
                "eq2": data["eq2"],
                "result": data["result"]
            })

        else:

            steps.append({
                "type": step.type,
                "content": step.content
            })

    methods["elimination"] = steps

    # -----------------------------
    # Graphical Solver
    # -----------------------------

    graph_solver = GraphicalSolver(system)

    points1, points2 = graph_solver.generate_tables()

    points1 = convert_points(points1)
    points2 = convert_points(points2)

    graph = {
        "equation1_points": points1,
        "equation2_points": points2,
        "intersection": solution
    }

    methods["graphical_steps"] = [
        "Generated value table for equation 1",
        "Generated value table for equation 2",
        "Plotted both equations",
        "Intersection point found"
    ]
    # -----------------------------
    # Save new equation system
    # -----------------------------

   

    # ---------------------------------
    # Save Elimination Method
    # ---------------------------------
    print("Saving solution methods for system:", system_id)
    print("Creating elimination record")
    elimination_record = SolutionMethod(
        system_id=system_id,
        method_name="elimination",
        solution=solution,
        steps=methods["elimination"],
        graph_data=None
    )

    db.add(elimination_record)


    # ---------------------------------
    # Save Graphical Method
    # ---------------------------------

    graphical_record = SolutionMethod(
        system_id=system_id,
        method_name="graphical",
        solution=solution,
        steps=methods["graphical_steps"],
        graph_data=graph
    )

    db.add(graphical_record)

    db.commit()
    # -----------------------------
    # Return Result
    # -----------------------------

    return {
        "solution": solution,
        "methods": methods,
        "graph": graph
    }