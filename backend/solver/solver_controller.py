from backend.solver.substitution_solver import SubstitutionSolver
from backend.solver.elimination_solver import EliminationSolver
from backend.solver.cramer_solver import CramerSolver


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
