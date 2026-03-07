class GraphicalSolver:

    def generate_points(self, a, b, c):

        points = []

        for x in range(-8, 9):

            if b != 0:

                y = (c - a*x) / b

                if y.is_integer():

                    y = int(y)

                    if -8 <= y <= 8:

                        points.append((x,y))

            if len(points) == 3:
                break

        return points


    def generate_table(self, points):

        x_values = []
        y_values = []
        pair_values = []

        for p in points:

            x_values.append(p[0])
            y_values.append(p[1])
            pair_values.append(f"({p[0]},{p[1]})")

        print("\nTable of Values")

        print("x :", x_values)
        print("y :", y_values)
        print("(x,y):", pair_values)