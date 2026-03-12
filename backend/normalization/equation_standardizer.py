from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Iterable

from backend.latex.equation_formatter import EquationFormatter
from backend.math_engine.equation import Equation
from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.system import EquationSystem


@dataclass
class _SurdRational:
    sign: int
    mult: int
    rad: int
    den: int

    def copy(self) -> "_SurdRational":
        return _SurdRational(self.sign, self.mult, self.rad, self.den)


class EquationStandardizer:
    """Deterministic standardization pipeline for 2x2 linear systems."""

    def standardize(self, system: EquationSystem, raw_equations: list[str] | None = None) -> dict:
        raw_equations = raw_equations or [
            self._format_equation(system.eq1, system.var1, system.var2),
            self._format_equation(system.eq2, system.var1, system.var2),
        ]

        eq1, steps_eq1 = self._standardize_equation(system.eq1, raw_equations[0], 1, system.var1, system.var2)
        eq2, steps_eq2 = self._standardize_equation(system.eq2, raw_equations[1], 2, system.var1, system.var2)

        standardized = EquationSystem(eq1, eq2, var1=system.var1, var2=system.var2)
        return {
            "system": standardized,
            "steps_eq1": steps_eq1,
            "steps_eq2": steps_eq2,
        }

    def _standardize_equation(self, eq: Equation, raw: str, number: int, var1: str, var2: str):
        steps: list[dict] = []

        steps.append({"type": "write_equation", "equation": raw})

        steps.append({
            "type": "rearrange_standard_form",
            "result": self._format_equation(eq, var1, var2),
        })

        a = self._from_fraction_surd(eq.a)
        b = self._from_fraction_surd(eq.b)
        c = self._from_fraction_surd(eq.c)

        if a.sign < 0:
            a.sign *= -1
            b.sign *= -1
            c.sign *= -1
            steps.append({"type": "make_leading_positive", "multiplied_by": -1})
        else:
            steps.append({"type": "make_leading_positive", "applied": False})

        den_squares = self._denominator_squares([eq.a, eq.b, eq.c])
        lcm_square = self._lcm_many(den_squares) if den_squares else 1
        multiplier_mult, multiplier_rad = self._sqrt_as_surd(lcm_square)

        a = self._multiply_by_surd(a, multiplier_mult, multiplier_rad)
        b = self._multiply_by_surd(b, multiplier_mult, multiplier_rad)
        c = self._multiply_by_surd(c, multiplier_mult, multiplier_rad)

        eq_after_den = Equation(self._to_fraction_surd(a), self._to_fraction_surd(b), self._to_fraction_surd(c))

        steps.append(
            {
                "type": "remove_denominator",
                "denominator_squares": den_squares,
                "lcm_square": lcm_square,
                "multiplier": self._surd_to_text(multiplier_mult, multiplier_rad),
                "result": self._format_equation(eq_after_den, var1, var2),
            }
        )

        squares = [self._square_value(a), self._square_value(b), self._square_value(c)]
        non_zero = [abs(v) for v in squares if v != 0]
        gcd_square = self._gcd_many(non_zero) if non_zero else 1
        divisor_mult, divisor_rad = self._sqrt_as_surd(gcd_square)

        a = self._divide_by_surd(a, divisor_mult, divisor_rad)
        b = self._divide_by_surd(b, divisor_mult, divisor_rad)
        c = self._divide_by_surd(c, divisor_mult, divisor_rad)

        standardized_equation = Equation(self._to_fraction_surd(a), self._to_fraction_surd(b), self._to_fraction_surd(c))

        steps.append(
            {
                "type": "reduce_equation",
                "coefficient_squares": squares,
                "gcd_square": gcd_square,
                "divisor": self._surd_to_text(divisor_mult, divisor_rad),
                "result": self._format_equation(standardized_equation, var1, var2),
            }
        )

        steps.append({"type": "assign_equation_number", "number": number})
        return standardized_equation, steps

    def _from_fraction_surd(self, value: FractionSurd) -> _SurdRational:
        signed_mult = value.num_mult
        sign = -1 if signed_mult < 0 or value.sign < 0 else 1
        mult = abs(signed_mult)
        rad = max(1, value.num_rad * value.den_rad)
        den = value.den_mult * value.den_rad
        return self._simplify(sign, mult, rad, den)

    def _to_fraction_surd(self, value: _SurdRational) -> FractionSurd:
        signed_mult = value.mult if value.sign > 0 else -value.mult
        return FractionSurd(signed_mult, value.rad, value.den, 1, 1)

    def _multiply_by_surd(self, value: _SurdRational, mult: int, rad: int) -> _SurdRational:
        return self._simplify(value.sign, value.mult * mult, value.rad * rad, value.den)

    def _divide_by_surd(self, value: _SurdRational, mult: int, rad: int) -> _SurdRational:
        # v / (mult*sqrt(rad)) == v * sqrt(rad) / (mult*rad)
        return self._simplify(value.sign, value.mult, value.rad * rad, value.den * mult * rad)

    def _square_value(self, value: _SurdRational) -> int:
        return (value.mult * value.mult * value.rad) // (value.den * value.den)

    def _denominator_squares(self, coeffs: Iterable[FractionSurd]) -> list[int]:
        out = []
        for coeff in coeffs:
            square = (coeff.den_mult * coeff.den_mult) * coeff.den_rad
            if square > 1:
                out.append(square)
        return out

    def _sqrt_as_surd(self, n: int) -> tuple[int, int]:
        outside, inside = self._split_square(n)
        return outside, inside

    def _split_square(self, n: int) -> tuple[int, int]:
        if n <= 0:
            return 0, 1

        outside = 1
        inside = n
        factor = 2
        while factor * factor <= inside:
            while inside % (factor * factor) == 0:
                outside *= factor
                inside //= factor * factor
            factor += 1
        return outside, inside

    def _simplify(self, sign: int, mult: int, rad: int, den: int) -> _SurdRational:
        if mult == 0:
            return _SurdRational(1, 0, 1, 1)

        outside, inside = self._split_square(rad)
        mult *= outside

        if den != 0:
            common = gcd(mult, den)
            if common > 1:
                mult //= common
                den //= common

        if den < 0:
            den *= -1
            sign *= -1

        return _SurdRational(-1 if sign < 0 else 1, mult, inside, den)

    def _surd_to_text(self, mult: int, rad: int) -> str:
        if mult == 0:
            return "0"
        if rad == 1:
            return str(mult)
        if mult == 1:
            return f"√{rad}"
        return f"{mult}√{rad}"

    def _format_equation(self, eq: Equation, var1: str, var2: str) -> str:
        return EquationFormatter.format_equation(
            eq.a.to_sympy(),
            eq.b.to_sympy(),
            eq.c.to_sympy(),
            var1,
            var2,
        )

    def _lcm_many(self, values: list[int]) -> int:
        current = 1
        for v in values:
            current = (current * v) // gcd(current, v)
        return current

    def _gcd_many(self, values: list[int]) -> int:
        current = values[0]
        for v in values[1:]:
            current = gcd(current, v)
        return current
