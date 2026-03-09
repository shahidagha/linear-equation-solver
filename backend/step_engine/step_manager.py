class StepManager:

    def __init__(self):
        self.steps = []

    def add_step(self, description, expression):
        self.steps.append((description, expression))

    def show_steps(self):

        for step in self.steps:
            print("\n", step[0])
            print(step[1])