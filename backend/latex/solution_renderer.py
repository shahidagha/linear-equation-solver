import re
from typing import Any, Dict, List, Optional

import sympy as sp


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
        raw_equations: Optional[List[str]] = None,
        standardization_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, str]:
        steps = steps or []
        raw_equations = raw_equations or equations
        # Given block shows user-defined raw equations; fall back to standardized only if no raw provided
        given_equations = raw_equations if raw_equations else equations

        detailed_lines = self._given_equations_block(given_equations)
        medium_lines = self._given_equations_block(given_equations)
        # Short: standardization = Given + eq (1) + eq (2) only; method steps appended later as before
        if standardization_steps:
            short_lines = self._given_equations_block(given_equations)
            if equations:
                short_lines.append(f"{equations[0]}\\; ...(1)")
            if len(equations) > 1:
                short_lines.append(f"{equations[1]}\\; ...(2)")
        else:
            short_lines = self._given_equations_block(given_equations)

        if standardization_steps:
            self._append_standardization(standardization_steps, detailed_lines, medium_lines)

        if method_name == "elimination":
            self._append_elimination(steps, detailed_lines, medium_lines, short_lines)
        elif method_name == "substitution":
            self._append_substitution(equations, solution, detailed_lines, medium_lines, short_lines)
        elif method_name == "cramer":
            self._append_cramer(equations, solution, detailed_lines, medium_lines, short_lines)
        elif method_name == "graphical":
            self._append_graphical(graph_data or {}, equations, detailed_lines, medium_lines, short_lines)

        final_answer = self._final_answer(solution)
        detailed_lines.append(final_answer)
        medium_lines.append(final_answer)
        short_lines.append(final_answer)

        return {
            "latex_detailed": self._aligned(detailed_lines),
            "latex_medium": self._aligned(medium_lines),
            "latex_short": self._aligned(short_lines),
        }

    def _given_equations_block(self, equations: List[str]) -> List[str]:
        """Render raw user input as a right-brace 'Given equations' block."""
        if not equations:
            return ["\\text{Given equations}"]

        body = " \\\\ ".join(equations)
        block = f"\\left.\\begin{{aligned}} {body} \\end{{aligned}}\\right\\}}\\;\\text{{Given equations}}"
        return [block]

    def _standardization_text_for_medium(self, content: str) -> str:
        """Shorten standardization text for medium only; detailed and short unchanged."""
        if not content:
            return content
        out = content.replace(" to make the leading coefficient positive.", "")
        out = out.replace(" to remove denominators.", "")
        out = out.replace(" to simplify coefficients.", "")
        return out

    def _append_standardization(self, steps: List[Dict[str, Any]], detailed: List[str], medium: List[str]) -> None:
        """Append standardization step content to detailed and medium only (short uses Given + eq1 + eq2)."""
        for step in steps:
            s_type = step.get("type")
            content = step.get("content", "")
            if not content:
                continue
            if s_type == "equation":
                detailed.append(content)
                medium.append(content)
            elif s_type == "text":
                for ln in self._wrap_text(content):
                    line = f"\\text{{{self._escape_text(ln)}}}"
                    detailed.append(line)
                medium_content = self._standardization_text_for_medium(content)
                for ln in self._wrap_text(medium_content):
                    medium.append(f"\\text{{{self._escape_text(ln)}}}")

    def _append_elimination(self, steps, detailed, medium, short):
        last_content = None
        # Short = medium minus steps (1), (3), (5), (7), (9), (11) by append order
        medium_step = 0
        _skip_short = (1, 3, 5, 7, 9, 11)

        for step in steps:
            s_type = step.get("type")
            if s_type == "vertical_elimination":
                block = self._vertical_array(
                    step["eq1"], step["eq2"], step["result"], op=step.get("op")
                )
                detailed.append(block)
                medium.append(block)
                medium_step += 1
                if medium_step not in _skip_short:
                    short.append(block)
            elif s_type == "substitution_intro":
                # Detailed: why we chose this equation; Medium: short substitution line only
                detailed_content = step.get("detailed_content", "")
                content = step.get("content", "")
                for ln in self._wrap_text(detailed_content):
                    detailed.append(f"\\text{{{self._escape_text(ln)}}}")
                if content:
                    medium.append(f"\\text{{{self._escape_text(content)}}}")
                    medium_step += 1
                    if medium_step not in _skip_short:
                        short.append(f"\\text{{{self._escape_text(content)}}}")
            elif s_type == "divide_step":
                # Step (5): detailed and medium text; short blank
                detailed_content = step.get("detailed", "")
                medium_content = step.get("medium", "")
                for ln in self._wrap_text(detailed_content):
                    detailed.append(f"\\text{{{self._escape_text(ln)}}}")
                if medium_content:
                    line = f"\\text{{{self._escape_text(medium_content)}}}"
                    medium.append(line)
                    medium_step += 1
                    if medium_step not in _skip_short:
                        short.append(line)
            elif s_type == "detailed_only":
                # Step (11): only in detailed; blank for medium and short
                content = step.get("content", "")
                for ln in self._wrap_text(content):
                    detailed.append(f"\\text{{{self._escape_text(ln)}}}")
            elif s_type in {"operation", "text", "equation"}:
                content = step.get("content", "")
                if not content:
                    continue
                if content == last_content:
                    continue
                last_content = content
                if s_type == "equation":
                    # Equation content is LaTeX; append as-is so it renders in the aligned environment
                    detailed.append(content)
                    medium.append(content)
                    medium_step += 1
                    if medium_step not in _skip_short:
                        short.append(content)
                else:
                    # Strategy explanations and other prose are rendered as wrapped text.
                    # We soft-wrap long sentences into multiple shorter lines so there is
                    # no horizontal scrolling in the aligned environment.
                    lines = self._wrap_text(content)

                    # LCM / Six step strategy explanations appear only in detailed view.
                    lcm_expl = (
                        "Elimination strategy: LCM" in content
                        or "Using LCM Elimination strategy" in content
                        or "Six step Method" in content
                        or "Using Six Step Method" in content
                        or "Elimination Strategy: Six step" in content
                    )
                    for ln in lines:
                        text_line = f"\\text{{{self._escape_text(ln)}}}"
                        detailed.append(text_line)
                        if not lcm_expl:
                            medium.append(text_line)
                            medium_step += 1
                            if medium_step not in _skip_short:
                                short.append(text_line)

        if medium_step == 0:
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

    def _format_coord(self, value: Any) -> str:
        """Format a numeric coordinate for LaTeX (integer or fraction)."""
        try:
            n = float(value)
            if n == int(n):
                return str(int(n))
            return sp.latex(sp.simplify(sp.S(str(value))))
        except (TypeError, ValueError):
            return str(value)

    def _points_table_latex(self, points: List[List[Any]]) -> str:
        """Build LaTeX array: x row, y row, (x,y) row. Uses up to 3 points."""
        points = points[:3]
        if not points:
            return "\\varnothing"
        x_vals = [self._format_coord(p[0]) for p in points]
        y_vals = [self._format_coord(p[1]) for p in points]
        pair_vals = [f"({self._format_coord(p[0])}, {self._format_coord(p[1])})" for p in points]
        n = len(points)
        cols = "|c|" + "c|" * n
        row_x = "x & " + " & ".join(x_vals) + " \\\\"
        row_y = "y & " + " & ".join(y_vals) + " \\\\"
        row_xy = "(x, y) & " + " & ".join(pair_vals) + " \\\\"
        return (
            f"\\begin{{array}}{{{cols}}}\n"
            "\\hline\n"
            f"{row_x}\n"
            "\\hline\n"
            f"{row_y}\n"
            "\\hline\n"
            f"{row_xy}\n"
            "\\hline\n"
            "\\end{array}"
        )

    def _append_graphical(self, graph_data, equations: List[str], detailed, medium, short):
        p1 = graph_data.get("equation1_points", [])
        p2 = graph_data.get("equation2_points", [])
        eq1_line = (equations[0] if equations else "") + " \\; ...(1)"
        eq2_line = (equations[1] if len(equations) > 1 else "") + " \\; ...(2)"
        table1 = self._points_table_latex(p1)
        table2 = self._points_table_latex(p2)
        for lines in (detailed, medium, short):
            lines.append(eq1_line + ":")
            lines.append(table1)
            lines.append(eq2_line + ":")
            lines.append(table2)

    def _vertical_array(self, eq1: str, eq2: str, result: str, op: str = None) -> str:
        t1 = self._split_equation(eq1)
        t2 = self._split_equation(eq2)
        t3 = self._split_equation(result)

        # Use explicit op from solver when provided ("add" -> +, "subtract" -> -); else infer from signs
        if op == "add":
            op = "+"
        elif op == "subtract":
            op = "-"
        else:
            op = "-" if self._same_sign(t1[1], t2[1]) else "+"
        eq2_sign = "\\boldsymbol{-}" if op == "-" else "\\boldsymbol{+}"
        # For addition there is no sign change, so no underset labels; for subtraction show (op) under terms
        if op == "+":
            row2 = f"&\\kern{{-5pt}}{eq2_sign} &\\kern{{-5pt}} &\\kern{{-5pt}}{{{t2[0]}}} &\\kern{{-5pt}} {t2[1]} &\\kern{{-5pt}} {t2[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} &\\kern{{-5pt}}{{{t2[3]}}} \\\\"
        else:
            row2 = f"&\\kern{{-5pt}}{eq2_sign} &\\kern{{-5pt}} \\underset{{({op})}}{{}}&\\kern{{-5pt}}{{{t2[0]}}} &\\kern{{-5pt}} \\underset{{({op})}}{{{t2[1]}}} &\\kern{{-5pt}} {t2[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} \\underset{{({op})}}{{}}&\\kern{{-5pt}}{{{t2[3]}}} \\\\"

        return (
            "\\begin{array}{cccccccc}"
            f" &\\kern{{-5pt}} &\\kern{{-5pt}} &\\kern{{-5pt}}{t1[0]} &\\kern{{-5pt}} {t1[1]} &\\kern{{-5pt}} {t1[2]} &\\kern{{-5pt}} = &\\kern{{-5pt}} &\\kern{{-5pt}} {t1[3]} \\\\"
            f"{row2}"
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
        # Single-term left-hand side (e.g. "x = 1"): no explicit + term.
        # Use empty sign so the vertical layout does not show an extra "+".
        return lhs, "", "", rhs

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
        a_latex = sp.latex(sp.simplify(sp.S(str(a)))) if a != "" and a is not None else ""
        b_latex = sp.latex(sp.simplify(sp.S(str(b)))) if b != "" and b is not None else ""
        return f"\\therefore ({self.var1},{self.var2}) = ({a_latex},{b_latex}) \\text{{ is the solution of the given equations.}}"

    def _aligned(self, lines: List[str]) -> str:
        """Build aligned block; add [6pt] vertical space after lines that contain fraction coefficients."""
        if not lines:
            return "\\begin{aligned}\n\\end{aligned}"
        body_parts = []
        for i, line in enumerate(lines):
            body_parts.append(f"& {line}")
            if i < len(lines) - 1:
                body_parts.append(" \\\\[6pt]\n" if "\\frac" in line else " \\\\\n")
        body = "".join(body_parts)
        return f"\\begin{{aligned}}\n{body}\n\\end{{aligned}}"

    def _points_to_latex(self, points: List[List[Any]]) -> str:
        if not points:
            return "\\varnothing"
        return ",\\;".join([f"({p[0]},{p[1]})" for p in points])

    def _escape_text(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("_", "\\_")

    def _wrap_text(self, value: str, max_len: int = 70) -> List[str]:
        """Soft-wrap a plain text string into multiple lines of at most max_len chars."""
        words = value.split()
        if not words:
            return [value]

        lines: List[str] = []
        current: List[str] = []
        current_len = 0

        for w in words:
            extra = len(w) + (1 if current else 0)
            if current and current_len + extra > max_len:
                lines.append(" ".join(current))
                current = [w]
                current_len = len(w)
            else:
                current.append(w)
                current_len += extra

        if current:
            lines.append(" ".join(current))

        return lines
