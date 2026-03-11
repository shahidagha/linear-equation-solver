import sympy as sp


class CramerSolver:

    @staticmethod
    def _to_sympy(value):
        return value.to_sympy() if hasattr(value, "to_sympy") else value

    def solve(self, system):

        a1 = self._to_sympy(system.eq1.a)
        b1 = self._to_sympy(system.eq1.b)
        c1 = self._to_sympy(system.eq1.c)

        a2 = self._to_sympy(system.eq2.a)
        b2 = self._to_sympy(system.eq2.b)
        c2 = self._to_sympy(system.eq2.c)

        # Determinants
        D = sp.simplify(a1 * b2 - a2 * b1)
        Dx = sp.simplify(c1 * b2 - c2 * b1)
        Dy = sp.simplify(a1 * c2 - a2 * c1)

        if D == 0:
            return "No unique solution"

        x = sp.simplify(Dx / D)
        y = sp.simplify(Dy / D)

        return {"x": x, "y": y}
