# agente_chat/application/prompt_builder.py

"""
Construção de prompts para recomendação de ferramentas.
Compatível com pipeline RAG + Qwen 2.5.
"""

from __future__ import annotations

from typing import Any

# =========================================================
# SYSTEM PROMPT
# =========================================================


class HarmonIASystemPrompt:
    """Prompt de sistema para o modelo de recomendação."""

    TEXTO = """
Você é o HarmonIA, um sistema especialista em recomendação de ferramentas de IA.

Sua tarefa é analisar o PERFIL TÉCNICO, a PERGUNTA e o CONTEXTO RECUPERADO para recomendar as ferramentas mais adequadas.

REGRAS DE OURO:
1. Utilize exclusivamente informações presentes no CONTEXTO TÉCNICO RECUPERADO.
2. Não invente funcionalidades, características ou dados inexistentes.
3. Se não houver informação suficiente no contexto, responda que não foram encontradas ferramentas compatíveis no banco.
4. Responda sempre em Português.
5. O nível de complexidade da explicação deve ser proporcional ao perfil do usuário.
6. Retorne SOMENTE um JSON válido. Não escreva nenhum texto antes ou depois do JSON.

FORMATO DE RESPOSTA (JSON ESTRITO):
{
  "resumo": "Explicação técnica macro sobre como as ferramentas encontradas resolvem o problema.",
  "tools": [
    {
      "id": "ID exato do contexto (tool_uuidv7)",
      "nome": "Nome exato da ferramenta",
      "score": 0.0,
      "justificativa": "Explique por que esta ferramenta é adequada para o perfil do usuário."
    }
  ]
}
""".strip()

    @classmethod
    def build(cls) -> str:
        return cls.TEXTO


# =========================================================
# USER PROMPT TEMPLATE
# =========================================================


class RecommendationPromptTemplate:
    """Template do prompt do usuário para recomendação."""

    TEMPLATE = """
### CONFIGURAÇÃO DO AMBIENTE
- Perfil Técnico do Usuário (Nível): {perfil}

### SOLICITAÇÃO DO USUÁRIO
"{pergunta}"

### CONTEXTO TÉCNICO RECUPERADO
<INICIO_CONTEXTO>
{context_block}
<FIM_CONTEXTO>

### REQUISITO FINAL
- Gere o JSON de recomendação adaptando a linguagem para o nível {perfil}.
- Não adicione textos explicativos fora do bloco JSON.
""".strip()

    @classmethod
    def render(cls, perfil: int, pergunta: str, context_block: str) -> str:
        return cls.TEMPLATE.format(
            perfil=perfil,
            pergunta=pergunta,
            context_block=context_block,
        )


# =========================================================
# MESSAGE BUILDER
# =========================================================


class RecommendationMessageBuilder:
    """Constrói a lista de mensagens para o LLM."""

    MAX_FERRAMENTAS = 5
    MAX_DESCRICAO_CHARS = 1200

    @staticmethod
    def _truncar_texto(texto: str, limite: int) -> str:
        if not texto:
            return ""
        if len(texto) <= limite:
            return texto
        return texto[:limite] + "..."

    @classmethod
    def _formatar_contexto(cls, context_snippets: list[dict[str, Any]]) -> str:
        """Formata dados vindos do retriever para o LLM."""
        if not context_snippets:
            return "Nenhuma ferramenta encontrada com os filtros aplicados."

        formatted = []
        for i, c in enumerate(context_snippets[: cls.MAX_FERRAMENTAS], start=1):
            descricao = cls._truncar_texto(
                c.get("tool_description", ""),
                cls.MAX_DESCRICAO_CHARS,
            )
            snippet = (
                f"[Ferramenta {i}]\n"
                f"- ID: {c.get('tool_uuidv7')}\n"
                f"- Nome: {c.get('tool_name')}\n"
                f"- Complexidade: {c.get('tool_complexity')}\n"
                f"- Descrição Técnica: {descricao}\n"
                f"- Score de Similaridade: {c.get('score')}\n"
            )
            formatted.append(snippet)

        return "\n".join(formatted)

    @classmethod
    def build(
        cls,
        perfil: int,
        pergunta: str,
        context_snippets: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        contexto_formatado = cls._formatar_contexto(context_snippets)
        user_content = RecommendationPromptTemplate.render(
            perfil=perfil,
            pergunta=pergunta,
            context_block=contexto_formatado,
        )
        return [
            {"role": "system", "content": HarmonIASystemPrompt.build()},
            {"role": "user", "content": user_content},
        ]


# =========================================================
# API PÚBLICA
# =========================================================


def build_recommendation_messages(
    perfil: int,
    pergunta: str,
    context_snippets: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Constrói as mensagens de recomendação para o LLM."""
    return RecommendationMessageBuilder.build(perfil, pergunta, context_snippets)
