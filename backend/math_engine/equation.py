import sympy as sp
from backend.math_engine.fraction_surd import FractionSurd


class Equation:

    def __init__(self, a: FractionSurd, b: FractionSurd, c: FractionSurd):
        self.a = a
        self.b = b
        self.c = c

    def sympy_equation(self, var1: str = "x", var2: str = "y"):

        x = sp.Symbol(var1)
        y = sp.Symbol(var2)

        lhs = self.a.to_sympy() * x + self.b.to_sympy() * y
        rhs = self.c.to_sympy()

        return sp.Eq(lhs, rhs)

    def __str__(self):

        return str(self.sympy_equation())
