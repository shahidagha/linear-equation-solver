from step_engine.duplicate_filter import DuplicateFilter
from step_engine.verbosity_filter import VerbosityFilter

class StepBuilder:

    def __init__(self):

        self.steps = []
        self.duplicate_filter = DuplicateFilter()
        self.verbosity_filter = VerbosityFilter()

    def add(self, description, expression):

        step = {
            "description": description,
            "expression": expression
        }

        self.steps.append(step)

    def show(self, level="normal"):

        filtered = self.duplicate_filter.filter(self.steps)

        filtered = self.verbosity_filter.filter(filtered, level)

        for step in filtered:

            print("\n" + step["description"])
            print(step["expression"])