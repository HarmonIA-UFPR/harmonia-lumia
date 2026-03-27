# app/infrastructure/repositories/user_repository_impl.py
from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.entity import User, UserProfile
from app.infrastructure.database.models.user_model import UserModel


class UserRepositoryImpl:
    """
    Implementação concreta do UserRepository
    usando SQLAlchemy AsyncSession.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        return User(
            user_uuidv7=model.user_uuidv7,
            user_fullname=model.user_fullname,
            user_email=model.user_email,
            user_password_hash=model.user_password_hash,
            user_profile=UserProfile(model.user_profile),
        )

    @staticmethod
    def _to_model(entity: User) -> UserModel:
        return UserModel(
            user_uuidv7=entity.user_uuidv7,
            user_fullname=entity.user_fullname,
            user_email=entity.user_email,
            user_password_hash=entity.user_password_hash,
            user_profile=(
                entity.user_profile.value
                if isinstance(entity.user_profile, UserProfile)
                else entity.user_profile
            ),
        )

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        model = await self._session.scalar(
            select(UserModel).where(UserModel.user_uuidv7 == user_id)
        )
        if model:
            return self._to_domain(model)
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        model = await self._session.scalar(
            select(UserModel).where(UserModel.user_email == email)
        )
        if model:
            return self._to_domain(model)
        return None

    async def get_by_profile(self, profile: UserProfile) -> list[User]:
        result = await self._session.scalars(
            select(UserModel).where(UserModel.user_profile == profile.value)
        )
        return [self._to_domain(m) for m in result.all()]

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self._session.scalars(
            select(UserModel).limit(limit).offset(offset)
        )
        return [self._to_domain(m) for m in result.all()]

    async def exists_by_email(self, email: str) -> bool:
        return await self.get_by_email(email) is not None

    async def save(self, user: User) -> User:
        # Check if exists to update or insert
        model = await self._session.get(UserModel, user.user_uuidv7)
        if model:
            model.user_fullname = user.user_fullname
            model.user_email = user.user_email
            model.user_password_hash = user.user_password_hash
            model.user_profile = (
                user.user_profile.value
                if isinstance(user.user_profile, UserProfile)
                else user.user_profile
            )
        else:
            model = self._to_model(user)
            self._session.add(model)

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, user_id: uuid.UUID) -> None:
        model = await self._session.get(UserModel, user_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()
