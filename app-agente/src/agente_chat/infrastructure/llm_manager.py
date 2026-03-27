# agente_chat/infrastructure/llm_manager.py

"""
Pool de instâncias LLM — thread-safe.
Gerencia 2 instâncias (P-Cores + E-Cores) para permitir concorrência.
"""

from __future__ import annotations

import logging
import time
from queue import Empty, Queue
from threading import Lock

from agente_chat.infrastructure.llm_service import HarmoniaLLM

logger = logging.getLogger("HarmonIA.LLMManager")

# Configurações por tipo de core do i7-13700
OV_CONFIG_PCORE = {
    "INFERENCE_NUM_THREADS": "8",
    "PERFORMANCE_HINT": "LATENCY",
    "ENABLE_CPU_PINNING": "YES",
    "SCHEDULING_CORE_TYPE": "PCORE_ONLY",
}

OV_CONFIG_ECORE = {
    "INFERENCE_NUM_THREADS": "8",
    "PERFORMANCE_HINT": "THROUGHPUT",
    "ENABLE_CPU_PINNING": "YES",
    "SCHEDULING_CORE_TYPE": "ECORE_ONLY",
}


class LLMManager:
    """
    Pool de 2 instâncias LLM.
    - Instância 0 → P-Cores (alta prioridade, baixa latência)
    - Instância 1 → E-Cores (segunda requisição simultânea)
    """

    def __init__(self, timeout: int = 60, warmup: bool = True) -> None:
        self.timeout = timeout
        self.pool: Queue[HarmoniaLLM] = Queue(maxsize=2)
        self.lock = Lock()

        # Métricas
        self.total_requests = 0
        self.total_wait_time = 0.0
        self.total_inference_time = 0.0

        logger.info("Inicializando LLMManager — i7-13700 (P-Cores + E-Cores)")

        configs = [
            (0, OV_CONFIG_PCORE, "P-Cores"),
            (1, OV_CONFIG_ECORE, "E-Cores"),
        ]

        for instance_id, ov_config, label in configs:
            logger.info("Carregando instância %d (%s)...", instance_id, label)
            modelo = HarmoniaLLM(ov_config=ov_config, instance_id=instance_id)

            if warmup:
                logger.info("Warmup instância %d...", instance_id)
                try:
                    modelo.gerar_resposta([{"role": "user", "content": "Responda apenas: ok"}])
                    logger.info("Warmup %d concluído.", instance_id)
                except Exception as e:
                    logger.warning("Warmup instância %d falhou: %s", instance_id, e)

            self.pool.put(modelo)

        logger.info("LLMManager pronto — 2 instâncias disponíveis.")

    def gerar_resposta(self, mensagens: list[dict]) -> str:
        """
        Pega instância livre do pool, gera resposta e devolve ao pool.
        Thread-safe — suporta 2 requisições simultâneas.
        """
        inicio_total = time.perf_counter()
        inicio_espera = time.perf_counter()

        try:
            modelo = self.pool.get(timeout=self.timeout)
        except Empty:
            raise RuntimeError(
                f"Timeout ({self.timeout}s) aguardando instância livre no pool. "
                "Ambas as instâncias estão ocupadas."
            )

        tempo_espera = time.perf_counter() - inicio_espera
        logger.info(
            "[LLMManager] Instância %d alocada | espera=%.1fms",
            modelo.instance_id,
            tempo_espera * 1000,
        )

        try:
            inicio_inferencia = time.perf_counter()
            resposta = modelo.gerar_resposta(mensagens)
            tempo_inferencia = time.perf_counter() - inicio_inferencia
        finally:
            self.pool.put(modelo)
            logger.info("[LLMManager] Instância %d devolvida ao pool", modelo.instance_id)

        tempo_total = time.perf_counter() - inicio_total

        with self.lock:
            self.total_requests += 1
            self.total_wait_time += tempo_espera
            self.total_inference_time += tempo_inferencia

        logger.info(
            "[LLMManager] Concluído | espera=%.1fms | inferência=%.1fms | total=%.1fms",
            tempo_espera * 1000,
            tempo_inferencia * 1000,
            tempo_total * 1000,
        )

        return resposta

    def stats(self) -> dict:
        """Retorna métricas acumuladas do pool."""
        with self.lock:
            if self.total_requests == 0:
                return {"status": "sem requisições ainda"}
            return {
                "total_requests": self.total_requests,
                "instancias_no_pool": self.pool.qsize(),
                "avg_wait_ms": round(self.total_wait_time / self.total_requests * 1000, 2),
                "avg_inference_ms": round(self.total_inference_time / self.total_requests * 1000, 2),
            }
