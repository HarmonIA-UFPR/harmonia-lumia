# HarmonIA Agente Chat

API de recomendação de ferramentas de IA via RAG + LLM com arquitetura **Domain Driven Design (DDD)**.

## Pré-requisitos

- Python 3.12.12
- Poetry 2.3.2
- Docker (para Weaviate)
- Modelos quantizados em `../modelos/` (LaBSE_int8 + Qwen_int8)

## Instalação

```bash
cd agente-chat
poetry env use 3.12
poetry install --no-root
```

## Executar

```bash
# 1. Garanta que o Weaviate está rodando
docker compose -f ../docker-compose.yaml up -d harmonia-weaviate

# 2. Inicie o agente
poetry run uvicorn src.agente_chat.interface.api:app --host 0.0.0.0 --port 8001
```

## Testar

```bash
# Testes unitários
poetry run pytest tests/ -v

# Teste funcional
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_uuid": "019c6dbb-1c92-7d0b-8bf2-f04afc387cb7",
    "user_prompt": "Preciso de uma IA para transcrever áudio",
    "user_profile": 2
  }'
```

## Arquitetura DDD

```
src/agente_chat/
├── domain/          # Entidades, Value Objects, Interfaces (Ports)
├── infrastructure/  # Weaviate, LLM, Embedding (Adapters)
├── application/     # Use Cases (Orquestração)
└── interface/       # FastAPI (API REST)
```

## Contrato

**Entrada:** `{ user_uuid, user_prompt, user_profile }`

**Saída:** `{ user_uuid, user_prompt, user_profile, resposta_llm, tools[3] }`

> A lista `tools` sempre contém **exatamente 3 elementos**. Posições sem recomendação são preenchidas com `{ "tool_uuid": "", "score": 0.0 }`.
