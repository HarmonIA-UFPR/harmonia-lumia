# agente_chat/infrastructure/llm_service.py

"""
Serviço LLM — Qwen 2.5 via OpenVINO INT8.
Cada instância é vinculada a um tipo de core (P-Core ou E-Core).
"""

from __future__ import annotations

import logging
from pathlib import Path

from optimum.intel.openvino import OVModelForCausalLM
from transformers import AutoTokenizer

from agente_chat.config.settings import settings

logger = logging.getLogger("HarmonIA.LLM")


class HarmoniaLLM:
    """Instância única do LLM Qwen via OpenVINO."""

    def __init__(self, ov_config: dict | None = None, instance_id: int = 0) -> None:
        """
        Inicializa o modelo LLM.

        Args:
            ov_config: Configuração OpenVINO por instância (P-Cores ou E-Cores).
            instance_id: Identificador para logs.
        """
        self.instance_id = instance_id
        model_path = str(Path(settings.LLM_MODEL_ID).expanduser().resolve())

        logger.info("Instância %d | Carregando de %s", instance_id, model_path)

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            local_files_only=True,
            fix_mistral_regex=True,
        )

        _ov_config = ov_config or {
            "INFERENCE_NUM_THREADS": str(settings.THREADS),
            "PERFORMANCE_HINT": "LATENCY",
            "ENABLE_CPU_PINNING": "YES",
            "SCHEDULING_CORE_TYPE": "PCORE_ONLY",
        }

        self.modelo = OVModelForCausalLM.from_pretrained(
            model_path,
            device="CPU",
            local_files_only=True,
            ov_config=_ov_config,
        )
        self.modelo.compile()

        self.modelo.generation_config.temperature = None
        self.modelo.generation_config.top_p = None
        self.modelo.generation_config.top_k = None
        self.modelo.generation_config.do_sample = False

        logger.info(
            "Instância %d pronta | cores=%s",
            instance_id,
            _ov_config.get("SCHEDULING_CORE_TYPE"),
        )

    def gerar_resposta(self, mensagens: list[dict]) -> str:
        """Gera resposta contendo apenas a saída do modelo."""
        prompt = self.tokenizer.apply_chat_template(
            mensagens,
            add_generation_prompt=True,
            tokenize=False,
        )
        logger.info("[LLM:%d] input_chars=%d", self.instance_id, len(prompt))

        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_len = inputs.input_ids.shape[1]
        logger.info("[LLM:%d] input_tokens=%d", self.instance_id, input_len)

        output = self.modelo.generate(
            **inputs,
            use_cache=True,
            max_new_tokens=1500,
            do_sample=False,
            return_dict_in_generate=True,
        )

        tokens_gerados = output.sequences[0][input_len:]
        resposta = self.tokenizer.decode(tokens_gerados, skip_special_tokens=True)
        logger.info(
            "[LLM:%d] output_tokens=%d | saída: %r",
            self.instance_id,
            len(tokens_gerados),
            resposta[:200],
        )
        return resposta
