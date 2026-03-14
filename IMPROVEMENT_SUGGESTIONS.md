# Improvement Suggestions — Linear Equation Solver

This document lists **drawbacks of the current project** and **concrete suggestions** to address them. It is intended to guide future work and prioritization.

---

## 1. Testing

### Drawbacks

- **Sparse automated tests:** Backend has no visible test suite for normalization, solvers, or LaTeX rendering. Frontend has some `.spec.ts` files but coverage is unclear.
- **Regression risk:** Changes to step recording, LaTeX wrapping, or solver logic can break output without being caught.
- **No integration tests:** The full flow (POST payload → DB → LaTeX response) is not asserted end-to-end.

### Suggestions

- **Backend:** Add unit tests for:
  - `EquationStandardizer` (standard form, LCM/GCD, sign normalization).
  - Each solver (elimination, substitution, Cramer, graphical) with fixed inputs and expected solution + step structure.
  - `SolutionLatexRenderer` (wrap logic, verbosity levels, no invalid LaTeX fragments).
- **Backend:** Add integration tests for `POST /solve-system` and `GET /systems` (e.g. with a test DB or SQLite in-memory).
- **Frontend:** Run and extend component/service tests; add e2e tests for the solve flow, method/verbosity switch, and copy actions.
- **CI:** Run backend and frontend tests on every commit/PR.

---

## 2. Database and schema

**Status: Addressed.** Alembic is in place; runtime DDL removed; `requirements.txt` pins backend deps. See README “Database migrations” and run `python -m alembic upgrade head` for a fresh install.

### Drawbacks (original)

- **Runtime schema changes:** `ensure_solution_methods_schema()` and similar logic alter the database at startup. In multi-instance or managed deployments this can cause races or inconsistent schema.
- **No migration history:** Schema changes are not versioned; rolling back or reproducing environments is harder.
- **Minimal `requirements.txt`:** Only `sympy` and `matplotlib` are listed; FastAPI, SQLAlchemy, Uvicorn, etc. are implied. New contributors may miss dependencies.

### Suggestions (implemented)

- **Migrations:** **Alembic** is used; initial migration in `alembic/versions/001_initial_schema.py`. No DDL at application startup; run `python -m alembic upgrade head` (or `python -m backend.init_db`) to apply schema.
- **Requirements:** Backend dependencies are pinned in `requirements.txt` (fastapi, uvicorn, sqlalchemy, pydantic, python-dotenv, sympy, matplotlib, alembic). Optional: `requirements-dev.txt` for test/lint tools.

---

## 3. API and contracts

**Status: Addressed.** Canonical storage (terms + constant only), response schemas, and /v1 versioning are in place. See AGENTS.md “API and canonical contract.”

### Drawbacks (original)

- **Contract drift:** Backend request/response shapes can diverge from frontend TypeScript interfaces. Payload normalization (`_normalize_payload`) supports multiple shapes, which increases complexity and edge cases.
- **Canonicalization and hashing:** Duplicate detection relies on canonical encoding that may depend on `term1`/`term2` vs `terms[]`. Inconsistent payloads can lead to duplicate systems not being recognized or wrong cache reuse.
- **No API versioning:** Breaking changes would affect all clients at once.

### Suggestions (implemented)

- **Canonicalization:** All equations are stored and hashed in one shape: `{ terms, constant }` only (`to_canonical_equation_dict` in `canonical_encoder`). GET /systems expands to `term1`/`term2` for the frontend (`to_frontend_equation_dict`).
- **Response schemas:** `SolveResponseSchema` and `SaveResponseSchema` in `equation_schema.py` document the API; frontend `SolverResponse` should stay aligned.
- **Versioning:** Routes are mounted at `/v1`; frontend uses `API_V1`; unversioned routes remain for backward compatibility but are deprecated.

---

## 4. Validation and edge cases

### Drawbacks

- **Limited validation:** Malformed or degenerate systems (e.g. non-linear terms, inconsistent equations, symbolic edge cases) may not be validated before solving, leading to confusing errors or crashes.
- **LaTeX wrapping edge cases:** Very long lines without safe break points can remain unsplit; edge cases around nested `\text{}` or unusual math could still produce invalid LaTeX in rare cases.

### Suggestions

- **Input validation:** Validate equation structure (linear, two variables, supported coefficient types) before building the system. Return clear 4xx errors with messages.
- **Solver guards:** (Addressed: per-method degenerate detection; API returns solution_type/message; frontend shows message and graph omits intersection.) Handle “no solution” / “infinite solutions” explicitly and return structured results instead of generic errors.
- **LaTeX:** Add tests for wrap logic with long lines, only-text, and mixed content; optionally add a LaTeX lint or render check in CI for sample outputs.

---

## 5. Security and production configuration

### Drawbacks

- **CORS:** `allow_origins=["*"]` is acceptable for development but unsafe for production; any origin can call the API.
- **No authentication:** Save/delete and solve are unauthenticated; suitable for a local/educational tool but not for a shared deployment.
- **No rate limiting:** API can be hammered; no protection against abuse or accidental loops.

