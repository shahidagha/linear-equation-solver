import sympy as sp

class FractionSurd:

    def __init__(self, num_mult, num_rad, den_mult, den_rad):

        self.num_mult = num_mult
        self.num_rad = num_rad
        self.den_mult = den_mult
        self.den_rad = den_rad


    def to_sympy(self):

        num = self.num_mult * sp.sqrt(self.num_rad)
        den = self.den_mult * sp.sqrt(self.den_rad)

        return num / den


    def simplify(self):

        expr = self.to_sympy()

        return sp.simplify(expr)


    def to_latex(self):

        expr = self.simplify()

        return sp.latex(expr)


    def display(self):

        expr = self.simplify()

        return str(expr)