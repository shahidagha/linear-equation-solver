# Linear Equation Solver

**Author:** Shahid Agha

A symbolic mathematics engine and web application for solving **systems of two linear equations in two variables** with **step-by-step textbook-style solutions**. The system preserves exact expressions (integers, fractions, surds), produces LaTeX output, and supports multiple solving methods including a full graphical view with plot and point tables.

---

## Overview

The project is an educational algebra engine that behaves like a mathematics teacher: it explains each step, avoids decimal approximations, and outputs solutions in a form suitable for teaching and learning. The backend is a **Python/FastAPI** service with a **SymPy**-based math engine; the frontend is an **Angular** single-page application. Solutions (and per-method LaTeX) are persisted in a database and can be cached for duplicate systems.

---

## Current State

### Backend (Python / FastAPI)

- **API**
  - `POST /solve-system`: Accepts two equations (symbolic coefficients), normalizes them, runs all four solvers, renders LaTeX at three verbosity levels per method, persists system and method results, returns solution plus LaTeX and graph data.
  - `GET /systems`: Returns saved equation systems with stored solution/method data.
  - Save/delete and duplicate detection via equation and system hashes; cached results reused when the same system is solved again.

- **Normalization / standardization**
  - Equations are standardized before solving: standard form, leading coefficient positive, denominators cleared (integer LCM), and coefficients reduced (GCD). Each standardization step is recorded for pedagogical LaTeX (given equations block, equation (1), equation (2)).
  - Shared standardization steps are prepended to method-specific steps (e.g. elimination) for all methods.

- **Solving methods (all four implemented and wired)**
  1. **Elimination**
     - Strategy detection: **DIRECT** (same coefficient magnitude), **CROSS** (six-step method when |a₁|=|b₂|, |a₂|=|b₁| and middle signs match), **LCM** (scale to match coefficients).
     - Variable chosen for elimination by minimizing multiplication steps (LCM for x vs y).
     - Conditional multiplication (no step when multiplier is ±1).
     - Full step recording: text, operations, scaled equations, vertical addition/subtraction, divide steps, reduced equations, substitution (with optional detailed explanation), and final answer.
     - Verbosity: **Detailed**, **Medium**, **Short** (short drops selected steps from medium for elimination; standardization short shows only given block + final eq (1) and eq (2)).
  2. **Substitution**
     - Solves one equation for one variable, substitutes into the other, returns solution. LaTeX is rendered at three verbosity levels; no fine-grained step recorder like elimination.
  3. **Cramer’s rule**
     - Determinants D, Dx, Dy; returns numeric solution or “No unique solution” when D = 0. LaTeX at three verbosity levels; no step-by-step trace.
  4. **Graphical**
     - Generates up to three points per equation (integer coordinates preferred in **[-8, 8]**; intercepts used if needed). Point tables and solution line are rendered in LaTeX. Graph data (points, intersection, equation labels) is returned for the frontend plot.

- **LaTeX rendering**
  - `SolutionLatexRenderer` builds `latex_detailed`, `latex_medium`, `latex_short` per method.
  - Supports: given-equations block (raw user input), equation numbering, vertical elimination arrays (with optional operation label), substitution intro (short/detailed), divide-step messages, standardization pipeline, graphical tables and solution line. Fraction lines get extra vertical space; coefficient 1 is hidden in output; deduplication of consecutive identical steps.

- **Persistence**
  - SQLAlchemy models: `EquationSystem` (equations, hashes, variables), `SolutionMethod` (per-method LaTeX and solution/graph JSON). PostgreSQL or SQLite (e.g. via `DATABASE_URL` or fallback). Schema ensured at startup for `solution_methods`.

### Frontend (Angular)

- **Solver page**
  - Header: “Linear Equation Solver” and “- Shahid Agha. Build two equations…” in one line.
  - Two equation input panels (equation builder with terms, variable selector).
  - Solution panel: method selector (Elimination, Substitution, Cramer’s rule, Graphical), verbosity (Detailed / Medium / Short), and rendered solution (KaTeX for LaTeX).

- **Actions**
  - **Copy Question:** Copies the two user-defined equations as raw LaTeX with ` ; ` between them.
  - **Copy Solution:** Copies the LaTeX of the selected method and verbosity (already in an aligned environment) to the clipboard, with success/failure message.
  - **Graphical method only:** “Copy graph as PNG” (draws graph offscreen, copies image to clipboard) and “View graph” (modal with canvas).

- **Graph (canvas)**
  - Axes from **-9 to 9** with arrows at both ends, labeled **X** and **Y**.
  - Grid: black, full horizontal and vertical lines.
  - Axis tick labels **-9 … 9**; single “0” at origin, offset 3 px from Y-axis; other labels offset 3 px (x: right, y: vertical).
  - Both equation lines drawn in black, clipped to the [-9, 9] box so end arrows are visible; arrows at both ends of each line; equation labels (from backend) drawn along the line near the arrow, on opposite sides, bold 13 px, rotated with slope.
  - Points on lines and intersection point in black; intersection labeled with coordinates (e.g. “(3, 2)”) in bold 15 px.
  - All elements black (no other colors). Canvas 560×560; copy-PNG uses same size.

