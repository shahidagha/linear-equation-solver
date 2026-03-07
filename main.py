from models.equation import Equation
from models.equation_system import EquationSystem
from solver.elimination_solver import EliminationSolver
from step_engine.step_manager import StepManager

# create equations
eq1 = Equation(2, 3, 4)
eq2 = Equation(1, 1, 1)

system = EquationSystem(eq1, eq2)

print("System of Equations:")
print(system.display())

# step manager
steps = StepManager()

steps.add_step("Equation (1)", eq1.display())
steps.add_step("Equation (2)", eq2.display())

# solver
solver = EliminationSolver()
solution = solver.solve(system)

steps.add_step("Solution", solution)

# show steps
steps.show_steps()