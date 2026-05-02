"""
Modelo de Usuário — representa clientes e profissionais na plataforma FixNow.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserType(str, PyEnum):
    """Tipo de usuário na plataforma."""
    CLIENT = "client"          # Quem contrata serviços
    PROFESSIONAL = "professional"  # Quem presta serviços
    ADMIN = "admin"            # Administrador da plataforma


class User(Base):
    """
    Tabela de usuários da plataforma.
    Um usuário pode ser cliente, profissional ou administrador.
    """

    __tablename__ = "users"

    # Identificador único
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Dados pessoais
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Tipo e status
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType),
        nullable=False,
        default=UserType.CLIENT,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

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

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} type={self.user_type}>"
