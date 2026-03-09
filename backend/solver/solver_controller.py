from solver.substitution_solver import SubstitutionSolver
from solver.elimination_solver import EliminationSolver
from solver.cramer_solver import CramerSolver

class SolverController:

    def solve(self, system, method):

        if method == "substitution":

            solver = SubstitutionSolver()
            return solver.solve(system)

        elif method == "elimination":

            solver = EliminationSolver()
            return solver.solve(system)

        elif method == "cramer":

            solver = CramerSolver()
            return solver.solve(system)

        else:
            return "Unknown solving method"