- **Saved systems**
  - List of saved systems; optional load/delete; duplicate and variable-conflict handling via API.

### Mathematical rules (enforced)

- No decimal arithmetic; symbolic math only (SymPy).
- Fractions and surds preserved; no conversion to floats for display.
- Denominators removed during normalization; final answers rationalized.
- Coefficient 1 hidden in output (e.g. `y` not `1y`).
- Duplicate consecutive steps suppressed in rendering.

---

## Architecture (high level)

```
linear-equation-solver/
├── backend/
│   ├── api_main.py              # FastAPI app, CORS, DB init
│   ├── database.py              # Engine, Base, session
│   ├── routes/
│   │   └── equation_routes.py   # POST /solve-system, GET /systems, save/delete
│   ├── services/
│   │   ├── equation_service.py  # Persist systems, list, delete, cache lookup
│   │   └── solver_service.py    # Build system, normalize, run solvers, render LaTeX, upsert methods
│   ├── math_engine/
│   │   ├── fraction_surd.py     # Symbolic number representation
│   │   ├── equation.py          # Equation ax + by = c
│   │   └── system.py            # EquationSystem (eq1, eq2)
│   ├── normalization/
│   │   └── equation_standardizer.py  # Standard form, leading positive, clear denominators, reduce
│   ├── solver/
│   │   ├── elimination_solver.py     # DIRECT/CROSS/LCM, step recorder
│   │   ├── substitution_solver.py
│   │   ├── cramer_solver.py
│   │   └── graphical_solver.py        # Point generation [-8, 8]
│   ├── latex/
│   │   ├── equation_formatter.py
│   │   └── solution_renderer.py       # Verbosity tiers, standardization, graphical tables
│   ├── utils/
│   │   ├── step_recorder.py
│   │   ├── step.py
│   │   └── equation_numbering.py
│   ├── models/
│   │   ├── equation_models.py
│   │   └── solution_methods.py
│   └── schemas/
│       └── equation_schema.py
├── frontend/app/
│   └── src/app/
│       ├── pages/solver-page/
│       ├── components/          # input-panel, solution-panel, equation-builder, method-selector,
│       │                       # solution-steps, view-graph-modal, saved-systems, etc.
│       ├── services/            # equation-api, solver-state
│       ├── utils/              # latex-generator, graph-drawer
│       └── models/
├── docs/
├── runserver.py                # uvicorn 127.0.0.1:8000
├── requirements.txt
└── README.md
```

---

## Technology stack

- **Backend:** Python 3, FastAPI, SymPy, SQLAlchemy (PostgreSQL or SQLite), Uvicorn.
- **Frontend:** Angular, KaTeX for LaTeX, Canvas API for graph.
- **Dev:** Node/npm for Angular; optional `.env` for `DATABASE_URL`.

---

## How to run

1. **Backend**
   - From project root: `pip install -r requirements.txt` (and any FastAPI/SQLAlchemy/uvicorn deps if not in file).
   - Set `DATABASE_URL` in `.env` if using PostgreSQL; otherwise backend may fall back to SQLite.
   - Run: `python runserver.py` (API at `http://127.0.0.1:8000`).

2. **Frontend**
   - `cd frontend/app` then `npm install` and `ng serve` (or equivalent). Open the URL shown (e.g. `http://localhost:4200`).

3. Use the UI to enter two equations, click Solve, choose method and verbosity, and use Copy Question / Copy Solution / View graph / Copy graph as PNG as needed.

---

## Future implementations

- **Step-by-step for Substitution and Cramer**
  - Record and serialize substitution steps (isolate variable, substitute, solve, back-substitute) and Cramer steps (determinants, formulas) so they can be rendered in the same way as elimination (with verbosity levels).

- **Tests**
  - Backend: unit tests for normalization, each solver, and LaTeX renderer; integration tests for `/solve-system` and persistence.
  - Frontend: unit tests for services and components; e2e for solve flow and copy actions.

- **Database**
  - Formal migrations (e.g. Alembic) instead of runtime schema changes; versioned schema for `equation_systems` and `solution_methods`.

- **API and contracts**
  - Strict request/response schemas and optional API versioning; shared types or OpenAPI-driven frontend types to avoid drift.

- **Production hardening**
  - Authentication and authorization for save/delete if needed; rate limiting; structured logging and observability; restrict CORS to known origins.

- **Graph**
  - Optional: configurable range or zoom; export graph as SVG; accessibility (e.g. text alternative for the plot).

- **Documentation**
  - Keep `AGENTS.md` and `docs/` in sync with behavior (e.g. standardization steps, verbosity rules, graph behavior). Update this README when new methods or features are added.

---

## Project goal

The long-term goal is a **symbolic algebra engine for educational mathematics** that produces complete, step-by-step solutions similar to textbooks, with exact arithmetic, multiple methods, and a clear, reproducible presentation (including LaTeX and graphs).

---

## Author

Shahid Agha
