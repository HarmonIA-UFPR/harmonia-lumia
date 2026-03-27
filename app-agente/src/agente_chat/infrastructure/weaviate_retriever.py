# agente_chat/infrastructure/weaviate_retriever.py

"""
Retriever de contexto via Weaviate.
Implementa busca near_vector + MMR otimizado (sem sklearn).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import weaviate
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.connect import ConnectionParams

from agente_chat.config.settings import settings
from agente_chat.infrastructure.embedding_service import gerar_embedding_unico

logger = logging.getLogger("HarmonIA.Retriever")

# =========================================================
# CONSTANTES
# =========================================================

NIVEL_MAXIMO_COMPLEXIDADE = 4
SCORE_EXCELENTE = 0.93    # Acima disso, resultado é suficientemente
SCORE_MINIMO = 0.70       # Abaixo disso, resultado é descartado

# =========================================================
# CONEXÃO SINGLETON
# =========================================================


class WeaviateConnectionFactory:
    """Fábrica singleton para conexão com Weaviate."""

    _client: weaviate.WeaviateClient | None = None

    @classmethod
    def get_client(cls) -> weaviate.WeaviateClient:
        if cls._client is None:
            cls._client = weaviate.WeaviateClient(
                connection_params=ConnectionParams.from_params(
                    http_host=settings.WEAVIATE_HOST,
                    http_port=settings.WEAVIATE_HTTP_PORT,
                    http_secure=False,
                    grpc_host=settings.WEAVIATE_HOST,
                    grpc_port=settings.WEAVIATE_GRPC_PORT,
                    grpc_secure=False,
                )
            )
            cls._client.connect()
        return cls._client


# =========================================================
# MMR OTIMIZADO (SEM SKLEARN)
# =========================================================


class MMRSelector:
    """Maximal Marginal Relevance — implementação vetorizada com NumPy."""

    @staticmethod
    def selecionar(
        query_vector: np.ndarray,
        candidatos_vectors: np.ndarray,
        k: int,
        lambda_param: float,
    ) -> list[int]:
        if len(candidatos_vectors) == 0:
            return []

        if len(candidatos_vectors) <= k:
            return list(range(len(candidatos_vectors)))

        selected: list[int] = []
        unselected = list(range(len(candidatos_vectors)))

        # Similaridade com query (vetores já normalizados)
        relevances = np.dot(candidatos_vectors, query_vector)

        # Primeiro: maior relevância
        first_idx = int(np.argmax(relevances))
        selected.append(first_idx)
        unselected.remove(first_idx)

        while len(selected) < k and unselected:
            best_score = -np.inf
            idx_to_add = None

            for idx in unselected:
                relevance = relevances[idx]

                # Redundância: maior similaridade com os já selecionados
                redundancy = np.max(
                    np.dot(candidatos_vectors[idx], candidatos_vectors[selected].T)
                )

                score = lambda_param * relevance - (1 - lambda_param) * redundancy

                if score > best_score:
                    best_score = score
                    idx_to_add = idx

            if idx_to_add is None:
                break

            selected.append(idx_to_add)
            unselected.remove(idx_to_add)

        return selected


# =========================================================
# RETRIEVER
# =========================================================


class WeaviateRetriever:
    """Retriever que busca contexto no Weaviate com MMR."""

    def __init__(self) -> None:
        self.collection_name = settings.COLLECTION_NAME


    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _buscar_por_nivel(
        self,
        colecao,
        query_vec: list,
        nivel: int,
        fetch_k: int,
    ) -> list:
        """Executa uma única query no Weaviate filtrando por complexity <= nivel."""
        select = Filter.by_property("tool_complexity").less_or_equal(nivel)
        resposta = colecao.query.near_vector(
            near_vector=query_vec,
            limit=fetch_k,
            filters=select,
            return_properties=[
                "tool_description",
                "tool_name",
                "tool_uuidv7",
                "tool_complexity",
            ],
            return_metadata=MetadataQuery(certainty=True),
            include_vector=True,
        )
        return resposta.objects if resposta.objects else []

    def _escalonar_candidatos(
        self,
        colecao,
        query_vec: list,
        perfil: int,
        fetch_k: int,
    ) -> list:
        """
        Busca adaptativa por nível de complexidade.

        - Começa no nível do perfil do usuário.
        - Sobe até NIVEL_MAXIMO_COMPLEXIDADE se o score não atingir SCORE_EXCELENTE.
        - Descarta candidatos com score abaixo de SCORE_MINIMO.
        - Preserva o melhor conjunto encontrado entre todos os níveis testados.
        """
        melhores_candidatos: list = []
        melhor_score_global: float = 0.0

        for nivel in range(int(perfil), NIVEL_MAXIMO_COMPLEXIDADE + 1):
            logger.debug("Buscando candidatos no nível de complexidade %d...", nivel)

            candidatos = self._buscar_por_nivel(colecao, query_vec, nivel, fetch_k)

            if not candidatos:
                logger.debug("Nenhum candidato encontrado no nível %d.", nivel)
                continue

            score = candidatos[0].metadata.certainty or 0.0
            logger.debug("Melhor score no nível %d: %.4f", nivel, score)

            # Descarta resultados abaixo do threshold mínimo
            if score < SCORE_MINIMO:
                logger.debug(
                    "Score %.4f abaixo do mínimo aceito (%.2f). Subindo nível.",
                    score, SCORE_MINIMO,
                )
                continue

            # Guarda se for melhor que qualquer resultado anterior
            if score > melhor_score_global:
                melhores_candidatos = candidatos
                melhor_score_global = score

            # Resultado excelente — não precisa continuar subindo
            if score > SCORE_EXCELENTE:
                logger.info(
                    "Score excelente (%.4f) no nível %d. Encerrando escalonamento.",
                    score, nivel,
                )
                break

        return melhores_candidatos


    def buscar_contexto(
        self,
        query: str,
        perfil: int,
        k: int = 3,
        fetch_k: int = 10,
        lambda_param: float = 0.5,
    ) -> list[dict[str, Any]]:
        """
        Busca contextos relevantes no Weaviate usando near_vector + MMR.

        Returns:
            Lista de dicts com tool_description, tool_name, tool_uuidv7,
            tool_complexity e score.
        """
        try:
            # 1. Embedding da query
            query_vec = gerar_embedding_unico(query)
            if not query_vec:
                logger.warning("Embedding vazio para query='%s'. Retornando [].", query)
                return []


            # 2. Busca adaptativa por nível de complexidade
            #colecao = self._client.collections.get(self.collection_name)
            colecao = WeaviateConnectionFactory.get_client().collections.get(self.collection_name)
            candidatos = self._escalonar_candidatos(colecao, query_vec, perfil, fetch_k)


            # 3. Seleção com MMR
            query_vector = np.array(query_vec)
            candidatos_vectors = np.array([
                obj.vector["default"] for obj in candidatos
            ])

            # 3. Seleção MMR otimizada
            selected_indices = MMRSelector.selecionar(
                query_vector=query_vector,
                candidatos_vectors=candidatos_vectors,
                k=min(k, len(candidatos)),
                lambda_param=lambda_param,
            )

            # 4. Montagem do resultado
            resultado = []
            for idx in selected_indices:
                obj = candidatos[idx]
                resultado.append(
                    {
                        "tool_description": obj.properties.get("tool_description"),
                        "tool_name": obj.properties.get("tool_name"),
                        "tool_uuidv7": obj.properties.get("tool_uuidv7"),
                        "tool_complexity": int(obj.properties.get("tool_complexity", 0)),
                        "score": float(obj.metadata.certainty or 0.0),
                    }
                )

            return resultado

        except KeyError as exc:
            logger.error(
                "Vetor 'default' ausente em um dos candidatos: %s", exc, exc_info=True
            )
            return []
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Erro inesperado na busca MMR para query='%s': %s",
                query, exc, exc_info=True,
            )
            return []
