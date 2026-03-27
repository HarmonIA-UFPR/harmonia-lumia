from http import HTTPStatus

import pytest

UUID_LENGTH = 36


@pytest.mark.asyncio
async def test_api_create_tool(client):
    payload = {
        'tool_name': 'FastAPI Test Framework',
        'tool_description': 'Super fast framework testing',
        'tool_data_prog': True,
        'tool_official_link': 'https://fastapi.tiangolo.com',
        'tool_complexity': 2,
    }

    response = await client.post('/tools/', json=payload)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()

    assert data['tool_name'] == payload['tool_name']
    assert data['tool_data_prog'] == payload['tool_data_prog']
    assert data['tool_official_link'] == payload['tool_official_link']
    assert 'tool_uuidv7' in data
    assert isinstance(data['tool_uuidv7'], str)
    assert len(data['tool_uuidv7']) == UUID_LENGTH


@pytest.mark.asyncio
async def test_api_read_tools(client):
    tools = [
        {
            'tool_name': 'FastAPI',
            'tool_description': 'Web framework',
            'tool_data_prog': True,
            'tool_complexity': 3,
        },
        {
            'tool_name': 'SQLAlchemy',
            'tool_description': 'ORM',
            'tool_data_prog': True,
            'tool_complexity': 4,
        },
    ]

    for tool in tools:
        await client.post('/tools/', json=tool)

    response = await client.get('/tools/')

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    # The expected output might be a list directly, or under a key depending
    # on your dto. We will assume a straight list based on typical FastAPI
    # generic list responses. If the response wrapper has 'tools', adjust here.
    assert isinstance(data, list) or 'tools' in data

    if 'tools' in data:
        items = data['tools']
    else:
        items = data

    assert len(items) >= len(tools)

    for item in items:
        assert 'tool_name' in item
        assert 'tool_complexity' in item
        assert 'tool_uuidv7' in item
