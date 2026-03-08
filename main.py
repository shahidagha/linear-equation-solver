from math_engine.fraction_surd import FractionSurd


a = FractionSurd(3,2,1,1,1)     # 3√2
b = FractionSurd(5,1,1,3,-1)    # -5/√3

print("a =", a)
print("b =", b)

print("a + b =", a.add(b))
print("a * b =", a.multiply(b))