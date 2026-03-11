from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from backend.database import Base

class EquationSystem(Base):
    __tablename__ = "equation_systems"

    id = Column(Integer, primary_key=True, index=True)

    variables = Column(JSONB, nullable=False)

    equation1 = Column(JSONB, nullable=False)
    equation2 = Column(JSONB, nullable=False)

    equation_hash = Column(String, index=True)
    system_hash = Column(String, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())