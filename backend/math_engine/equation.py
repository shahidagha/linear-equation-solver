import sympy as sp
from backend.math_engine.fraction_surd import FractionSurd


class Equation:

    def __init__(self, a: FractionSurd, b: FractionSurd, c: FractionSurd, var1="x", var2="y"):
        self.a = a
        self.b = b
        self.c = c
        self.var1 = var1
        self.var2 = var2

    def sympy_equation(self):

        x = sp.Symbol(self.var1)
        y = sp.Symbol(self.var2)

        lhs = self.a.to_sympy() * x + self.b.to_sympy() * y
        rhs = self.c.to_sympy()

        return sp.Eq(lhs, rhs)

    def __str__(self):

        return str(self.sympy_equation())