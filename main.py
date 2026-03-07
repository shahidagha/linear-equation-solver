from models.equation import Equation
from models.equation_system import EquationSystem
from solver.elimination_solver import EliminationSolver

# create equations
eq1 = Equation(2, 3, 4)
eq2 = Equation(1, 1, 1)

# create system
system = EquationSystem(eq1, eq2)

print("System of Equations:")
print(system.display())

# solve
solver = EliminationSolver()
solution = solver.solve(system)

print("\nSolution:")
print(solution)