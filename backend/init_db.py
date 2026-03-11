from database import engine, ensure_solution_methods_schema
from models.equation_models import Base


def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_solution_methods_schema()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")