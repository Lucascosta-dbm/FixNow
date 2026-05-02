"""
Testes básicos da API de usuários e autenticação.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """Cliente HTTP assíncrono para testes."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Testa se a API está respondendo."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    """Testa a rota raiz."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "FixNow"
    assert data["status"] == "online"


@pytest.mark.asyncio
async def test_register_user(client):
    """Testa o registro de um novo usuário."""
    payload = {
        "name": "João Silva",
        "email": "joao@fixnow.com.br",
        "password": "senha123456",
        "user_type": "client",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "hashed_password" not in data  # Senha nunca deve aparecer na resposta


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Testa que não é possível registrar dois usuários com o mesmo email."""
    payload = {
        "name": "Maria Santos",
        "email": "maria@fixnow.com.br",
        "password": "senha123456",
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    """Testa login com credenciais válidas."""
    # Registra usuário
    await client.post("/api/v1/auth/register", json={
        "name": "Pedro Costa",
        "email": "pedro@fixnow.com.br",
        "password": "senha123456",
    })

    # Faz login
    response = await client.post("/api/v1/auth/login", data={
        "username": "pedro@fixnow.com.br",
        "password": "senha123456",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Testa login com senha incorreta."""
    response = await client.post("/api/v1/auth/login", data={
        "username": "naoexiste@fixnow.com.br",
        "password": "senhaerrada",
    })
    assert response.status_code == 401