### Suggestions

- **CORS:** Restrict `allow_origins` to the frontend origin(s) in production (e.g. via env var).
- **Auth (if needed):** Add authentication (e.g. JWT or session) for save/delete and optionally for solve; document “local use only” if auth is out of scope.
- **Rate limiting:** Add rate limiting middleware (e.g. by IP or user) for `/solve-system` and write endpoints.

---

## 6. Codebase and maintainability

### Drawbacks

- **Dead or underused code:** `backend/graph/graph_plotter.py` and `backend/latex/math_to_latex.py` may not be in the main request path; unclear whether they are legacy or for future use.
- **Naming and layout:** Some references still say “Normalizer” while the actual module is `equation_standardizer`; docs and comments can get out of sync.
- **Mixed legacy formats:** Support for both `term1`/`term2` and `terms[]` increases branching and maintenance cost.

### Suggestions

- **Audit modules:** Confirm whether `graph_plotter.py` and `math_to_latex.py` are used. If not, remove or document as “optional/future” and avoid importing in the main flow until needed.
- **Documentation:** Keep `README.md`, `AGENTS.md`, and `TECHNICAL_ARCHITECTURE_REPORT.md` aligned with actual module names (e.g. `EquationStandardizer`, not “Normalizer”) and entry points.
- **Payload format:** Migrate to a single payload shape (`terms[]` + variables) and deprecate legacy keys; simplify `_normalize_payload` once frontend is updated.

---

## 7. Observability and operations

### Drawbacks

- **No structured logging:** Logs are not in a structured format (e.g. JSON with request id, method, duration), making it harder to debug and monitor.
- **No health check:** There is no dedicated endpoint for liveness/readiness (e.g. for containers or load balancers).
- **Errors:** Exceptions may bubble as 500s without correlation IDs or consistent error shapes.

### Suggestions

- **Structured logging:** Use structured logging (e.g. `structlog` or JSON logs) with request ID, endpoint, and duration. Log solver method and system id (or hash) for debugging.
- **Health endpoint:** Add `GET /health` (and optionally `GET /ready` that checks DB connectivity) for deployment and monitoring.
- **Error responses:** Standardize error response format (code, message, optional request id) and avoid leaking stack traces in production.

---

## 8. Frontend and UX

### Drawbacks

- **Edit/save flow:** Past issues (e.g. “Solve in edit not saving”, “variable names not saved”) have been fixed; remaining edge cases around mode switch or validation messages may still exist.
- **Accessibility:** Graph and equation display may not have sufficient ARIA labels or text alternatives for screen readers.
- **Mobile:** Layout and graph size may not be optimized for small screens.

### Suggestions

- **E2e tests:** Cover edit → save → solve and variable-name change → save to prevent regressions.
- **Accessibility:** Add ARIA labels and roles for solution panel and graph; provide a text summary of the solution or graph (e.g. “Intersection at (3, 2)”).
- **Responsiveness:** Consider responsive layout and optional graph scaling or scroll for smaller viewports.

---

## 9. Documentation and onboarding

### Drawbacks

- **`docs/` empty:** No user-facing or developer docs in `docs/` (e.g. architecture blueprint exists elsewhere as `.docx`).
- **AGENTS.md:** Still lists “Planned” for substitution and Cramer; they are implemented and should be updated.
- **Runbooks:** No runbook for common tasks (e.g. “add a new solver”, “change LaTeX format”).

### Suggestions

- **Update AGENTS.md:** Mark substitution and Cramer as implemented; add a short note on LaTeX wrapping and step types (e.g. `subst_solve_step`, `divide_step`).
- **docs/:** Add at least a short architecture overview (or link to `TECHNICAL_ARCHITECTURE_REPORT.md`) and a “Development” section (run backend/frontend, run tests, env vars).
- **Runbooks:** Add a `docs/DEVELOPMENT.md` or section in README: how to add a new method, how to change verbosity content, where to adjust graph range/labels.

---

## 10. Summary and priority

| Area              | Drawback summary                          | Suggested priority |
|-------------------|-------------------------------------------|--------------------|
| Testing           | Few/no tests; regression risk            | High               |
| Database          | Runtime DDL; no migrations                | High               |
| API/contracts     | Drift; canonicalization complexity        | Medium             |
| Validation        | Limited input/edge-case handling          | Medium             |
| Security/config   | CORS; no auth/rate limit                  | Medium (if deployed) |
| Codebase          | Dead code; naming drift                   | Low                |
| Observability     | No structured logs; no health check       | Medium (if deployed) |
| Frontend/UX       | A11y; mobile; e2e                         | Low–Medium         |
| Documentation     | AGENTS.md outdated; docs/ empty           | Low                |

Addressing **testing** and **migrations** first will reduce regression risk and make schema evolution safe. **API contracts** and **canonicalization** will improve long-term maintainability. **Security and observability** become important when moving from local to shared or production use.
