class DuplicateFilter:

    def filter(self, steps):

        filtered_steps = []
        last_expression = None

        for step in steps:

            expr = step["expression"]

            if expr != last_expression:
                filtered_steps.append(step)
                last_expression = expr

        return filtered_steps