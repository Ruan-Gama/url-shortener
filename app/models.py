"""
Modelos ORM (SQLAlchemy) da aplicação.

Define a estrutura das tabelas do banco de dados.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class URL(Base):
    """Representa uma URL encurtada armazenada no banco."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)