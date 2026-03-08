# Linear Equation Solver — AI Agent Instructions

You are an AI coding agent working on a Python symbolic mathematics project.

Before performing any coding task you MUST first read and analyze the following files:

1. README.md
2. docs/ folder
3. architecture_blueprint.docx
4. project source code

These documents describe the architecture and mathematical constraints of the system.

Never start coding before understanding these files.

---

PROJECT PURPOSE

This repository implements an educational algebra engine that solves systems of two linear equations in two variables and generates step-by-step solutions.

The solver must behave like a mathematics teacher explaining every step.

The system must produce:

• step-by-step algebraic solutions  
• LaTeX formatted output  
• graphical plotting points  

---

CRITICAL MATHEMATICAL RULES

These rules are mandatory.

1. No decimal arithmetic allowed.
2. Use symbolic math only.
3. Preserve fractions and surds.
4. Do not convert expressions to floats.
5. Remove denominators during normalization.
6. Rationalize final answers.
7. Avoid duplicate steps.
8. Hide coefficient 1 in output.

Example:

1y → y  
-1y → -y  

---

PROJECT ARCHITECTURE

The repository structure is:

math_engine/
    fraction_surd.py
    equation.py
    system.py

solver/
    elimination_solver.py
    graphical_solver.py

utils/
    step_recorder.py
    step.py
    equation_numbering.py

latex/
    equation_formatter.py
    latex_generator.py

docs/
    architecture_blueprint.docx

main.py

You must preserve this modular architecture.

Do not move responsibilities between modules.

---

STEP RECORDING

All solver actions must be recorded using StepRecorder.

Each step must contain:

type
content

Example types:

equation
operation
vertical_elimination
substitution
text

---

SOLVER METHODS

Implemented:

• elimination method
• graphical method

Planned:

• substitution method
• Cramer's rule

New solvers must follow the same step-recording architecture.

---

ELIMINATION METHOD RULES

Detect elimination strategy:

DIRECT
CROSS
LCM

Example logic:

if abs(a1) == abs(a2) or abs(b1) == abs(b2):
    DIRECT

elif a1 == b2 and b1 == a2 and signs match:
    CROSS

else:
    LCM

---

VARIABLE ELIMINATION SELECTION

Choose elimination variable by minimizing multiplication steps.

Procedure:

1. compute LCM for x
2. compute LCM for y
3. count multiplication steps
4. choose variable with fewer steps
5. if equal choose y

---

MULTIPLICATION RULE

If multiplier = 1 or -1

DO NOT multiply the equation.

Never flip signs unnecessarily.

---

VERTICAL ELIMINATION FORMAT

Solutions must display:

 14x + 7y = 49
+ 4x - 7y = 41
--------------
 18x = 90

This formatting must be preserved.

---

GRAPHICAL METHOD RULES

Generate points satisfying the equation.

Prefer:

• integer coordinates
• range [-8, 8]

If insufficient points exist:

generate intercepts.

---

LATEX OUTPUT

Solutions must be convertible to LaTeX using:

aligned environment

Example:

\begin{aligned}
2x + y &= 7 \\
4x - 7y &= 41
\end{aligned}

---

CODING RULES

When modifying code:

1. analyze the module first
2. identify problems
3. explain reasoning briefly
4. return full updated file
5. maintain compatibility with project architecture

Never return partial code fragments.

---

WORKFLOW

Before coding:

1. read README.md
2. read docs/ folder
3. inspect repository structure
4. analyze existing code

Then implement the requested changes.