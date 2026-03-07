class GraphicalSolver:

    def generate_points(self, a, b, c):

        points = []

        for x in range(-8, 9):

            if b != 0:
                y = (c - a*x) / b

                if y.is_integer():

                    y = int(y)

                    if -8 <= y <= 8:
                        points.append((x, y))

            if len(points) == 3:
                break

        return points