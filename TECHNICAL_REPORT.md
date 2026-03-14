# Linear Equation Solver — Deep Technical Repository Report

## 1. Repository Structure

```text
linear-equation-solver/
├── AGENTS.md
├── README.md
├── requirements.txt
├── start-dev.ps1
├── fix.patch
├── main.py                              # legacy CLI demo entrypoint
├── solver/                              # legacy solver package (pre-backend layout)
│   ├── elimination_solver.py
│   └── graphical_solver.py
├── docs/
│   └── linear_equation_solver_architecture_blueprint.docx
├── backend/
│   ├── api_main.py
│   ├── main.py                          # backend-local CLI demo
│   ├── runserver.py
│   ├── init_db.py
│   ├── database.py
│   ├── graph/
│   │   └── graph_plotter.py
│   ├── latex/
│   │   ├── equation_formatter.py
│   │   ├── latex_formatter.py
│   │   ├── latex_generator.py
│   │   ├── latex_step_renderer.py
│   │   ├── math_to_latex.py
│   │   ├── solution_renderer.py
│   │   └── vertical_operation_formatter.py
│   ├── math_engine/
│   │   ├── _init_.py
│   │   ├── equation.py
│   │   ├── fraction_surd.py
│   │   └── system.py
│   ├── models/
│   │   ├── coefficient.py
│   │   ├── equation.py
│   │   ├── equation_models.py
│   │   ├── solution_methods.py
│   │   └── step.py
│   ├── normalization/
│   │   └── equation_standardizer.py
│   ├── routes/
│   │   └── equation_routes.py
│   ├── services/
│   │   ├── equation_service.py
│   │   └── solver_service.py
│   ├── solver/
│   │   ├── cramer_solver.py
│   │   ├── elimination_solver.py
│   │   ├── elimination_strategy.py
│   │   ├── graphical_solver.py
│   │   ├── solver_controller.py
│   │   └── substitution_solver.py
│   ├── step_engine/
│   │   ├── duplicate_filter.py
│   │   ├── step_builder.py
│   │   ├── step_manager.py
│   │   └── verbosity_filter.py
│   └── utils/
│       ├── canonical_encoder.py
│       ├── equation_numbering.py
│       ├── hash_utils.py
│       ├── step.py
│       └── step_recorder.py
└── frontend/
    └── app/
        ├── angular.json
        ├── package.json
        ├── package-lock.json
        ├── tsconfig*.json
        ├── public/
        └── src/
            ├── index.html
            ├── main.ts
            ├── styles.css
            └── app/
                ├── app.component.*
                ├── app.config.ts
                ├── app.routes.ts
                ├── models/
                ├── services/
                ├── utils/
                ├── pages/solver-page/
                └── components/
```

