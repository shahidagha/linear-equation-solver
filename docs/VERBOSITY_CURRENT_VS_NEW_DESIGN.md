# How Detailed, Medium, and Short are generated: current vs new design

**Discussion only.** No code. The user-selectable Short design is **deferred**; current three-level verbosity is unchanged for now.

---

## Current method: how the three levels are generated

### Where it happens

- **Backend:** `SolutionLatexRenderer` in `backend/latex/solution_renderer.py`.
- **Input:** One call to `render()` with method name, equations, solution, steps (from the solver), graph data, etc.
- **Output:** Three **pre-built LaTeX strings**: `latex_detailed`, `latex_medium`, `latex_short`. Each is a single string (e.g. one big `\begin{aligned} ... \end{aligned}` block).

### How the three lists are built

The renderer keeps **three lists of lines** (detailed_lines, medium_lines, short_lines). It fills them in one pass by iterating over standardization steps and method steps:

1. **Start:** All three lists get the same “Given equations” block.
2. **Standardization:**
   - **Detailed:** All standardization steps (equations + full text).
   - **Medium:** Same steps but some **text shortened** (e.g. “to make the leading coefficient positive” removed).
   - **Short:** Does **not** get the full standardization; it gets only “Given” plus equation (1) and equation (2) as two lines. So Short has a **fixed, minimal** opening.
3. **Method steps (e.g. elimination):** For each step the renderer decides what to append to each list:
   - **Detailed:** Everything (every block, every text line, including “detailed_only” steps that only Detailed gets).
   - **Medium:** Almost the same as Detailed but sometimes shorter text (e.g. strategy explanations shortened or omitted in places).
   - **Short:** **Fixed rule per method.** For elimination, a counter `medium_step` is incremented for each “medium” item; Short gets only items where `medium_step` is **not** in a hard-coded tuple `(1, 3, 5, 7, 9, 11)`. So Short is “every other step” in a fixed pattern. For substitution and Cramer, Short often gets the same as Medium (no skip pattern). So **what goes into Short is decided entirely in the renderer by code**, not by the user.
4. **End:** The **final answer** line (e.g. “therefore (x, y) = …”) is appended to **all three** lists.
5. Each list is turned into **one LaTeX string** via `_aligned()` and returned.

### What the frontend gets and does

- The API returns **three ready-made strings** per method (e.g. `elimination_latex.latex_detailed`, `latex_medium`, `latex_short`).
- The frontend has **no list of steps** and **no per-step control**. It only:
  - Stores these three strings.
  - When the user picks “Detailed”, “Medium”, or “Short”, it **displays the corresponding string** (e.g. in KaTeX).
- So **verbosity = choose one of three pre-computed outputs.** No checkboxes, no user choice of which steps appear in Short.

### Summary of current behaviour

| Aspect | Current |
|--------|--------|
| **Who decides Short content?** | Backend renderer, via fixed rules (skip indices, or “same as medium” per method). |
| **Shape of output** | Three **monolithic LaTeX strings**. No structured “list of steps.” |
| **User control** | None. User only switches among Detailed / Medium / Short. |
| **Where logic lives** | Entirely in `solution_renderer.py` (and solver step structure). |

---

## New design: user-selectable steps for Short

### Idea

- **Medium** is the “full” list of steps (same content as today’s medium output, but **as a list of items**, not one string).
- Each step has a **checkbox**. The user checks which steps they want in **Short**.
- **Short** = only the **checked** steps, in the same order as Medium. So Short is **user-defined**, not fixed by code.

### How it would differ from current

| Aspect | New design |
|--------|------------|
| **Who decides Short content?** | **User**, by checking/unchecking steps in the Medium list. |
| **Shape of output** | For Medium: need a **list of steps** (each with content). Short = that list **filtered by checkbox state**. So Short is “filtered Medium,” not a separate pre-built string. |
| **User control** | User sees the Medium step list, checks the steps they want in Short; Short view shows only those. |
| **Where logic lives** | **Frontend** holds the step list and the selection (which indices are checked). When displaying Short, it shows only selected steps. The backend may still produce the three strings for backward compatibility, or the API could expose a **steps array** for Medium so the frontend can render the list and build Short from it. |

### What has to change for the new design

- **Current:** Backend sends three strings. Frontend picks one. No step list.
- **New:** To support checkboxes and “Short = selected steps,” the app needs **per-step content** for Medium. So either:
  - **Option A:** Backend **also** sends a **structured list** of steps (e.g. array of `{ content: "…", index: 0 }`) that corresponds to what went into `latex_medium`. Frontend renders that list with checkboxes, stores which indices are checked, and builds the Short view by concatenating only the content of checked steps (and wrapping in the same aligned block). The existing `latex_medium` string can still be used to render “Medium” verbosity as today; the same content is what appears in the list.
  - **Option B:** Backend **only** sends the step list; frontend builds both Medium and Short from it (Medium = all steps, Short = selected steps). Then there are no pre-built `latex_medium` / `latex_short` strings for that view, or they are built on the frontend from the list.

So the main **conceptual** change is: **Short is no longer a second pre-computed string from the backend; it is “the subset of the Medium step list that the user selected.”** That implies a **structured step list** (from backend or derived) and **selection state** (and optionally persistence) on the frontend.

---

## Side-by-side comparison

| | **Current** | **New design** |
|--|--------------|-----------------|
| **Detailed** | One pre-built string from backend. | Unchanged: still one pre-built string (or same as now). |
| **Medium** | One pre-built string from backend. | Either same string **or** a list of steps that corresponds to that content; list is shown with checkboxes. |
| **Short** | One pre-built string from backend, built by **fixed rules** (e.g. skip steps 1,3,5,7,9,11 in medium order). | **Not** a separate backend string. Short = **only the steps from the Medium list that the user checked**, in order. |
| **Control** | User only chooses “Detailed”, “Medium”, or “Short”. | User chooses verbosity **and**, for Short, **which steps** to include via checkboxes on the Medium list. |
| **Backend** | Produces three strings per method. | Either (a) still produces three strings and **additionally** a step list for Medium, or (b) produces a step list and the frontend builds Medium and Short from it. |
| **Frontend** | Displays one of the three strings. | For Medium: displays step list with checkboxes (or the medium string and a separate “customize short” list). For Short: displays only the checked steps, in order. |

---

## Summary

- **Current:** Detailed, Medium, and Short are **three fixed LaTeX strings** produced in one pass in the backend. The rule for Short is **hard-coded** (e.g. skip certain step indices for elimination). The frontend only chooses which of the three strings to show.
- **New:** Medium is (or is driven by) a **list of steps**; the user **selects** which steps appear in Short via checkboxes. Short is **“Medium filtered by selection,”** not a second pre-built string. That requires exposing or building a **step list** and handling **selection state** on the frontend; the backend either keeps sending the three strings and adds a step list, or sends a step list and the frontend builds Medium and Short from it.

No code in this document; it only explains and compares the two approaches.
