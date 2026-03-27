# agente_chat/application/use_cases.py

"""
Caso de uso principal: Processar Chat.
Orquestra o fluxo RAG → Prompt → LLM → Parse → Normalização.
NÃO grava nada em banco de dados — retorna ChatResponse puro.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

try:
    from json_repair import repair_json
    _JSON_REPAIR_AVAILABLE = True
except ImportError:
    _JSON_REPAIR_AVAILABLE = False

from agente_chat.application.prompt_builder import build_recommendation_messages
from agente_chat.domain.entities import ChatRequest, ChatResponse, ToolRecommendation
from agente_chat.infrastructure.llm_manager import LLMManager
from agente_chat.infrastructure.weaviate_retriever import WeaviateRetriever

logger = logging.getLogger("HarmonIA.UseCase")


class ProcessarChatUseCase:
    """
    Caso de uso: recebe um ChatRequest e devolve um ChatResponse.

    Fluxo:
        1. Busca contextos no Weaviate (RAG + MMR)
        2. Monta prompt com os contextos
        3. Gera resposta via LLM
        4. Faz parsing do JSON retornado pelo LLM
        5. Normaliza as tools (score do Weaviate) e adiciona omitidas
        6. Garante que sempre há exatamente 3 tools na resposta
    """

    def __init__(self) -> None:
        self.retriever = WeaviateRetriever()
        self.llm = LLMManager(timeout=60, warmup=True)

    def executar(self, request: ChatRequest) -> ChatResponse:
        """Processa a requisição de chat e retorna a resposta."""
        try:
            logger.info(
                "Iniciando processamento | Usuário: %s | Prompt: %s",
                request.user_uuid,
                request.user_prompt[:80],
            )

            # 1. RAG — busca contextos similares
            contextos_raw = self.retriever.buscar_contexto(
                query=request.user_prompt,
                perfil=request.user_profile,
                k=3,
            )
            logger.info("[RAG] %d contextos recuperados", len(contextos_raw))

            # 2. Prompt — monta mensagens para o LLM
            mensagens = build_recommendation_messages(
                perfil=request.user_profile,
                pergunta=request.user_prompt,
                context_snippets=contextos_raw,
            )

            # 3. LLM — gera resposta
            resposta_llm_raw = self.llm.gerar_resposta(mensagens)
            logger.info("[LLM RAW] %r", resposta_llm_raw[:400])

            # 4. Parse JSON
            resposta_json = self._parse_llm_output(resposta_llm_raw)
            logger.info("[PARSED] keys=%s", list(resposta_json.keys()))

            # 5. Normaliza tools — score vem do Weaviate, não do LLM
            scores_weaviate = {
                str(c["tool_uuidv7"]): c["score"]
                for c in contextos_raw
                if "tool_uuidv7" in c
            }
            logger.info("[SCORES WEAVIATE] %s", scores_weaviate)

            tool_recommendations = self._extrair_tools(resposta_json, scores_weaviate)
            logger.info("[TOOLS NORMALIZADAS] %s", tool_recommendations)

            # 6. Monta resposta — ChatResponse garante exatamente 3 tools
            resposta_texto = (
                resposta_json.get("resumo")
                or resposta_json.get("resposta")
                or resposta_llm_raw
            )

            return ChatResponse(
                user_uuid=request.user_uuid,
                user_prompt=request.user_prompt,
                user_profile=request.user_profile,
                resposta_llm=resposta_texto,
                tools=tool_recommendations,
            )

        except Exception as e:
            logger.error("Erro crítico | Usuário: %s | %s", request.user_uuid, e, exc_info=True)
            raise

    # ----------------------------------------------------------
    # Parsing do JSON do LLM
    # ----------------------------------------------------------

    def _parse_llm_output(self, raw: str) -> dict[str, Any]:
        """Tenta extrair JSON válido da saída do LLM."""
        try:
            clean = raw.replace("```json", "").replace("```", "").strip()

            # Tenta parse direto
            try:
                return json.loads(clean)
            except json.JSONDecodeError:
                pass

            # Tentativa 2: json-repair direto no clean (lida com trailing commas,
            # aspas faltando, e também faz a extração do bloco JSON internamente)
            if _JSON_REPAIR_AVAILABLE:
                try:
                    repaired = repair_json(clean, return_objects=True)
                    if isinstance(repaired, dict) and repaired:
                        return repaired
                except Exception:
                    pass

            # Extrai bloco JSON via regex
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    json_str = self._fechar_json_truncado(json_str)
                    return json.loads(json_str)

            raise ValueError("Nenhum bloco JSON encontrado na resposta do LLM")

        except Exception as ex:
            logger.warning("Falha no parsing JSON | %s", ex)
            logger.warning("[RAW COMPLETO] %s", raw)
            return {"resposta": raw, "tools": [], "status": "raw_text"}




    @staticmethod
    def _fechar_json_truncado(json_str: str) -> str:
        """Fecha chaves/colchetes abertos em um JSON truncado pelo LLM."""
        json_str = re.sub(r",\s*$", "", json_str.strip())
        json_str += "]" * (json_str.count("[") - json_str.count("]"))
        json_str += "}" * (json_str.count("{") - json_str.count("}"))
        return json_str

    # ----------------------------------------------------------
    # Normalização de tools
    # ----------------------------------------------------------

    def _extrair_tools(
        self,
        resposta_json: dict[str, Any],
        scores_weaviate: dict[str, float] | None = None,
    ) -> list[ToolRecommendation]:
        """
        Normaliza a lista de ferramentas usando scores do Weaviate.
        Retorna lista de ToolRecommendation.
        """
        tools = resposta_json.get("tools", [])
        if not isinstance(tools, list):
            logger.warning("[EXTRAIR_TOOLS] 'tools' não é lista: %s", type(tools))
            return []

        scores_weaviate = scores_weaviate or {}
        normalizado: list[ToolRecommendation] = []

        ja_adicionadas = set()
        for t in tools:
            try:
                tool_uuid = str(t.get("id", ""))
                if not tool_uuid or tool_uuid in ja_adicionadas:
                    continue

                # Prioriza score do Weaviate; fallback para score do LLM
                score_weaviate = scores_weaviate.get(tool_uuid)
                score_final = score_weaviate if score_weaviate is not None else float(t.get("score", 0))

                if score_weaviate is None:
                    logger.warning(
                        "[EXTRAIR_TOOLS] UUID %s não encontrado no Weaviate — usando score do LLM",
                        tool_uuid,
                    )

                normalizado.append(
                    ToolRecommendation(
                        tool_uuid=tool_uuid,
                        score=score_final,
                    )
                )
                ja_adicionadas.add(tool_uuid)
            except Exception as ex:
                logger.warning("[EXTRAIR_TOOLS] Erro ao normalizar %s: %s", t, ex)

        # Completa com as ferramentas do Weaviate que o LLM não listou
        weaviate_sorted = sorted(scores_weaviate.items(), key=lambda x: x[1], reverse=True)
        for tool_uuid, score in weaviate_sorted:
            if tool_uuid not in ja_adicionadas:
                normalizado.append(ToolRecommendation(tool_uuid=tool_uuid, score=score))
                ja_adicionadas.add(tool_uuid)

        return normalizado

    def encerrar(self) -> None:
        """Libera recursos do retriever se necessário."""
        if hasattr(self.retriever, "fechar"):
            self.retriever.fechar()
