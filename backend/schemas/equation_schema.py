from pydantic import BaseModel, Field, model_validator


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
    system_id: int | None = None
    variables: list[str] | VariablesSchema
    equation1: EquationSchema
    equation2: EquationSchema
