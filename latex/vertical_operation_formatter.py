class VerticalFormatter:

    def add_equations(self, eq1, eq2):

        a1, b1, c1 = eq1
        a2, b2, c2 = eq2

        a = a1 + a2
        b = b1 + b2
        c = c1 + c2

        line1 = f"{a1}x + {b1}y = {c1}"
        line2 = f"+ {a2}x + {b2}y = {c2}"
        line3 = "------------------"
        line4 = f"{a}x + {b}y = {c}"

        return "\n".join([line1,line2,line3,line4])