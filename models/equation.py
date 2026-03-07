import sympy as sp

class Equation:

    def __init__(self, a, b, c):

        self.a = a
        self.b = b
        self.c = c


    def to_sympy(self):

        x, y = sp.symbols('x y')

        a_val = self.a.to_sympy() if hasattr(self.a, "to_sympy") else self.a
        b_val = self.b.to_sympy() if hasattr(self.b, "to_sympy") else self.b

        expr = a_val*x + b_val*y

        return sp.Eq(expr, self.c)


    def display(self):

        a_val = self.a.display() if hasattr(self.a,"display") else self.a
        b_val = self.b.display() if hasattr(self.b,"display") else self.b

        return f"{a_val}x + {b_val}y = {self.c}"