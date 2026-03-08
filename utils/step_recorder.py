class StepRecorder:

    def __init__(self):

        self.steps = []


    def add(self, text):

        # prevent duplicate steps
        if len(self.steps) == 0 or self.steps[-1] != text:
            self.steps.append(text)


    def get_steps(self):

        return self.steps