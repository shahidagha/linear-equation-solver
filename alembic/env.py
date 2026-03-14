"""
Alembic environment: uses backend database URL and model metadata.
Run from project root: python -m alembic upgrade head
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import create_engine

# Load .env so DATABASE_URL is available
from dotenv import load_dotenv
load_dotenv()

# Use same URL and engine behavior as the application
from backend.database import Base, DATABASE_URL

# Import all models so Base.metadata has every table
from backend.models.equation_models import EquationSystem  # noqa: F401
from backend.models.solution_methods import SolutionMethod  # noqa: F401

config = context.config
target_metadata = Base.metadata

# Set url in config from env (so Alembic and our get_url() agree)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    """Use application DATABASE_URL (from .env or default SQLite)."""
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL only)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB)."""
    url = get_url()
    connect_args = {}
    if "sqlite" in url:
        connect_args["check_same_thread"] = False
    connectable = create_engine(url, connect_args=connect_args, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
