"""
Rotas de Profissionais — perfil, listagem e Trust Score.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalUpdate,
    ProfessionalResponse,
    TrustScoreResponse,
)
from app.services.professional_service import professional_service
from app.services.trust_score_service import trust_score_service

router = APIRouter()


def _build_response(prof) -> ProfessionalResponse:
    """Monta o schema de resposta adicionando o nível do Trust Score."""
    return ProfessionalResponse(
        id=prof.id,
        user_id=prof.user_id,
        bio=prof.bio,
        specialties=prof.specialties,
        service_area_km=prof.service_area_km,
        hourly_rate=prof.hourly_rate,
        is_available=prof.is_available,
        is_verified=prof.is_verified,
        avg_rating=prof.avg_rating,
        total_services=prof.total_services,
        completed_services=prof.completed_services,
        trust_score=prof.trust_score,
        trust_level=trust_score_service.get_level(prof.trust_score),
        created_at=prof.created_at,
    )


@router.post("/profile", response_model=ProfessionalResponse, status_code=201)
async def create_profile(
    payload: ProfessionalCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Cria o perfil profissional do usuário autenticado.

    - **specialties**: Lista de especialidades (ex: ["eletricista", "pintor"])
    - **service_area_km**: Raio máximo de atendimento em km
    - **hourly_rate**: Valor por hora (opcional)
    """
    prof = await professional_service.create(db, uuid.UUID(current_user_id), payload)
    return _build_response(prof)


@router.get("/", response_model=list[ProfessionalResponse])
async def list_professionals(
    specialty: Optional[str] = Query(None, description="Filtrar por especialidade"),
    min_trust_score: float = Query(0.0, ge=0, le=100, description="Trust Score mínimo"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Lista profissionais disponíveis, ordenados por Trust Score.

    Use os filtros para refinar a busca por especialidade e nível de confiança.
    """
    professionals = await professional_service.list_available(
        db, specialty, min_trust_score, limit
    )
    return [_build_response(p) for p in professionals]


@router.get("/me", response_model=ProfessionalResponse)
async def get_my_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retorna o perfil profissional do usuário autenticado."""
    prof = await professional_service.get_by_user_id(db, uuid.UUID(current_user_id))
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil profissional não encontrado",
        )
    return _build_response(prof)


@router.get("/{professional_id}", response_model=ProfessionalResponse)
async def get_professional(
    professional_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Busca um profissional pelo ID."""
    prof = await professional_service.get_by_id(db, professional_id)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado",
        )
    return _build_response(prof)


@router.get("/{professional_id}/trust-score", response_model=TrustScoreResponse)
async def get_trust_score(
    professional_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna o Trust Score detalhado de um profissional.

    Mostra a contribuição de cada componente para o score final,
    garantindo total transparência para o profissional.
    """
    prof = await professional_service.get_by_id(db, professional_id)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado",
        )

    breakdown = trust_score_service.calculate(prof)

    return TrustScoreResponse(
        total             = breakdown.total,
        level             = trust_score_service.get_level(breakdown.total),
        rating_score      = breakdown.rating_score,
        completion_score  = breakdown.completion_score,
        punctuality_score = breakdown.punctuality_score,
        seniority_score   = breakdown.seniority_score,
        avg_rating        = breakdown.avg_rating,
        completion_rate   = breakdown.completion_rate,
        total_services    = breakdown.total_services,
        months_active     = breakdown.months_active,
        rating_weight     = breakdown.rating_weight,
        completion_weight = breakdown.completion_weight,
        punctuality_weight= breakdown.punctuality_weight,
        seniority_weight  = breakdown.seniority_weight,
    )


@router.patch("/me", response_model=ProfessionalResponse)
async def update_my_profile(
    payload: ProfessionalUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza o perfil profissional do usuário autenticado."""
    prof = await professional_service.get_by_user_id(db, uuid.UUID(current_user_id))
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil profissional não encontrado",
        )
    updated = await professional_service.update(db, prof, payload)
    return _build_response(updated)
