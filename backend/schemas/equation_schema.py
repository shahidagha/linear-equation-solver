from pydantic import BaseModel, Field


class TermSchema(BaseModel):
    sign: str | int
    numCoeff: int
    numRad: int
    denCoeff: int
    denRad: int


class EquationSchema(BaseModel):
    terms: list[TermSchema] = Field(..., min_length=2, max_length=2)
    constant: TermSchema


class SolveRequestSchema(BaseModel):
    variables: list[str] = Field(..., min_length=2, max_length=2)
    equation1: EquationSchema
    equation2: EquationSchema
