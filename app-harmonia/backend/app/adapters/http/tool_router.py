from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.tool.dto import (
    ToolCreateDTO,
    ToolListDTO,
    ToolPublicDTO,
    ToolUpdateDTO,
)
from app.application.tool.service import ToolService
from app.domain.tool.exceptions import (
    ToolAlreadyExistsException,
    ToolNotFoundException,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.tool_repository_impl import (
    ToolRepositoryImpl,
)

router = APIRouter(prefix='/tools', tags=['Ferramentas'])


def get_tool_service(
    session: AsyncSession = Depends(get_session),
) -> ToolService:
    return ToolService(ToolRepositoryImpl(session))


@router.post('/', status_code=HTTPStatus.CREATED, response_model=ToolPublicDTO)
async def create_tool(
    dto: ToolCreateDTO,
    service: ToolService = Depends(get_tool_service),
) -> ToolPublicDTO:
    try:
        return await service.create_tool(dto)
    except ToolAlreadyExistsException as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=e.message)


@router.get('/', status_code=HTTPStatus.OK, response_model=ToolListDTO)
async def list_tools(
    limit: int = 100,
    offset: int = 0,
    service: ToolService = Depends(get_tool_service),
) -> ToolListDTO:
    return await service.list_tools(limit=limit, offset=offset)


@router.get(
    '/{tool_id}', status_code=HTTPStatus.OK, response_model=ToolPublicDTO
)
async def get_tool(
    tool_id: uuid.UUID,
    service: ToolService = Depends(get_tool_service),
) -> ToolPublicDTO:
    try:
        return await service.get_tool(tool_id)
    except ToolNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)


@router.patch(
    '/{tool_id}', status_code=HTTPStatus.OK, response_model=ToolPublicDTO
)
async def update_tool(
    tool_id: uuid.UUID,
    dto: ToolUpdateDTO,
    service: ToolService = Depends(get_tool_service),
) -> ToolPublicDTO:
    try:
        return await service.update_tool(tool_id, dto)
    except ToolNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)


@router.delete(
    '/{tool_id}', status_code=HTTPStatus.OK, response_model=ToolPublicDTO
)
async def delete_tool(
    tool_id: uuid.UUID,
    service: ToolService = Depends(get_tool_service),
) -> ToolPublicDTO:
    try:
        return await service.delete_tool(tool_id)
    except ToolNotFoundException as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.message)
