"""
Matching Service — Algoritmo de seleção do melhor profissional para um serviço.

Este é o coração operacional da plataforma FixNow.
Combina 5 critérios ponderados para ranquear profissionais em tempo real:

    MatchScore = (0.30 × Proximidade)
               + (0.25 × Avaliação)
               + (0.20 × TrustScore)
               + (0.15 × Disponibilidade)
               + (0.10 × TempoResposta)

Referência acadêmica: Multi-Criteria Decision Making (MCDM)
aplicado a sistemas de recomendação em marketplaces.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional

# ── Pesos do algoritmo (devem somar 1.0) ────────────────────────────────────
WEIGHT_PROXIMITY      = 0.30
WEIGHT_RATING         = 0.25
WEIGHT_TRUST_SCORE    = 0.20
WEIGHT_AVAILABILITY   = 0.15
WEIGHT_RESPONSE_TIME  = 0.10

# ── Parâmetros de normalização ───────────────────────────────────────────────
MAX_DISTANCE_KM       = 30.0   # Distância máxima considerada no matching
MAX_RESPONSE_TIME_MIN = 60.0   # Tempo de resposta máximo (minutos)


# ── Estruturas de dados ──────────────────────────────────────────────────────

@dataclass
class ProfessionalCandidate:
    """
    Representa um profissional candidato ao matching.
    Contém todos os dados necessários para calcular o score.
    """
    id: str
    name: str
    specialty: str

    # Localização (latitude/longitude)
    latitude: float
    longitude: float

    # Métricas (todas normalizadas para 0-100 internamente)
    avg_rating: float        # 0.0 a 5.0 estrelas
    trust_score: float       # 0 a 100
    is_available: bool       # Online e apto a atender
    avg_response_time_min: float  # Tempo médio para aceitar (minutos)

    # Resultado do matching (preenchido pelo algoritmo)
    distance_km: float = 0.0
    match_score: float = 0.0
    score_breakdown: dict = field(default_factory=dict)


@dataclass
class MatchRequest:
    """Dados da solicitação de serviço do cliente."""
    client_id: str
    specialty: str
    client_latitude: float
    client_longitude: float
    max_distance_km: float = MAX_DISTANCE_KM


@dataclass
class MatchResult:
    """Resultado do matching: ranking de profissionais."""
    request: MatchRequest
    ranked_candidates: List[ProfessionalCandidate]
    total_candidates_evaluated: int
    total_candidates_filtered: int  # Eliminados por distância/disponibilidade

    @property
    def best_match(self) -> Optional[ProfessionalCandidate]:
        """Retorna o profissional com maior score (o recomendado)."""
        return self.ranked_candidates[0] if self.ranked_candidates else None


# ── Algoritmo principal ──────────────────────────────────────────────────────

class MatchingService:
    """
    Serviço de Matching da plataforma FixNow.

    Implementa um algoritmo de decisão multicritério (MCDM) que:
    1. Filtra candidatos inválidos (indisponíveis, fora do raio)
    2. Normaliza cada critério para escala 0-100
    3. Aplica pesos e calcula score final
    4. Retorna candidatos ranqueados do melhor para o pior
    """

    # ── Cálculo de distância ─────────────────────────────────────────────────

    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        """
        Calcula a distância em km entre dois pontos geográficos
        usando a fórmula de Haversine.

        Mais precisa que distância euclidiana para coordenadas geográficas.
        """
        R = 6371  # Raio médio da Terra em km

        lat1_r = math.radians(lat1)
        lat2_r = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # ── Normalização dos critérios ───────────────────────────────────────────

    def _normalize_proximity(self, distance_km: float, max_km: float) -> float:
        """
        Converte distância em score de proximidade (0-100).
        Quanto menor a distância, maior o score.
        """
        if distance_km >= max_km:
            return 0.0
        return (1.0 - distance_km / max_km) * 100

    def _normalize_rating(self, avg_rating: float) -> float:
        """Converte avaliação (0-5) em score (0-100)."""
        return (avg_rating / 5.0) * 100

    def _normalize_trust_score(self, trust_score: float) -> float:
        """Trust Score já está em escala 0-100."""
        return min(max(trust_score, 0.0), 100.0)

    def _normalize_availability(self, is_available: bool) -> float:
        """Disponibilidade: 100 se online, 0 se offline."""
        return 100.0 if is_available else 0.0

    def _normalize_response_time(self, avg_response_min: float) -> float:
        """
        Converte tempo de resposta em score (0-100).
        Quanto mais rápido, maior o score.
        """
        if avg_response_min >= MAX_RESPONSE_TIME_MIN:
            return 0.0
        return (1.0 - avg_response_min / MAX_RESPONSE_TIME_MIN) * 100

    # ── Score final ──────────────────────────────────────────────────────────

    def _calculate_match_score(
        self,
        candidate: ProfessionalCandidate,
        request: MatchRequest,
    ) -> tuple[float, dict]:
        """
        Calcula o MatchScore final do candidato e retorna o breakdown.
        """
        # Normaliza cada critério para 0-100
        proximity_score    = self._normalize_proximity(candidate.distance_km, request.max_distance_km)
        rating_score       = self._normalize_rating(candidate.avg_rating)
        trust_score        = self._normalize_trust_score(candidate.trust_score)
        availability_score = self._normalize_availability(candidate.is_available)
        response_score     = self._normalize_response_time(candidate.avg_response_time_min)

        # Aplica pesos e calcula score ponderado
        final_score = (
            proximity_score    * WEIGHT_PROXIMITY     +
            rating_score       * WEIGHT_RATING        +
            trust_score        * WEIGHT_TRUST_SCORE   +
            availability_score * WEIGHT_AVAILABILITY  +
            response_score     * WEIGHT_RESPONSE_TIME
        )

        breakdown = {
            "proximity":     {"score": round(proximity_score, 2),    "weight": WEIGHT_PROXIMITY,     "distance_km": round(candidate.distance_km, 2)},
            "rating":        {"score": round(rating_score, 2),       "weight": WEIGHT_RATING,        "avg_rating": candidate.avg_rating},
            "trust_score":   {"score": round(trust_score, 2),        "weight": WEIGHT_TRUST_SCORE,   "raw": candidate.trust_score},
            "availability":  {"score": round(availability_score, 2), "weight": WEIGHT_AVAILABILITY,  "is_available": candidate.is_available},
            "response_time": {"score": round(response_score, 2),     "weight": WEIGHT_RESPONSE_TIME, "avg_min": candidate.avg_response_time_min},
        }

        return round(final_score, 2), breakdown

    # ── Método principal ─────────────────────────────────────────────────────

    def match(
        self,
        request: MatchRequest,
        candidates: List[ProfessionalCandidate],
    ) -> MatchResult:
        """
        Executa o algoritmo de matching completo.

        Args:
            request: Dados da solicitação do cliente (localização, especialidade).
            candidates: Lista de profissionais disponíveis na plataforma.

        Returns:
            MatchResult com candidatos ranqueados do melhor para o pior.
        """
        total_evaluated = len(candidates)
        valid_candidates = []

        for candidate in candidates:
            # ── Etapa 1: Calcula distância ───────────────────────────────
            candidate.distance_km = self._haversine_distance(
                request.client_latitude, request.client_longitude,
                candidate.latitude, candidate.longitude,
            )

            # ── Etapa 2: Filtros eliminatórios ───────────────────────────
            if candidate.distance_km > request.max_distance_km:
                continue  # Muito longe

            if not candidate.is_available:
                continue  # Indisponível

            if candidate.specialty != request.specialty:
                continue  # Especialidade diferente

            # ── Etapa 3: Calcula score ───────────────────────────────────
            score, breakdown = self._calculate_match_score(candidate, request)
            candidate.match_score = score
            candidate.score_breakdown = breakdown

            valid_candidates.append(candidate)

        # ── Etapa 4: Ordena por score decrescente ────────────────────────
        ranked = sorted(valid_candidates, key=lambda c: c.match_score, reverse=True)

        return MatchResult(
            request=request,
            ranked_candidates=ranked,
            total_candidates_evaluated=total_evaluated,
            total_candidates_filtered=total_evaluated - len(valid_candidates),
        )


# Instância global
matching_service = MatchingService()
