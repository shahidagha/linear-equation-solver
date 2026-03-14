"""
Run database migrations (Alembic). Use this to create or update schema.
Run from project root: python -m backend.init_db
Or directly: python -m alembic upgrade head
"""
import os
import subprocess
import sys


def main() -> int:
    # Alembic must run from project root (where alembic.ini lives)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=project_root,
    )
    if result.returncode == 0:
        print("Database schema up to date.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
