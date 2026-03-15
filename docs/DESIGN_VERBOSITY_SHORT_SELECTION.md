# Design: User-selectable steps for Short verbosity

**Status:** Deferred. Design only; no code. Keeping current verbosity (three pre-built strings) for now; revisit this idea later.

---

## Goal

- The user sees **all steps at verbosity Medium** as a **list**.
- Each step has a **checkbox**.
- The user **checks or unchecks** steps.
- **Verbosity Short** shows **only the steps that are checked**, in the same order as Medium.
- Short is therefore **user-defined**: “the subset of Medium steps I selected.”

---

## Concepts

| Concept | Meaning |
|--------|--------|
| **Medium** | Full list of solution steps (current “medium” verbosity content). |
| **Short** | Subset of Medium steps chosen by the user via checkboxes. |
| **Step** | One item in the Medium list (one line or block of content, with optional index/ID). |
| **Selection** | Set of steps that are checked; exactly these steps appear when Short is selected. |

---

## Data

- **Step list (Medium):** Ordered list of steps. Each step has:
  - **Content** (text/LaTeX to display).
  - **Index or ID** (for storing which are selected).
- **Selection state:** Which steps are “in Short.” Stored as:
  - List of indices, e.g. `[0, 2, 5]`, or
  - List of step IDs if steps have stable IDs, or
  - Per-step boolean array aligned with the step list.
- **Default selection:** When the user has not customized:
  - Either use the **current fixed Short** (map existing short steps to indices and pre-check those), or
  - **All checked** (short = medium until the user unchecks), or
  - **None checked** (short empty until the user checks).

---

## UI layout

- **Where:** In the solution panel, in the area where steps are shown for the selected method and verbosity.
- **When verbosity is Medium:**
  - Show the full list of steps.
  - Each step has a **checkbox** (e.g. left of the content).
  - Checkbox label or tooltip: e.g. “Include in Short” or “Show in Short view.”
- **When verbosity is Short:**
  - Show only the steps that are **checked**, in the same order as in Medium.
  - No checkboxes in the Short view (or optionally show them so the user can change selection without switching to Medium).
- **Optional:** A separate “Customize Short” section that always shows the Medium step list with checkboxes, independent of current verbosity.

---

## Interaction

1. User selects a **method** (e.g. Elimination) and **Medium** verbosity.
2. The app shows the **Medium step list** with a **checkbox** next to each step.
3. User **checks** the steps they want to see in Short.
4. User switches verbosity to **Short**.
5. The app shows **only the checked steps**, in order.
6. User can switch back to Medium to change checkboxes; Short view updates next time they switch to Short.

---

## Selection lifecycle

- **On new solve / change method / change system:** Selection is **reset to default** (e.g. current fixed short, or all checked, or none).
- **Optional (later):** Persist selection per system or per method (e.g. local storage or backend) so it is restored when the user returns to the same system.

---

## Edge cases

| Case | Design choice |
|------|----------------|
| No steps checked | Short view shows a single message, e.g. “No steps selected for Short. Switch to Medium and check steps to include.” |
| All steps checked | Short = Medium (same content). |
| User changes method | Selection resets to default for the new method. |
| Copy Solution (Short) | Copy the content of the **selected steps only**, in order, in the same format as current copy (e.g. LaTeX). |

---

## Dependencies

- **Structured steps:** The app must have the Medium steps as an **ordered list of items** (each with content and index/ID), not only a single pre-rendered “medium” string. If the API currently returns only `latex_medium` (one string), the design requires either (a) an API change to return a list of steps, or (b) a way to derive that list (e.g. backend sends both `latex_medium` and a `steps[]` array; or a parser that splits the string—less robust).

---

## Summary

- **Medium:** Full step list + checkboxes per step.
- **Short:** Same steps, filtered by checkbox state, same order.
- **Selection:** Stored in frontend; reset on method/system change unless persistence is added.
- **Copy / export:** Short uses only selected steps.

No code in this document; implementation follows this design.
