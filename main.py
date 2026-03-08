from math_engine.fraction_surd import FractionSurd
from math_engine.equation import Equation
from math_engine.system import EquationSystem


# Equation 1
a1 = FractionSurd(3,2,1,1,1)
b1 = FractionSurd(5,1,1,3,-1)
c1 = FractionSurd(7,1,1,1,1)

eq1 = Equation(a1,b1,c1)


# Equation 2
a2 = FractionSurd(2,1,1,1,1)
b2 = FractionSurd(1,1,1,1,1)
c2 = FractionSurd(4,1,1,1,1)

eq2 = Equation(a2,b2,c2)


system = EquationSystem(eq1,eq2)

print(system)