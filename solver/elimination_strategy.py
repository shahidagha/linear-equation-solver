class EliminationStrategy:

    def detect(self, eq1, eq2):

        a1,b1,c1 = eq1
        a2,b2,c2 = eq2

        # Direct elimination
        if abs(a1) == abs(a2) or abs(b1) == abs(b2):
            return "DIRECT"

        # Cross elimination
        if a1 == b2 and b1 == a2:
            return "CROSS"

        # Otherwise
        return "LCM"