from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine

# Import models so SQLAlchemy registers them (for session/relationships)
from backend.models.equation_models import EquationSystem
from backend.models.solution_methods import SolutionMethod

from backend.routes.equation_routes import router as equation_router

app = FastAPI(
    title="Linear Equation Solver API",
    version="1.0",
    description="Solve systems of two linear equations; canonical request shape: variables as [var1, var2], each equation as { terms, constant }.",
)

# Schema is managed by Alembic. Run: python -m alembic upgrade head

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API (preferred)
app.include_router(equation_router, prefix="/v1", tags=["v1"])
# Legacy unversioned (deprecated; use /v1 for new clients)
app.include_router(equation_router)
