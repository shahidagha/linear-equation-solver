from backend.math_engine.fraction_surd import FractionSurd
from backend.math_engine.equation import Equation
from backend.math_engine.system import EquationSystem

from backend.solver.elimination_solver import EliminationSolver
from backend.solver.graphical_solver import GraphicalSolver

from backend.latex.latex_generator import LatexGenerator


# -----------------------------
# Equation 1
# -----------------------------

a1 = FractionSurd(2,1,1,1,1)
b1 = FractionSurd(1,1,1,1,1)
c1 = FractionSurd(7,1,1,1,1)

eq1 = Equation(a1,b1,c1)


# -----------------------------
# Equation 2
# -----------------------------

a2 = FractionSurd(4,1,1,1,1)
b2 = FractionSurd(-7,1,1,1,1)
c2 = FractionSurd(41,1,1,1,1)

eq2 = Equation(a2,b2,c2)


# -----------------------------
# Build System
# -----------------------------

system = EquationSystem(eq1,eq2)


# -----------------------------
# Elimination Method
# -----------------------------

solver = EliminationSolver(system)

solution = solver.solve()


# -----------------------------
# Graphical Method
# -----------------------------

print("\nRunning Graphical Solver...\n")

graph_solver = GraphicalSolver(system)

points1, points2 = graph_solver.generate_tables()

print("Graphical Method Points\n")

print("Equation 1 Points:", points1)
print("Equation 2 Points:", points2)


# -----------------------------
# Print Recorded Steps
# -----------------------------

print("\nRecorded Steps:\n")

for step in solver.recorder.get_steps():

    if step.type == "vertical_elimination":

        data = step.content

        print("")
        print(f"  {data['eq1']}")
        print(f"+ {data['eq2']}")
        print("--------------")
        print(f"  {data['result']}")
        print("")

    else:

        print(step.content)


# -----------------------------
# Generate LaTeX
# -----------------------------

latex = LatexGenerator(solver.recorder.get_steps())

latex_output = latex.generate()

print("\nLaTeX Output:\n")
print(latex_output)


# -----------------------------
# Final Solution
# -----------------------------

print("\nFinal Solution:", solution)
