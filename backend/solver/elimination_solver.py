import sympy as sp
from backend.utils.step_recorder import StepRecorder
from backend.utils.step_roles import (
    BLOCK_INTRO,
    EXPLANATION_RESULT_TEXT,
    EXPLANATION_TEXT,
    STUDENT_CALC,
    STUDENT_CALC_LAST_LINE,
)
from backend.utils.back_substitute_block import back_substitute, get_visible_steps as get_visible_back_sub_steps
from backend.utils.degenerate import degenerate_none, degenerate_infinite, above_grade
from backend.utils.solve_for_var_block import (
    get_visible_steps as get_visible_solve_steps,
    solve_coeff_var_equals_constant,
)
from backend.utils.grade_scope import would_add_subtract_unlike_surds
from backend.latex.equation_formatter import EquationFormatter


class EliminationSolver:

    def __init__(self, system):

        self.system = system
        self.eq1 = system.eq1
        self.eq2 = system.eq2

        # Records only elimination‑specific steps.
        # Standardization and equation numbering are handled upstream
        # by EquationStandardizer and the LaTeX renderer.
        self.recorder = StepRecorder()

    # -----------------------------
    # vertical elimination display
    # -----------------------------

    def vertical_elimination(self, eq1, eq2, result, op=None):
        """op: 'add' or 'subtract' so the layout shows + or − and underset only for subtract."""
        self.recorder.add_vertical(eq1, eq2, result, op=op, role=STUDENT_CALC)

    def _record_and_return_degenerate(self, eq_line1, eq_line2, C, op):
        """Record 0 = C or 0 = 0, add conclusion step, return degenerate_none() or degenerate_infinite()."""
        C = sp.simplify(C)
        if C == 0:
            result_line = "0 = 0"
        else:
            result_line = f"0 = {sp.latex(C)}"
        self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
        self.recorder.add_equation(result_line, role=STUDENT_CALC_LAST_LINE)
        if C == 0:
            self.recorder.add_equation(
                "\\text{We get } 0 = 0 \\text{; the equations are dependent — infinitely many solutions.}",
                role=EXPLANATION_RESULT_TEXT,
            )
            return degenerate_infinite()
        self.recorder.add_equation(
            "\\text{We get } 0 = k \\text{ with } k \\neq 0 \\text{ — the system has no solution (inconsistent).}",
            role=EXPLANATION_RESULT_TEXT,
        )
        return degenerate_none()

    @staticmethod
    def _term(coeff, var):

        coeff = sp.simplify(coeff)

        if coeff == 1:
            return var

        if coeff == -1:
            return f"-{var}"

        return f"{sp.latex(coeff)}{var}"

    # -----------------------------
    # like‑surd guard: at add/subtract step, unlike surds → above grade
    # -----------------------------

    def _check_like_surds_and_maybe_above_grade(self, a1, b1, c1, a2, b2, c2):
        """If any pair (a1,a2), (b1,b2), (c1,c2) would add/subtract unlike surds, record step and return above_grade()."""
        if would_add_subtract_unlike_surds(a1, a2) or would_add_subtract_unlike_surds(b1, b2) or would_add_subtract_unlike_surds(c1, c2):
            self.recorder.add_equation(
                "\\text{At this step we would add or subtract expressions involving surds with different radicands, "
                "which is beyond the scope of the current grade.}",
                role=EXPLANATION_TEXT,
            )
            return above_grade()
        return None

    # -----------------------------
    # strategy detection
    # -----------------------------

    def detect_strategy(self):

        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()

        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()

        # DIRECT when matching columns
        if abs(b1) == abs(b2) or abs(a1) == abs(a2):
            return "DIRECT"

        # CROSS only when DIRECT is not applicable
        if abs(a1) == abs(b2) and abs(a2) == abs(b1) and sp.sign(b1) == sp.sign(b2):
            return "CROSS"

        return "LCM"

    # -----------------------------
    # variable selection
    # -----------------------------

    def choose_variable(self):

        a1 = abs(self.eq1.a.to_sympy())
        a2 = abs(self.eq2.a.to_sympy())

        b1 = abs(self.eq1.b.to_sympy())
        b2 = abs(self.eq2.b.to_sympy())

        lcm_x = sp.lcm(a1, a2)
        lcm_y = sp.lcm(b1, b2)

        mx1 = lcm_x / a1
        mx2 = lcm_x / a2

        my1 = lcm_y / b1
        my2 = lcm_y / b2

        x_steps = (mx1 != 1) + (mx2 != 1)
        y_steps = (my1 != 1) + (my2 != 1)

        if y_steps < x_steps:
            return "y"

        if x_steps < y_steps:
            return "x"

        return "y"

    # -----------------------------
    # final substitution helper (SECTION 5)
    # -----------------------------

    def _record_solve_one_var_after_elimination(self, coeff, constant, var_name):
        """Record steps from coeff*var = constant to var = value (skip equation step; already shown)."""
        steps = solve_coeff_var_equals_constant(coeff, constant, var_name)
        for s in get_visible_solve_steps(steps):
            if s["type"] != "equation":
                self.recorder.add_equation(s["latex"])

    def _choose_substitution_equation(self):
        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()
        c1 = self.eq1.c.to_sympy()

        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()
        c2 = self.eq2.c.to_sympy()

        candidates = [(a1, b1, c1, 1), (a2, b2, c2, 2)]
        best = None
        for a, b, c, idx in candidates:
            if a > 0 and b > 0:
                score = abs(a) + abs(b)
                if best is None or score < best[0]:
                    best = (score, a, b, c, idx)

        if best is None:
            return a1, b1, c1, 1

        _, a, b, c, idx = best
        return a, b, c, idx

    def _substitute_x(self, x_value):
        a, b, c, idx = self._choose_substitution_equation()
        var2 = getattr(self.system, "var2", "y")

        x_latex = sp.latex(x_value)
        short = f"Substitute x = {x_latex} in equation ({idx})"
        detailed = (
            f"We substitute x = {x_latex} into equation ({idx}) because equation ({idx}) "
            "has the simpler coefficients (smaller sum of coefficients), so the arithmetic for finding y is easier."
        )
        content_latex = (
            f"\\text{{Substitute }} x = {x_latex} \\text{{ in equation ({idx})}}"
        )
        detailed_latex = (
            f"\\text{{We substitute }} x = {x_latex} \\text{{ into equation ({idx}) because equation ({idx}) "
            "has the simpler coefficients (smaller sum of coefficients), so the arithmetic for finding y is easier.}"
        )
        self.recorder.add(
            {"short": short, "detailed": detailed, "content_latex": content_latex, "detailed_latex": detailed_latex},
            role=BLOCK_INTRO,
        )

        steps = back_substitute(a, b, c, "x", x_value, var2, eq_num=idx)
        visible = get_visible_back_sub_steps(steps)
        for s in visible:
            if s["type"] != "intro":
                self.recorder.add_equation(s["latex"])

        y_value = sp.simplify((c - a * x_value) / b)
        return y_value

    def _substitute_y(self, y_value):
        a, b, c, idx = self._choose_substitution_equation()
        var1 = getattr(self.system, "var1", "x")

        y_latex = sp.latex(y_value)
        short = f"Substitute y = {y_latex} in equation ({idx})"
        detailed = (
            f"We substitute y = {y_latex} into equation ({idx}) because equation ({idx}) "
            "has the simpler coefficients (smaller sum of coefficients), so the arithmetic for finding x is easier."
        )
        content_latex = (
            f"\\text{{Substitute }} y = {y_latex} \\text{{ in equation ({idx})}}"
        )
        detailed_latex = (
            f"\\text{{We substitute }} y = {y_latex} \\text{{ into equation ({idx}) because equation ({idx}) "
            "has the simpler coefficients (smaller sum of coefficients), so the arithmetic for finding x is easier.}"
        )
        self.recorder.add(
            {"short": short, "detailed": detailed, "content_latex": content_latex, "detailed_latex": detailed_latex},
            role=BLOCK_INTRO,
        )

        steps = back_substitute(a, b, c, "y", y_value, var1, eq_num=idx)
        visible = get_visible_back_sub_steps(steps)
        for s in visible:
            if s["type"] != "intro":
                self.recorder.add_equation(s["latex"])

        x_value = sp.simplify((c - b * y_value) / a)
        return x_value

    # -----------------------------
    # DIRECT strategy (SECTION 2)
    # -----------------------------

    def _solve_direct(self, a1, b1, c1, a2, b2, c2):
        var1 = getattr(self.system, "var1", "x")
        var2 = getattr(self.system, "var2", "y")
        if abs(b1) == abs(b2):
            eliminate = "y"
        else:
            eliminate = "x"

        if eliminate == "y":
            self.recorder.add_equation(
                f"\\text{{Using Direct Elimination on }} {var2} \\text{{ (}}|b_1| = |b_2|\\text{{)}}",
                role=EXPLANATION_TEXT,
            )
            if sp.sign(b1) != sp.sign(b2):
                self.recorder.add(
                    {
                        "detailed": f"Adding equations (coefficients of {var2} have opposite signs)",
                        "medium": "Adding equations (1) and (2)",
                        "detailed_latex": f"\\text{{Adding equations (coefficients of }} {var2} \\text{{ have opposite signs)}}",
                        "medium_latex": "\\text{Adding equations (1) and (2)}",
                    },
                    role=STUDENT_CALC,
                )
                result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                if result is not None:
                    return result
                A = a1 + a2
                C = c1 + c2
            else:
                if a1 > a2:
                    self.recorder.add_equation("\\text{Subtracting equations } (1) - (2)")
                    result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                    if result is not None:
                        return result
                    A = a1 - a2
                    C = c1 - c2
                else:
                    self.recorder.add_equation("\\text{Subtracting equations } (2) - (1)")
                    result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                    if result is not None:
                        return result
                    A = a2 - a1
                    C = c2 - c1

            op = "add" if sp.sign(b1) != sp.sign(b2) else "subtract"
            eq_line1 = EquationFormatter.format_equation(a1, b1, c1, var1, var2)
            eq_line2 = EquationFormatter.format_equation(a2, b2, c2, var1, var2)
            if A == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            # Use _term so coefficient 1 is hidden in the result line.
            x_term = self._term(A, var1)
            result_line = f"{x_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(A, C, var1)

            x_value = sp.simplify(C / A)
            self._substitute_x(x_value)
        else:
            self.recorder.add_equation(
                f"\\text{{Using Direct Elimination on }} {var1} \\text{{ (}}|a_1| = |a_2|\\text{{)}}",
                role=EXPLANATION_TEXT,
            )
            if sp.sign(a1) != sp.sign(a2):
                self.recorder.add(
                    {
                        "detailed": f"Adding equations (coefficients of {var1} have opposite signs)",
                        "medium": "Adding equations (1) and (2)",
                        "detailed_latex": f"\\text{{Adding equations (coefficients of }} {var1} \\text{{ have opposite signs)}}",
                        "medium_latex": "\\text{Adding equations (1) and (2)}",
                    },
                    role=STUDENT_CALC,
                )
                result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                if result is not None:
                    return result
                B = b1 + b2
                C = c1 + c2
            else:
                if b1 > b2:
                    self.recorder.add_equation("\\text{Subtracting equations } (1) - (2)")
                    result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                    if result is not None:
                        return result
                    B = b1 - b2
                    C = c1 - c2
                else:
                    self.recorder.add_equation("\\text{Subtracting equations } (2) - (1)")
                    result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
                    if result is not None:
                        return result
                    B = b2 - b1
                    C = c2 - c1

            op = "add" if sp.sign(a1) != sp.sign(a2) else "subtract"
            eq_line1 = EquationFormatter.format_equation(a1, b1, c1, var1, var2)
            eq_line2 = EquationFormatter.format_equation(a2, b2, c2, var1, var2)
            if B == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            y_term = self._term(B, var2)
            result_line = f"{y_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(B, C, var2)

            y_value = sp.simplify(C / B)
            self._substitute_y(y_value)

    # -----------------------------
    # CROSS strategy (SECTION 3)
    # -----------------------------

    def _solve_cross(self, a1, b1, c1, a2, b2, c2):
        self.recorder.add_equation("\\text{Using Six Step Method.}")

        # Step 1: add (1) and (2)
        result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
        if result is not None:
            return result

        a3 = a1 + a2
        b3 = b1 + b2
        c3 = c1 + c2
        var1 = getattr(self.system, "var1", "x")
        var2 = getattr(self.system, "var2", "y")

        self.recorder.add_equation("\\text{Adding equations (1) and (2)}")
        eq1_line = EquationFormatter.format_equation(a1, b1, c1, var1, var2)
        eq2_line = EquationFormatter.format_equation(a2, b2, c2, var1, var2)
        eq3_line = EquationFormatter.format_equation(a3, b3, c3, var1, var2)
        self.vertical_elimination(eq1_line, eq2_line, eq3_line, op="add")
        # Step (4) suppressed: no separate equation (3) line, no old divide text

        # Step (5): divide message (detailed / medium; short blank). Divisor for (3) is a3.
        divisor = a3
        var1 = getattr(self.system, "var1", "x")
        var2 = getattr(self.system, "var2", "y")
        self.recorder.add({
            "detailed": (
                f"Divide this equation by {sp.latex(divisor)} so that coefficient of x and y becomes ±1 (x ± y = m)."
            ),
            "medium": f"Divide the equation by {sp.latex(divisor)}, we get,",
            "detailed_latex": (
                f"\\text{{Divide this equation by }} {sp.latex(divisor)} \\text{{ so that coefficient of }} "
                f"{var1} \\text{{ and }} {var2} \\text{{ becomes }} \\pm 1 \\text{{ (}} {var1} \\pm {var2} = m \\text{{).}}"
            ),
            "medium_latex": f"\\text{{Divide the equation by }} {sp.latex(divisor)} \\text{{, we get,}}",
        })
        # Step (6): reduced equation (3) with number
        m = sp.simplify(c3 / a3)
        coeff_y3 = sp.simplify(b3 / a3)
        eq3_reduced = EquationFormatter.format_equation(
            sp.Integer(1), coeff_y3, m, var1, var2
        )
        self.recorder.add_equation(f"{eq3_reduced}\\; ...(3)")

        # Step 3: subtract equations according to a1, a2
        if a1 > a2:
            self.recorder.add_equation("\\text{Subtracting equation (2) from (1)}")
            result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
            if result is not None:
                return result
            a4 = a1 - a2
            b4 = b1 - b2
            c4 = c1 - c2
        else:
            self.recorder.add_equation("\\text{Subtracting equation (1) from (2)}")
            result = self._check_like_surds_and_maybe_above_grade(a1, b1, c1, a2, b2, c2)
            if result is not None:
                return result
            a4 = a2 - a1
            b4 = b2 - b1
            c4 = c2 - c1

        eq1_line = EquationFormatter.format_equation(a1, b1, c1, var1, var2)
        eq2_line = EquationFormatter.format_equation(a2, b2, c2, var1, var2)
        eq4_line = EquationFormatter.format_equation(a4, b4, c4, var1, var2)
        self.vertical_elimination(eq1_line, eq2_line, eq4_line, op="subtract")

        # Step (9): divide equation (4) — structured detailed/medium
        divisor = a4
        self.recorder.add({
            "detailed": (
                f"Divide this equation by {sp.latex(divisor)} so that coefficient of x and y becomes ±1 (x ∓ y = n)."
            ),
            "medium": f"Divide the equation by {sp.latex(divisor)}, we get,",
            "detailed_latex": (
                f"\\text{{Divide this equation by }} {sp.latex(divisor)} \\text{{ so that coefficient of }} "
                f"{var1} \\text{{ and }} {var2} \\text{{ becomes }} \\pm 1 \\text{{ (}} {var1} \\mp {var2} = n \\text{{).}}"
            ),
            "medium_latex": f"\\text{{Divide the equation by }} {sp.latex(divisor)} \\text{{, we get,}}",
        })
        # Step (10): reduced equation (4) with label
        n = sp.simplify(c4 / a4)
        coeff_y4 = sp.simplify(b4 / a4)
        eq4_reduced = EquationFormatter.format_equation(
            sp.Integer(1), coeff_y4, n, var1, var2
        )
        self.recorder.add_equation(f"{eq4_reduced}\\; ...(4)")

        # Step (11): blank for medium and short (detailed only)
        self.recorder.add({
            "detailed": "Add equations (3) and (4) to eliminate y and obtain 2x = m + n.",
            "medium": "",
            "short": "",
        })

        # Normalize (3) and (4) to form x ± y = m and x ∓ y = n (divide by x-coefficient)
        m = sp.simplify(c3 / a3)
        coeff_y3 = sp.simplify(b3 / a3)
        eq3_norm = EquationFormatter.format_equation(
            sp.Integer(1), coeff_y3, m, var1, var2
        )
        eq4_norm = EquationFormatter.format_equation(
            sp.Integer(1), coeff_y4, n, var1, var2
        )

        self.recorder.add_operation("Adding equations (3) and (4)")
        result_rhs = sp.simplify(m + n)
        result_line = f"{self._term(sp.Integer(2), var1)} = {sp.latex(result_rhs)}"
        self.vertical_elimination(eq3_norm, eq4_norm, result_line, op="add")
        self.recorder.add_equation(result_line)
        self._record_solve_one_var_after_elimination(sp.Integer(2), result_rhs, var1)

        x_value = sp.simplify(result_rhs / 2)
        self._substitute_x(x_value)

    # -----------------------------
    # LCM strategy (SECTION 4)
    # -----------------------------

    def _solve_lcm(self, a1, b1, c1, a2, b2, c2):
        var1 = getattr(self.system, "var1", "x")
        var2 = getattr(self.system, "var2", "y")
        # Equation (1) and (2) come from the standardization phase.
        # Track the current equation numbers for each row and auto‑increment
        # when we create new scaled equations.
        next_eq_number = 3
        current_eq_no1 = 1
        current_eq_no2 = 2

        def _record_scaled_equation(current_no: int, A, B, C, mult, next_no: int):
            """
            Record the scaled equation with a new equation number when a non‑trivial
            multiplier has been applied, and return updated (current_no, next_no).
            """
            if mult == 1:
                return current_no, next_no

            eq_line = EquationFormatter.format_equation(A, B, C, var1, var2)
            numbered = f"{eq_line}\\; ...({next_no})"
            self.recorder.add_equation(numbered)
            return next_no, next_no + 1
        # Step 1: |b1| = 1 or |b2| = 1 → eliminate y
        if abs(b1) == 1 or abs(b2) == 1:
            if abs(b1) == 1:
                mult1 = abs(b2)
                mult2 = 1
                self.recorder.add(
                    f"Using LCM Elimination strategy: in equation (1) the coefficient of y is "
                    f"{sp.latex(b1)} and in equation (2) it is {sp.latex(b2)}. Because equation (1) "
                    f"already has coefficient 1, we multiply equation (1) by {sp.latex(mult1)} so that "
                    f"both y–coefficients become {sp.latex(abs(b2))} and will cancel when we combine "
                    "the equations."
                )
                self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
            else:
                mult1 = 1
                mult2 = abs(b1)
                self.recorder.add(
                    f"Using LCM Elimination strategy: in equation (1) the coefficient of y is "
                    f"{sp.latex(b1)} and in equation (2) it is {sp.latex(b2)}. Because equation (2) "
                    f"already has coefficient 1, we multiply equation (2) by {sp.latex(mult2)} so that "
                    f"both y–coefficients become {sp.latex(abs(b1))} and will cancel when we combine "
                    "the equations."
                )
                self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")

            A1 = a1 * mult1
            B1 = b1 * mult1
            C1 = c1 * mult1

            A2 = a2 * mult2
            B2 = b2 * mult2
            C2 = c2 * mult2
            # Record any new scaled equations with fresh equation numbers and keep
            # track of which equation numbers we are now combining.
            current_eq_no1, next_eq_number = _record_scaled_equation(current_eq_no1, A1, B1, C1, mult1, next_eq_number)
            current_eq_no2, next_eq_number = _record_scaled_equation(current_eq_no2, A2, B2, C2, mult2, next_eq_number)

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1, var1, var2)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2, var1, var2)

            if sp.sign(B1) != sp.sign(B2):
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_equation(f"\\text{{Adding equations ({current_eq_no1}) and ({current_eq_no2})}}")
            else:
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_equation(f"\\text{{Subtracting equation ({current_eq_no2}) from ({current_eq_no1})}}")

            op = "add" if sp.sign(A1) != sp.sign(A2) else "subtract"
            if A == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            x_term = self._term(A, var1)
            result_line = f"{x_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(A, C, var1)

            x_value = sp.simplify(C / A)
            self._substitute_x(x_value)
            return


        # Step 2: |a1| = 1 or |a2| = 1 → eliminate x
        if abs(a1) == 1 or abs(a2) == 1:
            if abs(a1) == 1:
                mult1 = abs(a2)
                mult2 = 1
                self.recorder.add(
                    f"Using LCM Elimination strategy: in equation (1) the coefficient of x is "
                    f"{sp.latex(a1)} and in equation (2) it is {sp.latex(a2)}. Because equation (1) "
                    f"already has coefficient 1, we multiply equation (1) by {sp.latex(mult1)} so that "
                    f"both x–coefficients become {sp.latex(abs(a2))} and will cancel when we combine "
                    "the equations."
                )
                self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
            else:
                mult1 = 1
                mult2 = abs(a1)
                self.recorder.add(
                    f"Using LCM Elimination strategy: in equation (1) the coefficient of x is "
                    f"{sp.latex(a1)} and in equation (2) it is {sp.latex(a2)}. Because equation (2) "
                    f"already has coefficient 1, we multiply equation (2) by {sp.latex(mult2)} so that "
                    f"both x–coefficients become {sp.latex(abs(a1))} and will cancel when we combine "
                    "the equations."
                )
                self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")


            A1 = a1 * mult1
            B1 = b1 * mult1
            C1 = c1 * mult1

            A2 = a2 * mult2
            B2 = b2 * mult2
            C2 = c2 * mult2
            # Record any new scaled equations with fresh equation numbers.
            current_eq_no1, next_eq_number = _record_scaled_equation(current_eq_no1, A1, B1, C1, mult1, next_eq_number)
            current_eq_no2, next_eq_number = _record_scaled_equation(current_eq_no2, A2, B2, C2, mult2, next_eq_number)

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1, var1, var2)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2, var1, var2)

            if sp.sign(A1) != sp.sign(A2):
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                B = B1 + B2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                B = B1 - B2
                C = C1 - C2
                self.recorder.add_equation("\\text{Subtracting equations}")

            op = "add" if sp.sign(A1) != sp.sign(A2) else "subtract"
            if B == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            y_term = self._term(B, var2)
            result_line = f"{y_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(B, C, var2)

            y_value = sp.simplify(C / B)
            self._substitute_y(y_value)
            return


        # Step 3: any b negative → LCM on b to eliminate y
        if b1 < 0 or b2 < 0:
            lcm = sp.lcm(abs(b1), abs(b2))
            self.recorder.add(
                f"Using LCM Elimination strategy: the y–coefficients are {sp.latex(b1)} in equation (1) "
                f"and {sp.latex(b2)} in equation (2). Because one is negative, we take the LCM of their "
                f"absolute values, LCM({sp.latex(abs(b1))}, {sp.latex(abs(b2))}) = {sp.latex(lcm)}, and "
                "scale each equation so that the y–coefficients become equal in size but opposite in sign, "
                "so y will cancel when we add the equations."
            )


            mult1 = lcm / abs(b1)
            mult2 = lcm / abs(b2)

            if mult1 != 1:
                self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
            if mult2 != 1:
                self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")

            A1 = a1 * mult1
            B1 = b1 * mult1
            C1 = c1 * mult1

            A2 = a2 * mult2
            B2 = b2 * mult2
            C2 = c2 * mult2
            # Record any new scaled equations with fresh equation numbers.
            current_eq_no1, next_eq_number = _record_scaled_equation(current_eq_no1, A1, B1, C1, mult1, next_eq_number)
            current_eq_no2, next_eq_number = _record_scaled_equation(current_eq_no2, A2, B2, C2, mult2, next_eq_number)

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1, var1, var2)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2, var1, var2)

            if sp.sign(B1) != sp.sign(B2):
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_equation("\\text{Subtracting equations}")

            op = "add" if sp.sign(B1) != sp.sign(B2) else "subtract"
            if A == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            x_term = self._term(A, var1)
            result_line = f"{x_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(A, C, var1)

            x_value = sp.simplify(C / A)
            self._substitute_x(x_value)
            return

        # Step 4: both b1 and b2 positive → compare LCM(b) and LCM(a)
        lcm_b = sp.lcm(b1, b2)
        lcm_a = sp.lcm(a1, a2)

        if lcm_b < lcm_a:
            eliminate = "y"
            self.recorder.add(
                f"Using LCM Elimination strategy: LCM of the y–coefficients is "
                f"LCM({sp.latex(b1)}, {sp.latex(b2)}) = {sp.latex(lcm_b)}, while LCM of the x–coefficients "
                f"is LCM({sp.latex(a1)}, {sp.latex(a2)}) = {sp.latex(lcm_a)}. Because the LCM for y is smaller, "
                "it is more efficient to eliminate y by scaling each equation so their y–coefficients match."
            )
        else:
            eliminate = "x"
            self.recorder.add(
                f"Using LCM Elimination strategy: LCM of the x–coefficients is "
                f"LCM({sp.latex(a1)}, {sp.latex(a2)}) = {sp.latex(lcm_a)}, while LCM of the y–coefficients "
                f"is LCM({sp.latex(b1)}, {sp.latex(b2)}) = {sp.latex(lcm_b)}. Because the LCM for x is smaller "
                "or equal, it is more efficient to eliminate x by scaling each equation so their x–coefficients match."
            )

        if eliminate == "y":
            lcm = sp.lcm(abs(b1), abs(b2))
            mult1 = lcm / abs(b1)
            mult2 = lcm / abs(b2)
        else:
            lcm = sp.lcm(abs(a1), abs(a2))
            mult1 = lcm / abs(a1)
            mult2 = lcm / abs(a2)

        if mult1 != 1:
            self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
        if mult2 != 1:
            self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")

        A1 = a1 * mult1
        B1 = b1 * mult1
        C1 = c1 * mult1

        A2 = a2 * mult2
        B2 = b2 * mult2
        C2 = c2 * mult2
        # Record any new scaled equations with fresh equation numbers.
        current_eq_no1, next_eq_number = _record_scaled_equation(current_eq_no1, A1, B1, C1, mult1, next_eq_number)
        current_eq_no2, next_eq_number = _record_scaled_equation(current_eq_no2, A2, B2, C2, mult2, next_eq_number)

        eq_line1 = EquationFormatter.format_equation(A1, B1, C1, var1, var2)
        eq_line2 = EquationFormatter.format_equation(A2, B2, C2, var1, var2)

        if eliminate == "y":
            if sp.sign(B1) != sp.sign(B2):
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_equation(f"\\text{{Adding equations ({current_eq_no1}) and ({current_eq_no2})}}")
            else:
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_equation(f"\\text{{Subtracting equation ({current_eq_no2}) from ({current_eq_no1})}}")

            op = "add" if sp.sign(B1) != sp.sign(B2) else "subtract"
            if A == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            x_term = self._term(A, var1)
            result_line = f"{x_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(A, C, var1)

            x_value = sp.simplify(C / A)
            self._substitute_x(x_value)
        else:
            if sp.sign(A1) != sp.sign(A2):
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                B = B1 + B2
                C = C1 + C2
                self.recorder.add_equation(f"\\text{{Adding equations ({current_eq_no1}) and ({current_eq_no2})}}")
            else:
                result = self._check_like_surds_and_maybe_above_grade(A1, B1, C1, A2, B2, C2)
                if result is not None:
                    return result
                B = B1 - B2
                C = C1 - C2
                self.recorder.add_equation(f"\\text{{Subtracting equation ({current_eq_no2}) from ({current_eq_no1})}}")

            op = "add" if sp.sign(A1) != sp.sign(A2) else "subtract"
            if B == 0:
                return self._record_and_return_degenerate(eq_line1, eq_line2, C, op)

            y_term = self._term(B, var2)
            result_line = f"{y_term} = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line, op=op)
            self.recorder.add_equation(result_line)
            self._record_solve_one_var_after_elimination(B, C, var2)

            y_value = sp.simplify(C / B)
            self._substitute_y(y_value)

    # -----------------------------
    # main solver
    # -----------------------------

    def solve(self):
        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()
        c1 = self.eq1.c.to_sympy()

        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()
        c2 = self.eq2.c.to_sympy()

        strategy = self.detect_strategy()

        # Record a strategy explanation (Detailed only; Medium hides it).
        if strategy == "LCM":
            self.recorder.add(
                "Elimination strategy: LCM. We choose the LCM method because the coefficients of x and y do not "
                "line up for direct or cross elimination; by multiplying each equation to make one variable share "
                "the same coefficient (with opposite signs), that variable will cancel in a single addition or "
                "subtraction step.",
                role=EXPLANATION_TEXT,
            )
        elif strategy == "DIRECT":
            self.recorder.add(
                "Elimination strategy: Direct. The coefficients of x or y already match in size, so we can add "
                "or subtract the equations immediately to eliminate one variable.",
                role=EXPLANATION_TEXT,
            )
        else:  # CROSS → Six step Method
            self.recorder.add_equation(
                "\\text{Elimination Strategy: Six step Method. Since } |a_1|=|b_2| \\text{ and } |a_2|=|b_1| "
                "\\text{ and both equations have same middle sign we will implement six step method.}",
                role=EXPLANATION_TEXT,
            )

        result = None
        if strategy == "DIRECT":
            result = self._solve_direct(a1, b1, c1, a2, b2, c2)
        elif strategy == "CROSS":
            result = self._solve_cross(a1, b1, c1, a2, b2, c2)
        else:
            result = self._solve_lcm(a1, b1, c1, a2, b2, c2)

        if result is not None:
            return result

        x = sp.Symbol(self.system.var1)
        y = sp.Symbol(self.system.var2)

        eq1 = self.eq1.sympy_equation(self.system.var1, self.system.var2)
        eq2 = self.eq2.sympy_equation(self.system.var1, self.system.var2)

        solution = sp.solve((eq1, eq2), (x, y))

        return solution
