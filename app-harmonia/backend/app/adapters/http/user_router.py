from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user.dto import (
    UserCreateDTO,
    UserListDTO,
    UserPublicDTO,
    UserUpdateDTO,
)
from app.application.user.service import UserService
from app.domain.user.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)

router = APIRouter(prefix='/users', tags=['Usuários'])


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(UserRepositoryImpl(session))


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublicDTO)
async def create_user(
    dto: UserCreateDTO,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    try:
        return await service.create_user(dto)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)


@router.get('/', status_code=HTTPStatus.OK, response_model=UserListDTO)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    service: UserService = Depends(get_user_service),
) -> UserListDTO:
    return await service.list_users(limit=limit, offset=offset)


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicDTO
)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    try:
        return await service.get_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicDTO
)
async def update_user(
    user_id: uuid.UUID,
    dto: UserUpdateDTO,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    try:
        return await service.update_user(user_id, dto)
    except UserNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)


@router.delete(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicDTO
)
async def delete_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    try:
        return await service.delete_user(user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)
