# Upgrade and Security Roadmap

This document is **discussion and planning only**. It records (1) security guidelines for a future server launch with compulsory login, and (2) a step-by-step guide for expanding the project beyond systems of two linear equations in two variables. No code here; implement when ready.

---

## Part 1: Security guidelines (for future server + compulsory login)

When the app is **launched on a server** and **login is compulsory**, treat the following as requirements, not optional.

### Authentication (required)

- Every user must authenticate before using the app.
- Choose and implement a mechanism: **sessions** (server-side, cookie-based) or **JWT** (stateless tokens). Each has trade-offs (revocation, scaling, simplicity).
- Define and implement: **login**, **logout**, and optionally **password reset** / account management.
- Store credentials and tokens securely (e.g. hashed passwords, HTTPS-only cookies or secure token storage on the client).
- Document token/session lifetime and refresh (if any) so “compulsory login” cannot be bypassed by long-lived tokens.

### Authorization (required)

- Decide who can do what: e.g. only logged-in users can **save**; users can **delete** only their own saved systems; **solve** may be allowed for all authenticated users (or restricted by role if you add roles later).
- Tie saved systems (and any new data) to **user identity** in the database (e.g. `user_id` on `equation_systems`).
- For every new feature (sharing, teams, history, admin), define and enforce “who can see/edit/delete what.”

### CORS and HTTPS

- Restrict **CORS** `allow_origins` to the real frontend origin(s) (e.g. `https://yourapp.com`). Do not use `*` in production.
- Serve the app and API over **HTTPS only** in production. Enforce redirect from HTTP to HTTPS if needed.

### Rate limiting

- Add **rate limiting** (e.g. by user or IP) on: login, solve-system, save-system, delete, and any other expensive or sensitive endpoints.
- This protects the server and database and limits abuse once many users share the same deployment.

### Secrets and configuration

- Keep all secrets (session secret, JWT secret, DB URL, API keys) in **environment or config**, not in code.
- Use different values per environment (development, staging, production).

### Observability and security

- **Structured logging** (request ID, user id if available, endpoint, duration) helps with audit and incident response.
- Consider logging security-relevant events (e.g. login success/failure, delete, permission denied) without logging sensitive data (passwords, tokens).

### Summary checklist (implement later)

- [ ] Authentication (login / logout / tokens or sessions)
- [ ] Authorization (per-resource: save, delete, solve; user_id on data)
- [ ] CORS restricted to frontend origin(s)
- [ ] HTTPS only in production
- [ ] Rate limiting on login, solve, save, delete
- [ ] Secrets from environment; no secrets in code
- [ ] Logging and error handling that do not leak stack traces or secrets in production

---

## Part 2: Step-by-step guide to expand the project

Right now the app **only solves systems of two linear equations in two variables**. The goal is to expand to **quadratic equations**, **linear equations in one variable**, and **other types** later. Below is a phased, discussion-only roadmap.

### Phase 0: Clarify scope and types

**Step 0.1 — List problem types you want to support**

- **Linear in one variable** (e.g. \( ax + b = 0 \)).
- **Linear system in two variables** (current: \( a_1 x + b_1 y = c_1 \), \( a_2 x + b_2 y = c_2 \)).
- **Quadratic in one variable** (e.g. \( ax^2 + bx + c = 0 \)).
- **Quadratic in two variables** (e.g. conics, or systems mixing linear and quadratic) — optional, more complex.
- Later: **polynomial**, **inequalities**, **word problems**, etc.

**Step 0.2 — Decide the product shape**

- **Single “solver” with a type selector** (user picks “linear 1 variable”, “linear 2 variables”, “quadratic”, etc.) and the UI/API adapt.
- Or **separate flows** (e.g. different routes or apps per type). A single app with a type selector is usually easier to maintain and expand.

Recommendation: one app, one API, with a **problem type** (or “mode”) that drives which input form and which solver run.

---

### Phase 1: Prepare the architecture for multiple problem types

**Step 1.1 — Introduce a “problem type” or “solver type” concept**

- In the **API**: add something like `problem_type` or `solver_type` to the request (e.g. `linear_2x2`, `linear_1x`, `quadratic_1x`). The backend uses this to choose the solver and validation.
- In the **frontend**: add a top-level choice (tabs, dropdown, or menu) for “Linear (2 variables)”, “Linear (1 variable)”, “Quadratic”, etc. Each option loads the right input form and calls the API with the right type.
- In the **database** (if you keep saving): store `problem_type` with each saved system so you can reload the correct form and re-run the right solver.

**Step 1.2 — Generalize the request/response contract**

- Current contract is tailored to “two equations, two variables.” For one variable you have one equation; for quadratic you have coefficients \( a, b, c \), etc.
- Define a **generic shape** or **per-type payload**: e.g. for `linear_1x` the payload might be `{ equation: { a, b } }` (for \( ax + b = 0 \)); for `quadratic_1x` it might be `{ equation: { a, b, c } }` (for \( ax^2 + bx + c = 0 \)).
- Response can stay “solution + steps + LaTeX” but the **structure of the solution** will vary (one value vs two; real roots vs complex; degenerate cases). Plan a response that can represent “one number,” “two numbers,” “no real solution,” “infinitely many,” etc., plus a human-readable message and LaTeX.

**Step 1.3 — Keep the current flow as the first “mode”**

- Treat “linear 2×2 system” as the first supported type. Ensure the new `problem_type` and routing do not break the existing flow. All current API calls can send `problem_type: "linear_2x2"` (or equivalent) and keep the existing payload shape.

---

### Phase 2: Add “linear equation in one variable”

**Step 2.1 — Math and backend**

