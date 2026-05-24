from sqlalchemy import (
    Column, Integer, String, JSON, Boolean, DateTime
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String, unique=True)
    description = Column(String)
    skills = Column(JSON)
    tools = Column(JSON)
    endpoint = Column(String)
    cost_model = Column(String)
    owner = Column(String)

    # 👇 novo campo
    status = Column(String, default="available")



class Collaboration(Base):
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True)
    from_agent = Column(String)
    to_agent = Column(String)

    task = Column(String)
    expected_output = Column(String)

    status = Column(String, default="pending")  # pending | completed
    output = Column(JSON, nullable=True)

    success = Column(Boolean, nullable=True)
    rating = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
