from sqlalchemy.orm import Session

from math_engine.equation import Equation
from math_engine.fraction_surd import FractionSurd
from math_engine.system import EquationSystem
from models.solution_methods import SolutionMethod
from solver.elimination_solver import EliminationSolver
from solver.graphical_solver import GraphicalSolver
from solver.substitution_solver import SubstitutionSolver
from solver.cramer_solver import CramerSolver
from latex.equation_formatter import EquationFormatter
from latex.solution_renderer import SolutionLatexRenderer


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


def _equation_lines(eq1: Equation, eq2: Equation, var1: str, var2: str):
    return [
        EquationFormatter.format_equation(eq1.a.to_sympy(), eq1.b.to_sympy(), eq1.c.to_sympy(), var1, var2),
        EquationFormatter.format_equation(eq2.a.to_sympy(), eq2.b.to_sympy(), eq2.c.to_sympy(), var1, var2),
    ]


def _upsert_method_record(
    db: Session,
    system_id: int,
    method_name: str,
    latex_payload: dict,
    solution_json: dict,
    graph_data: dict,
):
    record = db.query(SolutionMethod).filter(
        SolutionMethod.system_id == system_id,
        SolutionMethod.method_name == method_name,
    ).first()

    if record is None:
        record = SolutionMethod(system_id=system_id, method_name=method_name)
        db.add(record)

    record.latex_detailed = latex_payload["latex_detailed"]
    record.latex_medium = latex_payload["latex_medium"]
    record.latex_short = latex_payload["latex_short"]
    record.solution_json = solution_json
    record.graph_data = graph_data


def solve_system(db: Session, system_id: int, payload: dict):
    var1 = payload["variables"]["var1"]
    var2 = payload["variables"]["var2"]

    eq1_data = payload["equation1"]
    eq2_data = payload["equation2"]

    a1 = build_fraction_surd(eq1_data["term1"])
    b1 = build_fraction_surd(eq1_data["term2"])
    c1 = build_fraction_surd(eq1_data["constant"])
    eq1 = Equation(a1, b1, c1, var1=var1, var2=var2)

    a2 = build_fraction_surd(eq2_data["term1"])
    b2 = build_fraction_surd(eq2_data["term2"])
    c2 = build_fraction_surd(eq2_data["constant"])
    eq2 = Equation(a2, b2, c2, var1=var1, var2=var2)

    methods = {}
    system = EquationSystem(eq1, eq2)

    renderer = SolutionLatexRenderer(var1=var1, var2=var2)
    equations = _equation_lines(eq1, eq2, var1, var2)

    elimination_solver = EliminationSolver(system)
    elimination_raw_solution = elimination_solver.solve()
    elimination_solution = {
        var1: to_python_number(elimination_raw_solution[list(elimination_raw_solution.keys())[0]]),
        var2: to_python_number(elimination_raw_solution[list(elimination_raw_solution.keys())[1]]),
    }

    elimination_steps = []
    for step in elimination_solver.recorder.get_steps():
        if step.type == "vertical_elimination":
            elimination_steps.append(
                {
                    "type": "vertical_elimination",
                    "eq1": step.content["eq1"],
                    "eq2": step.content["eq2"],
                    "result": step.content["result"],
                }
            )
        else:
            elimination_steps.append({"type": step.type, "content": step.content})

    elimination_latex = renderer.render(
        method_name="elimination",
        equations=equations,
        solution=elimination_solution,
        steps=elimination_steps,
    )

    methods["elimination"] = elimination_steps
    methods["elimination_latex"] = elimination_latex

    substitution_solver = SubstitutionSolver()
    substitution_raw = substitution_solver.solve(system)
    substitution_solution = {
        var1: to_python_number(substitution_raw[list(substitution_raw.keys())[0]]),
        var2: to_python_number(substitution_raw[list(substitution_raw.keys())[1]]),
    }
    substitution_latex = renderer.render(
        method_name="substitution",
        equations=equations,
        solution=substitution_solution,
    )
    methods["substitution_latex"] = substitution_latex

    cramer_solver = CramerSolver()
    cramer_raw = cramer_solver.solve(system)
    if isinstance(cramer_raw, str):
        cramer_solution = {var1: cramer_raw, var2: cramer_raw}
    else:
        cramer_solution = {
            var1: to_python_number(cramer_raw.get("x")),
            var2: to_python_number(cramer_raw.get("y")),
        }
    cramer_latex = renderer.render(
        method_name="cramer",
        equations=equations,
        solution=cramer_solution,
    )
    methods["cramer_latex"] = cramer_latex

    graph_solver = GraphicalSolver(system)
    points1, points2 = graph_solver.generate_tables()
    graph = {
        "equation1_points": convert_points(points1),
        "equation2_points": convert_points(points2),
        "intersection": elimination_solution,
    }

    graphical_latex = renderer.render(
        method_name="graphical",
        equations=equations,
        solution=elimination_solution,
        graph_data=graph,
    )
    methods["graphical_latex"] = graphical_latex

    _upsert_method_record(db, system_id, "elimination", elimination_latex, elimination_solution, None)
    _upsert_method_record(db, system_id, "substitution", substitution_latex, substitution_solution, None)
    _upsert_method_record(db, system_id, "cramer", cramer_latex, cramer_solution, None)
    _upsert_method_record(db, system_id, "graphical", graphical_latex, elimination_solution, graph)

    db.commit()

    return {
        "solution": elimination_solution,
        "methods": methods,
        "graph": graph,
    }
