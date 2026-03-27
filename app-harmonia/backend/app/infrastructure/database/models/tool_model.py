from typing import Optional
from uuid import UUID

from edwh_uuid7 import uuid7
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.tool.entity import ToolComplexity
from app.infrastructure.database.models.base import Base


class ToolModel(Base):
    __tablename__ = 'tool'
    # schema removido para compatibilidade total entre
    # SQLite in-memory (testes) e Postgres

    tool_uuidv7: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    tool_name: Mapped[str] = mapped_column(String, nullable=False)
    tool_description: Mapped[str] = mapped_column(String, nullable=False)
    tool_data_prog: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tool_official_link: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=None
    )
    tool_repository_link: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=None
    )
    tool_documentation_link: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=None
    )
    # Enum types persist as Integers in DB
    tool_complexity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=ToolComplexity.INICIANTE.value,
        server_default='1',
    )
