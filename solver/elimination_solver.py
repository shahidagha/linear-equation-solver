import sympy as sp


class EliminationSolver:

    def __init__(self, system):

        self.eq1 = system.eq1
        self.eq2 = system.eq2


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


    def solve(self):

        strategy = self.detect_strategy()

        print("Elimination Strategy:", strategy)

        eq1 = self.eq1.sympy_equation()
        eq2 = self.eq2.sympy_equation()

        x = sp.Symbol(self.eq1.var1)
        y = sp.Symbol(self.eq1.var2)

        solution = sp.solve((eq1, eq2), (x, y))

        return solution