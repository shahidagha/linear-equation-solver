from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, ensure_solution_methods_schema

# Import models so SQLAlchemy registers them
from backend.models.equation_models import EquationSystem
from backend.models.solution_methods import SolutionMethod

from backend.routes.equation_routes import router as equation_router


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)
ensure_solution_methods_schema()

# Allow Angular frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(equation_router)
