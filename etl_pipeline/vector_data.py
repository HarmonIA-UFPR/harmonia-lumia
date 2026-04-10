# etl_pipeline/vector_data.py

"""
Pipeline de Ingestão HarmonIA - Versão Alpha
Campos: tool_uuidv7, tool_name, tool_complexity, tool_description.
Vetorização: Apenas 'tool_description' via LaBSE.
Conectividade: Integrada com Docker Network e Pydantic Settings.
Vetorização: LaBSE INT8 via Optimum-Intel.
"""
import multiprocessing as mp
mp.set_start_method("spawn", force=True)


import json
import uuid
import logging
import sys
from pathlib import Path

import weaviate
from weaviate.collections.classes.config import (
    Configure,
    Property,
    DataType,
)

# --- CONFIGURAÇÃO DE PATHS ---
# No container, PROJECT_ROOT é mapeado para /app
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path("/app") 

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from config.config import settings
    # Importa a versão otimizada com OpenVINO que criamos
    from .embedding import gerar_embeddings_lote 
except ImportError as e:
    print(f"Erro ao importar módulos internos: {e}")
    sys.exit(1)

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s | %(levelname)s | ETL-Ingestor | %(message)s"
)
logger = logging.getLogger(__name__)

class WeaviateIngestor:
    def __init__(self):
        self.collection_name = settings.COLLECTION_NAME
        self.client = self._conectar()

    def _conectar(self):
        """Conecta ao Weaviate via Docker Network."""
        try:
            client = weaviate.WeaviateClient(
                connection_params=weaviate.connect.ConnectionParams.from_params(
                    http_host=settings.WEAVIATE_HOST,
                    http_port=settings.WEAVIATE_HTTP_PORT,
                    http_secure=False,
                    grpc_host=settings.WEAVIATE_HOST,
                    grpc_port=settings.WEAVIATE_GRPC_PORT,
                    grpc_secure=False
                )
            )
            client.connect()
            if client.is_ready():
                logger.info(f"Conexão estável com Weaviate em {settings.WEAVIATE_HOST}")
            return client
        except Exception as e:
            logger.error(f"Falha crítica na conexão Weaviate: {e}")
            sys.exit(1)

    def preparar_colecao(self, force_reset: bool = False):
        """Configura o Schema da coleção no Weaviate v4."""
        if force_reset and self.client.collections.exists(self.collection_name):
            logger.warning(f"Resetando coleção existente: {self.collection_name}")
            self.client.collections.delete(self.collection_name)

        if not self.client.collections.exists(self.collection_name):
            self.client.collections.create(
                name=self.collection_name,
                description="Repositório de ferramentas para recomendação HarmonIA",
                properties=[
                    Property(name="tool_uuidv7", data_type=DataType.TEXT),
                    Property(name="tool_name", data_type=DataType.TEXT),
                    Property(name="tool_complexity", data_type=DataType.INT), 
                    Property(name="tool_description", data_type=DataType.TEXT),
                ],
                # Habilita inserção de vetores externos (LaBSE)
                vector_config=Configure.Vectors.self_provided(),
            )
            logger.info(f"Schema '{self.collection_name}' criado com sucesso.")

    def processar_arquivos(self, arquivo_jsonl: Path):
        """Fluxo Principal: Leitura -> Vetorização OpenVINO -> Batch Ingestion."""
        self.preparar_colecao(force_reset=True)
        colecao = self.client.collections.get(self.collection_name)
        
        objetos_validos = []
        
        if not arquivo_jsonl.exists():
            logger.error(f"Arquivo não encontrado: {arquivo_jsonl}")
            return

        # 1. Leitura e Limpeza
        with open(arquivo_jsonl, 'r', encoding='utf-8') as f:
            for linha in f:
                try:
                    item = json.loads(linha)
                    if item.get("tool_description") and item.get("tool_uuidv7"):
                        objetos_validos.append(item)
                except json.JSONDecodeError:
                    continue

        if not objetos_validos:
            logger.warning("Nenhum dado válido para ingestão.")
            return

        # 2. Geração de Embeddings (Agora acelerado pelo seu i7 + OpenVINO)
        descricoes = [obj["tool_description"] for obj in objetos_validos]
        logger.info(f"Iniciando vetorização de {len(descricoes)} itens via LaBSE INT8...")
        vetores = gerar_embeddings_lote(descricoes)

        # 3. Inserção em Lote Dinâmico
        logger.info(f"Enviando dados para o Weaviate...")
        
        with colecao.batch.dynamic() as batch:
            for item, vetor in zip(objetos_validos, vetores):
                try:
                    # Cast garantido para INT (essencial para o filtro que criamos)
                    complexity_val = int(item.get("tool_complexity", 0))
                    
                    batch.add_object(
                        properties={
                            "tool_uuidv7": str(item["tool_uuidv7"]),
                            "tool_name": item["tool_name"],
                            "tool_complexity": complexity_val, 
                            "tool_description": item["tool_description"],
                        },
                        vector=vetor.tolist(),
                        uuid=uuid.UUID(item["tool_uuidv7"]) 
                    )
                except Exception as e:
                    logger.error(f"Erro no objeto {item.get('tool_uuidv7')}: {e}")

        logger.info(f"Ingestão concluída. Total de registros: {len(objetos_validos)}")
        self.client.close()

if __name__ == "__main__":
    # Caminho do arquivo gerado pelo process_data.py
    ARQUIVO_ALVO = BASE_DIR / "sql_data.jsonl"
    
    ingestor = WeaviateIngestor()
    ingestor.processar_arquivos(ARQUIVO_ALVO)
