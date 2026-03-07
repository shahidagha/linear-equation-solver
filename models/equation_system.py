class EquationSystem:

    def __init__(self, eq1, eq2):
        """
        Represents a system of two equations
        """

        self.eq1 = eq1
        self.eq2 = eq2

    def display(self):

        return f"{self.eq1.display()}\n{self.eq2.display()}"