from models.coefficient import FractionSurd
from models.equation import Equation
from normalization.normalizer import Normalizer

# example equation
a = FractionSurd(3,2,1,1)     # 3√2
b = FractionSurd(5,1,1,3)     # 5/(√3)
c = 7

eq = Equation(a,b,c)

print("Original Equation:")
print(eq.display())

normalizer = Normalizer()

a,b,c = normalizer.normalize(eq)

print("\nNormalized:")
print(a,"x +",b,"y =",c)