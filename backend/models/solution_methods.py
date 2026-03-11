from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from database import Base


class SolutionMethod(Base):

    __tablename__ = "solution_methods"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("equation_systems.id"))
    method_name = Column(String)

    latex_detailed = Column(String)
    latex_medium = Column(String)
    latex_short = Column(String)

    solution_json = Column(JSONB)
    graph_data = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
