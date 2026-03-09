import sympy as sp


class EquationFormatter:

    @staticmethod
    def term_to_latex(coeff, var):

        coeff = sp.simplify(coeff)

        if coeff == 1:
            return f"{var}"

        if coeff == -1:
            return f"-{var}"

        return f"{sp.latex(coeff)}{var}"


    @staticmethod
    def format_equation(a, b, c, var1="x", var2="y"):

        a = sp.simplify(a)
        b = sp.simplify(b)
        c = sp.simplify(c)

        x_term = EquationFormatter.term_to_latex(a, var1)
        y_term = EquationFormatter.term_to_latex(abs(b), var2)

        if b >= 0:
            left = f"{x_term} + {y_term}"
        else:
            left = f"{x_term} - {y_term}"

        right = sp.latex(c)

        return f"{left} = {right}"