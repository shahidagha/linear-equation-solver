from solver.elimination_strategy import EliminationStrategy

strategy = EliminationStrategy()

eq1 = (3,1,18)
eq2 = (4,14,17)

result = strategy.detect(eq1,eq2)

print("Elimination Strategy:")
print(result)