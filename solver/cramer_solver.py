class CramerSolver:

    def solve(self, system):

        a1 = system.eq1.a
        b1 = system.eq1.b
        c1 = system.eq1.c

        a2 = system.eq2.a
        b2 = system.eq2.b
        c2 = system.eq2.c

        # Determinants
        D = a1*b2 - a2*b1
        Dx = c1*b2 - c2*b1
        Dy = a1*c2 - a2*c1

        if D == 0:
            return "No unique solution"

        x = Dx / D
        y = Dy / D

        return {"x": x, "y": y}