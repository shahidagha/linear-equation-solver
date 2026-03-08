# Linear Equation Solver

A symbolic mathematics engine designed to solve **systems of two linear equations in two variables** while producing **step-by-step textbook-style solutions**.

The solver preserves **exact mathematical expressions** such as integers, fractions, and surds instead of converting them to decimals.

---

# Features

- Exact symbolic computation
- Step-by-step algebraic solutions
- Multiple solving methods
- LaTeX output generation
- Graphical method support
- Fraction and surd coefficient support
- Educational solution formatting

---

# Supported Equation Format

The solver works with equations of the form:

ax + by = c  
dx + ey = f

Where coefficients may be:

- Integers
- Fractions
- Surds
- Fraction-surds

Example:

2x + y = 7  
4x − 7y = 41

---

# Implemented Solving Methods

## Elimination Method

Features implemented:

- Strategy detection
- Direct elimination
- LCM elimination
- Cross elimination
- Vertical addition / subtraction layout
- Substitution step generation

Example output:

```
14x + 7y = 49
4x − 7y = 41
--------------
18x = 90

x = 5
y = −3
```

---

## Graphical Method

The solver generates coordinate points for plotting the equations.

Rules:

- Prefer integer coordinate points
- Coordinate range limited to −8 to 8
- Intercepts generated if necessary

Example output:

```
Equation 1 Points:
(0,7) (1,5) (2,3)

Equation 2 Points:
(-2,-7) (5,-3) (41/4,0)
```

---

# Architecture

Project structure:

```
linear-equation-solver

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
    latex_step_renderer.py

docs/
    architecture_blueprint.docx

main.py
```

---

# Key Components

## Mathematical Engine

Provides symbolic representation of numbers and equations.

Core classes:

- `FractionSurd`
- `Equation`
- `EquationSystem`

---

## Solver Engine

Responsible for solving equation systems.

Modules:

- Elimination solver
- Graphical solver

Planned:

- Substitution solver
- Cramer's rule solver

---

## Step Recording System

All solution steps are stored as structured objects.

Example step types:

- equation
- operation
- vertical_elimination
- substitution

This allows easy generation of LaTeX output.

---

## LaTeX Rendering

The solver can generate LaTeX representations of the full solution.

Example:

```
\begin{aligned}
2x + y &= 7 \\
4x - 7y &= 41
\end{aligned}
```

---

# Technology Stack

Language:

Python

Symbolic Mathematics Library:

SymPy

Planned Frontend:

Angular

---

# Design Constraints

The solver follows strict mathematical constraints:

- No decimal approximations
- Exact symbolic arithmetic
- Surd expressions preserved
- Denominators removed during normalization
- Rationalization applied to final answers

---

# Future Development

Planned improvements:

- Substitution method solver
- Cramer's rule solver
- Graphical table LaTeX generator
- Verbosity levels
- Angular front-end interface
- Database storage for generated solutions

---

# Project Goal

The long-term goal is to build a **symbolic algebra engine for educational mathematics**, capable of generating complete step-by-step solutions similar to those found in textbooks.

---

# Author

Shahid Agha

---