# app/application/user/service.py
from __future__ import annotations

import hashlib
import uuid

from app.application.user.dto import (
    UserCreateDTO,
    UserPublicDTO,
    UserUpdateDTO,
)
from app.domain.user.entity import User
from app.domain.user.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.domain.user.repository import UserRepository


class UserService:
    """Orquestra os casos de uso do domínio User."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    async def create_user(self, dto: UserCreateDTO) -> UserPublicDTO:
        if await self._repo.exists_by_email(dto.user_email):
            raise UserAlreadyExistsException()
        user = User(
            user_fullname=dto.user_fullname,
            user_email=dto.user_email,
            user_profile=dto.user_profile,
            user_password_hash=hashlib.sha256(
                dto.user_password.encode()
            ).hexdigest(),
        )
        saved = await self._repo.save(user)
        return UserPublicDTO.model_validate(saved)

    async def authenticate_user(
        self, email: str, password_hash: str
    ) -> UserPublicDTO | None:
        user = await self._repo.get_by_email(email)
        if not user:
            return None

        # A senha enviada já estaria supostamente em plain text, fazemos o hash
        computed_hash = hashlib.sha256(password_hash.encode()).hexdigest()

        if user.user_password_hash == computed_hash:
            return UserPublicDTO.model_validate(user)

        return None

    async def get_user(self, user_id: uuid.UUID) -> UserPublicDTO:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return UserPublicDTO.model_validate(user)

    async def list_users(self, limit: int = 100, offset: int = 0) -> dict:
        users = await self._repo.list_all(limit=limit, offset=offset)
        return {
            'users': [UserPublicDTO.model_validate(u) for u in users],
            'total': len(users),
        }

    async def update_user(
        self, user_id: uuid.UUID, dto: UserUpdateDTO
    ) -> UserPublicDTO:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        for field, value in dto.model_dump(exclude_none=True).items():
            if field == 'user_password':
                user.user_password_hash = hashlib.sha256(
                    value.encode()
                ).hexdigest()
            else:
                setattr(user, field, value)

        updated = await self._repo.save(user)
        return UserPublicDTO.model_validate(updated)

    async def delete_user(self, user_id: uuid.UUID) -> UserPublicDTO:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        snapshot = UserPublicDTO.model_validate(user)
        await self._repo.delete(user_id)
        return snapshot
