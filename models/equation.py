class Equation:

    def __init__(self, a, b, c):
        """
        Represents equation:

        ax + by = c
        """

        self.a = a
        self.b = b
        self.c = c

    def display(self):
        return f"{self.a}x + {self.b}y = {self.c}"