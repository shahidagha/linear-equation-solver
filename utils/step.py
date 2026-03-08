class Step:

    def __init__(self, step_type, content):

        self.type = step_type
        self.content = content

    def __str__(self):

        return f"{self.type}: {self.content}"