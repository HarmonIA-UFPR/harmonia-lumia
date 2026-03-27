from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, registry

# 1. Criamos o MetaData definindo o schema padrão
# Removemos o schema="test" hardcoded para compatibilidade total entre
# SQLite in-memory e Postgres local
metadata_obj = MetaData()

# Cria o registry central do SQLAlchemy 2.0
table_registry = registry(metadata=metadata_obj)


# Base pura do SQLAlchemy sem MappedAsDataclass (o domínio é a dataclass agora)
class Base(DeclarativeBase):
    registry = table_registry
