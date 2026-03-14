# Linear Equation Solver

**Author:** Shahid Agha

A symbolic mathematics engine and web application for solving **systems of two linear equations in two variables** with **step-by-step textbook-style solutions**. The system preserves exact expressions (integers, fractions, surds), produces LaTeX output, and supports four solving methods—including a graphical view with plot and point tables.

---

## Overview

The project is an educational algebra engine that behaves like a mathematics teacher: it explains each step, avoids decimal approximations, and outputs solutions in a form suitable for teaching and learning. The backend is a **Python/FastAPI** service with a **SymPy**-based math engine; the frontend is an **Angular** single-page application. Solutions and per-method LaTeX are persisted in a database and cached for duplicate systems.

---

## Features

- **Four solving methods:** Elimination, Substitution, Cramer's rule, Graphical
- **Step-by-step LaTeX** at three verbosity levels (Detailed, Medium, Short) for all methods
- **Term input modes:** Rational, Irrational (\(a\sqrt{b}\)), Fraction, Fraction surd (full term format)
- **Graph:** Canvas plot with axes [-9, 9], grid, equation lines, intersection label; copy graph as PNG
- **Copy:** Question (equations) and solution (LaTeX) to clipboard
- **Saved systems:** List, load for edit/solve, delete; duplicate and variable-conflict handling

---

## Current State

### Backend (Python / FastAPI)

- **API** (preferred base path: `/v1`)
  - `POST /v1/save-system`: Save equation system (variables, two equations).
  - `POST /v1/solve-system`: Normalize equations, run all four solvers, render LaTeX, persist results; returns solution, method LaTeX, and graph data. Supports update when `system_id` is provided.
  - `GET /v1/systems`: Return saved equation systems with stored solution/method data.
  - Delete and duplicate detection via equation and system hashes; cached results reused when the same system is solved again.
  - **Canonical contract:** Request can send variables as `[var1, var2]` or `{ var1, var2 }`, and each equation as `terms[]` or `term1`/`term2`; storage and hashing use a single canonical shape `{ terms, constant }` only. See AGENTS.md.

- **Normalization**
  - `EquationStandardizer`: standard form, leading coefficient positive, denominators cleared (LCM), coefficients reduced (GCD). Standardization steps are recorded for LaTeX (given equations, equation (1), equation (2)) and shared across all methods.

- **Solving methods (all four implemented with full step recording)**
  1. **Elimination**
     - Strategy: **DIRECT** (same coefficient magnitude), **CROSS** (six-step when |a₁|=|b₂|, |a₂|=|b₁| and signs match), **LCM** (scale to match).
     - Variable chosen to minimize multiplication steps; no step when multiplier is ±1.
     - Steps: strategy text, operations, scaled equations, vertical add/subtract, divide steps, back-substitution, final answer. Rendered at Detailed / Medium / Short.
  2. **Substitution**
     - Solve one equation for one variable, substitute into the other, solve, back-substitute with explicit intermediate steps (e.g. \(q = 7 - 15/3\), then \(q = 7 - 5\), then \(q = 2\)). Full step recording and LaTeX at three verbosity levels.
  3. **Cramer's rule**
     - Coefficients identified, D / Dₓ / Dᵧ with symbolic and numeric matrices, full computation and division steps, final solution. Step-by-step LaTeX at three verbosity levels.
  4. **Graphical**
     - Up to three points per equation (integer coordinates preferred in [-8, 8]; intercepts if needed). Point tables and solution line in LaTeX; graph data (points, intersection, labels) for frontend plot.

- **LaTeX rendering**
  - `SolutionLatexRenderer` builds `latex_detailed`, `latex_medium`, `latex_short` per method.
  - Mixed text/math style (`\text{...} \; math \; \text{...}`) for consistency. LaTeX-aware line wrapping: if line > 70 chars, break at safe points (`} \text{`, ` \; `) or after the last math block in the first 70 characters; for text-only lines, break at a space with `} \ & \text{`.

- **Persistence**
  - SQLAlchemy: `EquationSystem` (equations, hashes, variables), `SolutionMethod` (per-method LaTeX and solution/graph JSON). PostgreSQL or SQLite via `DATABASE_URL` or fallback. Schema ensured at startup for `solution_methods`.

### Frontend (Angular)

- **Solver page**
  - Header: “Linear Equation Solver” and “- Shahid Agha. Build two equations…”.
  - **Input panel:** Variable selector (two symbols); **Term Format** with four modes: Rational, Irrational, Fraction, Fraction surd. Equation builders with term inputs; live equation preview; Solve button.
  - **Right panel:** Method selector (Elimination, Substitution, Cramer’s rule, Graphical), verbosity (Detailed / Medium / Short), rendered solution (KaTeX).

- **Actions**
  - **Copy Question:** Equations as LaTeX to clipboard.
  - **Copy Solution:** LaTeX of selected method and verbosity to clipboard.
  - **Graphical:** “Copy graph as PNG” and “View graph” (modal with canvas).

- **Graph (canvas)**
  - Axes -9 to 9, arrows, grid; axis labels; equation lines with end arrows; equation labels along lines; intersection point and coordinate label; 560×560 canvas.

- **Saved systems**
  - List with load (edit/solve) and delete; edit opens in Fraction surd with optional mode suggestion (Rational / Irrational / Fraction) when applicable.

### Mathematical rules (enforced)

