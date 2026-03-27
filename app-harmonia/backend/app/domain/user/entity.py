import enum
from dataclasses import dataclass, field
from uuid import UUID

from edwh_uuid7 import uuid7


# 1. Definição do Enum com valores inteiros
class UserProfile(enum.IntEnum):
    INICIANTE = 1
    INTERMEDIARIO = 2
    AVANCADO = 3
    EXPERT = 4


@dataclass
class User:
    user_fullname: str
    user_email: str
    user_password_hash: str
    user_profile: UserProfile = UserProfile.INICIANTE
    user_uuidv7: UUID = field(default_factory=uuid7)
