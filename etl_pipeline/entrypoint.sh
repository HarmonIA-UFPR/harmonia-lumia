#!/bin/bash
set -e  # Aborta se qualquer comando falhar

echo "============================================"
echo "  HarmonIA ETL Pipeline"
echo "============================================"

# Aguarda o Weaviate estar pronto antes de iniciar
# echo "[*] Aguardando Weaviate em ${WEAVIATE_HOST}:${WEAVIATE_HTTP_PORT}..."
# until curl -sf "http://${WEAVIATE_HOST}:${WEAVIATE_HTTP_PORT}/v1/.well-known/ready" > /dev/null; do
#   echo "    Weaviate ainda não está pronto. Tentando novamente em 3s..."
#   sleep 3
# done
# echo "[+] Weaviate está pronto."
# echo ""

# Etapa 1: Download do LaBSE
echo "--------------------------------------------"
echo "[1/5] Baixando modelo LaBSE do Hugging Face..."
echo "--------------------------------------------"
poetry run python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='sentence-transformers/LaBSE', local_dir='modelos/LaBSE')"

echo ""

# Etapa 2: Quantização do LaBSE
echo "--------------------------------------------"
echo "[2/5] Quantizando modelo LaBSE..."
echo "--------------------------------------------"
poetry run python -m etl_pipeline.quantize_labse

echo ""

# Etapa 3: Download do Qwen
echo "--------------------------------------------"
echo "[3/5] Baixando modelo Qwen do Hugging Face..."
echo "--------------------------------------------"
poetry run python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Qwen/Qwen2.5-1.5B-Instruct', local_dir='modelos/Qwen')"

echo ""

# Etapa 4: Quantização do Qwen
echo "--------------------------------------------"
echo "[4/5] Quantizando modelo Qwen..."
echo "--------------------------------------------"
poetry run python -m etl_pipeline.quantize_model

echo ""

# Limpeza: remove os pesos originais FP32 (já temos as versões INT8 e OpenVINO)
echo "--------------------------------------------"
echo "[*] Removendo modelos originais FP32..."
echo "--------------------------------------------"
rm -rf modelos/LaBSE modelos/Qwen
echo "[+] Liberado espaço em disco."

echo ""

# Etapa 5: Ingestão no Weaviate
echo "--------------------------------------------"
echo "[5/5] Populando banco vetorial (Weaviate)..."
echo "--------------------------------------------"
poetry run python -m etl_pipeline.vector_data

echo ""
echo "============================================"
echo "  Pipeline concluído com sucesso!"
echo "============================================"
