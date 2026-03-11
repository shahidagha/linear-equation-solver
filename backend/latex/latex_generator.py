from backend.latex.math_to_latex import MathToLatex


class LatexGenerator:

    def __init__(self, steps):

        self.steps = steps


    def convert_line(self, line):

        parts = line.split()

        converted = []

        for p in parts:

            if any(ch.isdigit() for ch in p):

                converted.append(MathToLatex.convert(p))

            else:

                converted.append(p)

        return " ".join(converted)


    def generate(self):

        lines = []

        lines.append("\\begin{aligned}")

        for step in self.steps:

            content = step.content

            if isinstance(content, str):

                latex_line = self.convert_line(content)

                lines.append(f"& {latex_line} \\\\")

        lines.append("\\end{aligned}")

        return "\n".join(lines)