from backend.math_engine.equation import Equation


class EquationSystem:

    def __init__(self, eq1: Equation, eq2: Equation, var1: str = "x", var2: str = "y"):
        self.eq1 = eq1
        self.eq2 = eq2
        self.var1 = var1
        self.var2 = var2

    def __str__(self):

        return f"""
System of Equations

{self.eq1.sympy_equation(self.var1, self.var2)}
{self.eq2.sympy_equation(self.var1, self.var2)}
"""
