"""
Cramer's rule for 2×2 linear systems.
Step 1 (standardization) is done upstream.
Steps 2–7: identify coefficients, compute D, D_x, D_y, apply rule, state answer.
When D = 0: compute D_x and D_y to distinguish no solution (inconsistent) vs infinitely many (dependent).
"""
import sympy as sp
from backend.utils.step_recorder import StepRecorder
from backend.utils.step_roles import (
    BLOCK_INTRO,
    EXPLANATION_CALC,
    EXPLANATION_RESULT_TEXT,
    EXPLANATION_TEXT,
    STUDENT_CALC,
    STUDENT_CALC_LAST_LINE,
    STUDENT_RESULT_TEXT,
)
from backend.utils.degenerate import degenerate_none, degenerate_infinite, above_grade
from backend.utils.grade_scope import would_add_subtract_unlike_surds


def _to_sympy(value):
    return value.to_sympy() if hasattr(value, "to_sympy") else value


def _expr_latex(expr):
    return sp.latex(sp.simplify(expr))


def _wrap_if_negative(expr):
    """LaTeX for expr; wrap in parentheses only if negative."""
    e = sp.simplify(expr)
    s = sp.latex(e)
    if s.strip().startswith("-") and len(s.strip()) > 1:
        return f"\\left({s}\\right)"
    return s


