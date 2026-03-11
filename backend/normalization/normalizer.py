import sympy as sp

from backend.math_engine.equation import Equation
from backend.math_engine.system import EquationSystem


class _SympyValue:
    def __init__(self, value):
        self._value = sp.simplify(value)

    def to_sympy(self):
        return self._value


class Normalizer:
    @staticmethod
    def _to_sympy(value):
        return value.to_sympy() if hasattr(value, "to_sympy") else sp.sympify(value)

    def _normalize_equation(self, equation):
        a = self._to_sympy(equation.a)
        b = self._to_sympy(equation.b)
        c = self._to_sympy(equation.c)

        coeffs = [sp.together(a), sp.together(b), sp.together(c)]

        integer_denominators = []
        for coeff in coeffs:
            _, den = sp.fraction(coeff)
            if den.is_Integer:
                integer_denominators.append(abs(int(den)))

        if integer_denominators:
            lcm_den = sp.ilcm(*integer_denominators)
            coeffs = [sp.simplify(coeff * lcm_den) for coeff in coeffs]

        if all(value.is_Integer for value in coeffs):
            gcd_value = sp.igcd(*[abs(int(value)) for value in coeffs if value != 0]) if any(value != 0 for value in coeffs) else 1
            if gcd_value not in (0, 1):
                coeffs = [sp.simplify(value / gcd_value) for value in coeffs]

        a_norm, b_norm, c_norm = coeffs

        if (a_norm.is_number and a_norm < 0) or (a_norm == 0 and b_norm.is_number and b_norm < 0):
            a_norm = -a_norm
            b_norm = -b_norm
            c_norm = -c_norm

        return Equation(
            _SympyValue(a_norm),
            _SympyValue(b_norm),
            _SympyValue(c_norm),
            var1=equation.var1,
            var2=equation.var2,
        )

    def normalize(self, system):
        if isinstance(system, EquationSystem):
            return EquationSystem(
                self._normalize_equation(system.eq1),
                self._normalize_equation(system.eq2),
            )

        return self._normalize_equation(system)
