"""
Modelo de Profissional — estende o usuário com dados específicos de quem presta serviços.
Inclui o Trust Score, que é o principal diferencial da plataforma FixNow.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List

from sqlalchemy import (
    String, Float, Integer, Boolean, DateTime,
    ForeignKey, Enum, func, Text
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Specialty(str, PyEnum):
    """Especialidades disponíveis na plataforma."""
    ELECTRICIAN   = "eletricista"
    PLUMBER       = "encanador"
    PAINTER       = "pintor"
    MASON         = "pedreiro"
    CLEANER       = "diarista"
    LOCKSMITH     = "chaveiro"
    AC_TECHNICIAN = "tecnico_ar_condicionado"
    CARPENTER     = "marceneiro"
    GARDENER      = "jardineiro"
    OTHER         = "outros"


class Professional(Base):
    """
    Perfil do profissional na plataforma FixNow.

    Relacionamento 1:1 com User — todo profissional é também um usuário.

    O Trust Score (0-100) é o coração do diferencial competitivo da plataforma:
    ele agrega avaliação média, taxa de conclusão, pontualidade e tempo na
    plataforma em um único número que ranqueia profissionais no matching.
    """

    __tablename__ = "professionals"

    # Identificador único
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Relacionamento com User (1:1)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Dados profissionais
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    specialties: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
    )
    service_area_km: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=10.0,  # Raio padrão de 10 km
    )
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Métricas que alimentam o Trust Score ---

    # Avaliação média (0.0 a 5.0)
    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)

    # Contadores de serviços
    total_services: Mapped[int] = mapped_column(Integer, default=0)
    completed_services: Mapped[int] = mapped_column(Integer, default=0)
    cancelled_services: Mapped[int] = mapped_column(Integer, default=0)

    # Pontualidade: % de chegadas dentro do prazo (0.0 a 1.0)
    punctuality_score: Mapped[float] = mapped_column(Float, default=1.0)

    # Tempo na plataforma em meses (usado para calcular senioridade)
    months_active: Mapped[int] = mapped_column(Integer, default=0)

    # --- Trust Score final (calculado pelo TrustScoreService) ---
    trust_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relacionamento com User
    user = relationship("User", backref="professional_profile", lazy="joined")

    @property
    def completion_rate(self) -> float:
        """Taxa de conclusão de serviços (0.0 a 1.0)."""
        if self.total_services == 0:
            return 1.0  # Profissional novo começa com taxa máxima
        return self.completed_services / self.total_services

    def __repr__(self) -> str:
        return (
            f"<Professional id={self.id} "
            f"trust_score={self.trust_score} "
            f"specialties={self.specialties}>"
        )
