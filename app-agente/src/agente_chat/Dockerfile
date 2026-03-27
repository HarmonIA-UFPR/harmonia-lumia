# Estágio 1: Builder (instala dependências e compila pacotes C)
FROM python:3.12-slim-trixie AS builder

# Instala ferramentas de build
RUN apt update && apt upgrade -y && \
    apt install -y --no-install-recommends build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Cria o virtualenv em /opt/venv e ativa
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

# Instala o Poetry dentro do virtualenv
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copia apenas os arquivos de dependências primeiro (otimiza cache do Docker)
COPY pyproject.toml poetry.lock ./

# Instala as dependências usando o virtualenv ativo
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# ---
# Estágio 2: Runtime (imagem final leve)
FROM python:3.12-slim-trixie

# Variáveis de ambiente essenciais para logs e comportamento do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

WORKDIR /app

# Copia apenas o ambiente virtual do estágio builder
COPY --from=builder /opt/venv /opt/venv

# Copia o restante do código (será sobrescrito pelo volume no compose, mas útil para build)
COPY . .

# Expõe a porta interna
EXPOSE 50053

# Comando padrão (usando o uvicorn do venv via PATH)
# cli: uvicorn --app-dir src agente_chat.interface.api:app --host 0.0.0.0 --port 8001
CMD ["uvicorn", "--app-dir", "src", "agente_chat.interface.api:app", "--host", "0.0.0.0", "--port", "50053", "--reload"]

