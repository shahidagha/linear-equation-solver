from sympy import symbols, Eq, solve

class SubstitutionSolver:

    def solve(self, system):

        x, y = symbols('x y')

        eq1 = Eq(system.eq1.a*x + system.eq1.b*y, system.eq1.c)
        eq2 = Eq(system.eq2.a*x + system.eq2.b*y, system.eq2.c)

        # Solve eq1 for x
        x_expr = solve(eq1, x)[0]

        # Substitute into eq2
        eq_sub = eq2.subs(x, x_expr)

        # Solve for y
        y_value = solve(eq_sub, y)[0]

        # Substitute back for x
        x_value = x_expr.subs(y, y_value)

        return {x: x_value, y: y_value}