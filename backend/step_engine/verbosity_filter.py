class VerbosityFilter:

    def filter(self, steps, level):

        if level == "short":

            return [steps[0], steps[-1]]

        elif level == "normal":

            return steps

        elif level == "detailed":

            return steps

        else:

            return steps