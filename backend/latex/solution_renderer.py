import re
from typing import Any, Dict, List, Optional


class SolutionLatexRenderer:
    """Render solver output into MathJax/KaTeX-friendly LaTeX blocks."""

    def __init__(self, var1: str = "x", var2: str = "y"):
        self.var1 = var1
        self.var2 = var2

    def render(
        self,
        method_name: str,
        equations: List[str],
        solution: Dict[str, Any],
        steps: Optional[List[Dict[str, Any]]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        steps = steps or []

        detailed_lines = self._equation_lines(equations)
        medium_lines = self._equation_lines(equations)
        short_lines = self._equation_lines(equations)

        if method_name == "elimination":
            self._append_elimination(steps, detailed_lines, medium_lines, short_lines)
        elif method_name == "substitution":
            self._append_substitution(equations, solution, detailed_lines, medium_lines, short_lines)
        elif method_name == "cramer":
            self._append_cramer(equations, solution, detailed_lines, medium_lines, short_lines)
        elif method_name == "graphical":
            self._append_graphical(graph_data or {}, detailed_lines, medium_lines, short_lines)

        final_answer = self._final_answer(solution)
        detailed_lines.append(final_answer)
        medium_lines.append(final_answer)
        short_lines.append(final_answer)

        return {
            "latex_detailed": self._aligned(detailed_lines),
            "latex_medium": self._aligned(medium_lines),
            "latex_short": self._aligned(short_lines),
        }

    def _equation_lines(self, equations: List[str]) -> List[str]:
        rendered = []
        for idx, eq in enumerate(equations, start=1):
            rendered.append(f"{eq}\\quad ({idx})")
        return rendered

    def _append_elimination(self, steps, detailed, medium, short):
        for step in steps:
            s_type = step.get("type")
            if s_type == "vertical_elimination":
                block = self._vertical_array(step["eq1"], step["eq2"], step["result"])
                detailed.append(block)
                medium.append(block)
            elif s_type in {"operation", "text", "equation"}:
                content = step.get("content", "")
                if not content:
                    continue
                detailed.append(f"\\text{{{self._escape_text(content)}}}")
                if s_type == "equation":
                    medium.append(content)

        short.append("\\text{Elimination completed.}")

    def _append_substitution(self, equations, solution, detailed, medium, short):
        eq1 = equations[0]
        detailed.append("\\text{Solve (1) for one variable and substitute into (2).}")
        detailed.append(f"\\text{{From (1): }} {eq1}")
        medium.append("\\text{Substitute expression from (1) into (2).}")
        short.append("\\text{Substitution method applied.}")

    def _append_cramer(self, equations, solution, detailed, medium, short):
        # Equations are expected in form ax + by = c
        coeffs = [self._parse_coeffs(eq) for eq in equations]
        if any(c is None for c in coeffs):
            detailed.append("\\text{Cramer's rule applied.}")
            medium.append("\\text{Cramer's rule applied.}")
            short.append("\\text{Cramer.}")
            return

        (a1, b1, c1), (a2, b2, c2) = coeffs

        d = f"\\begin{{vmatrix}} {a1} & {b1} \\\\ {a2} & {b2} \\end{{vmatrix}}"
        dx = f"\\begin{{vmatrix}} {c1} & {b1} \\\\ {c2} & {b2} \\end{{vmatrix}}"
        dy = f"\\begin{{vmatrix}} {a1} & {c1} \\\\ {a2} & {c2} \\end{{vmatrix}}"

        detailed.extend([
            "\\text{Compute determinants:}",
            f"D = {d}",
            f"D_x = {dx}",
            f"D_y = {dy}",
            f"{self.var1} = \\frac{{D_x}}{{D}}",
            f"{self.var2} = \\frac{{D_y}}{{D}}",
        ])
        medium.extend([f"D = {d}", f"D_x = {dx}", f"D_y = {dy}"])
        short.append("\\text{Cramer's determinants evaluated.}")

    def _append_graphical(self, graph_data, detailed, medium, short):
        p1 = graph_data.get("equation1_points", [])
        p2 = graph_data.get("equation2_points", [])
        detailed.append(f"\\text{{Equation 1 points: }} {self._points_to_latex(p1)}")
        detailed.append(f"\\text{{Equation 2 points: }} {self._points_to_latex(p2)}")
        medium.append("\\text{Plotted both equations and read intersection.}")
        short.append("\\text{Graphical intersection determined.}")

    def _vertical_array(self, eq1: str, eq2: str, result: str) -> str:
        t1 = self._split_equation(eq1)
        t2 = self._split_equation(eq2)
        t3 = self._split_equation(result)

        op = "-" if self._same_sign(t1[1], t2[1]) else "+"
        eq2_sign = "\\boldsymbol{-}" if op == "-" else "\\boldsymbol{+}"

        return (
            "\\begin{array}{cccccccc}"
            f" &\\kern{{-5pt}} &\\kern{{-5pt}} &\\kern{{-5pt}}{t1[0]} &\\kern{{-5pt}} {t1[1]} &\\kern{{-5pt}} {t1[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} &\\kern{{-5pt}} {t1[3]} \\\\"
            f"&\\kern{{-5pt}}{eq2_sign} &\\kern{{-5pt}} \\underset{{({op})}}{{}}&\\kern{{-5pt}}{{{t2[0]}}} &\\kern{{-5pt}} \\underset{{({op})}}{{{t2[1]}}} &\\kern{{-5pt}} {t2[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} \\underset{{({op})}}{{}}&\\kern{{-5pt}}{{{t2[3]}}} \\\\"
            "\\hline"
            f" &\\kern{{-5pt}} &\\kern{{-5pt}} &\\kern{{-5pt}}{t3[0]} &\\kern{{-5pt}} {t3[1]} &\\kern{{-5pt}} {t3[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} &\\kern{{-5pt}} {t3[3]}"
            "\\end{array}"
        )

    def _split_equation(self, equation: str):
        compact = equation.strip()
        if "=" not in compact:
            return compact, "+", "", ""
        lhs, rhs = [p.strip() for p in compact.split("=", 1)]
        m = re.match(r"(.+?)\s*([+-])\s*(.+)", lhs)
        if m:
            return m.group(1).strip(), m.group(2), m.group(3).strip(), rhs
        return lhs, "+", "", rhs

    def _same_sign(self, sign1: str, sign2: str) -> bool:
        return sign1 == sign2

    def _parse_coeffs(self, equation: str):
        m = re.match(
            r"\s*([^ ]+)" + re.escape(self.var1) + r"\s*([+-])\s*([^ ]+)" + re.escape(self.var2) + r"\s*=\s*(.+)",
            equation,
        )
        if not m:
            return None
        a = m.group(1)
        if a in {"", "+"}:
            a = "1"
        if a == "-":
            a = "-1"
        b = m.group(3)
        if m.group(2) == "-":
            b = f"-{b}"
        c = m.group(4)
        return a, b, c

    def _final_answer(self, solution: Dict[str, Any]) -> str:
        a = solution.get(self.var1, "")
        b = solution.get(self.var2, "")
        return f"({self.var1},{self.var2}) = ({a},{b})"

    def _aligned(self, lines: List[str]) -> str:
        body = " \\\\\n".join(f"& {line}" for line in lines)
        return f"\\begin{{aligned}}\n{body}\n\\end{{aligned}}"

    def _points_to_latex(self, points: List[List[Any]]) -> str:
        if not points:
            return "\\varnothing"
        return ",\\;".join([f"({p[0]},{p[1]})" for p in points])

    def _escape_text(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("_", "\\_")
