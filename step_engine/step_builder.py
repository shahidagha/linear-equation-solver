from step_engine.duplicate_filter import DuplicateFilter

class StepBuilder:

    def __init__(self):

        self.steps = []
        self.filter = DuplicateFilter()

    def add(self, description, expression):

        step = {
            "description": description,
            "expression": expression
        }

        self.steps.append(step)

    def show(self):

        filtered = self.filter.filter(self.steps)

        for step in filtered:

            print("\n" + step["description"])
            print(step["expression"])