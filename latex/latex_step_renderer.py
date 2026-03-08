class LatexStepRenderer:

    def __init__(self, steps):

        self.steps = steps


    def render_vertical(self, data):

        eq1 = data["eq1"]
        eq2 = data["eq2"]
        result = data["result"]

        latex = []

        latex.append("\\begin{array}{cccc}")
        latex.append(f"{eq1} \\\\")
        latex.append(f"+ {eq2} \\\\")
        latex.append("\\hline")
        latex.append(f"{result}")
        latex.append("\\end{array}")

        return "\n".join(latex)


    def generate(self):

        lines = []

        lines.append("\\begin{aligned}")

        for step in self.steps:

            if step.type == "vertical_elimination":

                vertical_block = self.render_vertical(step.content)

                lines.append("& " + vertical_block + " \\\\")

            else:

                text = step.content.replace("_", "\\_")

                lines.append(f"& {text} \\\\")

        lines.append("\\end{aligned}")

        return "\n".join(lines)