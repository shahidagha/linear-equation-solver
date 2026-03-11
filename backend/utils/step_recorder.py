from backend.utils.step import Step


class StepRecorder:

    def __init__(self):

        self.steps = []


    def add(self, content):

        step = Step("text", content)

        self.steps.append(step)


    def add_equation(self, eq):

        step = Step("equation", eq)

        self.steps.append(step)


    def add_vertical(self, eq1, eq2, result):

        step = Step(
            "vertical_elimination",
            {
                "eq1": eq1,
                "eq2": eq2,
                "result": result
            }
        )

        self.steps.append(step)


    def add_operation(self, text):

        step = Step("operation", text)

        self.steps.append(step)


    def get_steps(self):

        return self.steps