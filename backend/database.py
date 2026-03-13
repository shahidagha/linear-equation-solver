from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./equations.db"

# Create database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for database models
Base = declarative_base()


def ensure_solution_methods_schema():
    """Backfill required columns for deployments without migrations."""
    inspector = inspect(engine)
    if "solution_methods" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("solution_methods")}
    # Use TEXT for JSON columns on SQLite (no JSONB)
    json_type = "TEXT" if "sqlite" in DATABASE_URL else "JSONB"
    required_columns = {
        "latex_detailed": "TEXT",
        "latex_medium": "TEXT",
        "latex_short": "TEXT",
        "solution_json": json_type,
        "graph_data": json_type,
    }

    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name in existing_columns:
                continue
            connection.execute(
                text(f"ALTER TABLE solution_methods ADD COLUMN IF NOT EXISTS {column_name} {column_type}")
            )


# Dependency used by FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
