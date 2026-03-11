import sympy as sp


class SubstitutionSolver:

    def solve(self, system):

        x = sp.Symbol(system.eq1.var1)
        y = sp.Symbol(system.eq1.var2)

        eq1 = sp.Eq(
            system.eq1.a.to_sympy() * x + system.eq1.b.to_sympy() * y,
            system.eq1.c.to_sympy(),
        )
        eq2 = sp.Eq(
            system.eq2.a.to_sympy() * x + system.eq2.b.to_sympy() * y,
            system.eq2.c.to_sympy(),
        )

        x_expr = sp.solve(eq1, x)[0]
        eq_sub = eq2.subs(x, x_expr)
        y_value = sp.solve(eq_sub, y)[0]
        x_value = x_expr.subs(y, y_value)

        return {x: sp.simplify(x_value), y: sp.simplify(y_value)}
