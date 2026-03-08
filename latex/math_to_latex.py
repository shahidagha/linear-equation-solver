import sympy as sp


class MathToLatex:

    @staticmethod
    def convert(expr):

        try:

            sym_expr = sp.sympify(expr)

            return sp.latex(sym_expr)

        except Exception:

            return str(expr)