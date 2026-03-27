import uuid
from http import HTTPStatus

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user.dto import UserPublicDTO
from app.application.user.service import UserService
from app.core.security import verify_token
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    """Retorna uma instância de UserService (Domain API)."""
    return UserService(UserRepositoryImpl(session))


async def get_current_user(
    request: Request,
    service: UserService = Depends(get_user_service),
) -> UserPublicDTO:
    """
    Extrai o token JWT do cookie 'access_token', verifica sua validade e
    retorna o usuário logado via UserService. Lança 401 caso inválido.
    """
    token = request.cookies.get('access_token')

    if not token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Não autenticado',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Sessão expirada ou token inválido',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user_id_str = payload.get('sub')
    if not user_id_str:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token inválido',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        user_id = uuid.UUID(user_id_str)
        user = await service.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Usuário não encontrado',
            headers={'WWW-Authenticate': 'Bearer'},
        )
