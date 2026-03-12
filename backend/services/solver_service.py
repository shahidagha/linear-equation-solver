from sqlalchemy.orm import Session

from backend.math_engine.equation import Equation
from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.system import EquationSystem
from backend.models.solution_methods import SolutionMethod
from backend.normalization.normalizer import Normalizer
from backend.solver.elimination_solver import EliminationSolver
from backend.solver.graphical_solver import GraphicalSolver
from backend.solver.substitution_solver import SubstitutionSolver
from backend.solver.cramer_solver import CramerSolver
from backend.latex.equation_formatter import EquationFormatter
from backend.latex.solution_renderer import SolutionLatexRenderer
import sympy as sp


def build_fraction_surd(term: dict):
    """Convert frontend term JSON into FractionSurd object."""

    # helper to safely convert values
    def safe_int(value, default=1):
        if value in ["", "+", "++", None]:
            return default
        if value == "-":
            return -1
        return int(value)

    sign = term.get("sign", 1)
    num_coeff = safe_int(term.get("numCoeff", 1))
    num_rad = safe_int(term.get("numRad", 1))
    den_coeff = safe_int(term.get("denCoeff", 1))
    den_rad = safe_int(term.get("denRad", 1))

    # normalize sign
    sign = -1 if str(sign).strip() == "-" else 1

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


def _normalize_solution_map(raw_solution, var1: str, var2: str) -> dict:
    """Normalize solver outputs to a stable {var1: value, var2: value} mapping."""

    sym_var1 = sp.Symbol(var1)
    sym_var2 = sp.Symbol(var2)

    if isinstance(raw_solution, dict):
        if sym_var1 in raw_solution and sym_var2 in raw_solution:
            return {var1: raw_solution[sym_var1], var2: raw_solution[sym_var2]}
        if var1 in raw_solution and var2 in raw_solution:
            return {var1: raw_solution[var1], var2: raw_solution[var2]}

    if isinstance(raw_solution, list) and raw_solution:
        # SymPy may return a flat list like [x_value, y_value].
        if len(raw_solution) >= 2 and not isinstance(raw_solution[0], (dict, tuple, list)):
            return {var1: raw_solution[0], var2: raw_solution[1]}

        first = raw_solution[0]
        if isinstance(first, dict):
            return _normalize_solution_map(first, var1, var2)
        if isinstance(first, (tuple, list)) and len(first) >= 2:
            return {var1: first[0], var2: first[1]}

    if isinstance(raw_solution, tuple) and len(raw_solution) >= 2:
        return {var1: raw_solution[0], var2: raw_solution[1]}

    if raw_solution == []:
        # SymPy returns [] when no unique solution exists.
        no_unique = "No unique solution"
        return {var1: no_unique, var2: no_unique}

    raise ValueError(f"Unsupported solver output format: {type(raw_solution).__name__}")


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
    var1 = payload["variables"][0]
    var2 = payload["variables"][1]

    eq1_data = payload["equation1"]
    eq2_data = payload["equation2"]

    a1 = build_fraction_surd(eq1_data["terms"][0])
    b1 = build_fraction_surd(eq1_data["terms"][1])
    c1 = build_fraction_surd(eq1_data["constant"])
    eq1 = Equation(a1, b1, c1, var1=var1, var2=var2)

    a2 = build_fraction_surd(eq2_data["terms"][0])
    b2 = build_fraction_surd(eq2_data["terms"][1])
    c2 = build_fraction_surd(eq2_data["constant"])
    eq2 = Equation(a2, b2, c2, var1=var1, var2=var2)

    methods = {}
    system = EquationSystem(eq1, eq2)

    normalizer = Normalizer()
    system = normalizer.normalize(system)

    renderer = SolutionLatexRenderer(var1=var1, var2=var2)
    equations = _equation_lines(system.eq1, system.eq2, var1, var2)

    elimination_solver = EliminationSolver(system)
    elimination_raw_solution = elimination_solver.solve()
    elimination_map = _normalize_solution_map(elimination_raw_solution, var1, var2)
    elimination_solution = {
        var1: to_python_number(elimination_map[var1]),
        var2: to_python_number(elimination_map[var2]),
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
    substitution_map = _normalize_solution_map(substitution_raw, var1, var2)
    substitution_solution = {
        var1: to_python_number(substitution_map[var1]),
        var2: to_python_number(substitution_map[var2]),
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
