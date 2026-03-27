# agente_chat/interface/api.py

"""
API FastAPI do Agente Chat.
Endpoints:
- POST /chat - Chat com LLM
- CRUD /history-chats - Gerenciamento do histórico de chat
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from agente_chat.application.use_cases import ProcessarChatUseCase
from agente_chat.domain.entities import ChatRequest
from agente_chat.domain.history_chat.entity import HistoryChat
from agente_chat.domain.history_chat.value_objects import ToolRecommendation
from agente_chat.infrastructure.history_chat_repository import PostgresHistoryChatRepository
from agente_chat.interface.schemas import (
    ChatRequestSchema,
    ChatResponseSchema,
    HistoryChatCreateSchema,
    HistoryChatListResponseSchema,
    HistoryChatRequestSchema,
    HistoryChatResponseSchema,
    ToolRecommendationSchema,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("HarmonIA.API")

# Referências globais — inicializadas no lifespan
_use_case: ProcessarChatUseCase | None = None
_db_pool: asyncpg.Pool | None = None


async def get_repository() -> PostgresHistoryChatRepository:
    """Dependency to get the repository instance."""
    if _db_pool is None:
        raise HTTPException(status_code=503, detail="Banco de dados não está disponível.")
    return PostgresHistoryChatRepository(_db_pool)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Inicializa o use case (carrega modelos) e conexão com PostgreSQL."""
    global _use_case, _db_pool

    logger.info("Inicializando Agente Chat...")

    # Inicializa o use case
    _use_case = ProcessarChatUseCase()
    logger.info("Agente Chat pronto.")

    # Inicializa conexão com PostgreSQL
    try:
        _db_pool = await PostgresHistoryChatRepository.create_pool()
        logger.info("Conexão com PostgreSQL estabelecida.")
    except Exception as e:
        logger.error("Erro ao conectar ao PostgreSQL: %s", e)
        _db_pool = None

    yield

    logger.info("Encerrando Agente Chat...")
    if _use_case is not None:
        _use_case.encerrar()
    if _db_pool is not None:
        await _db_pool.close()
        logger.info("Conexão com PostgreSQL fechada.")


