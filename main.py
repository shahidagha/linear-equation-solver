from step_engine.step_builder import StepBuilder

steps = StepBuilder()

steps.add("Equation (1)", "2x + 3y = 4")
steps.add("Equation (2)", "x + y = 1")
steps.add("Multiply equation (2) by 2", "2x + 2y = 2")
steps.add("Subtract equations", "y = 2")
steps.add("Substitute y = 2", "x = -1")

print("SHORT MODE")
steps.show("short")

print("\nNORMAL MODE")
steps.show("normal")