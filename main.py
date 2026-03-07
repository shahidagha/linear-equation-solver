from models.equation import Equation
from models.equation_system import EquationSystem
from normalization.normalizer import Normalizer

# create equations
eq1 = Equation(2, 3, 4)
eq2 = Equation(-1, -1, -1)

# create system
system = EquationSystem(eq1, eq2)

print("Original System:")
print(system.display())

# normalize
normalizer = Normalizer()

a, b, c = normalizer.normalize(eq2)

print("\nNormalized Equation 2:")
print(f"{a}x + {b}y = {c}")