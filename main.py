from sympy import symbols, Eq, solve

# Define variables
x, y = symbols('x y')

# Define equations
eq1 = Eq(2*x + 3*y, 4)
eq2 = Eq(x + y, 1)

# Solve system
solution = solve((eq1, eq2), (x, y))

print("Solution:", solution)