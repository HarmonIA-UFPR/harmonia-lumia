# etl_pipeline/embeddings.py

"""
Módulo de Vetorização HarmonIA - Versão OpenVINO INT8.
Otimizado para inferência de baixa latência no i7-13700.
"""

import threading
from pathlib import Path
import torch
import numpy as np
from optimum.intel.openvino import OVModelForFeatureExtraction
from transformers import AutoTokenizer

from config.config import settings


class EmbeddingModel:
    """
    Singleton thread-safe para modelo LaBSE via OpenVINO.
    Controla threads para não competir com o pool do LLM.
    """

    _instancia = None
    _tokenizer = None
    _carregado = False
    _lock = threading.Lock()  # Trava para garantir thread-safety no carregamento

    @classmethod
    def _carregar(cls):
        # Double-checked locking pattern para performance e segurança
        if cls._carregado:
            return

        with cls._lock:
            # Verifica novamente dentro do lock para evitar condição de corrida
            if cls._carregado:
                return

            model_root = Path(settings.EMBEDDING_MODEL_ID).expanduser().resolve()

            if not model_root.exists():
                raise FileNotFoundError(f"Diretório do modelo não encontrado: {model_root}")

            # Detecta estrutura exportada
            if (model_root / "openvino_model.xml").exists():
                model_path = model_root
                export_flag = False
            elif (model_root / "openvino_int8" / "openvino_model.xml").exists():
                model_path = model_root / "openvino_int8"
                export_flag = False
            else:
                print(f"[*] OpenVINO IR não encontrado em {model_root}. Exportando em tempo de execução...")
                model_path = model_root
                export_flag = True

            print(f"[*] Inicializando Embedding via OpenVINO em: {model_path}")

            # Tokenizer
            cls._tokenizer = AutoTokenizer.from_pretrained(model_path)

            # Limite explícito de threads do PyTorch (evita competir com LLM)
            torch.set_num_threads(4)

            # Configurações OpenVINO otimizadas para o i7-13700
            cls._instancia = OVModelForFeatureExtraction.from_pretrained(
                model_path,
                export=export_flag,
                device="CPU",
                ov_config={
                    "INFERENCE_NUM_THREADS": "4",
                    "NUM_STREAMS": "1",
                    "PERFORMANCE_HINT": "LATENCY",
                    "CACHE_DIR": str(model_root / "ov_cache")
                }
            )

            # Compilação prévia para evitar latência na primeira inferência
            cls._instancia.compile()

            cls._carregado = True
            print("[+] Embedding LaBSE carregado e compilado (4 threads).")

    @classmethod
    def encode(cls, textos: list[str]) -> np.ndarray:
        cls._carregar()

        if not textos:
            return np.array([])

        try:
            inputs = cls._tokenizer(
                textos,
                padding=True,
                truncation=True,
                max_length=settings.CHUNK_SIZE,
                return_tensors="pt"
            )

            with torch.no_grad():
                outputs = cls._instancia(**inputs)
                # O LaBSE usa o token [CLS] (índice 0) para a representação da sentença
                embeddings = outputs.last_hidden_state[:, 0, :]

            # Normalização L2 obrigatória para Similaridade de Cosseno no Weaviate
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            return embeddings.cpu().numpy()
            
        except Exception as e:
            print(f"[-] Erro durante a vetorização: {e}")
            # Retorna array vazio em caso de falha grave na tokenização/inferência
            return np.array([])


def gerar_embeddings_lote(textos: list[str]) -> np.ndarray:
    return EmbeddingModel.encode(textos)


def gerar_embedding_unico(texto: str) -> list[float]:
    emb = gerar_embeddings_lote([texto])
    return emb[0].tolist() if emb.size > 0 else []