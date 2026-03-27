from datetime import datetime, timedelta, timezone

import jwt

from app.core.settings import settings


def create_access_token(data: dict) -> str:
    """Gera um JWT assinado usando as configurações do sistema."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """Decodifica e verifica a validade do JWT.
    Retorna o payload dict se válido, None caso contrário."""
    try:
        decoded_payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_payload
    except jwt.PyJWTError:
        return None
