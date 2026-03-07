from sympy import symbols
from latex.latex_formatter import LatexFormatter

# define variables
x, y = symbols('x y')

# create expression
expr = 2*x + 3*y

# latex formatter
formatter = LatexFormatter()

latex_output = formatter.format_expression(expr)

print("Expression:")
print(expr)

print("\nLaTeX Output:")
print(latex_output)