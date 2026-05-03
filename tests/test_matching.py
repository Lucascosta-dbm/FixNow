"""
Testes unitários do Algoritmo de Matching.
Testa a lógica pura sem banco de dados.
"""

import pytest
from app.services.matching_service import (
    MatchingService,
    MatchRequest,
    ProfessionalCandidate,
    WEIGHT_PROXIMITY, WEIGHT_RATING, WEIGHT_TRUST_SCORE,
    WEIGHT_AVAILABILITY, WEIGHT_RESPONSE_TIME,
)


@pytest.fixture
def service():
    return MatchingService()


@pytest.fixture
def base_request():
    return MatchRequest(
        client_id="CLI-001",
        specialty="eletricista",
        client_latitude=-23.5614,
        client_longitude=-46.6558,
        max_distance_km=30.0,
    )


def make_candidate(
    id="PRO-001",
    name="Carlos",
    specialty="eletricista",
    lat=-23.5480,
    lon=-46.6388,
    avg_rating=4.5,
    trust_score=80.0,
    is_available=True,
    avg_response_time_min=5.0,
) -> ProfessionalCandidate:
    return ProfessionalCandidate(
        id=id,
        name=name,
        specialty=specialty,
        latitude=lat,
        longitude=lon,
        avg_rating=avg_rating,
        trust_score=trust_score,
        is_available=is_available,
        avg_response_time_min=avg_response_time_min,
    )


class TestMatchingFilters:
    """Testa os filtros eliminatórios."""

    def test_profissional_offline_eliminado(self, service, base_request):
        candidates = [make_candidate(is_available=False)]
        result = service.match(base_request, candidates)
        assert len(result.ranked_candidates) == 0
        assert result.total_candidates_filtered == 1

    def test_especialidade_errada_eliminada(self, service, base_request):
        candidates = [make_candidate(specialty="encanador")]
        result = service.match(base_request, candidates)
        assert len(result.ranked_candidates) == 0

    def test_muito_distante_eliminado(self, service, base_request):
        # Profissional em Porto Alegre (~1100 km)
        candidates = [make_candidate(lat=-30.0346, lon=-51.2177)]
        result = service.match(base_request, candidates)
        assert len(result.ranked_candidates) == 0

    def test_candidato_valido_nao_eliminado(self, service, base_request):
        candidates = [make_candidate()]
        result = service.match(base_request, candidates)
        assert len(result.ranked_candidates) == 1


class TestMatchingScore:
    """Testa o cálculo do score."""

    def test_pesos_somam_um(self):
        total = (
            WEIGHT_PROXIMITY + WEIGHT_RATING + WEIGHT_TRUST_SCORE
            + WEIGHT_AVAILABILITY + WEIGHT_RESPONSE_TIME
        )
        assert abs(total - 1.0) < 0.0001

    def test_score_dentro_intervalo(self, service, base_request):
        candidates = [make_candidate()]
        result = service.match(base_request, candidates)
        score = result.ranked_candidates[0].match_score
        assert 0.0 <= score <= 100.0

    def test_melhor_profissional_vence(self, service, base_request):
        """O profissional com melhores métricas deve ter score maior."""
        ruim = make_candidate(
            id="RUIM", avg_rating=2.0, trust_score=30.0,
            avg_response_time_min=45.0,
        )
        bom = make_candidate(
            id="BOM", avg_rating=5.0, trust_score=95.0,
            avg_response_time_min=2.0,
        )
        result = service.match(base_request, [ruim, bom])
        assert result.ranked_candidates[0].id == "BOM"

    def test_mais_proximo_tem_vantagem(self, service, base_request):
        """Com tudo igual, o mais próximo deve ganhar."""
        longe = make_candidate(id="LONGE", lat=-23.7000, lon=-46.8000)
        perto = make_candidate(id="PERTO", lat=-23.5620, lon=-46.6580)
        result = service.match(base_request, [longe, perto])
        assert result.ranked_candidates[0].id == "PERTO"

    def test_ranking_ordenado_por_score(self, service, base_request):
        """Candidatos devem estar em ordem decrescente de score."""
        candidates = [
            make_candidate(id=f"P{i}", avg_rating=float(i), trust_score=float(i * 10))
            for i in range(1, 5)
        ]
        result = service.match(base_request, candidates)
        scores = [c.match_score for c in result.ranked_candidates]
        assert scores == sorted(scores, reverse=True)

    def test_breakdown_presente(self, service, base_request):
        """Breakdown deve ter todos os 5 componentes."""
        result = service.match(base_request, [make_candidate()])
        breakdown = result.ranked_candidates[0].score_breakdown
        assert "proximity" in breakdown
        assert "rating" in breakdown
        assert "trust_score" in breakdown
        assert "availability" in breakdown
        assert "response_time" in breakdown


class TestMatchingResult:
    """Testa o objeto de resultado."""

    def test_best_match_e_o_primeiro(self, service, base_request):
        candidates = [make_candidate(id="A"), make_candidate(id="B", avg_rating=2.0)]
        result = service.match(base_request, candidates)
        assert result.best_match.id == result.ranked_candidates[0].id

    def test_sem_candidatos_retorna_vazio(self, service, base_request):
        result = service.match(base_request, [])
        assert result.best_match is None
        assert len(result.ranked_candidates) == 0

    def test_haversine_distancia_correta(self, service):
        """Testa cálculo de distância: SP → RJ ≈ 360 km."""
        dist = service._haversine_distance(
            -23.5505, -46.6333,  # São Paulo
            -22.9068, -43.1729,  # Rio de Janeiro
        )
        assert 340 < dist < 380
