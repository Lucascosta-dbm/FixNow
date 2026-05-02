"""
Testes unitários do Trust Score Service.

Esses testes são puros (sem banco de dados) — testam apenas a lógica matemática
do cálculo do score. São os testes mais importantes do TCC pois validam
o diferencial competitivo da plataforma.
"""

import pytest
from unittest.mock import MagicMock

from app.services.trust_score_service import TrustScoreService, WEIGHT_RATING, WEIGHT_COMPLETION


@pytest.fixture
def service():
    return TrustScoreService()


def make_professional(
    avg_rating=5.0,
    total_services=10,
    completed_services=10,
    cancelled_services=0,
    punctuality_score=1.0,
    months_active=12,
):
    """Cria um profissional mock com os dados fornecidos."""
    prof = MagicMock()
    prof.avg_rating = avg_rating
    prof.total_services = total_services
    prof.completed_services = completed_services
    prof.cancelled_services = cancelled_services
    prof.punctuality_score = punctuality_score
    prof.months_active = months_active
    prof.completion_rate = completed_services / total_services if total_services > 0 else 1.0
    return prof


class TestTrustScoreCalculation:
    """Testes da fórmula de cálculo do Trust Score."""

    def test_profissional_perfeito(self, service):
        """Profissional com métricas máximas deve ter score alto."""
        prof = make_professional(
            avg_rating=5.0,
            total_services=50,
            completed_services=50,
            punctuality_score=1.0,
            months_active=24,
        )
        breakdown = service.calculate(prof)
        assert breakdown.total >= 90.0, "Profissional perfeito deve ser Diamante"

    def test_profissional_novo(self, service):
        """Profissional novo (sem serviços) começa com score baixo mas não zero."""
        prof = make_professional(
            avg_rating=0.0,
            total_services=0,
            completed_services=0,
            punctuality_score=1.0,
            months_active=0,
        )
        prof.completion_rate = 1.0  # Novo profissional: taxa máxima por padrão
        breakdown = service.calculate(prof)
        # Com avg_rating=0 e months_active=0, score deve ser baixo
        assert 0.0 <= breakdown.total <= 60.0

    def test_score_dentro_intervalo(self, service):
        """Score sempre deve estar entre 0 e 100."""
        for rating in [0.0, 2.5, 5.0]:
            for months in [0, 12, 24, 48]:
                prof = make_professional(avg_rating=rating, months_active=months)
                breakdown = service.calculate(prof)
                assert 0.0 <= breakdown.total <= 100.0

    def test_pesos_somam_um(self, service):
        """A soma dos pesos deve ser exatamente 1.0."""
        from app.services.trust_score_service import (
            WEIGHT_RATING, WEIGHT_COMPLETION,
            WEIGHT_PUNCTUALITY, WEIGHT_SENIORITY
        )
        total_weight = WEIGHT_RATING + WEIGHT_COMPLETION + WEIGHT_PUNCTUALITY + WEIGHT_SENIORITY
        assert abs(total_weight - 1.0) < 0.0001

    def test_avaliacao_maior_aumenta_score(self, service):
        """Profissional com avaliação maior deve ter Trust Score maior."""
        prof_ruim = make_professional(avg_rating=2.0)
        prof_bom  = make_professional(avg_rating=4.8)

        score_ruim = service.calculate(prof_ruim).total
        score_bom  = service.calculate(prof_bom).total

        assert score_bom > score_ruim

    def test_alta_taxa_cancelamento_reduz_score(self, service):
        """Profissional que cancela muito deve ter score menor."""
        prof_confiavel = make_professional(
            total_services=20, completed_services=20, cancelled_services=0
        )
        prof_cancela = make_professional(
            total_services=20, completed_services=10, cancelled_services=10
        )
        prof_cancela.completion_rate = 10 / 20

        score_confiavel = service.calculate(prof_confiavel).total
        score_cancela   = service.calculate(prof_cancela).total

        assert score_confiavel > score_cancela

    def test_senioridade_com_cap(self, service):
        """Senioridade não deve continuar crescendo após 24 meses."""
        prof_24 = make_professional(months_active=24)
        prof_48 = make_professional(months_active=48)  # Além do cap

        score_24 = service.calculate(prof_24).seniority_score
        score_48 = service.calculate(prof_48).seniority_score

        assert score_24 == score_48 == 100.0, "Score de senioridade deve ser igual após o cap"

    def test_detalhamento_correto(self, service):
        """O breakdown deve mostrar cada componente corretamente."""
        prof = make_professional(
            avg_rating=4.0,
            total_services=10,
            completed_services=9,
            punctuality_score=0.8,
            months_active=12,
        )
        prof.completion_rate = 9 / 10

        breakdown = service.calculate(prof)

        assert breakdown.rating_score == pytest.approx((4.0 / 5.0) * 100, abs=0.1)
        assert breakdown.completion_score == pytest.approx(90.0, abs=0.1)
        assert breakdown.punctuality_score == pytest.approx(80.0, abs=0.1)
        assert breakdown.seniority_score == pytest.approx(50.0, abs=0.1)


class TestTrustScoreLevel:
    """Testes dos níveis/badges do Trust Score."""

    def test_niveis_corretos(self, service):
        assert service.get_level(95.0) == "Diamante"
        assert service.get_level(80.0) == "Ouro"
        assert service.get_level(65.0) == "Prata"
        assert service.get_level(45.0) == "Bronze"
        assert service.get_level(20.0) == "Iniciante"

    def test_fronteiras_dos_niveis(self, service):
        assert service.get_level(90.0) == "Diamante"
        assert service.get_level(89.9) == "Ouro"
        assert service.get_level(75.0) == "Ouro"
        assert service.get_level(74.9) == "Prata"


class TestTrustScoreUpdate:
    """Testes da atualização do score após serviços."""

    def test_servico_bem_avaliado_aumenta_score(self, service):
        """Serviço concluído com nota alta deve aumentar o Trust Score."""
        prof = make_professional(avg_rating=3.0, total_services=5, completed_services=5)
        prof.trust_score = service.calculate(prof).total
        score_antes = prof.trust_score

        service.update_after_service(prof, new_rating=5.0, was_completed=True, was_punctual=True)

        assert prof.trust_score >= score_antes

    def test_cancelamento_reduz_score(self, service):
        """Cancelamento deve reduzir a taxa de conclusão e consequentemente o score."""
        prof = make_professional(
            avg_rating=4.5, total_services=10, completed_services=10
        )
        prof.completion_rate = 1.0
        score_antes = service.calculate(prof).total

        # Simula cancelamento
        service.update_after_service(prof, new_rating=0, was_completed=False, was_punctual=False)

        score_depois = service.calculate(prof).total
        assert score_depois < score_antes

    def test_contadores_atualizados(self, service):
        """Após um serviço, os contadores devem ser incrementados."""
        prof = make_professional(total_services=5, completed_services=5)

        service.update_after_service(prof, new_rating=4.0, was_completed=True, was_punctual=True)

        assert prof.total_services == 6
        assert prof.completed_services == 6
