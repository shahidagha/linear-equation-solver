from backend.math_engine.equation import Equation


class EquationSystem:

    def __init__(self, eq1: Equation, eq2: Equation):
        self.eq1 = eq1
        self.eq2 = eq2

    def __str__(self):

        return f"""
System of Equations

{self.eq1}
{self.eq2}
"""