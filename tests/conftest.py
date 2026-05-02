"""
Configuração global dos testes — compatibilidade com Windows e asyncpg.
"""

import asyncio
import sys

import pytest
from sqlalchemy import text

from app.core.database import AsyncSessionLocal


def pytest_configure(config):  # noqa: ARG001
    """Garante SelectorEventLoop no Windows antes de qualquer loop ser criado."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def event_loop_policy():
    """Retorna a policy correta para a plataforma — obrigatório para asyncpg no Windows."""
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function", autouse=True)
async def clean_test_users():
    """Limpa usuários de teste do banco antes de cada sessão de testes."""
    test_emails = (
        "joao@fixnow.com.br",
        "maria@fixnow.com.br",
        "pedro@fixnow.com.br",
        "carlos@fixnow.com.br",
    )
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("DELETE FROM users WHERE email = ANY(:emails)"),
            {"emails": list(test_emails)},
        )
        await session.commit()
    yield
