from models.equation import Equation
from models.equation_system import EquationSystem
from solver.solver_controller import SolverController

# equations
eq1 = Equation(2,3,4)
eq2 = Equation(1,1,1)

system = EquationSystem(eq1,eq2)

controller = SolverController()

print("Substitution Method:")
print(controller.solve(system,"substitution"))

print("\nElimination Method:")
print(controller.solve(system,"elimination"))

print("\nCramer Method:")
print(controller.solve(system,"cramer"))