### Folder purposes
- **backend/**: FastAPI API, solver orchestration, DB persistence, symbolic engine integration.
- **frontend/app/**: Angular standalone-component SPA; equation builder + saved systems + solution viewer.
- **backend/math_engine/**: symbolic value + equation representations.
- **backend/solver/**: algorithm modules (elimination, substitution, Cramer, graphical).
- **backend/services/**: business-layer orchestration (save, solve, persistence, response shape).
- **backend/routes/**: HTTP endpoint layer.
- **backend/models/**: SQLAlchemy persistence models + some legacy domain model remnants.
- **backend/latex/**: equation/step/solution LaTeX rendering.
- **backend/step_engine/**: an older step filtering pipeline (duplicate + verbosity filters).
- **backend/utils/**: step recorder, hashing/canonicalization, equation numbering.
- **solver/** (top-level): legacy duplicate solvers used by root `main.py`; now mostly superseded by `backend/solver/`.

---

## 2. Backend Architecture (FastAPI)

### Application entry and runtime
- `backend/api_main.py`: creates FastAPI app, enables CORS, creates schema, includes routes.
- `backend/runserver.py`: launches `uvicorn` against `api_main:app`.
- `backend/database.py`: SQLAlchemy engine/session/base, and schema backfill helper for `solution_methods` columns.
- `backend/init_db.py`: utility initializer that imports models then creates all tables.

### Routes
- `backend/routes/equation_routes.py`
  - `POST /save-system`: stores system only.
  - `POST /solve-system`: save-or-detect-duplicate, then solve and store method outputs.
  - `GET /systems`: fetch all saved systems with optional stored response payload.
  - `DELETE /system/{id}`: cascaded delete of method rows + system row.

### Services
- `backend/services/equation_service.py`
  - `save_equation_system`: validates non-identical equations, duplicate detection via hashes, creates row.
  - `get_saved_systems`: joins systems + method records in memory and builds frontend-ready `stored_response`.
  - `delete_system_by_id`: removes linked method records then system record.
- `backend/services/solver_service.py`
  - `build_fraction_surd`: translates frontend term JSON to `FractionSurd`.
  - `to_python_number`: keeps exact integer/string representations (no float coercion).
  - `convert_points`: serializes graph points.
  - `_equation_lines`: canonical printable equations via formatter.
  - `_upsert_method_record`: insert/update solution method rows.
  - `solve_system`: central orchestration (build equations/system, run 4 solvers, render LaTeX variants, persist, respond).

### Solver modules
- `backend/solver/elimination_solver.py`: full pedagogical elimination workflow with recorded operations and vertical-elimination block data.
- `backend/solver/graphical_solver.py`: integer-point scan in [-8,8], fallback intercepts.
- `backend/solver/substitution_solver.py`: direct SymPy substitution pipeline.
- `backend/solver/cramer_solver.py`: determinant-based symbolic solve; returns no-unique message if D=0.
- `backend/solver/elimination_strategy.py`: independent strategy detector (not currently wired into solve path).
- `backend/solver/solver_controller.py`: method switcher, appears legacy/inactive.

### Math engine and normalization
- `backend/math_engine/fraction_surd.py`: symbolic fraction-surd structure and operations via SymPy.
- `backend/math_engine/equation.py`: variable-aware symbolic equation wrapper.
- `backend/math_engine/system.py`: equation pair container.
- `backend/normalization/equation_standardizer.py`: standardization (leading positive, LCM denominator clearing, GCD reduction); used in solve flow.

### Utilities and step tracking
- `backend/utils/step.py`: `Step(type, content)` DTO.
- `backend/utils/step_recorder.py`: step collection API (`add`, `add_equation`, `add_vertical`, `add_operation`).
- `backend/utils/equation_numbering.py`: equation label manager.
- `backend/utils/canonical_encoder.py`: canonical JSON serialization for equation hashing.
- `backend/utils/hash_utils.py`: equation-level and system-level SHA-256 hashing.

### LaTeX stack
- `backend/latex/equation_formatter.py`: robust algebraic text formatter with sign handling and hidden coeff 1.
- `backend/latex/solution_renderer.py`: main renderer producing `latex_detailed`, `latex_medium`, `latex_short` for each method.
- `backend/latex/latex_generator.py`, `latex_step_renderer.py`, `vertical_operation_formatter.py`, `math_to_latex.py`, `latex_formatter.py`: older/auxiliary renderers and format helpers.

### Graph helper
- `backend/graph/graph_plotter.py`: matplotlib plotting utility (not directly used by API response path).

### Backend models
- `backend/models/equation_models.py`: `equation_systems` table.
- `backend/models/solution_methods.py`: `solution_methods` table.
- `backend/models/coefficient.py`, `equation.py`, `step.py`: legacy domain representations parallel to `math_engine` and `utils/step.py`.

---

## 3. Frontend Architecture (Angular)

### Application shell and routing
- `app.config.ts`: provides router + HttpClient.
- `app.routes.ts`: single route to solver page.
- `app.component.*`: root wrapper with router outlet.
- `pages/solver-page/*`: page composition; left input panel + right state-driven panel.

### Services
- `services/equation-api.service.ts`: HTTP client for save/solve/list/delete endpoints.
- `services/solver-state.service.ts`: central UI state store (BehaviorSubjects for builder inputs, solution payload, selected method, verbosity, panel mode).

### Core components
- `input-panel`: binds variable selector + two equation builders; sends solve request.
- `variable-selector`: validates variable letters and uniqueness.
- `equation-builder`: term editing + frame-order controls + drag-drop + live LaTeX preview.
- `term-input`: numeric/signed term editor with input sanitization.
- `position-controls`: sets/reorders positions of term1/term2/equals/constant.
- `equation-preview`: KaTeX render of current equation.

### Result-side components
- `right-panel`: conditionally shows saved systems or solution panel from global state.
- `saved-systems`: table/card listing, search, paging, edit mode, solution-mode load, delete confirmation.
- `solution-panel`: method selector + verbosity + action buttons + steps region.
- `method-selector`: elimination/graphical/substitution/cramer tabs.
- `solution-steps`: renders elimination steps and graphical summary; supports verbosity filtering.
- `confirm-delete-modal`: reusable confirmation modal.
- `solution-viewer`: alternate viewer wrapper (appears not primary path now).

### Frontend models and utilities
- `models/term.model.ts`: symbolic term DTO.
- `models/equation.model.ts`: equation DTO.
- `models/solver-response.model.ts`: backend response typing.
- `utils/latex-generator.ts`: deterministic equation-to-LaTeX conversion with coefficient-1 suppression and position-aware side building.

---

## 4. Data Flow

### Frontend → Backend
1. User edits vars + coefficients in Angular builders.
2. `InputPanelComponent.saveSystem()` assembles payload and calls `POST /solve-system`.
3. Backend route stores or finds duplicate system, then invokes solver service.
4. Solver service builds symbolic objects and runs elimination/substitution/cramer/graphical modules.
5. Backend stores per-method LaTeX + solution JSON + graph points in `solution_methods`.
6. API returns `{solution, methods, graph}`.

### Backend → Frontend
1. Frontend receives solver response and stores it in `SolverStateService`.
2. `RightPanelComponent` switches to solution mode.
3. `SolutionPanel` + `SolutionSteps` render selected method and verbosity view.
4. KaTeX renders equations/steps in preview, saved system cards, and solution blocks.
5. On future reload/listing, `GET /systems` returns persisted `stored_response` for immediate render without re-solving.

---

## 5. Database Design

### `equation_systems`
- `id` (PK)
- `variables` (JSONB)
- `equation1` (JSONB)
- `equation2` (JSONB)
- `equation_hash` (String, indexed)
- `system_hash` (String, unique, indexed)
- `created_at` (timestamp)

Purpose: canonical storage of unique systems and duplicate detection basis.

### `solution_methods`
- `id` (PK)
- `system_id` (FK to `equation_systems.id`)
- `method_name` (String)
- `latex_detailed`, `latex_medium`, `latex_short` (String)
- `solution_json` (JSONB)
- `graph_data` (JSONB)
- `created_at` (timestamp)

Purpose: one row per solving method per system, including presentation-ready variants.

### Persistence behavior
- Save flow computes two hashes:
  - equation hash (structure-only)
  - system hash (variables + structure)
- `system_hash` duplicate -> return existing ID.
- Same equation hash + different vars -> variable conflict.
- Solving flow upserts method records by `(system_id, method_name)`.

---

## 6. Math Engine

- Core abstraction is symbolic, SymPy-backed `FractionSurd` with exact expression construction (`num*sqrt(rad) / den*sqrt(rad)`).
- `Equation` converts domain coefficients into symbolic `Eq(lhs, rhs)` with variable names from payload.
- `EquationSystem` wraps two equations passed to each solver.
- `EquationStandardizer` is used in the solve pipeline (solver_service).

### Representation notes
- Frontend term schema: `{sign, numCoeff, numRad, denCoeff, denRad}`.
- Backend converts to `FractionSurd`; no decimal conversion paths are used in solver orchestration.
- Response serialization converts SymPy integers to `int`, otherwise `str`.

---

## 7. Solver Architecture

### Elimination solver
Algorithm includes:
1. Strategy detection (`DIRECT`, `CROSS`, `LCM`).
2. Variable elimination choice by minimizing multiplication actions (tie → `y`).
3. Conditional multiplication recording (skip unnecessary steps).
4. Vertical elimination block creation for renderer.
5. Substitution back-solve narrative.
6. Final symbolic verification with `sp.solve`.

### Graphical solver
- Integer search across `x in [-8,8]` and keeps integer `y` points in range.
- Stops at three points; if insufficient, adds intercepts.

### Substitution and Cramer
- Implemented computationally and exposed in API response + database.
- Current step-by-step pedagogy for these methods is minimal (mostly renderer templates).

### Solver orchestration
- `solve_system` currently runs all methods regardless of selected method.
- Frontend method selector switches display among precomputed outputs.

---

## 8. Step Engine

There are **two parallel step systems**:

1. **Active path**: `utils/step.py` + `utils/step_recorder.py`
   - Used by backend elimination solver.
   - Supports typed steps (`text`, `equation`, `operation`, `vertical_elimination`).
2. **Legacy path**: `step_engine/*`
   - `StepBuilder`, `DuplicateFilter`, `VerbosityFilter`, `StepManager`.
   - Mostly print-oriented and not wired to API solve pipeline.

Verbosity in active UI is currently applied on frontend (`SolutionStepsComponent`) by list slicing/filtering; not via backend step-engine filters.

---

## 9. LaTeX Rendering

### Current production renderer
- `SolutionLatexRenderer.render()` produces three aligned-environment variants per method.
- Elimination includes vertical formatted array blocks and textual operations.
- Graphical includes plotted-point text.
- Cramer includes determinant matrices when equation parsing succeeds.

### Supporting formatters
- `EquationFormatter` creates readable equation strings and hides coefficient `1/-1`.
- Frontend has independent `equationToLatex` for live preview and saved list rendering.

### Numbering and vertical formatting
- Equation numbering appears in LaTeX preface lines (`(1)`, `(2)`).
- Vertical elimination is encoded as custom array layout for alignment and operation sign marking.

---

## 10. Current Completion Status

### Implemented
- ✅ FastAPI backend with solve/save/list/delete endpoints.
- ✅ Angular equation input UI with symbolic term controls.
- ✅ Equation preview rendering via KaTeX.
- ✅ Elimination solver with detailed recorded steps.
- ✅ Graphical point generation.
- ✅ Substitution and Cramer computational solve.
- ✅ PostgreSQL persistence for systems and method outputs.
- ✅ Duplicate detection and variable conflict handling.
- ✅ Saved systems browser (search, pagination, edit/delete, solution load).
- ✅ Multi-verbosity LaTeX payload generation.

### Partially implemented / inconsistent
- ⚠️ Backend has legacy duplicate modules (`solver/`, `main.py`, older latex/step utilities) alongside active stack.
- ⚠️ Substitution/Cramer pedagogical step recording is not equivalent to elimination detail.
- Normalization: `equation_standardizer.py` is integrated into solve flow.
- ⚠️ `step_engine/*` duplicate filtering/verbosity system not integrated with API pipeline.
- ⚠️ Solution panel actions `copyQuestion/copySolution` are stubs.

### Missing (relative to architecture goals)
- ❌ Rich step-by-step substitution method derivation pipeline.
- ❌ Rich step-by-step Cramer derivation pipeline with determinant arithmetic steps.
- ❌ True backend-controlled verbosity filtering across all methods.
- ❌ Automated migrations (backfill helper exists, but no migration framework).

---

## 11. Remaining Work (Priority Order)

1. **Unify active architecture; remove/retire legacy duplicate modules** (high).
2. **Integrate normalization pipeline in solver entrypoint** to enforce denominator clearing and canonical forms (high).
3. **Implement full step recording for substitution and Cramer** (high).
4. **Backend-driven verbosity and duplicate-step filtering** using one standard step schema (high).
5. **Complete UI utility actions** (copy question/solution export) (medium).
6. **Method-specific graph explanation improvements** (medium).
7. **DB migration strategy (Alembic)** replacing runtime schema patching (medium).
8. **Testing coverage expansion** across solver correctness + API + component behavior (medium).
9. **Optional caching** for repeated solves by system hash (low-medium).

---

## 12. Architecture Overview

```text
Angular Frontend
  ├─ Equation builder + variable controls
  ├─ Solver state store (BehaviorSubject)
  ├─ API service (HTTP)
  └─ KaTeX renderers
          │
          ▼
FastAPI Backend
  ├─ Routes (/save-system, /solve-system, /systems, /system/{id})
  ├─ Services (save/solve orchestration)
  ├─ Solver engine (elimination, graphical, substitution, Cramer)
  ├─ Math engine (FractionSurd, Equation, EquationSystem)
  ├─ Step recording (StepRecorder)
  └─ LaTeX renderer (detailed/medium/short)
          │
          ▼
PostgreSQL
  ├─ equation_systems
  └─ solution_methods
```

Interaction summary:
- Frontend sends canonical payload schema.
- Backend transforms payload → symbolic domain objects.
- Solver layer computes exact symbolic results and steps.
- Renderer layer creates LaTeX variants.
- Persistence layer stores method snapshots for replay in UI.

---

## 13. Future Improvements

### Architectural
- Consolidate to one solver package and one step-rendering pipeline.
- Create strict domain DTOs/Pydantic schemas instead of raw `dict` payloads.
- Introduce dependency inversion for solver methods (registry/factory pattern).

### Reliability and correctness
- Add solver regression suite with symbolic edge cases (zero coefficients, dependent/inconsistent systems, surd-heavy inputs).
- Add contract tests for API response shapes consumed by Angular.
- Enforce no-float policy via lint/test guards.

### Performance and scalability
- Hash-based solve cache for previously solved systems.
- Lazy solve by selected method (instead of always running all methods).

### DevEx and operations
- Add Alembic migrations.
- Add environment/bootstrap docs for backend + frontend full-stack startup.
- Add CI pipeline for backend tests + Angular tests/lint.

### UX
- Complete export/copy features.
- Add explicit method availability status badges (implemented vs preview).
- Improve graphical explanation UI using plotted chart rendering in frontend.

---

## Appendix: Full File-by-File Backend Function/Class Index (Quick Reference)

- `backend/database.py`: `ensure_solution_methods_schema`, `get_db`
- `backend/init_db.py`: `init_db`
- `backend/routes/equation_routes.py`: `save_system`, `solve_equation_system`, `get_systems`, `delete_system`
- `backend/services/equation_service.py`: `save_equation_system`, `get_saved_systems`, `delete_system_by_id`
- `backend/services/solver_service.py`: `build_fraction_surd`, `to_python_number`, `convert_points`, `_equation_lines`, `_upsert_method_record`, `solve_system`
- `backend/math_engine/fraction_surd.py`: class `FractionSurd` (+ arithmetic helpers)
- `backend/math_engine/equation.py`: class `Equation` (`sympy_equation`)
- `backend/math_engine/system.py`: class `EquationSystem`
- `backend/normalization/equation_standardizer.py`: class `EquationStandardizer.standardize`
- `backend/solver/elimination_solver.py`: class `EliminationSolver` (`detect_strategy`, `choose_variable`, `solve`, etc.)
- `backend/solver/graphical_solver.py`: class `GraphicalSolver` (`generate_points`, `generate_tables`)
- `backend/solver/substitution_solver.py`: class `SubstitutionSolver.solve`
- `backend/solver/cramer_solver.py`: class `CramerSolver.solve`
- `backend/solver/elimination_strategy.py`: class `EliminationStrategy.detect`
- `backend/solver/solver_controller.py`: class `SolverController.solve`
- `backend/utils/step.py`: class `Step`
- `backend/utils/step_recorder.py`: class `StepRecorder`
- `backend/utils/equation_numbering.py`: class `EquationNumbering`
- `backend/utils/hash_utils.py`: `generate_equation_hash`, `generate_system_hash`
- `backend/utils/canonical_encoder.py`: `canonicalize_equation`
- `backend/step_engine/*`: `StepBuilder`, `StepManager`, `DuplicateFilter`, `VerbosityFilter`
- `backend/latex/equation_formatter.py`: class `EquationFormatter`
- `backend/latex/solution_renderer.py`: class `SolutionLatexRenderer`
- `backend/latex/latex_generator.py`: class `LatexGenerator`
- `backend/latex/latex_step_renderer.py`: class `LatexStepRenderer`
- `backend/latex/math_to_latex.py`: class `MathToLatex`
- `backend/latex/latex_formatter.py`: class `LatexFormatter`
- `backend/latex/vertical_operation_formatter.py`: class `VerticalFormatter`
- `backend/graph/graph_plotter.py`: class `GraphPlotter`
- `backend/models/equation_models.py`: class `EquationSystem`
- `backend/models/solution_methods.py`: class `SolutionMethod`
- `backend/models/coefficient.py`: class `FractionSurd` (legacy)
- `backend/models/equation.py`: class `Equation` (legacy)
- `backend/models/step.py`: class `Step` (legacy)

