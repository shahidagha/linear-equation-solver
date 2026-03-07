from sympy import symbols, Eq, solve

class EliminationSolver:

    def solve(self, system):

        x, y = symbols('x y')

        eq1 = Eq(system.eq1.a * x + system.eq1.b * y, system.eq1.c)
        eq2 = Eq(system.eq2.a * x + system.eq2.b * y, system.eq2.c)

        solution = solve((eq1, eq2), (x, y))

        return solution