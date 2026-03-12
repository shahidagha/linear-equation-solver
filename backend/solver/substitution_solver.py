import sympy as sp


class SubstitutionSolver:

    @staticmethod
    def _build_equations(system):
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

        return x, y, eq1, eq2

    @staticmethod
    def _solve_unique_system(eq1, eq2, x, y):
        candidates = sp.solve((eq1, eq2), (x, y), dict=True)
        if not candidates:
            return []

        candidate = candidates[0]
        if x in candidate and y in candidate:
            return {x: sp.simplify(candidate[x]), y: sp.simplify(candidate[y])}

        # Parametric/infinite family does not represent a unique ordered pair.
        return []

    def solve(self, system):
        x, y, eq1, eq2 = self._build_equations(system)

        # Prefer isolating x from equation 1 when possible.
        isolate_source = None
        isolate_symbol = None
        substitute_symbol = None
        target_eq = None

        if system.eq1.a.to_sympy() != 0:
            isolate_source = eq1
            isolate_symbol = x
            substitute_symbol = y
            target_eq = eq2
        elif system.eq2.a.to_sympy() != 0:
            isolate_source = eq2
            isolate_symbol = x
            substitute_symbol = y
            target_eq = eq1
        elif system.eq1.b.to_sympy() != 0:
            isolate_source = eq1
            isolate_symbol = y
            substitute_symbol = x
            target_eq = eq2
        elif system.eq2.b.to_sympy() != 0:
            isolate_source = eq2
            isolate_symbol = y
            substitute_symbol = x
            target_eq = eq1
        else:
            return []

        isolated_values = sp.solve(isolate_source, isolate_symbol)
        if not isolated_values:
            return self._solve_unique_system(eq1, eq2, x, y)

        isolated_expression = isolated_values[0]
        substituted_equation = target_eq.subs(isolate_symbol, isolated_expression)

        substitute_values = sp.solve(substituted_equation, substitute_symbol)
        if not substitute_values:
            return self._solve_unique_system(eq1, eq2, x, y)

        substitute_value = sp.simplify(substitute_values[0])
        isolate_value = sp.simplify(isolated_expression.subs(substitute_symbol, substitute_value))

        if isolate_symbol == x:
            return {x: isolate_value, y: substitute_value}

        return {x: substitute_value, y: isolate_value}
