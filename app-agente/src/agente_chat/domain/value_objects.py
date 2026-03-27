# agente_chat/domain/value_objects.py

"""
Value Objects do domínio.
Objetos imutáveis que encapsulam validações de negócio.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserProfile:
    """Perfil técnico do usuário (1 = iniciante … 4 = expert)."""

    valor: int

    def __post_init__(self) -> None:
        if not 1 <= self.valor <= 4:
            raise ValueError(f"Perfil deve estar entre 1 e 4, recebido: {self.valor}")


@dataclass(frozen=True, slots=True)
class Score:
    """Score de similaridade normalizado entre 0.0 e 1.0."""

    valor: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.valor <= 1.0:
            raise ValueError(f"Score deve estar entre 0.0 e 1.0, recebido: {self.valor}")
