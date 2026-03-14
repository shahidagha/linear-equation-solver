from typing import Any

from pydantic import BaseModel, Field, model_validator


# ----- Request (API accepts terms[] or term1/term2; canonical form for storage is terms + constant only) -----

class TermSchema(BaseModel):
    sign: str | int
    numCoeff: int
    numRad: int
    denCoeff: int
    denRad: int


class EquationSchema(BaseModel):
    terms: list[TermSchema] | None = Field(default=None, min_length=2, max_length=2)
    term1: TermSchema | None = None
    term2: TermSchema | None = None
    constant: TermSchema

    @model_validator(mode="after")
    def ensure_terms(self):
        """Accept both legacy `terms` payload and current `term1`/`term2` payload."""

        if self.terms is None:
            if self.term1 is None or self.term2 is None:
                raise ValueError("Equation must provide either `terms` or `term1` and `term2`.")
            self.terms = [self.term1, self.term2]

        return self


class VariablesSchema(BaseModel):
    var1: str
    var2: str


class SolveRequestSchema(BaseModel):
    """Request for save-system and solve-system. Canonical storage uses variables as [var1, var2] and each equation as { terms, constant } only."""
    system_id: int | None = None
    variables: list[str] | VariablesSchema
    equation1: EquationSchema
    equation2: EquationSchema


# ----- Response (single source of truth for API contract; align frontend types with these) -----

class MethodLatexSchema(BaseModel):
    latex_detailed: str
    latex_medium: str
    latex_short: str


class SolveResponseSchema(BaseModel):
    """Response from POST /solve-system. Frontend SolverResponse should match this."""
    system_id: int | None = None
    solution: dict[str, str | int | float]
    methods: dict[str, MethodLatexSchema | Any]  # elimination_latex, substitution_latex, etc.
    graph: dict[str, Any]  # equation1_points, equation2_points, intersection, labels

    model_config = {"extra": "allow"}


class SaveResponseSchema(BaseModel):
    """Response from POST /save-system or from solve-system when it saves/updates."""
    status: str  # saved | duplicate | updated | invalid | variable_conflict | not_found
    id: int | None = None
    message: str | None = None
    existing_variables: list[str] | None = None

    model_config = {"extra": "allow"}
