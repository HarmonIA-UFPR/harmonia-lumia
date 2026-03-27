from http import HTTPStatus

import pytest


@pytest.mark.asyncio
async def test_auth_login_success(client):
    # 1. Arrange: Create a user first
    payload = {
        'user_fullname': 'Auth Test User',
        'user_email': 'auth@harmonia.com',
        'user_profile': 4,
        'user_password': 'my-secure-password',
    }
    await client.post('/users/', json=payload)

    # 2. Act: Try to login
    response = await client.post(
        '/auth/login',
        json={
            'user_email': 'auth@harmonia.com',
            'user_password': 'my-secure-password',
        },
    )

    # 3. Assert
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['user_email'] == payload['user_email']

    # Check if session cookie is set
    assert 'access_token' in response.cookies


@pytest.mark.asyncio
async def test_auth_login_failure(client):
    # 1. Arrange: Create a user
    payload = {
        'user_fullname': 'Auth Test Fail',
        'user_email': 'auth_fail@harmonia.com',
        'user_profile': 1,
        'user_password': 'correct-password',
    }
    await client.post('/users/', json=payload)

    # 2. Act: Try to login with wrong password
    response = await client.post(
        '/auth/login',
        json={
            'user_email': 'auth_fail@harmonia.com',
            'user_password': 'wrong-password',
        },
    )

    # 3. Assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credenciais inválidas'}


@pytest.mark.asyncio
async def test_auth_logout(client):
    # 1. Arrange: Create user and login
    await client.post(
        '/users/',
        json={
            'user_fullname': 'Logout User',
            'user_email': 'logout@harmonia.com',
            'user_profile': 1,
            'user_password': 'pass',
        },
    )

    login_response = await client.post(
        '/auth/login',
        json={
            'user_email': 'logout@harmonia.com',
            'user_password': 'pass',
        },
    )
    # We extract the user id from the login response to use in the logout path
    user_id = login_response.json()['user_uuidv7']

    # 2. Act: Logout
    logout_response = await client.post(f'/auth/logout/{user_id}')

    # 3. Assert
    assert logout_response.status_code == HTTPStatus.OK

    # In some FastAPI/Starlette setups, clearing a session removes the cookie
    # or empties its content
    # Let's ensure the logout endpoint returns success
    assert logout_response.json() == {'detail': 'Logout efetuado com sucesso'}


@pytest.mark.asyncio
async def test_auth_login_conflict(client):
    # 1. Arrange: Create user and login
    await client.post(
        '/users/',
        json={
            'user_fullname': 'Conflict User',
            'user_email': 'conflict@harmonia.com',
            'user_profile': 1,
            'user_password': 'pass',
        },
    )

    login_response = await client.post(
        '/auth/login',
        json={
            'user_email': 'conflict@harmonia.com',
            'user_password': 'pass',
        },
    )
    assert login_response.status_code == HTTPStatus.OK

    # 2. Act: Try to login again while having a valid access token in cookies
    login_conflict = await client.post(
        '/auth/login',
        json={
            'user_email': 'conflict@harmonia.com',
            'user_password': 'pass',
        },
    )

    # 3. Assert: Verify backend blocks duplicate login
    assert login_conflict.status_code == HTTPStatus.CONFLICT
    assert login_conflict.json() == {'detail': 'Usuário já está autenticado'}
