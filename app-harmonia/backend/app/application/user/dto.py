# app/application/user/dto.py
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.user.entity import UserProfile

# ─── Base compartilhada ──────────────────────────────────────────────────────


class UserBase(BaseModel):
    """Campos comuns a múltiplos DTOs."""

    user_fullname: str
    user_email: EmailStr
    user_profile: UserProfile = UserProfile.INICIANTE  # valida automaticamente

    model_config = ConfigDict(
        use_enum_values=True,  # serializa como int (1,2,3,4) no JSON
    )


# ─── Entrada (request) ───────────────────────────────────────────────────────


class UserCreateDTO(UserBase):
    """POST /users — criação de novo usuário."""

    user_password: str


class LoginDTO(BaseModel):
    """POST /auth/login — payload contendo as credenciais."""

    user_email: EmailStr
    user_password: str


class UserUpdateDTO(BaseModel):
    """PATCH /users/{id} — atualização parcial (todos opcionais)."""

    user_fullname: Optional[str] = None
    user_email: Optional[EmailStr] = None
    user_profile: Optional[UserProfile] = None
    user_password: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)


# ─── Saída (response) ────────────────────────────────────────────────────────


class UserPublicDTO(UserBase):
    """Resposta pública — sem expor senha."""

    user_uuidv7: UUID

    model_config = ConfigDict(
        from_attributes=True,  # permite model_validate(orm_object)
        use_enum_values=True,
    )


class UserListDTO(BaseModel):
    """Resposta para listagem de usuários."""

    users: list[UserPublicDTO]
    total: int = Field(default=0, description='Total de registros')
