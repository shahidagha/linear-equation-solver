class Step:

    def __init__(self, step_type, content, role=None):
        self.type = step_type
        self.content = content
        self.role = role

    def __str__(self):
        return f"{self.type}: {self.content}"