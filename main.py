from models.equation import Equation
from models.equation_system import EquationSystem
from solver.substitution_solver import SubstitutionSolver

# equations
eq1 = Equation(1,1,1)
eq2 = Equation(2,3,4)

system = EquationSystem(eq1,eq2)

solver = SubstitutionSolver()

solution = solver.solve(system)

print("Substitution Solution:")
print(solution)