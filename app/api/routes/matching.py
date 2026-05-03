"""
Rotas de Matching — conecta cliente ao melhor profissional disponível.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.professional import Professional
from app.schemas.matching import MatchRequestSchema, MatchResponseSchema, CandidateResultSchema
from app.services.matching_service import matching_service, MatchRequest, ProfessionalCandidate

router = APIRouter()


@router.post("/match", response_model=MatchResponseSchema)
async def find_best_professional(
    payload: MatchRequestSchema,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Encontra o melhor profissional para uma solicitação de serviço.

    O algoritmo avalia todos os profissionais cadastrados e retorna
    um ranking baseado em: proximidade, avaliação, Trust Score,
    disponibilidade e tempo médio de resposta.

    - **specialty**: Tipo de serviço (ex: eletricista, encanador)
    - **client_latitude / client_longitude**: Localização do cliente
    - **max_distance_km**: Raio máximo de busca (padrão: 30 km)
    """
    # Busca todos os profissionais no banco
    result = await db.execute(select(Professional))
    professionals = result.scalars().all()

    # Converte para candidatos do algoritmo
    candidates = []
    for prof in professionals:
        # Localização simulada para demonstração
        # Em produção: viria do GPS do app do profissional via Kafka
        import random
        base_lat = payload.client_latitude
        base_lon = payload.client_longitude
        offset = random.uniform(-0.1, 0.1)

        specialty = prof.specialties[0] if prof.specialties else "outros"

        candidates.append(ProfessionalCandidate(
            id=str(prof.id),
            name=prof.user.name if prof.user else "Profissional",
            specialty=specialty,
            latitude=base_lat + offset,
            longitude=base_lon + offset,
            avg_rating=prof.avg_rating,
            trust_score=prof.trust_score,
            is_available=prof.is_available,
            avg_response_time_min=5.0,
        ))

    # Executa o algoritmo de matching
    match_request = MatchRequest(
        client_id=current_user_id,
        specialty=payload.specialty,
        client_latitude=payload.client_latitude,
        client_longitude=payload.client_longitude,
        max_distance_km=payload.max_distance_km,
    )

    match_result = matching_service.match(match_request, candidates)

    # Monta resposta com ranking
    ranked_candidates = []
    for i, candidate in enumerate(match_result.ranked_candidates):
        ranked_candidates.append(CandidateResultSchema(
            rank=i + 1,
            professional_id=candidate.id,
            name=candidate.name,
            specialty=candidate.specialty,
            distance_km=round(candidate.distance_km, 2),
            avg_rating=candidate.avg_rating,
            trust_score=candidate.trust_score,
            match_score=candidate.match_score,
            score_breakdown=candidate.score_breakdown,
            is_recommended=(i == 0),
        ))

    return MatchResponseSchema(
        specialty=payload.specialty,
        total_evaluated=match_result.total_candidates_evaluated,
        total_filtered_out=match_result.total_candidates_filtered,
        total_matched=len(ranked_candidates),
        candidates=ranked_candidates,
        best_match_id=match_result.best_match.id if match_result.best_match else None,
    )
