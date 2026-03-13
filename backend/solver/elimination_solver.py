import sympy as sp
from backend.utils.step_recorder import StepRecorder
from backend.latex.equation_formatter import EquationFormatter


class EliminationSolver:

    def __init__(self, system):

        self.system = system
        self.eq1 = system.eq1
        self.eq2 = system.eq2
        self.above_grade = False

        # Records only elimination‑specific steps.
        # Standardization and equation numbering are handled upstream
        # by EquationStandardizer and the LaTeX renderer.
        self.recorder = StepRecorder()

    # -----------------------------
    # vertical elimination display
    # -----------------------------

    def vertical_elimination(self, eq1, eq2, result):

        self.recorder.add_vertical(eq1, eq2, result)

    @staticmethod
    def _term(coeff, var):

        coeff = sp.simplify(coeff)

        if coeff == 1:
            return var

        if coeff == -1:
            return f"-{var}"

        return f"{sp.latex(coeff)}{var}"

    # -----------------------------
    # like‑surd guard (SECTION 1)
    # -----------------------------

    @staticmethod
    def _radicand(expr):
        expr = sp.simplify(expr)
        roots = [p.base for p in expr.atoms(sp.Pow) if p.exp == sp.Rational(1, 2)]
        if not roots:
            return None
        base0 = sp.simplify(roots[0])
        for r in roots[1:]:
            if not sp.simplify(r - base0) == 0:
                return "MIXED"
        return base0

    def _above_grade(self):
        if not self.above_grade:
            self.recorder.add("Above the grade of the student")
            self.above_grade = True

    def _check_like_surd_pair(self, e1, e2):
        r1 = self._radicand(e1)
        r2 = self._radicand(e2)

        # Mixed radicands within a single coefficient.
        if r1 == "MIXED" or r2 == "MIXED":
            self._above_grade()
            return False

        # Both have a single radicand but they differ.
        if r1 is not None and r2 is not None and not sp.simplify(r1 - r2) == 0:
            self._above_grade()
            return False

        return True

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

        self.recorder.add(f"Substitute x = {sp.latex(x_value)} in equation ({idx})")
        b_term = self._term(b, "y")
        self.recorder.add(f"{sp.latex(a)}({sp.latex(x_value)}) + {b_term} = {sp.latex(c)}")

        lhs = sp.simplify(a * x_value)
        self.recorder.add(f"{sp.latex(lhs)} + {b_term} = {sp.latex(c)}")

        rhs = sp.simplify(c - lhs)
        equation_rhs_line = f"{b_term} = {sp.latex(rhs)}"

        y_value = sp.simplify(rhs / b)
        final_y_line = f"y = {sp.latex(y_value)}"

        if equation_rhs_line != final_y_line:
            self.recorder.add(equation_rhs_line)

        self.recorder.add(final_y_line)
        return y_value

    def _substitute_y(self, y_value):
        a, b, c, idx = self._choose_substitution_equation()

        self.recorder.add(f"Substitute y = {sp.latex(y_value)} in equation ({idx})")
        a_term = self._term(a, "x")
        substituted = sp.simplify(b * y_value)
        self.recorder.add(f"{a_term} + ({sp.latex(substituted)}) = {sp.latex(c)}")

        lhs = substituted
        self.recorder.add(f"{a_term} + {sp.latex(lhs)} = {sp.latex(c)}")

        rhs = sp.simplify(c - lhs)
        self.recorder.add(f"{a_term} = {sp.latex(rhs)}")

        x_value = sp.simplify(rhs / a)
        self.recorder.add(f"x = {sp.latex(x_value)}")
        return x_value

    # -----------------------------
    # DIRECT strategy (SECTION 2)
    # -----------------------------

    def _solve_direct(self, a1, b1, c1, a2, b2, c2):
        if abs(b1) == abs(b2):
            eliminate = "y"
        else:
            eliminate = "x"

        if eliminate == "y":
            self.recorder.add("Using Direct Elimination on y (|b₁| = |b₂|)")

            if sp.sign(b1) != sp.sign(b2):
                self.recorder.add_operation("Adding equations (coefficients of y have opposite signs)")
                if not (
                    self._check_like_surd_pair(a1, a2)
                    and self._check_like_surd_pair(b1, b2)
                    and self._check_like_surd_pair(c1, c2)
                ):
                    return
                A = a1 + a2
                C = c1 + c2
            else:
                if a1 > a2:
                    self.recorder.add_operation("Subtracting equations (1 − 2)")
                    if not (
                        self._check_like_surd_pair(a1, a2)
                        and self._check_like_surd_pair(b1, b2)
                        and self._check_like_surd_pair(c1, c2)
                    ):
                        return
                    A = a1 - a2
                    C = c1 - c2
                else:
                    self.recorder.add_operation("Subtracting equations (2 − 1)")
                    if not (
                        self._check_like_surd_pair(a1, a2)
                        and self._check_like_surd_pair(b1, b2)
                        and self._check_like_surd_pair(c1, c2)
                    ):
                        return
                    A = a2 - a1
                    C = c2 - c1

            if A == 0:
                return

            eq_line1 = EquationFormatter.format_equation(a1, b1, c1)
            eq_line2 = EquationFormatter.format_equation(a2, b2, c2)
            result_line = f"{sp.latex(A)}x = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            x_value = sp.simplify(C / A)
            self.recorder.add(f"x = {sp.latex(x_value)}")
            self._substitute_x(x_value)
        else:
            self.recorder.add("Using Direct Elimination on x (|a₁| = |a₂|)")

            if sp.sign(a1) != sp.sign(a2):
                self.recorder.add_operation("Adding equations (coefficients of x have opposite signs)")
                if not (
                    self._check_like_surd_pair(a1, a2)
                    and self._check_like_surd_pair(b1, b2)
                    and self._check_like_surd_pair(c1, c2)
                ):
                    return
                B = b1 + b2
                C = c1 + c2
            else:
                if b1 > b2:
                    self.recorder.add_operation("Subtracting equations (1 − 2)")
                    if not (
                        self._check_like_surd_pair(a1, a2)
                        and self._check_like_surd_pair(b1, b2)
                        and self._check_like_surd_pair(c1, c2)
                    ):
                        return
                    B = b1 - b2
                    C = c1 - c2
                else:
                    self.recorder.add_operation("Subtracting equations (2 − 1)")
                    if not (
                        self._check_like_surd_pair(a1, a2)
                        and self._check_like_surd_pair(b1, b2)
                        and self._check_like_surd_pair(c1, c2)
                    ):
                        return
                    B = b2 - b1
                    C = c2 - c1

            if B == 0:
                return

            eq_line1 = EquationFormatter.format_equation(a1, b1, c1)
            eq_line2 = EquationFormatter.format_equation(a2, b2, c2)
            result_line = f"{sp.latex(B)}y = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            y_value = sp.simplify(C / B)
            self.recorder.add(f"y = {sp.latex(y_value)}")
            self._substitute_y(y_value)

    # -----------------------------
    # CROSS strategy (SECTION 3)
    # -----------------------------

    def _solve_cross(self, a1, b1, c1, a2, b2, c2):
        self.recorder.add("Using Cross Elimination strategy")

        # Step 1: add (1) and (2)
        if not (
            self._check_like_surd_pair(a1, a2)
            and self._check_like_surd_pair(b1, b2)
            and self._check_like_surd_pair(c1, c2)
        ):
            return

        a3 = a1 + a2
        b3 = b1 + b2
        c3 = c1 + c2

        self.recorder.add_operation("Adding equations (1) and (2)")
        eq1_line = EquationFormatter.format_equation(a1, b1, c1)
        eq2_line = EquationFormatter.format_equation(a2, b2, c2)
        eq3_line = EquationFormatter.format_equation(a3, b3, c3)
        self.vertical_elimination(eq1_line, eq2_line, eq3_line)
        self.recorder.add_equation(eq3_line)  # (3)
        self.recorder.add("Divide equation (3) so that coefficient of x or y becomes 1 (x ± y = m).")

        # Step 3: subtract equations according to a1, a2
        if a1 > a2:
            self.recorder.add_operation("Subtracting equations (1 − 2)")
            if not (
                self._check_like_surd_pair(a1, a2)
                and self._check_like_surd_pair(b1, b2)
                and self._check_like_surd_pair(c1, c2)
            ):
                return
            a4 = a1 - a2
            b4 = b1 - b2
            c4 = c1 - c2
        else:
            self.recorder.add_operation("Subtracting equations (2 − 1)")
            if not (
                self._check_like_surd_pair(a1, a2)
                and self._check_like_surd_pair(b1, b2)
                and self._check_like_surd_pair(c1, c2)
            ):
                return
            a4 = a2 - a1
            b4 = b2 - b1
            c4 = c2 - c1

        eq4_line = EquationFormatter.format_equation(a4, b4, c4)
        self.recorder.add_equation(eq4_line)  # (4)
        self.recorder.add("Divide equation (4) so that coefficient of x or y becomes 1 (x ∓ y = n).")
        self.recorder.add("Add equations (3) and (4) to eliminate y and obtain 2x = m + n.")

    # -----------------------------
    # LCM strategy (SECTION 4)
    # -----------------------------

    def _solve_lcm(self, a1, b1, c1, a2, b2, c2):
        self.recorder.add(
            "Using LCM Elimination strategy. In this method we first choose which variable to eliminate "
            "by comparing the coefficients of x and y in both equations. We then multiply each equation "
            "so that this chosen variable has the same numerical coefficient (but opposite signs), which "
            "allows that variable to vanish when we add or subtract the equations, leaving a single-variable "
            "equation that is easy to solve."
        )

        # Step 1: |b1| = 1 or |b2| = 1 → eliminate y
        if abs(b1) == 1 or abs(b2) == 1:
            if abs(b1) == 1:
                mult1 = abs(b2)
                mult2 = 1
                self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
            else:
                mult1 = 1
                mult2 = abs(b1)
                self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")

            A1 = a1 * mult1
            B1 = b1 * mult1
            C1 = c1 * mult1

            A2 = a2 * mult2
            B2 = b2 * mult2
            C2 = c2 * mult2

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2)

            if sp.sign(B1) != sp.sign(B2):
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_operation("Subtracting equations")

            if A == 0:
                return

            result_line = f"{sp.latex(A)}x = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            x_value = sp.simplify(C / A)
            self.recorder.add(f"x = {sp.latex(x_value)}")
            self._substitute_x(x_value)
            return


        # Step 2: |a1| = 1 or |a2| = 1 → eliminate x
        if abs(a1) == 1 or abs(a2) == 1:
            if abs(a1) == 1:
                mult1 = abs(a2)
                mult2 = 1
                self.recorder.add_operation(f"Multiplying equation (1) by {mult1}")
            else:
                mult1 = 1
                mult2 = abs(a1)
                self.recorder.add_operation(f"Multiplying equation (2) by {mult2}")


            A1 = a1 * mult1
            B1 = b1 * mult1
            C1 = c1 * mult1

            A2 = a2 * mult2
            B2 = b2 * mult2
            C2 = c2 * mult2

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2)

            if sp.sign(A1) != sp.sign(A2):
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                B = B1 + B2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                B = B1 - B2
                C = C1 - C2
                self.recorder.add_operation("Subtracting equations")

            if B == 0:
                return

            result_line = f"{sp.latex(B)}y = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            y_value = sp.simplify(C / B)
            self.recorder.add(f"y = {sp.latex(y_value)}")
            self._substitute_y(y_value)
            return


        # Step 3: any b negative → LCM on b to eliminate y
        if b1 < 0 or b2 < 0:
            lcm = sp.lcm(abs(b1), abs(b2))
            self.recorder.add(f"LCM of {abs(b1)} and {abs(b2)} = {lcm}")


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

            eq_line1 = EquationFormatter.format_equation(A1, B1, C1)
            eq_line2 = EquationFormatter.format_equation(A2, B2, C2)

            if sp.sign(B1) != sp.sign(B2):
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_operation("Subtracting equations")

            if A == 0:
                return

            result_line = f"{sp.latex(A)}x = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            x_value = sp.simplify(C / A)
            self.recorder.add(f"x = {sp.latex(x_value)}")
            self._substitute_x(x_value)
            return

        # Step 4: both b1 and b2 positive → compare LCM(b) and LCM(a)
        lcm_b = sp.lcm(b1, b2)
        lcm_a = sp.lcm(a1, a2)

        if lcm_b < lcm_a:
            eliminate = "y"
            self.recorder.add(f"LCM({b1}, {b2}) = {lcm_b} is smaller, eliminate y.")
        else:
            eliminate = "x"
            self.recorder.add(f"LCM({a1}, {a2}) = {lcm_a} is smaller or equal, eliminate x.")

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

        eq_line1 = EquationFormatter.format_equation(A1, B1, C1)
        eq_line2 = EquationFormatter.format_equation(A2, B2, C2)

        if eliminate == "y":
            if sp.sign(B1) != sp.sign(B2):
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 + A2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                A = A1 - A2
                C = C1 - C2
                self.recorder.add_operation("Subtracting equations")

            if A == 0:
                return

            result_line = f"{sp.latex(A)}x = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            x_value = sp.simplify(C / A)
            self.recorder.add(f"x = {sp.latex(x_value)}")
            self._substitute_x(x_value)
        else:
            if sp.sign(A1) != sp.sign(A2):
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                B = B1 + B2
                C = C1 + C2
                self.recorder.add_operation("Adding equations")
            else:
                if not (
                    self._check_like_surd_pair(A1, A2)
                    and self._check_like_surd_pair(B1, B2)
                    and self._check_like_surd_pair(C1, C2)
                ):
                    return
                B = B1 - B2
                C = C1 - C2
                self.recorder.add_operation("Subtracting equations")

            if B == 0:
                return

            result_line = f"{sp.latex(B)}y = {sp.latex(C)}"
            self.vertical_elimination(eq_line1, eq_line2, result_line)
            self.recorder.add_equation(result_line)

            y_value = sp.simplify(C / B)
            self.recorder.add(f"y = {sp.latex(y_value)}")
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

        # Record a strategy explanation. For LCM we provide a teacher-style rationale
        # only in the detailed view (renderer will hide it in other verbosities).
        if strategy == "LCM":
            self.recorder.add(
                "Elimination strategy: LCM. We choose the LCM method because the coefficients of x and y do not "
                "line up for direct or cross elimination; by multiplying each equation to make one variable share "
                "the same coefficient (with opposite signs), that variable will cancel in a single addition or "
                "subtraction step."
            )
        elif strategy == "DIRECT":
            self.recorder.add(
                "Elimination strategy: Direct. The coefficients of x or y already match in size, so we can add "
                "or subtract the equations immediately to eliminate one variable."
            )
        else:  # CROSS
            self.recorder.add(
                "Elimination strategy: Cross. By combining the equations in a criss-cross way we create new "
                "equations where adding and subtracting quickly isolates x and y."
            )

        if strategy == "DIRECT":
            self._solve_direct(a1, b1, c1, a2, b2, c2)
        elif strategy == "CROSS":
            self._solve_cross(a1, b1, c1, a2, b2, c2)
        else:
            self._solve_lcm(a1, b1, c1, a2, b2, c2)

        x = sp.Symbol(self.system.var1)
        y = sp.Symbol(self.system.var2)

        eq1 = self.eq1.sympy_equation(self.system.var1, self.system.var2)
        eq2 = self.eq2.sympy_equation(self.system.var1, self.system.var2)

        solution = sp.solve((eq1, eq2), (x, y))

        return solution
