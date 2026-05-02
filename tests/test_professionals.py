"""
Testes de integração do módulo de Profissionais.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

# Dados reutilizáveis nos testes
USER_PAYLOAD = {
    "name": "Carlos Eletricista",
    "email": "carlos@fixnow.com.br",
    "password": "senha123456",
    "user_type": "professional",
}

PROFILE_PAYLOAD = {
    "specialties": ["eletricista", "pintor"],
    "service_area_km": 15.0,
    "hourly_rate": 80.0,
    "bio": "10 anos de experiência em instalações elétricas residenciais.",
}


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_token(client):
    """Registra usuário e retorna token JWT."""
    await client.post("/api/v1/auth/register", json=USER_PAYLOAD)
    response = await client.post("/api/v1/auth/login", data={
        "username": USER_PAYLOAD["email"],
        "password": USER_PAYLOAD["password"],
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.mark.asyncio
async def test_criar_perfil_profissional(client, auth_headers):
    """Testa criação do perfil de profissional."""
    response = await client.post(
        "/api/v1/professionals/profile",
        json=PROFILE_PAYLOAD,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "eletricista" in data["specialties"]
    assert data["service_area_km"] == 15.0
    assert "trust_score" in data
    assert "trust_level" in data


@pytest.mark.asyncio
async def test_trust_score_inicial(client, auth_headers):
    """Profissional novo deve ter Trust Score definido."""
    await client.post("/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
    response = await client.get("/api/v1/professionals/me", headers=auth_headers)
    data = response.json()
    assert 0.0 <= data["trust_score"] <= 100.0
    assert data["trust_level"] in ["Iniciante", "Bronze", "Prata", "Ouro", "Diamante"]


@pytest.mark.asyncio
async def test_trust_score_detalhado(client, auth_headers):
    """Endpoint de Trust Score deve retornar breakdown completo."""
    # Cria perfil
    create_resp = await client.post(
        "/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers
    )
    prof_id = create_resp.json()["id"]

    # Busca Trust Score detalhado
    response = await client.get(f"/api/v1/professionals/{prof_id}/trust-score")
    assert response.status_code == 200

    data = response.json()
    assert "total" in data
    assert "level" in data
    assert "rating_score" in data
    assert "completion_score" in data
    assert "punctuality_score" in data
    assert "seniority_score" in data
    assert "rating_weight" in data


@pytest.mark.asyncio
async def test_listar_profissionais(client, auth_headers):
    """Listagem deve retornar profissionais disponíveis ordenados por Trust Score."""
    await client.post("/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers)

    response = await client.get("/api/v1/professionals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_filtrar_por_especialidade(client, auth_headers):
    """Filtro por especialidade deve retornar apenas profissionais correspondentes."""
    await client.post("/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers)

    response = await client.get("/api/v1/professionals/?specialty=eletricista")
    assert response.status_code == 200
    for prof in response.json():
        assert "eletricista" in prof["specialties"]


@pytest.mark.asyncio
async def test_nao_pode_criar_dois_perfis(client, auth_headers):
    """Um usuário não pode ter dois perfis profissionais."""
    await client.post("/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers)
    response = await client.post(
        "/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_atualizar_perfil(client, auth_headers):
    """Deve ser possível atualizar dados do perfil."""
    await client.post("/api/v1/professionals/profile", json=PROFILE_PAYLOAD, headers=auth_headers)

    response = await client.patch(
        "/api/v1/professionals/me",
        json={"hourly_rate": 100.0, "is_available": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hourly_rate"] == 100.0
    assert data["is_available"] == False
