class Step:

    def __init__(self, description, expression):
        self.description = description
        self.expression = expression

    def display(self):
        return f"{self.description}\n{self.expression}"