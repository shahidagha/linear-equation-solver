import sympy as sp
from utils.step_recorder import StepRecorder
from utils.equation_numbering import EquationNumbering
from latex.equation_formatter import EquationFormatter


class EliminationSolver:

    def __init__(self, system):

        self.eq1 = system.eq1
        self.eq2 = system.eq2

        self.recorder = StepRecorder()
        self.eq_numbers = EquationNumbering()


    # -----------------------------
    # vertical elimination display
    # -----------------------------

    def vertical_elimination(self, eq1, eq2, result):

        self.recorder.add("")
        self.recorder.add(f"  {eq1}")
        self.recorder.add(f"+ {eq2}")
        self.recorder.add("--------------")
        self.recorder.add(f"  {result}")
        self.recorder.add("")


    # -----------------------------
    # strategy detection
    # -----------------------------

    def detect_strategy(self):

        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()

        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()

        if abs(a1) == abs(a2) or abs(b1) == abs(b2):
            return "DIRECT"

        elif a1 == b2 and b1 == a2:
            return "CROSS"

        else:
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
    # main solver
    # -----------------------------

    def solve(self):

        strategy = self.detect_strategy()

        # -----------------------------
        # initial equations
        # -----------------------------

        eq1_str = EquationFormatter.format_equation(
            self.eq1.a.to_sympy(),
            self.eq1.b.to_sympy(),
            self.eq1.c.to_sympy()
        )

        n1 = self.eq_numbers.add(eq1_str)

        self.recorder.add(f"Equation ({n1})")
        self.recorder.add(f"{eq1_str} ... ({n1})")

        eq2_str = EquationFormatter.format_equation(
            self.eq2.a.to_sympy(),
            self.eq2.b.to_sympy(),
            self.eq2.c.to_sympy()
        )

        n2 = self.eq_numbers.add(eq2_str)

        self.recorder.add(f"Equation ({n2})")
        self.recorder.add(f"{eq2_str} ... ({n2})")


        self.recorder.add(f"Elimination strategy: {strategy}")

        var = self.choose_variable()

        self.recorder.add(f"Choosing to eliminate {var}")


        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()
        c1 = self.eq1.c.to_sympy()

        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()
        c2 = self.eq2.c.to_sympy()


        # -----------------------------
        # compute LCM
        # -----------------------------

        if var == "y":

            lcm = sp.lcm(abs(b1), abs(b2))
            self.recorder.add(f"LCM of {abs(b1)} and {abs(b2)} = {lcm}")

            m1 = lcm / b1
            m2 = lcm / b2

        else:

            lcm = sp.lcm(abs(a1), abs(a2))
            self.recorder.add(f"LCM of {abs(a1)} and {abs(a2)} = {lcm}")

            m1 = lcm / a1
            m2 = lcm / a2


        # -----------------------------
        # multiplication decision
        # -----------------------------

        mult1 = abs(m1) != 1
        mult2 = abs(m2) != 1

        if mult1 and not mult2:
            self.recorder.add(f"Multiplying equation (1) by {m1}")

        elif mult2 and not mult1:
            self.recorder.add(f"Multiplying equation (2) by {m2}")

        elif mult1 and mult2:
            self.recorder.add(f"Multiplying equation (1) by {m1}")
            self.recorder.add(f"Multiplying equation (2) by {m2}")


        if abs(m1) == 1:
            m1 = 1

        if abs(m2) == 1:
            m2 = 1


        # -----------------------------
        # build multiplied equations
        # -----------------------------

        A1 = a1 * m1
        B1 = b1 * m1
        C1 = c1 * m1

        A2 = a2 * m2
        B2 = b2 * m2
        C2 = c2 * m2


        eq_line1 = EquationFormatter.format_equation(A1, B1, C1)
        eq_line2 = EquationFormatter.format_equation(A2, B2, C2)


        self.recorder.add_equation(eq_line1)
        self.recorder.add_equation(eq_line2)

        # -----------------------------
        # elimination
        # -----------------------------

        if var == "y":

            if B1 + B2 == 0:

                A = A1 + A2
                C = C1 + C2
                result_line = f"{A}x = {C}"

                self.recorder.add("Adding equations")

            else:

                A = A1 - A2
                C = C1 - C2
                result_line = f"{A}x = {C}"

                self.recorder.add("Subtracting equations")


            self.vertical_elimination(eq_line1, eq_line2, result_line)

            self.recorder.add(result_line)

            x_value = C / A
            self.recorder.add(f"x = {x_value}")


            # -----------------------------
            # substitution
            # -----------------------------

            self.recorder.add(f"Substitute x = {x_value} in equation ({n1})")

            self.recorder.add(f"{a1}({x_value}) + {b1}y = {c1}")

            lhs = a1 * x_value

            self.recorder.add(f"{lhs} + {b1}y = {c1}")

            rhs = c1 - lhs

            self.recorder.add(f"{b1}y = {rhs}")

            y_value = rhs / b1

            self.recorder.add(f"y = {y_value}")


        # -----------------------------
        # verification using sympy
        # -----------------------------

        x = sp.Symbol(self.eq1.var1)
        y = sp.Symbol(self.eq1.var2)

        eq1 = self.eq1.sympy_equation()
        eq2 = self.eq2.sympy_equation()

        solution = sp.solve((eq1, eq2), (x, y))


        print("\nRecorded Steps:\n")

        for step in self.recorder.get_steps():
            print(step)

        return solution