from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.equation_routes import router as equation_router


app = FastAPI()

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