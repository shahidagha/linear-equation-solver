"""
Canonical roles for solution steps. Verbosity is defined by which roles to show:
- Detailed: all roles (teacher explanation + calculation block)
- Medium: block_intro + calculation block only (student_* + final_result_text); no explanation_calc
- Short: student_calc_last_line + student_result_text + final_result_text

For Cramer determinants: steps 1+3 (symbolic matrix, formula) = teacher = EXPLANATION_CALC (Detailed only);
steps 2,4,5 (filled matrix, numeric formula, simplify) = calculation = STUDENT_CALC (Detailed + Medium).
"""
# Shown in Detailed only (teacher explanation part)
EXPLANATION_TEXT = "explanation_text"
EXPLANATION_CALC = "explanation_calc"
EXPLANATION_CALC_LAST_LINE = "explanation_calc_last_line"
EXPLANATION_RESULT_TEXT = "explanation_result_text"

# Shown in Detailed + Medium (not Short)
BLOCK_INTRO = "block_intro"

# Student-facing: Detailed + Medium; Short only last lines / result / final
STUDENT_TEXT = "student_text"
STUDENT_CALC = "student_calc"
STUDENT_CALC_LAST_LINE = "student_calc_last_line"
STUDENT_RESULT_TEXT = "student_result_text"

# Shown in all verbosities
FINAL_RESULT_TEXT = "final_result_text"

# Verbosity role sets (used by renderer)
MEDIUM_ROLES = frozenset({
    BLOCK_INTRO,
    STUDENT_TEXT,
    STUDENT_CALC,
    STUDENT_CALC_LAST_LINE,
    STUDENT_RESULT_TEXT,
    EXPLANATION_RESULT_TEXT,  # e.g. "no solution" / "infinitely many" so conclusion shows in Medium
    FINAL_RESULT_TEXT,
})
SHORT_ROLES = frozenset({
    STUDENT_CALC_LAST_LINE,
    STUDENT_RESULT_TEXT,
    EXPLANATION_RESULT_TEXT,
    FINAL_RESULT_TEXT,
})
