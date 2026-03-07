import sympy as sp

class Normalizer:

    def normalize(self, eq):

        a = eq.a
        b = eq.b
        c = eq.c

        # convert FractionSurd if needed
        if hasattr(a,"to_sympy"):
            a = a.to_sympy()

        if hasattr(b,"to_sympy"):
            b = b.to_sympy()

        expr = sp.Eq(a*sp.symbols('x') + b*sp.symbols('y'), c)

        # Step 3: ensure first coefficient positive
        if a < 0:
            a = -a
            b = -b
            c = -c

        # Step 4: clear denominators
        a,b,c = sp.together(a), sp.together(b), sp.together(c)

        # Step 5: simplify
        a = sp.simplify(a)
        b = sp.simplify(b)
        c = sp.simplify(c)

        return a,b,c