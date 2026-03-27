from __future__ import annotations

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user.dto import LoginDTO, UserPublicDTO
from app.application.user.service import UserService
from app.core.security import create_access_token, verify_token
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)

router = APIRouter(prefix='/auth', tags=['Autenticação'])


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    return UserService(UserRepositoryImpl(session))


@router.post('/login', status_code=HTTPStatus.OK, response_model=UserPublicDTO)
async def login(
    request: Request,
    response: Response,
    dto: LoginDTO,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    existing_token = request.cookies.get('access_token')
    if existing_token:
        payload = verify_token(existing_token)
        if payload and payload.get('sub'):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Usuário já está autenticado',
            )

    user = await service.authenticate_user(dto.user_email, dto.user_password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Credenciais inválidas'
        )

    access_token = create_access_token(data={'sub': str(user.user_uuidv7)})
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        samesite='lax',
        path='/',
        secure=False,  # Set to True in production (HTTPS)
    )

    return user


@router.post('/logout/{user_id}', status_code=HTTPStatus.OK)
async def logout(
    user_id: str,
    response: Response,
) -> dict:
    response.delete_cookie('access_token', path='/', samesite='lax')
    return {'detail': 'Logout efetuado com sucesso'}
