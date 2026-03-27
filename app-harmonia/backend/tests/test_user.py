from http import HTTPStatus
from uuid import UUID

import pytest
from edwh_uuid7 import uuid7
from sqlalchemy import select

from app.domain.user.entity import UserProfile
from app.infrastructure.database.models.user_model import UserModel

UUID_LENGTH = 36

# =========================================================================
# TESTES DE BANCO (SESSÃO E MODELS DIRETAS)
# =========================================================================


@pytest.mark.asyncio
async def test_create_user_com_id_manual(db_session):
    # Fornece ID manualmente no modelo
    id_manual = uuid7()
    new_user_model = UserModel(
        user_uuidv7=id_manual,
        user_fullname='Albano Manual',
        user_email='manual@harmonia.com',
        user_profile=UserProfile.INTERMEDIARIO.value,
        user_password_hash='123',
    )
    db_session.add(new_user_model)
    await db_session.commit()

    user = await db_session.scalar(
        select(UserModel).where(UserModel.user_uuidv7 == id_manual)
    )
    assert user is not None
    assert user.user_uuidv7 == id_manual


@pytest.mark.asyncio
async def test_create_user_com_id_automatico(db_session):
    # NÃO fornece o ID
    new_user_model = UserModel(
        user_fullname='Albano Auto',
        user_email='auto@harmonia.com',
        user_profile=UserProfile.INICIANTE.value,
        user_password_hash='456',
    )
    db_session.add(new_user_model)
    await db_session.commit()

    user = await db_session.scalar(
        select(UserModel).where(UserModel.user_fullname == 'Albano Auto')
    )

    assert user is not None
    assert user.user_uuidv7 is not None
    assert isinstance(user.user_uuidv7, UUID)


# =========================================================================
# TESTES DE API (ROTEADOR /users)
# =========================================================================


@pytest.mark.asyncio
async def test_api_create_user(client):
    payload = {
        'user_fullname': 'Patrick Ribeiro',
        'user_email': 'patrick@harmonia.com',
        'user_profile': 4,
        'user_password': '666-5-hash-1234567890',
    }

    response = await client.post('/users/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()

    assert data['user_fullname'] == payload['user_fullname']
    assert data['user_email'] == payload['user_email']
    assert data['user_profile'] == payload['user_profile']
    assert 'user_password_hash' not in data
    assert 'user_uuidv7' in data
    assert isinstance(data['user_uuidv7'], str)
    assert len(data['user_uuidv7']) == UUID_LENGTH


@pytest.mark.asyncio
async def test_api_read_users(client):
    usuarios_para_criar = [
        {
            'user_fullname': 'Patrick Ribeiro2',
            'user_email': 'patrick2@harmonia.com',
            'user_profile': 4,
            'user_password': 'hash-1',
        },
        {
            'user_fullname': 'Fulano Silva',
            'user_email': 'fulano@harmonia.com',
            'user_profile': 2,
            'user_password': 'hash-2',
        },
    ]

    for payload in usuarios_para_criar:
        await client.post('/users/', json=payload)

    response = await client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert 'users' in data
    assert isinstance(data['users'], list)
    assert len(data['users']) >= len(usuarios_para_criar)

    for user in data['users']:
        assert isinstance(user.get('user_fullname'), str)
        assert isinstance(user.get('user_email'), str)
        assert '@' in user.get('user_email')
        assert isinstance(user.get('user_profile'), int)
        assert 'user_password_hash' not in user
        assert 'user_uuidv7' in user
        assert isinstance(user['user_uuidv7'], str)
        assert len(user['user_uuidv7']) == UUID_LENGTH
