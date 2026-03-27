#!/usr/bin/env python3
"""
Entry point para o servidor FastAPI do Agente Chat.

Uso:
    poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    
Ou via script Poetry:
    poetry run agente-chat
"""

import uvicorn

from agente_chat.interface.api import app


def run_server() -> None:
    """Função para iniciar o servidor via script de entry point."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
