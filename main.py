from solver.graphical_solver import GraphicalSolver

solver = GraphicalSolver()

# equation x + y = 5
points = solver.generate_points(1,1,5)

solver.generate_table(points)