import sympy as sp


class FractionSurd:

    def __init__(self, num_mult=1, num_rad=1, den_mult=1, den_rad=1, sign=1):
        self.num_mult = num_mult
        self.num_rad = num_rad
        self.den_mult = den_mult
        self.den_rad = den_rad
        self.sign = sign

    def to_sympy(self):

        num = self.num_mult * sp.sqrt(self.num_rad)
        den = self.den_mult * sp.sqrt(self.den_rad)

        value = num / den

        if self.sign < 0:
            value = -value

        return sp.simplify(value)

    def __str__(self):
        return str(self.to_sympy())

    def multiply(self, other):

        result = self.to_sympy() * other.to_sympy()

        return result

    def divide(self, other):

        result = self.to_sympy() / other.to_sympy()

        return result

    def add(self, other):

        result = self.to_sympy() + other.to_sympy()

        return result

    def subtract(self, other):

        result = self.to_sympy() - other.to_sympy()

        return result