app = FastAPI(
    title="HarmonIA Agente Chat",
    description="API de recomendação de ferramentas de IA via RAG + LLM (DDD) com persistência PostgreSQL",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://200.17.199.216",
        "http://200.17.199.216:4200",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Chat Endpoint (existente)
# =============================================================================

@app.post(
    "/chat",
    response_model=ChatResponseSchema,
    summary="Processar pergunta e recomendar ferramentas",
    description="Recebe user_uuid, user_prompt e user_profile. "
    "Retorna resposta do LLM e exatamente 3 ferramentas recomendadas.",
)
async def chat(req: ChatRequestSchema) -> ChatResponseSchema:
    """Endpoint principal de chat."""
    if _use_case is None:
        raise HTTPException(status_code=503, detail="Agente ainda não foi inicializado.")

    try:
        domain_request = ChatRequest(
            user_uuid=req.user_uuid,
            user_prompt=req.user_prompt,
            user_profile=req.user_profile,
        )

        domain_response = _use_case.executar(domain_request)

        tools_schema = [
            ToolRecommendationSchema(
                tool_uuid=t.tool_uuid,
                score=t.score,
            )
            for t in domain_response.tools
        ]

        return ChatResponseSchema(
            user_uuid=domain_response.user_uuid,
            user_prompt=domain_response.user_prompt,
            user_profile=domain_response.user_profile,
            resposta_llm=domain_response.resposta_llm,
            tools=tools_schema,
        )

    except Exception as e:
        logger.error("Erro ao processar chat: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no Agente Chat.")


# =============================================================================
# HistoryChat CRUD Endpoints
# =============================================================================

def _entity_to_response(entity: HistoryChat) -> HistoryChatResponseSchema:
    """Convert HistoryChat entity to response schema."""
    return HistoryChatResponseSchema(
        his_session_uuidv7=entity.his_session_uuidv7,
        his_chat_uuidv7=entity.his_chat_uuidv7,
        his_user_uuidv7=entity.his_user_uuidv7,
        his_user_profile=entity.his_user_profile,
        his_user_prompt=entity.his_user_prompt,
        his_tool_recom_jsonb=[
            ToolRecommendationSchema(tool_uuid=str(t.tool_uuid), score=float(t.score))
            for t in entity.his_tool_recom_jsonb
        ],
        his_llm_response=entity.his_llm_response,
    )


@app.post(
    "/history-chats",
    response_model=HistoryChatResponseSchema,
    summary="Criar um novo registro de chat processado",
    description="Cria um novo histórico de chat consumindo o LLM para gerar resposta e recomendações. Se for uma nova sessão, omita o his_session_uuidv7. Para continuar uma sessão, envie o UUID da sessão existente.",
    status_code=201,
)
async def create_history_chat(
    data: HistoryChatRequestSchema,
    repo: PostgresHistoryChatRepository = Depends(get_repository),
) -> HistoryChatResponseSchema:
    """Create a new history chat entry from a chat request."""
    if _use_case is None:
        raise HTTPException(status_code=503, detail="Agente ainda não foi inicializado.")

    try:
        # Passo 1: consome o endpoint /chat delegando ao _use_case
        domain_request = ChatRequest(
            user_uuid=data.user_uuid,
            user_prompt=data.user_prompt,
            user_profile=data.user_profile,
        )

        domain_response = _use_case.executar(domain_request)

        # Passo 2: Instancia o objeto history-chat e transfere os dados
        from edwh_uuid7 import uuid7
        from decimal import Decimal

        tools_list = []
        for t in domain_response.tools:
            tool_uuid_str = str(t.tool_uuid)
            if not tool_uuid_str:
                # Omitir ferramentas sem uuid
                continue
            
            try:
                # Try to parse to UUID if it's a valid uuid form, otherwise let runtime handle it
                # or create from string
                tool_uuid = UUID(tool_uuid_str)
            except ValueError:
                # If it's something like "uuid-1", we leave as string or omit?
                # The prompt example shows "uuid-1", but usually it's a real UUID.
                # Assuming real UUID format. If it fails, just use the string.
                # Domain value object expects uuid.UUID but runtime allows string.
                # But for Postgres, it might need to match UUID type if jsonb mapping expects it
                pass 
                
            # Na entity, tools_from_jsonb handles type check, here we instantiate the VO
            tools_list.append(
                ToolRecommendation(
                    tool_uuid=tool_uuid_str, # type: ignore
                    score=Decimal(str(t.score))
                )
            )

        entity = HistoryChat(
            his_session_uuidv7=data.his_session_uuidv7 or uuid7(),
            his_chat_uuidv7=uuid7(),
            his_user_uuidv7=domain_response.user_uuid,
            his_user_profile=domain_response.user_profile,
            his_user_prompt=domain_response.user_prompt,
            his_tool_recom_jsonb=tools_list,
            his_tool_recom_composite_type=tools_list,
            his_llm_response=domain_response.resposta_llm,
        )

        saved = await repo.save(entity)
        return _entity_to_response(saved)

    except Exception as e:
        logger.error("Erro ao criar history chat: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao criar registro.")


@app.get(
    "/history-chats",
    response_model=HistoryChatListResponseSchema,
    summary="Listar todos os registros de chat",
    description="Retorna uma lista paginada de histórico de chat.",
)
async def list_history_chats(
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    repo: PostgresHistoryChatRepository = Depends(get_repository),
) -> HistoryChatListResponseSchema:
    """List all history chat entries with pagination."""
    try:
        items, total = await repo.list_all(limit=limit, offset=offset)
        return HistoryChatListResponseSchema(
            history_chats=[_entity_to_response(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error("Erro ao listar history chats: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao listar registros.")


@app.get(
    "/history-chats/by-session/{session_uuid}",
    response_model=HistoryChatListResponseSchema,
    summary="Listar chats por sessão",
    description="Retorna todos os históricos de chat de uma sessão específica.",
)
async def list_history_chats_by_session(
    session_uuid: UUID,
    repo: PostgresHistoryChatRepository = Depends(get_repository),
) -> HistoryChatListResponseSchema:
    """List all history chat entries for a specific session."""
    try:
        items = await repo.find_by_session(session_uuid)
        return HistoryChatListResponseSchema(
            history_chats=[_entity_to_response(item) for item in items],
            total=len(items),
            limit=len(items),
            offset=0,
        )

    except Exception as e:
        logger.error("Erro ao buscar history chats por sessão: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar registros.")


@app.get(
    "/history-chats/by-user/{user_uuidv7}",
    response_model=list[UUID],
    summary="Listar sessões de chat por usuário",
    description="Retorna uma lista contendo os UUIDs de sessão únicos para um usuário específico.",
)
async def list_history_sessions_by_user(
    user_uuidv7: UUID,
    repo: PostgresHistoryChatRepository = Depends(get_repository),
) -> list[UUID]:
    """List all unique history session UUIDs for a specific user."""
    try:
        items = await repo.find_sessions_by_user(user_uuidv7)
        return items

    except Exception as e:
        logger.error("Erro ao buscar sessões por usuário: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar sessões.")
