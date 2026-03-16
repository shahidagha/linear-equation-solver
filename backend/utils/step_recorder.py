from backend.utils.step import Step


class StepRecorder:

    def __init__(self):
        self.steps = []

    def add(self, content, role=None):
        step = Step("text", content, role=role)
        self.steps.append(step)

    def add_equation(self, eq, role=None):
        step = Step("equation", eq, role=role)
        self.steps.append(step)

    def add_vertical(self, eq1, eq2, result, op=None, role=None):
        """op: 'add' or 'subtract' so the renderer shows the correct sign and underset."""
        step = Step(
            "vertical_elimination",
            {"eq1": eq1, "eq2": eq2, "result": result, "op": op},
            role=role,
        )
        self.steps.append(step)

    def add_operation(self, text, role=None):
        step = Step("operation", text, role=role)
        self.steps.append(step)

    def get_steps(self):
        return self.steps