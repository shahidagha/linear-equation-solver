from step_engine.step_builder import StepBuilder

steps = StepBuilder()

steps.add("Step 1", "18x = 90")
steps.add("Step 2", "18x = 90")   # duplicate
steps.add("Step 3", "x = 5")

steps.show()