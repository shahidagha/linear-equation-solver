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

    system = EquationSystem(eq1, eq2)
    normalizer = Normalizer()
    normalizer.normalize(system)

    method_labels = ["Elimination", "Substitution", "Cramer", "Graphical"]
    level_map = {
        "Explain": "explain",
        "Student Solution": "student",
        "Brief": "brief",
    }

    placeholder_methods = {}
    for method in method_labels:
        method_key = method.lower()
        placeholder_methods[method_key] = {}
        for level_label, level_key in level_map.items():
            placeholder_methods[method_key][level_key] = f"{method}-{level_label}"

    _upsert_method_record(
        db,
        system_id,
        "elimination",
        {
            "latex_detailed": placeholder_methods["elimination"]["explain"],
            "latex_medium": placeholder_methods["elimination"]["student"],
            "latex_short": placeholder_methods["elimination"]["brief"],
        },
        {"x": "pipeline-test", "y": "pipeline-test"},
        None,
    )
    _upsert_method_record(
        db,
        system_id,
        "substitution",
        {
            "latex_detailed": placeholder_methods["substitution"]["explain"],
            "latex_medium": placeholder_methods["substitution"]["student"],
            "latex_short": placeholder_methods["substitution"]["brief"],
        },
        {"x": "pipeline-test", "y": "pipeline-test"},
        None,
    )
    _upsert_method_record(
        db,
        system_id,
        "cramer",
        {
            "latex_detailed": placeholder_methods["cramer"]["explain"],
            "latex_medium": placeholder_methods["cramer"]["student"],
            "latex_short": placeholder_methods["cramer"]["brief"],
        },
        {"x": "pipeline-test", "y": "pipeline-test"},
        None,
    )
    _upsert_method_record(
        db,
        system_id,
        "graphical",
        {
            "latex_detailed": placeholder_methods["graphical"]["explain"],
            "latex_medium": placeholder_methods["graphical"]["student"],
            "latex_short": placeholder_methods["graphical"]["brief"],
        },
        {"x": "pipeline-test", "y": "pipeline-test"},
        {"status": "pipeline-test"},
    )

    db.commit()

    return {
        "solution": "pipeline-test",
        "method": "elimination",
        "verbosity": "student",
        "content": placeholder_methods["elimination"]["student"],
    }
