"""
Optional low-level SymPy expression-to-LaTeX conversion. The main pipeline uses
SolutionLatexRenderer and equation_formatter; this module is not imported in the
request path. Kept for reuse or future use.
"""
import sympy as sp


class MathToLatex:

    @staticmethod
    def convert(expr):

        try:

            sym_expr = sp.sympify(expr)

            return sp.latex(sym_expr)

        except Exception:

            return str(expr)