class CramerSolver:
    def __init__(self, system):
        self.system = system
        self.var1 = getattr(system, "var1", "x")
        self.var2 = getattr(system, "var2", "y")
        self.recorder = StepRecorder()
        a1 = _to_sympy(system.eq1.a)
        b1 = _to_sympy(system.eq1.b)
        c1 = _to_sympy(system.eq1.c)
        a2 = _to_sympy(system.eq2.a)
        b2 = _to_sympy(system.eq2.b)
        c2 = _to_sympy(system.eq2.c)
        self._a1, self._b1, self._c1 = a1, b1, c1
        self._a2, self._b2, self._c2 = a2, b2, c2

    def solve(self):
        """Solve using Cramer's rule; record steps 2–7. Return {var1: x, var2: y} or 'No unique solution'."""
        a1, b1, c1 = self._a1, self._b1, self._c1
        a2, b2, c2 = self._a2, self._b2, self._c2

        # Step 2: Compare Equation (1) and (2) — mixed \text and math so subscripts render
        self.recorder.add_equation(
            f"\\text{{Comparing Equation (1) with }} \\; a_1 {self.var1} + b_1 {self.var2} = c_1 \\; \\text{{ we get:}}",
            role=BLOCK_INTRO,
        )
        self.recorder.add_equation(
            f"a_1 = {_expr_latex(a1)}, \\quad b_1 = {_expr_latex(b1)}, \\quad c_1 = {_expr_latex(c1)}",
            role=STUDENT_CALC,
        )
        self.recorder.add_equation(
            f"\\text{{Comparing Equation (2) with }} \\; a_2 {self.var1} + b_2 {self.var2} = c_2 \\; \\text{{ we get:}}",
            role=BLOCK_INTRO,
        )
        self.recorder.add_equation(
            f"a_2 = {_expr_latex(a2)}, \\quad b_2 = {_expr_latex(b2)}, \\quad c_2 = {_expr_latex(c2)}",
            role=STUDENT_CALC,
        )

        # Step 3: D — Teacher explanation (steps 1+3 + intro: Detailed only) + Calculation block (steps 2,4,5: Detailed + Medium)
        self.recorder.add_equation(
            "\\text{Compute } D \\text{ (determinant of coefficient matrix):}",
            role=EXPLANATION_TEXT,
        )
        # Teacher explanation (step 1): symbolic determinant — Detailed only
        self.recorder.add_equation(r"D = \begin{vmatrix} a_1 & b_1 \\ a_2 & b_2 \end{vmatrix}", role=EXPLANATION_CALC)
        # Calculation block (step 2): substitute values into matrix — Detailed + Medium
        self.recorder.add_equation(
            f"D = \\begin{{vmatrix}} {_expr_latex(a1)} & {_expr_latex(b1)} \\\\ {_expr_latex(a2)} & {_expr_latex(b2)} \\end{{vmatrix}}",
            role=STUDENT_CALC,
        )
        if would_add_subtract_unlike_surds(a1 * b2, a2 * b1):
            self.recorder.add_equation(
                "\\text{At this step we would add or subtract expressions involving surds with different radicands, "
                "which is beyond the scope of the current grade.}",
                role=EXPLANATION_TEXT,
            )
            return above_grade()
        D = sp.simplify(a1 * b2 - a2 * b1)
        # _record_det_computation: step 3 (formula) = EXPLANATION_CALC; steps 4,5 (numeric + simplify) = STUDENT_CALC
        self._record_det_computation("D", a1 * b2, a2 * b1, D, "a_1 b_2 - a_2 b_1", a1, b2, a2, b1)

        if D == 0:
            self.recorder.add_equation(
                "\\text{Since } D = 0 \\text{, the system has no unique solution.}",
                role=EXPLANATION_TEXT,
            )
            if would_add_subtract_unlike_surds(c1 * b2, c2 * b1) or would_add_subtract_unlike_surds(a1 * c2, a2 * c1):
                self.recorder.add_equation(
                    "\\text{At this step we would add or subtract expressions involving surds with different radicands, "
                    "which is beyond the scope of the current grade.}",
                    role=EXPLANATION_TEXT,
                )
                return above_grade()
            Dx = sp.simplify(c1 * b2 - c2 * b1)
            Dy = sp.simplify(a1 * c2 - a2 * c1)
            self.recorder.add_equation(
                f"\\text{{Compute }} D_{{{self.var1}}} = c_1 b_2 - c_2 b_1 = {_expr_latex(Dx)} \\text{{, }} "
                f"D_{{{self.var2}}} = a_1 c_2 - a_2 c_1 = {_expr_latex(Dy)}.",
                role=STUDENT_CALC,
            )
            if Dx != 0 or Dy != 0:
                self.recorder.add_equation(
                    "\\text{Since } D = 0 \\text{ but at least one of } D_x, D_y \\text{ is not zero, "
                    "the system is inconsistent and has no solution.}",
                    role=EXPLANATION_RESULT_TEXT,
                )
                return degenerate_none()
            self.recorder.add_equation(
                "\\text{Since } D = D_x = D_y = 0 \\text{, the equations are dependent; "
                "the system has infinitely many solutions (the same line).}",
                role=EXPLANATION_RESULT_TEXT,
            )
            return degenerate_infinite()

        # Step 4: D_x — Teacher (intro + steps 1+3) = Detailed only; Calculation (steps 2,4,5) = Medium too.
        self.recorder.add_equation(
            f"\\text{{To find }} D_{{{self.var1}}} \\text{{, in }} D \\text{{ strike out the first column }} (a_1, a_2) \\text{{; replace with }} (c_1, c_2) \\text{{:}}",
            role=EXPLANATION_TEXT,
        )
        # Teacher (step 1): symbolic D_x matrix — Detailed only
        self.recorder.add_equation(
            f"D_{{{self.var1}}} = \\begin{{vmatrix}} c_1 & b_1 \\\\ c_2 & b_2 \\end{{vmatrix}}",
            role=EXPLANATION_CALC,
        )
        # Calculation (step 2): filled matrix — Detailed + Medium
        self.recorder.add_equation(
            f"D_{{{self.var1}}} = \\begin{{vmatrix}} {_expr_latex(c1)} & {_expr_latex(b1)} \\\\ {_expr_latex(c2)} & {_expr_latex(b2)} \\end{{vmatrix}}",
            role=STUDENT_CALC,
        )
        if would_add_subtract_unlike_surds(c1 * b2, c2 * b1):
            self.recorder.add_equation(
                "\\text{At this step we would add or subtract expressions involving surds with different radicands, "
                "which is beyond the scope of the current grade.}",
                role=EXPLANATION_TEXT,
            )
            return above_grade()
        Dx = sp.simplify(c1 * b2 - c2 * b1)
        self._record_det_computation(f"D_{{{self.var1}}}", c1 * b2, c2 * b1, Dx, "c_1 b_2 - c_2 b_1", c1, b2, c2, b1)

        # Step 5: D_y — Teacher (intro + steps 1+3) = Detailed only; Calculation (steps 2,4,5) = Medium too.
        self.recorder.add(
            f"To find D for {self.var2}, in D strike out the second column (b1, b2); replace with c1, c2:",
            role=EXPLANATION_TEXT,
        )
        # Teacher (step 1): symbolic D_y matrix — Detailed only
        self.recorder.add_equation(
            f"D_{{{self.var2}}} = \\begin{{vmatrix}} a_1 & c_1 \\\\ a_2 & c_2 \\end{{vmatrix}}",
            role=EXPLANATION_CALC,
        )
        # Calculation (step 2): filled matrix — Detailed + Medium
        self.recorder.add_equation(
            f"D_{{{self.var2}}} = \\begin{{vmatrix}} {_expr_latex(a1)} & {_expr_latex(c1)} \\\\ {_expr_latex(a2)} & {_expr_latex(c2)} \\end{{vmatrix}}",
            role=STUDENT_CALC,
        )
        if would_add_subtract_unlike_surds(a1 * c2, a2 * c1):
            self.recorder.add_equation(
                "\\text{At this step we would add or subtract expressions involving surds with different radicands, "
                "which is beyond the scope of the current grade.}",
                role=EXPLANATION_TEXT,
            )
            return above_grade()
        Dy = sp.simplify(a1 * c2 - a2 * c1)
        self._record_det_computation(f"D_{{{self.var2}}}", a1 * c2, a2 * c1, Dy, "a_1 c_2 - a_2 c_1", a1, c2, a2, c1)

        # Step 6: Apply rule — var1 = Dx/D, var2 = Dy/D with all calculation steps
        self.recorder.add_equation("\\text{Apply Cramer's rule:}", role=BLOCK_INTRO)
        self._record_division_steps(self.var1, Dx, D)
        self._record_division_steps(self.var2, Dy, D)

        # Step 7: Answer is appended by the renderer via _final_answer(solution)

        return {sp.Symbol(self.var1): sp.simplify(Dx / D), sp.Symbol(self.var2): sp.simplify(Dy / D)}

    def _record_det_computation(self, label, term1, term2, result, formula, v1, v2, v3, v4):
        """Record determinant calculation: Teacher (step 3) = formula (EXPLANATION_CALC, Detailed only).
        Calculation block (steps 4,5): numeric products, simplify, therefore (STUDENT_CALC, Detailed + Medium)."""
        t1 = sp.simplify(term1)
        t2 = sp.simplify(term2)
        # Teacher explanation (step 3): general formula — Detailed only
        self.recorder.add_equation(f"{label} = {formula}", role=EXPLANATION_CALC)
        # Calculation (step 4): substitute values with brackets for negatives — Detailed + Medium
        p1 = _wrap_if_negative(v1)
        p2 = _wrap_if_negative(v2)
        p3 = _wrap_if_negative(v3)
        p4 = _wrap_if_negative(v4)
        self.recorder.add_equation(f"{label} = {p1} \\times {p2} - {p3} \\times {p4}", role=STUDENT_CALC)
        sub1 = _wrap_if_negative(t1)
        sub2 = _wrap_if_negative(t2)
        self.recorder.add_equation(f"= {sub1} - {sub2}", role=STUDENT_CALC)
        t2_latex = sp.latex(sp.simplify(t2))
        t2_is_negative = t2_latex.strip().startswith("-") and len(t2_latex.strip()) > 1
        if t2_is_negative:
            t2_neg = sp.simplify(-t2)
            self.recorder.add_equation(f"= {_expr_latex(t1)} + {_expr_latex(t2_neg)}", role=STUDENT_CALC)
        self.recorder.add_equation(f"\\therefore {label} = {_expr_latex(result)}", role=STUDENT_CALC_LAST_LINE)

    def _record_division_steps(self, var_name, num, den):
        """Record var = num/den with all calculation steps (show fraction, then simplify if needed)."""
        self.recorder.add_equation(
            f"{var_name} = \\frac{{D_{{{var_name}}}}}{{D}} = \\frac{{{_expr_latex(num)}}}{{{_expr_latex(den)}}}",
            role=STUDENT_CALC,
        )
        value = sp.simplify(num / den)
        try:
            n, d = int(num), int(den)
            frac_display = sp.Mul(n, sp.Pow(d, -1, evaluate=False), evaluate=False)
            if sp.simplify(frac_display) != value:
                self.recorder.add_equation(f"{var_name} = {sp.latex(frac_display)}", role=STUDENT_CALC)
        except (TypeError, ValueError):
            pass
        self.recorder.add_equation(f"{var_name} = {_expr_latex(value)}", role=STUDENT_RESULT_TEXT)
