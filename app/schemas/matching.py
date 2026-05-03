"""
Schemas Pydantic para o Algoritmo de Matching.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class MatchRequestSchema(BaseModel):
    """Dados da solicitação de matching enviados pelo cliente."""
    specialty: str = Field(..., examples=["eletricista"])
    client_latitude: float = Field(..., examples=[-23.5505])
    client_longitude: float = Field(..., examples=[-46.6333])
    max_distance_km: float = Field(default=30.0, ge=1, le=100)


class ScoreComponentSchema(BaseModel):
    """Detalhamento de um componente do score."""
    score: float
    weight: float


class ScoreBreakdownSchema(BaseModel):
    """Breakdown completo do MatchScore por componente."""
    proximity: dict
    rating: dict
    trust_score: dict
    availability: dict
    response_time: dict


class CandidateResultSchema(BaseModel):
    """Resultado de um profissional no matching."""
    rank: int
    professional_id: str
    name: str
    specialty: str
    distance_km: float
    avg_rating: float
    trust_score: float
    match_score: float
    score_breakdown: dict
    is_recommended: bool  # True apenas para o 1º colocado


class MatchResponseSchema(BaseModel):
    """Resposta completa do endpoint de matching."""
    specialty: str
    total_evaluated: int
    total_filtered_out: int
    total_matched: int
    candidates: List[CandidateResultSchema]
    best_match_id: Optional[str] = None
