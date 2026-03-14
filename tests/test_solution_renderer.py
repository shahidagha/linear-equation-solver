"""Unit tests for SolutionLatexRenderer (wrap logic, verbosity levels, final answer)."""
import pytest

from backend.latex.solution_renderer import SolutionLatexRenderer


def test_render_returns_three_verbosity_levels():
    """Renderer returns latex_detailed, latex_medium, latex_short."""
    r = SolutionLatexRenderer(var1="x", var2="y")
    out = r.render(
        method_name="elimination",
        equations=["2x + y = 7", "4x - 7y = 41"],
        solution={"x": 5, "y": -3},
        steps=[],
    )
    assert "latex_detailed" in out
    assert "latex_medium" in out
    assert "latex_short" in out
    assert "\\\\" in out["latex_detailed"] or "aligned" in out["latex_detailed"]


def test_final_answer_unique_solution():
    """_final_answer for unique solution produces (x,y) = (5,-3) style."""
    r = SolutionLatexRenderer(var1="x", var2="y")
    result = r._final_answer({"x": 5, "y": -3})
    assert "\\therefore" in result
    assert "x" in result and "y" in result
    assert "5" in result and "-3" in result


def test_final_answer_degenerate_message():
    """_final_answer for degenerate uses solution_type and message."""
    r = SolutionLatexRenderer(var1="x", var2="y")
    result = r._final_answer({
        "solution_type": "none",
        "message": "The system has no solution (inconsistent).",
    })
    assert "\\therefore" in result
    assert "no solution" in result or "inconsistent" in result


def test_wrap_latex_short_line_unchanged():
    """Short line is returned as single element."""
    r = SolutionLatexRenderer()
    lines = r._wrap_latex("2x + y = 7")
    assert lines == ["2x + y = 7"]


def test_wrap_latex_long_line_splits():
    """Long line (over 70 chars) is split into multiple lines."""
    r = SolutionLatexRenderer()
    long_line = "\\text{" + "word " * 20 + "}"
    lines = r._wrap_latex(long_line, max_len=70)
    assert len(lines) >= 2
    for ln in lines:
        assert len(ln) <= 80  # allow some slack


def test_given_equations_block():
    """_given_equations_block produces Given equations block."""
    r = SolutionLatexRenderer()
    block = r._given_equations_block(["2x + y = 7", "4x - 7y = 41"])
    assert len(block) == 1
    assert "aligned" in block[0]
    assert "Given" in block[0] or "given" in block[0].lower()


def test_aligned_wraps_lines():
    """_aligned produces \\begin{aligned} ... \\end{aligned}."""
    r = SolutionLatexRenderer()
    out = r._aligned(["a", "b"])
    assert out.startswith("\\begin{aligned}")
    assert out.endswith("\\end{aligned}")
    assert "a" in out and "b" in out
