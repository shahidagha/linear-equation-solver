import sympy as sp


class GraphicalSolver:
    """Generate points for plotting; can classify system as unique, no solution, or infinitely many."""

    def __init__(self, system):
        self.eq1 = system.eq1
        self.eq2 = system.eq2
        self._system = system

    def classify(self):
        """
        Classify the system from the two lines: unique intersection, parallel (no solution), or same line (infinite).
        Returns "unique" | "none" | "infinite".
        """
        a1 = self.eq1.a.to_sympy()
        b1 = self.eq1.b.to_sympy()
        c1 = self.eq1.c.to_sympy()
        a2 = self.eq2.a.to_sympy()
        b2 = self.eq2.b.to_sympy()
        c2 = self.eq2.c.to_sympy()
        # Same line: (a1,b1,c1) proportional to (a2,b2,c2). Parallel: same slope -a/b, different line.
        if b1 == 0 and b2 == 0:
            if a1 == 0 and a2 == 0:
                return "infinite" if sp.simplify(c1 - c2) == 0 else "none"
            if a2 == 0:
                return "none"
            if sp.simplify(a1 * c2 - a2 * c1) == 0:
                return "infinite"
            return "none"
        if b1 == 0 or b2 == 0:
            return "unique"
        D = sp.simplify(a1 * b2 - a2 * b1)
        if D != 0:
            return "unique"
        if sp.simplify(a1 * c2 - a2 * c1) == 0 and sp.simplify(b1 * c2 - b2 * c1) == 0:
            return "infinite"
        return "none"

    def generate_points(self, equation):
        a = equation.a.to_sympy()
        b = equation.b.to_sympy()
        c = equation.c.to_sympy()

        points = []

        # 1. search integer points
        for x in range(-8, 9):
            if b == 0:
                continue

            y = (c - a*x) / b
            y = y.simplify()

            if y.is_integer:
                y_val = int(y)

                if -8 <= y_val <= 8:
                    points.append((x, y_val))

            if len(points) == 3:
                return points

        # 2. add intercept points if needed

        if a != 0:
            x_intercept = c / a
            points.append((x_intercept, 0))

        if b != 0:
            y_intercept = c / b
            points.append((0, y_intercept))

        return points[:3]

    def generate_tables(self):
        p1 = self.generate_points(self.eq1)
        p2 = self.generate_points(self.eq2)

        return p1, p2
