"""
Schemas Pydantic para validação de dados de profissionais.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.models.professional import Specialty


class ProfessionalCreate(BaseModel):
    """Schema para criação do perfil de profissional."""
    bio: Optional[str] = None
    specialties: List[Specialty]
    service_area_km: float = 10.0
    hourly_rate: Optional[float] = None

    @field_validator("specialties")
    @classmethod
    def must_have_at_least_one_specialty(cls, v: List[Specialty]) -> List[Specialty]:
        if not v:
            raise ValueError("Informe ao menos uma especialidade")
        return v

    @field_validator("service_area_km")
    @classmethod
    def area_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("A área de atendimento deve ser positiva")
        return v


class ProfessionalUpdate(BaseModel):
    """Schema para atualização do perfil."""
    bio: Optional[str] = None
    specialties: Optional[List[Specialty]] = None
    service_area_km: Optional[float] = None
    hourly_rate: Optional[float] = None
    is_available: Optional[bool] = None


class TrustScoreResponse(BaseModel):
    """Schema de resposta detalhada do Trust Score."""
    total: float
    level: str                # Iniciante / Bronze / Prata / Ouro / Diamante

    # Detalhamento por componente
    rating_score: float       # Contribuição da avaliação média
    completion_score: float   # Contribuição da taxa de conclusão
    punctuality_score: float  # Contribuição da pontualidade
    seniority_score: float    # Contribuição da senioridade

    # Dados brutos
    avg_rating: float
    completion_rate: float
    total_services: int
    months_active: int

    # Pesos aplicados
    rating_weight: float
    completion_weight: float
    punctuality_weight: float
    seniority_weight: float


class ProfessionalResponse(BaseModel):
    """Schema de resposta com dados completos do profissional."""
    id: uuid.UUID
    user_id: uuid.UUID
    bio: Optional[str]
    specialties: List[str]
    service_area_km: float
    hourly_rate: Optional[float]
    is_available: bool
    is_verified: bool

    # Métricas
    avg_rating: float
    total_services: int
    completed_services: int
    trust_score: float
    trust_level: str          # Badge calculado pelo serviço

    created_at: datetime

    model_config = {"from_attributes": True}
