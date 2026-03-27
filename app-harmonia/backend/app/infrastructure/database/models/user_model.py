from typing import Optional
from uuid import UUID

from edwh_uuid7 import uuid7
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.user.entity import UserProfile
from app.infrastructure.database.models.base import Base


class UserModel(Base):
    __tablename__ = 'user'

    user_uuidv7: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )
    user_fullname: Mapped[Optional[str]] = mapped_column(
        String, nullable=False, default=None
    )
    user_email: Mapped[Optional[str]] = mapped_column(
        String, unique=True, nullable=False, default=None
    )
    user_password_hash: Mapped[Optional[str]] = mapped_column(
        String, nullable=False, default=None
    )

    # Enum types persist as Integers in DB
    user_profile: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=UserProfile.INICIANTE.value,
        server_default='1',
    )