- Implement a small **solver** for \( ax + b = 0 \): solution \( x = -b/a \) (with handling for \( a = 0 \): no solution or identity).
- Reuse or adapt **step recording** and **LaTeX rendering**: “given equation”, “divide by \( a \)”, “therefore \( x = \ldots \)”. Reuse the same LaTeX pipeline if it is generic enough, or add a simple path for “one equation, one unknown.”
- **Validation**: one equation, one variable; acceptable coefficient types (rational, surd, etc., as in current design).

**Step 2.2 — API and DB**

- New (or extended) endpoint or same endpoint with `problem_type: "linear_1x"` and payload like `{ equation: { a, b }, variable: "x" }`.
- If you save: store `problem_type` and the new payload shape; when loading, detect type and show the right form.

**Step 2.3 — Frontend**

- New **input form** for one equation: one variable name, coefficients for the single equation (e.g. \( a \), \( b \) in \( ax + b = 0 \)).
- Reuse **solution panel** and **verbosity**; show one solution value and steps. Little or no “graph” for 1D; you can skip graph or show a number line later if desired.

This gives you a **second problem type** and validates the “multi-type” architecture before tackling quadratics.

---

### Phase 3: Add “quadratic equation in one variable”

**Step 3.1 — Math and backend**

- Implement a **quadratic solver** for \( ax^2 + bx + c = 0 \): discriminant, formula \( x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \), and cases: two real roots, one (repeated) root, no real roots (optional: complex roots or “no real solution” message).
- Decide whether coefficients are **rational/surd only** (like now) or if you allow decimals; stick to exact/symbolic if you want consistency with the rest of the app.
- **Step recording**: show “given equation”, “identify \( a, b, c \)”, “discriminant”, “apply formula”, “roots.” Reuse or extend the LaTeX renderer for these steps.
- **Validation**: one equation, one variable, degree 2; validate coefficient shape and buildability (e.g. no division by zero when \( a = 0 \) — then treat as linear or reject).

**Step 3.2 — API and DB**

- New type e.g. `problem_type: "quadratic_1x"` with payload `{ equation: { a, b, c }, variable: "x" }`.
- Response: e.g. `roots: [r1, r2]` or `root: r` (repeated), plus `discriminant`, `message` for “no real roots,” and full step-by-step LaTeX.

**Step 3.3 — Frontend**

- New **input form** for quadratic: one variable, three coefficients \( a, b, c \). Optionally show a simple **graph** of the parabola (optional, can come later).
- Solution panel: show one or two roots, discriminant, and steps. Handle “no real solution” in the same way you handle degenerate cases today (message, no numeric roots).

**Step 3.4 — “Above grade” and edge cases**

- If you keep an “above grade” concept (e.g. surd arithmetic), define when it applies in the quadratic solver (e.g. simplifying \( \sqrt{b^2 - 4ac} \) when the radicand is not a perfect square). Reuse or adapt the same idea as in the linear 2×2 flow.

---

### Phase 4: Generalize further (later)

**Step 4.1 — More equation types**

- **Linear in three variables** (3×3 systems): same idea — new type, new payload, new solver (e.g. elimination or matrix), new step format.
- **Higher-degree polynomials** (cubic, quartic): symbolically hard; you may rely on SymPy or another library and focus on **input/output and step presentation** rather than hand-written solution steps.
- **Inequalities** (e.g. \( ax + b > 0 \)): new semantics (solution sets, intervals), new solvers, new LaTeX (number line, intervals).

**Step 4.2 — Shared building blocks**

- **Coefficient/term representation**: you already have FractionSurd-like ideas; generalize so one-variable and quadratic equations use the same or a compatible representation.
- **Step recorder and LaTeX**: make the step types and renderer **pluggable** per problem type (e.g. “elimination steps” vs “quadratic formula steps” vs “linear 1x steps”) so adding a new type mostly means adding a new solver and a new step layout, not rewriting the whole pipeline.
- **Validation**: keep a **per-type** validation layer (like current Rules 1–4 for linear 2×2) so each problem type has clear, documented rules and error messages.

**Step 4.3 — Database and saved systems**

- Schema: `problem_type` (or `solver_type`) plus a **JSON payload** per type. When loading, the frontend reads the type and renders the correct form and re-runs the correct solver.
- If you add **user accounts** (see Part 1), tie saved systems to `user_id` and enforce authorization per type as needed.

---

### Phase 5: Order of implementation (suggested)

1. **Document and agree** on the list of problem types and the desired UX (single app with type selector vs multiple apps).
2. **Introduce `problem_type`** in API and frontend without changing behavior of the current linear 2×2 flow.
3. **Add linear 1 variable**: backend solver + steps + LaTeX, API, DB shape, frontend form and solution view. This validates the multi-type design.
4. **Add quadratic 1 variable**: same pattern — solver, steps, LaTeX, API, DB, frontend. Optionally graph later.
5. **Generalize** step recorder and LaTeX so new types are easier to add.
6. When you **launch on a server with compulsory login**, implement the **security guidelines** from Part 1 in parallel or just before launch.

---

### Summary: how to proceed from here

- **Short term:** Add a `problem_type` (or mode) and keep current behavior as `linear_2x2`. Design a minimal request/response shape for “linear 1 variable” and “quadratic 1 variable.”
- **Next:** Implement linear 1 variable end-to-end (solver, API, DB, UI). Use it to confirm that your architecture supports multiple types.
- **Then:** Implement quadratic 1 variable the same way.
- **Later:** Add more types (3×3, inequalities, etc.) and shared components (generic step/LaTeX, validation per type). When you move to a server and compulsory login, apply Part 1 security guidelines and implement them step by step.

No code in this document; use it as a roadmap and adjust the order and scope to match your priorities and timeline.
