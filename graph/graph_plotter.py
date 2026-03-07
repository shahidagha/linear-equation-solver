import matplotlib.pyplot as plt

class GraphPlotter:

    def plot_lines(self, points1, points2):

        x1, y1 = zip(*points1)
        x2, y2 = zip(*points2)

        plt.plot(x1, y1, label="Equation 1")
        plt.plot(x2, y2, label="Equation 2")

        plt.axhline(0)
        plt.axvline(0)

        plt.grid(True)
        plt.legend()

        plt.show()