- No decimal arithmetic; symbolic math only (SymPy).
- Fractions and surds preserved; no float conversion for display.
- Denominators removed during normalization; final answers rationalized.
- Coefficient 1 hidden in output (e.g. `y` not `1y`).
- Duplicate consecutive steps suppressed in rendering.

---

## Architecture

```
linear-equation-solver/
├── backend/
│   ├── api_main.py              # FastAPI app, CORS, DB init
│   ├── database.py              # Engine, Base, session
│   ├── runserver.py              # Uvicorn entry
│   ├── routes/
│   │   └── equation_routes.py   # save-system, solve-system, systems, delete
│   ├── services/
│   │   ├── equation_service.py   # Persist systems, list, delete, cache lookup
│   │   └── solver_service.py    # Build system, standardize, run solvers, render LaTeX, upsert methods
│   ├── math_engine/
│   │   ├── fraction_surd.py     # Symbolic number (rational, surd, fraction)
│   │   ├── equation.py          # Equation ax + by = c
│   │   └── system.py            # EquationSystem (eq1, eq2)
│   ├── normalization/
│   │   └── equation_standardizer.py  # Standard form, leading positive, clear denominators, reduce
│   ├── solver/
│   │   ├── elimination_solver.py
│   │   ├── substitution_solver.py
│   │   ├── cramer_solver.py
│   │   └── graphical_solver.py
│   ├── latex/
│   │   ├── equation_formatter.py
│   │   ├── math_to_latex.py       # optional; not in request path
│   │   └── solution_renderer.py  # Verbosity tiers, standardization, wrap, graphical tables
│   ├── normalization/
│   │   └── equation_standardizer.py
│   ├── graph/
│   │   └── graph_plotter.py       # optional; not in request path
│   ├── utils/
│   │   ├── step_recorder.py
│   │   ├── step.py
│   │   ├── equation_numbering.py
│   │   ├── canonical_encoder.py
│   │   └── hash_utils.py
│   ├── models/
│   ├── schemas/
│   └── init_db.py
├── frontend/app/
│   └── src/app/
│       ├── pages/solver-page/
│       ├── components/          # input-panel, right-panel, solution-panel, equation-builder,
│       │                       # term-input, variable-selector, equation-preview, method-selector,
│       │                       # solution-steps, solution-viewer, view-graph-modal, saved-systems,
│       │                       # confirm-delete-modal, position-controls
│       ├── services/            # equation-api, solver-state
│       ├── models/
│       └── utils/
├── docs/
├── runserver.py                 # uvicorn 127.0.0.1:8000
├── requirements.txt
├── AGENTS.md                    # AI agent instructions
└── README.md
```

---

## Technology stack

- **Backend:** Python 3, FastAPI, SymPy, SQLAlchemy (PostgreSQL or SQLite), Uvicorn.
- **Frontend:** Angular 19, KaTeX, Canvas API for graph.
- **Dev:** Node/npm for Angular; optional `.env` for `DATABASE_URL`.

---

## How to run

1. **Backend**
   - From project root: `pip install -r requirements.txt`.
   - Set `DATABASE_URL` in `.env` for PostgreSQL; otherwise SQLite is used.
   - **Apply database schema:** run `python -m alembic upgrade head` (or `python -m backend.init_db`). Do this once for a fresh install, and after pulling new migrations.
   - Run: `python runserver.py` (API at `http://127.0.0.1:8000`).

2. **Frontend**
   - `cd frontend/app`, then `npm install` and `ng serve` (or `npm start`). Open the URL shown (e.g. `http://localhost:4200`).

3. Use the UI to enter two equations (choose variable names and term format), click Solve, select method and verbosity, and use Copy Question / Copy Solution / View graph / Copy graph as PNG as needed.

---

## Database migrations

Schema is managed by **Alembic**. No tables are created at application startup.

- **New install or after pull:** from project root run `python -m alembic upgrade head`.
- **Existing DB that already has the tables** (e.g. you used the app before Alembic, or you see `DuplicateTable: relation "equation_systems" already exists`): run **`python -m alembic stamp head`** once. That marks the DB as up-to-date without running the initial migration; then `upgrade head` is safe to use for future migrations.
- **Add a new migration:** `python -m alembic revision --autogenerate -m "description"`, then review and run `python -m alembic upgrade head`.

---

## Running tests

Backend tests live in **`tests/`**. Install dev dependencies and run:

- `pip install -r requirements-dev.txt`
- From project root: `PYTHONPATH=. python -m pytest tests/ -v`

Tests cover: EquationStandardizer, all four solvers (elimination, substitution, Cramer, graphical), SolutionLatexRenderer, request validation (Rules 1–4), and API 422 responses for invalid payloads. See **IMPROVEMENT_SUGGESTIONS.md** §1 for details.

---

## Future work

- Extend automated tests (frontend e2e, CI on commit/PR); backend unit and integration tests are in place.
- Stricter API contracts and optional versioning; shared types to avoid frontend/backend drift.
- Production hardening: auth, rate limiting, structured logging, restrict CORS.
- Graph: configurable range, SVG export, accessibility.

See **IMPROVEMENT_SUGGESTIONS.md** for a detailed list of improvements and drawbacks to address.

---

## Project goal

The long-term goal is a **symbolic algebra engine for educational mathematics** that produces complete, step-by-step solutions similar to textbooks, with exact arithmetic, multiple methods, and clear, reproducible presentation (LaTeX and graphs).

---

## Author

Shahid Agha
