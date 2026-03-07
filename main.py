from models.coefficient import FractionSurd
from models.equation import Equation

# coefficients
a = FractionSurd(3,2,1,1)    # 3√2
b = FractionSurd(5,1,1,3)    # 5/(√3)

c = 7

eq = Equation(a,b,c)

print("Equation:")
print(eq.display())

print("\nSymPy form:")
print(eq.to_sympy())