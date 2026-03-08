class GraphicalSolver:
    print("GraphicalSolver module loaded")
    def __init__(self, system):
        print("GraphicalSolver initialized")
        self.eq1 = system.eq1
        self.eq2 = system.eq2


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
        print("DEBUG: Running GraphicalSolver")
        p1 = self.generate_points(self.eq1)
        p2 = self.generate_points(self.eq2)
        print("DEBUG Points:", p1, p2)

        return p1, p2