"""
Trust Score Service — núcleo do diferencial competitivo da plataforma FixNow.

O Trust Score é um índice de confiabilidade do profissional (0 a 100),
calculado automaticamente com base em quatro dimensões:

    TrustScore = (avaliação_média  × 0.35)
               + (taxa_conclusão   × 0.30)
               + (pontualidade     × 0.20)
               + (senioridade      × 0.15)

Esse score alimenta diretamente o algoritmo de matching,
priorizando profissionais mais confiáveis para os clientes.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.professional import Professional


# --- Pesos do Trust Score (somam 1.0) ---
WEIGHT_RATING      = 0.35  # Qualidade percebida pelo cliente
WEIGHT_COMPLETION  = 0.30  # Comprometimento com os serviços aceitos
WEIGHT_PUNCTUALITY = 0.20  # Respeito ao tempo do cliente
WEIGHT_SENIORITY   = 0.15  # Experiência acumulada na plataforma

# Tempo máximo considerado para senioridade (em meses)
MAX_SENIORITY_MONTHS = 24


@dataclass
class TrustScoreBreakdown:
    """
    Detalhamento do Trust Score por componente.
    Usado no endpoint /trust-score para transparência total.
    """
    total: float              # Score final (0-100)

    rating_score: float       # Componente de avaliação (0-100)
    completion_score: float   # Componente de conclusão (0-100)
    punctuality_score: float  # Componente de pontualidade (0-100)
    seniority_score: float    # Componente de senioridade (0-100)

    rating_weight: float      = WEIGHT_RATING
    completion_weight: float  = WEIGHT_COMPLETION
    punctuality_weight: float = WEIGHT_PUNCTUALITY
    seniority_weight: float   = WEIGHT_SENIORITY

    # Dados brutos usados no cálculo
    avg_rating: float         = 0.0
    completion_rate: float    = 0.0
    punctuality_raw: float    = 0.0
    months_active: int        = 0
    total_services: int       = 0


class TrustScoreService:
    """
    Serviço responsável por calcular e atualizar o Trust Score dos profissionais.

    O cálculo é determinístico — dado os mesmos dados de entrada,
    sempre produz o mesmo score. Isso garante auditabilidade e transparência.
    """

    def calculate(self, professional: "Professional") -> TrustScoreBreakdown:
        """
        Calcula o Trust Score completo com detalhamento por componente.

        Args:
            professional: Instância do modelo Professional com dados atualizados.

        Returns:
            TrustScoreBreakdown com score total e detalhamento de cada componente.
        """

        # --- Componente 1: Avaliação Média (peso 35%) ---
        # Normaliza de 0-5 estrelas para 0-100 pontos
        rating_score = (professional.avg_rating / 5.0) * 100

        # --- Componente 2: Taxa de Conclusão (peso 30%) ---
        # % de serviços aceitos que foram efetivamente concluídos
        completion_score = professional.completion_rate * 100

        # --- Componente 3: Pontualidade (peso 20%) ---
        # % de chegadas dentro do prazo combinado com o cliente
        punctuality_score = professional.punctuality_score * 100

        # --- Componente 4: Senioridade (peso 15%) ---
        # Tempo na plataforma, com cap em MAX_SENIORITY_MONTHS
        # Profissional novo = 0, profissional com 2+ anos = 100
        seniority_ratio = min(professional.months_active / MAX_SENIORITY_MONTHS, 1.0)
        seniority_score = seniority_ratio * 100

        # --- Score Final Ponderado ---
        total = (
            rating_score      * WEIGHT_RATING +
            completion_score  * WEIGHT_COMPLETION +
            punctuality_score * WEIGHT_PUNCTUALITY +
            seniority_score   * WEIGHT_SENIORITY
        )

        # Garante que o score fique no intervalo [0, 100]
        total = round(min(max(total, 0.0), 100.0), 2)

        return TrustScoreBreakdown(
            total             = total,
            rating_score      = round(rating_score, 2),
            completion_score  = round(completion_score, 2),
            punctuality_score = round(punctuality_score, 2),
            seniority_score   = round(seniority_score, 2),
            avg_rating        = professional.avg_rating,
            completion_rate   = professional.completion_rate,
            punctuality_raw   = professional.punctuality_score,
            months_active     = professional.months_active,
            total_services    = professional.total_services,
        )

    def get_level(self, score: float) -> str:
        """
        Retorna o nível do profissional com base no Trust Score.
        Usado na UI do app para mostrar um badge ao usuário.
        """
        if score >= 90:
            return "Diamante"    # Top 5% da plataforma
        elif score >= 75:
            return "Ouro"        # Profissional excelente
        elif score >= 60:
            return "Prata"       # Profissional confiável
        elif score >= 40:
            return "Bronze"      # Profissional em desenvolvimento
        else:
            return "Iniciante"   # Novo na plataforma

    def update_after_service(
        self,
        professional: "Professional",
        new_rating: float,
        was_completed: bool,
        was_punctual: bool,
    ) -> "Professional":
        """
        Atualiza as métricas do profissional após um serviço e recalcula o Trust Score.

        Args:
            professional: Profissional que prestou o serviço.
            new_rating: Nota dada pelo cliente (1.0 a 5.0).
            was_completed: Se o serviço foi concluído (True) ou cancelado (False).
            was_punctual: Se o profissional chegou dentro do prazo.

        Returns:
            Professional com Trust Score atualizado.
        """

        # Atualiza contadores
        professional.total_services += 1
        if was_completed:
            professional.completed_services += 1
        else:
            professional.cancelled_services += 1

        # Recalcula média de avaliação (média móvel)
        if was_completed and new_rating > 0:
            total_ratings = professional.avg_rating * (professional.completed_services - 1)
            professional.avg_rating = (total_ratings + new_rating) / professional.completed_services

        # Recalcula pontualidade (média móvel)
        punctual_value = 1.0 if was_punctual else 0.0
        professional.punctuality_score = (
            (professional.punctuality_score * (professional.total_services - 1) + punctual_value)
            / professional.total_services
        )

        # Recalcula o Trust Score final
        breakdown = self.calculate(professional)
        professional.trust_score = breakdown.total

        return professional


# Instância global do serviço
trust_score_service = TrustScoreService()
