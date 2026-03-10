from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

# Import models so SQLAlchemy registers them
from models.equation_models import EquationSystem
from models.solution_methods import SolutionMethod

from routes.equation_routes import router as equation_router


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

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