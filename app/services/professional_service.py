"""
Serviço de Profissionais — CRUD e lógica de negócio do perfil profissional.
"""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.professional import Professional, Specialty
from app.schemas.professional import ProfessionalCreate, ProfessionalUpdate
from app.services.trust_score_service import trust_score_service


class ProfessionalService:
    """Serviço com todas as operações de perfil profissional."""

    async def get_by_id(
        self, db: AsyncSession, professional_id: uuid.UUID
    ) -> Optional[Professional]:
        """Busca profissional por ID."""
        result = await db.execute(
            select(Professional).where(Professional.id == professional_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Optional[Professional]:
        """Busca o perfil profissional de um usuário específico."""
        result = await db.execute(
            select(Professional).where(Professional.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: ProfessionalCreate,
    ) -> Professional:
        """
        Cria o perfil profissional para um usuário existente.
        Um usuário só pode ter um perfil profissional.
        """
        # Verifica se já tem perfil
        existing = await self.get_by_user_id(db, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este usuário já possui um perfil profissional",
            )

        # Converte Specialty enum para lista de strings
        specialties = [s.value for s in payload.specialties]

        professional = Professional(
            user_id=user_id,
            bio=payload.bio,
            specialties=specialties,
            service_area_km=payload.service_area_km,
            hourly_rate=payload.hourly_rate,
            avg_rating=0.0,
            total_services=0,
            completed_services=0,
            cancelled_services=0,
            punctuality_score=1.0,
            months_active=0,
        )

        # Calcula o Trust Score inicial (será baixo para profissional novo)
        breakdown = trust_score_service.calculate(professional)
        professional.trust_score = breakdown.total

        db.add(professional)
        await db.flush()
        await db.refresh(professional)
        return professional

    async def update(
        self,
        db: AsyncSession,
        professional: Professional,
        payload: ProfessionalUpdate,
    ) -> Professional:
        """Atualiza dados do perfil profissional."""
        update_data = payload.model_dump(exclude_unset=True)

        # Converte especialidades para strings se fornecidas
        if "specialties" in update_data and update_data["specialties"]:
            update_data["specialties"] = [s.value for s in update_data["specialties"]]

        for field, value in update_data.items():
            setattr(professional, field, value)

        await db.flush()
        await db.refresh(professional)
        return professional

    async def list_available(
        self,
        db: AsyncSession,
        specialty: Optional[str] = None,
        min_trust_score: float = 0.0,
        limit: int = 20,
    ) -> List[Professional]:
        """
        Lista profissionais disponíveis com filtros opcionais.
        Ordenados por Trust Score decrescente — os mais confiáveis primeiro.
        """
        query = (
            select(Professional)
            .where(Professional.is_available == True)
            .where(Professional.trust_score >= min_trust_score)
            .order_by(Professional.trust_score.desc())
            .limit(limit)
        )

        # Filtro por especialidade
        if specialty:
            query = query.where(Professional.specialties.contains([specialty]))

        result = await db.execute(query)
        return list(result.scalars().all())

    async def simulate_service_completion(
        self,
        db: AsyncSession,
        professional_id: uuid.UUID,
        rating: float,
        was_completed: bool = True,
        was_punctual: bool = True,
    ) -> Professional:
        """
        Simula a conclusão de um serviço e recalcula o Trust Score.
        Usado para demonstração no TCC e testes do algoritmo.
        """
        professional = await self.get_by_id(db, professional_id)
        if not professional:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profissional não encontrado",
            )

        # Atualiza métricas e recalcula score
        trust_score_service.update_after_service(
            professional, rating, was_completed, was_punctual
        )

        await db.flush()
        await db.refresh(professional)
        return professional


# Instância global do serviço
professional_service = ProfessionalService()
