class StepBuilder:

    def __init__(self):
        self.steps = []

    def add(self, description, expression):

        step = {
            "description": description,
            "expression": expression
        }

        self.steps.append(step)

    def show(self):

        for step in self.steps:

            print("\n" + step["description"])
            print(step["expression"])