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
        self.recorder.add(f"Elimination strategy: {strategy}")

        if strategy == "DIRECT":
            self._solve_direct(a1, b1, c1, a2, b2, c2)
        elif strategy == "CROSS":
            self._solve_cross(a1, b1, c1, a2, b2, c2)
        else:
            # Reuse the existing LCM‑based variable choice for the generic LCM strategy.
            self._solve_lcm(a1, b1, c1, a2, b2, c2)

        x = sp.Symbol(self.system.var1)
        y = sp.Symbol(self.system.var2)

        eq1 = self.eq1.sympy_equation(self.system.var1, self.system.var2)
        eq2 = self.eq2.sympy_equation(self.system.var1, self.system.var2)

        solution = sp.solve((eq1, eq2), (x, y))

        return solution
