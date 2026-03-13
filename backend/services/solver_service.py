from sqlalchemy.orm import Session

from backend.math_engine.equation import Equation
from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.system import EquationSystem
from backend.models.solution_methods import SolutionMethod
from backend.normalization.equation_standardizer import EquationStandardizer
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

    def normalize_sign(value) -> int:
        """Normalize frontend sign payloads to +1 / -1."""

        if value is None:
            return 1

        # Support UI glyph variants such as U+2212 (−).
        text = str(value).strip().replace("−", "-")
        if text in {"-", "-1"}:
            return -1

        try:
            return -1 if int(text) < 0 else 1
        except (TypeError, ValueError):
            return 1

    sign = term.get("sign", 1)
    num_coeff = safe_int(term.get("numCoeff", 1))
    num_rad = safe_int(term.get("numRad", 1))
    den_coeff = safe_int(term.get("denCoeff", 1))
    den_rad = safe_int(term.get("denRad", 1))

    # normalize sign
    sign = normalize_sign(sign)

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

    return record


def _normalize_cramer_solution(raw_solution, var1: str, var2: str):
    if isinstance(raw_solution, dict):
        if var1 in raw_solution and var2 in raw_solution:
            return raw_solution
        if "x" in raw_solution and "y" in raw_solution:
            return {var1: raw_solution["x"], var2: raw_solution["y"]}
    return raw_solution


def _no_unique_solution(var1: str, var2: str):
    value = "No unique solution"
    return {var1: value, var2: value}


def _normalize_method_solution(raw_solution, var1: str, var2: str):
    if raw_solution == "No unique solution":
        return _no_unique_solution(var1, var2)

    if raw_solution == []:
        return _no_unique_solution(var1, var2)

    return _normalize_solution_map(raw_solution, var1, var2)


def _serialize_steps(steps):
    serialized = []
    for step in steps:
        if step.type == "vertical_elimination":
            serialized.append(
                {
                    "type": step.type,
                    "eq1": step.content.get("eq1"),
                    "eq2": step.content.get("eq2"),
                    "result": step.content.get("result"),
                }
            )
        else:
            serialized.append({"type": step.type, "content": str(step.content)})
    return serialized


def _normalize_eq_for_compare(s: str) -> str:
    """Normalize equation string for step comparison (strip, collapse spaces)."""
    if not s:
        return ""
    return " ".join(str(s).strip().split())


def _standardization_steps_for_equation(steps, number: int):
    """Convert EquationStandardizer steps into renderer-friendly step dicts.
    A step is rendered only when its result differs from the previous step
    (so step N is shown only if result_N != result_{N-1}).
    When the raw equation is already in standard form, it is shown only once.
    """
    out = []
    # Plain label for use inside text sentences, and LaTeX label for equation lines
    label_plain = f"({number})"
    label_eq = f"\\\\quad \\\\dots ({number})"
    last_shown = None  # last equation string we emitted (without label)
    steps_list = list(steps)

    for i, step in enumerate(steps_list):
        s_type = step.get("type")

        if s_type == "write_equation":
            eq = step.get("equation", "")
            if not eq:
                continue
            # If already in standard form, show equation only once (skip redundant rearrange)
            std_result = None
            for j in range(i + 1, len(steps_list)):
                if steps_list[j].get("type") == "rearrange_standard_form":
                    std_result = steps_list[j].get("result")
                    break
            if std_result is not None and _normalize_eq_for_compare(eq) == _normalize_eq_for_compare(std_result):
                out.append({"type": "equation", "content": f"{std_result}{label_eq}"})
                last_shown = _normalize_eq_for_compare(std_result)
            else:
                # Use std_result (LaTeX) when available so equation (1) renders properly below Given block
                content_eq = std_result if std_result is not None else eq
                out.append({"type": "equation", "content": f"{content_eq}{label_eq}"})
                last_shown = _normalize_eq_for_compare(content_eq)

        elif s_type == "rearrange_standard_form":
            result = step.get("result", "")
            if result and _normalize_eq_for_compare(result) != last_shown:
                out.append({"type": "equation", "content": f"{result}{label_eq}"})
                last_shown = _normalize_eq_for_compare(result)

        elif s_type == "make_leading_positive":
            # Only show when we actually applied (multiply by -1); skip "already positive"
            if step.get("multiplied_by") is not None:
                out.append(
                    {
                        "type": "text",
                        "content": f"Multiply equation {label_plain} by -1 to make the leading coefficient positive.",
                    }
                )
            # When applied, we don't have a new equation string here; next step will

        elif s_type == "remove_denominator":
            multiplier = step.get("multiplier")
            result = step.get("result", "")
            result_norm = _normalize_eq_for_compare(result)
            if result and result_norm != last_shown:
                if multiplier:
                    out.append(
                        {
                            "type": "text",
                            "content": f"Multiply equation {label_plain} by {multiplier} to remove denominators.",
                        }
                    )
                out.append({"type": "equation", "content": f"{result}{label_eq}"})
                last_shown = result_norm

        elif s_type == "reduce_equation":
            divisor = step.get("divisor")
            result = step.get("result", "")
            result_norm = _normalize_eq_for_compare(result)
            if result and result_norm != last_shown:
                if divisor:
                    out.append(
                        {
                            "type": "text",
                            "content": f"Divide equation {label_plain} by {divisor} to simplify coefficients.",
                        }
                    )
                out.append({"type": "equation", "content": f"{result}{label_eq}"})
                last_shown = result_norm

        elif s_type == "assign_equation_number":
            continue

    return out


