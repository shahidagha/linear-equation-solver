from math_engine.fraction_surd import FractionSurd
from math_engine.equation import Equation


a = FractionSurd(3,2,1,1,1)     # 3√2
b = FractionSurd(5,1,1,3,-1)    # -5/√3
c = FractionSurd(7,1,1,1,1)     # 7


eq = Equation(a,b,c)

print(eq)