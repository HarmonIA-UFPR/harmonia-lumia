# agente_chat/infrastructure/embedding_service.py

"""
Serviço de Embedding — LaBSE via OpenVINO INT8.
Singleton thread-safe otimizado para CPU.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch
from optimum.intel.openvino import OVModelForFeatureExtraction
from transformers import AutoTokenizer

from agente_chat.config.settings import settings

logger = logging.getLogger("HarmonIA.Embedding")


class EmbeddingModel:
    """
    Singleton thread-safe para modelo LaBSE via OpenVINO.
    Controla threads para não competir com o pool do LLM.
    """

    _instancia = None
    _tokenizer = None
    _carregado = False

    @classmethod
    def _carregar(cls) -> None:
        if cls._carregado:
            return

        model_root = Path(settings.EMBEDDING_MODEL_ID).expanduser().resolve()

        # Detecta estrutura exportada
        if (model_root / "openvino_model.xml").exists():
            model_path = model_root
            export_flag = False
        elif (model_root / "openvino_int8" / "openvino_model.xml").exists():
            model_path = model_root / "openvino_int8"
            export_flag = False
        else:
            logger.info("OpenVINO não encontrado em %s. Exportando...", model_root)
            model_path = model_root
            export_flag = True

        logger.info("Inicializando Embedding via OpenVINO em: %s", model_path)

        cls._tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Limite explícito de threads (evita competir com LLM)
        torch.set_num_threads(4)

        cls._instancia = OVModelForFeatureExtraction.from_pretrained(
            model_path,
            export=export_flag,
            device="CPU",
            ov_config={
                "INFERENCE_NUM_THREADS": "4",
                "NUM_STREAMS": "1",
                "PERFORMANCE_HINT": "LATENCY",
                "CACHE_DIR": str(model_root / "ov_cache"),
            },
        )

        cls._instancia.compile()
        cls._carregado = True
        logger.info("Embedding LaBSE pronto (4 threads).")

    @classmethod
    def encode(cls, textos: list[str]) -> np.ndarray:
        """Gera embeddings normalizados L2 para uma lista de textos."""
        cls._carregar()

        if not textos:
            return np.array([])

        inputs = cls._tokenizer(
            textos,
            padding=True,
            truncation=True,
            max_length=settings.CHUNK_SIZE,
            return_tensors="pt",
        )

        with torch.no_grad():
            outputs = cls._instancia(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :]

        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings.cpu().numpy()


def gerar_embeddings_lote(textos: list[str]) -> np.ndarray:
    """API pública para gerar embeddings em lote."""
    return EmbeddingModel.encode(textos)


def gerar_embedding_unico(texto: str) -> list[float]:
    """API pública para gerar embedding de um único texto."""
    emb = gerar_embeddings_lote([texto])
    return emb[0].tolist() if emb.size > 0 else []
