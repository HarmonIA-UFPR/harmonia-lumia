# Estágio 1: Builder (instala dependências e compila pacotes C)
FROM python:3.12.12-alpine3.23 AS builder

# Instala ferramentas de build
RUN apk add --no-cache build-base python3-dev linux-headers

# Instala o Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Cria o ambiente virtual em local seguro (fora da pasta /app)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

# Copia apenas os arquivos de dependências primeiro (otimiza cache do Docker)
COPY pyproject.toml poetry.lock ./

# Instala as dependências (o Poetry detectará o ambiente virtual ativado)
RUN poetry install --only main --no-interaction --no-ansi --no-root

# ---
# Estágio 2: Runtime (imagem final leve)
FROM python:3.12.12-alpine3.23

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
EXPOSE 50052

# Comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "50052", "--reload"]