def _standardization_steps_combined(standardization: dict):
    """Build a single ordered step list for both equations."""
    steps_eq1 = standardization.get("steps_eq1") or []
    steps_eq2 = standardization.get("steps_eq2") or []

    combined = []
    combined.extend(_standardization_steps_for_equation(steps_eq1, 1))
    combined.extend(_standardization_steps_for_equation(steps_eq2, 2))
    return combined


def solve_system(db: Session, system_id: int, payload: dict):
    var1 = payload["variables"][0]
    var2 = payload["variables"][1]

    eq1_data = payload["equation1"]
    eq2_data = payload["equation2"]

    a1 = build_fraction_surd(eq1_data["terms"][0])
    b1 = build_fraction_surd(eq1_data["terms"][1])
    c1 = build_fraction_surd(eq1_data["constant"])
    eq1 = Equation(a1, b1, c1)

    a2 = build_fraction_surd(eq2_data["terms"][0])
    b2 = build_fraction_surd(eq2_data["terms"][1])
    c2 = build_fraction_surd(eq2_data["constant"])
    eq2 = Equation(a2, b2, c2)

    system = EquationSystem(eq1, eq2, var1=var1, var2=var2)

    raw_equations = [
        payload.get("equation1_raw") or EquationFormatter.format_equation(eq1.a.to_sympy(), eq1.b.to_sympy(), eq1.c.to_sympy(), var1, var2),
        payload.get("equation2_raw") or EquationFormatter.format_equation(eq2.a.to_sympy(), eq2.b.to_sympy(), eq2.c.to_sympy(), var1, var2),
    ]

    standardization = EquationStandardizer().standardize(system, raw_equations=raw_equations)
    standardized_system = standardization["system"]
    standardization_steps = _standardization_steps_combined(standardization)

    elimination_solver = EliminationSolver(standardized_system)
    elimination_raw = elimination_solver.solve()
    elimination_method_steps = _serialize_steps(elimination_solver.recorder.get_steps())
    elimination_steps = standardization_steps + elimination_method_steps
    elimination_solution = _normalize_method_solution(elimination_raw, var1, var2)

    substitution_solver = SubstitutionSolver()
    substitution_raw = substitution_solver.solve(standardized_system)
    substitution_solution = _normalize_method_solution(substitution_raw, var1, var2)

    cramer_solver = CramerSolver()
    cramer_raw = _normalize_cramer_solution(cramer_solver.solve(standardized_system), var1, var2)
    cramer_solution = _normalize_method_solution(cramer_raw, var1, var2)

    graphical_solver = GraphicalSolver(standardized_system)
    points1, points2 = graphical_solver.generate_tables()
    graph_data = {
        "equation1_points": convert_points(points1),
        "equation2_points": convert_points(points2),
        "intersection": {
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
    }

    equations = _equation_lines(standardized_system.eq1, standardized_system.eq2, var1, var2)
    renderer = SolutionLatexRenderer(var1=var1, var2=var2)

    elimination_latex = renderer.render(
        method_name="elimination",
        equations=equations,
        raw_equations=raw_equations,
        solution={
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
        steps=elimination_steps,
    )
    substitution_latex = renderer.render(
        method_name="substitution",
        equations=equations,
        raw_equations=raw_equations,
        solution={
            var1: to_python_number(substitution_solution[var1]),
            var2: to_python_number(substitution_solution[var2]),
        },
    )
    cramer_latex = renderer.render(
        method_name="cramer",
        equations=equations,
        raw_equations=raw_equations,
        solution={
            var1: to_python_number(cramer_solution[var1]),
            var2: to_python_number(cramer_solution[var2]),
        },
    )
    graphical_latex = renderer.render(
        method_name="graphical",
        equations=equations,
        raw_equations=raw_equations,
        solution={
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
        graph_data=graph_data,
    )

    elimination_record = _upsert_method_record(
        db,
        system_id,
        "elimination",
        {
            "latex_detailed": elimination_latex["latex_detailed"],
            "latex_medium": elimination_latex["latex_medium"],
            "latex_short": elimination_latex["latex_short"],
        },
        {
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
        None,
    )
    substitution_record = _upsert_method_record(
        db,
        system_id,
        "substitution",
        {
            "latex_detailed": substitution_latex["latex_detailed"],
            "latex_medium": substitution_latex["latex_medium"],
            "latex_short": substitution_latex["latex_short"],
        },
        {
            var1: to_python_number(substitution_solution[var1]),
            var2: to_python_number(substitution_solution[var2]),
        },
        None,
    )
    cramer_record = _upsert_method_record(
        db,
        system_id,
        "cramer",
        {
            "latex_detailed": cramer_latex["latex_detailed"],
            "latex_medium": cramer_latex["latex_medium"],
            "latex_short": cramer_latex["latex_short"],
        },
        {
            var1: to_python_number(cramer_solution[var1]),
            var2: to_python_number(cramer_solution[var2]),
        },
        None,
    )
    graphical_record = _upsert_method_record(
        db,
        system_id,
        "graphical",
        {
            "latex_detailed": graphical_latex["latex_detailed"],
            "latex_medium": graphical_latex["latex_medium"],
            "latex_short": graphical_latex["latex_short"],
        },
        {
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
        graph_data,
    )

    db.commit()
    db.refresh(elimination_record)
    db.refresh(substitution_record)
    db.refresh(cramer_record)
    db.refresh(graphical_record)

    return {
        "solution": {
            var1: to_python_number(elimination_solution[var1]),
            var2: to_python_number(elimination_solution[var2]),
        },
        "methods": {
            "elimination_latex": {
                "latex_detailed": elimination_record.latex_detailed,
                "latex_medium": elimination_record.latex_medium,
                "latex_short": elimination_record.latex_short,
            },
            "substitution_latex": {
                "latex_detailed": substitution_record.latex_detailed,
                "latex_medium": substitution_record.latex_medium,
                "latex_short": substitution_record.latex_short,
            },
            "cramer_latex": {
                "latex_detailed": cramer_record.latex_detailed,
                "latex_medium": cramer_record.latex_medium,
                "latex_short": cramer_record.latex_short,
            },
            "graphical_latex": {
                "latex_detailed": graphical_record.latex_detailed,
                "latex_medium": graphical_record.latex_medium,
                "latex_short": graphical_record.latex_short,
            },
        },
        "graph": graph_data,
    }
