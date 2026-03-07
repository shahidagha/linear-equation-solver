from models.equation import Equation
from models.equation_system import EquationSystem
from solver.cramer_solver import CramerSolver

# equations
eq1 = Equation(2,1,7)
eq2 = Equation(4,-7,41)

system = EquationSystem(eq1,eq2)

solver = CramerSolver()

solution = solver.solve(system)

print("Cramer Solution:")
print(solution)