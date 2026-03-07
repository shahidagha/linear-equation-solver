class Normalizer:

    def normalize(self, equation):
        """
        Ensures equation is in the form:

        ax + by = c
        """

        a = equation.a
        b = equation.b
        c = equation.c

        # Step 1: ensure first coefficient positive
        if a < 0:
            a = -a
            b = -b
            c = -c

        return a, b, c