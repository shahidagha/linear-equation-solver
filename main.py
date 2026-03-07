from models.equation import Equation
from models.equation_system import EquationSystem
from step_engine.step_builder import StepBuilder

# equations
eq1 = Equation(2,3,4)
eq2 = Equation(1,1,1)

system = EquationSystem(eq1,eq2)

steps = StepBuilder()

steps.add("Equation (1)", eq1.display())
steps.add("Equation (2)", eq2.display())

steps.add("Multiply equation (2) by 2", "2x + 2y = 2")

steps.add("Subtract equations", "y = 2")

steps.add("Substitute y = 2", "x = -1")

steps.show()