"""
Serviço de Usuários — contém toda a lógica de negócio relacionada a usuários.
Camada intermediária entre as rotas (API) e o banco de dados (models).
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password, create_access_token


class UserService:
    """Serviço com todas as operações de usuário."""

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Busca usuário por ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Busca usuário por email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, payload: UserCreate) -> User:
        """
        Registra um novo usuário na plataforma.
        Verifica se o email já está em uso antes de criar.
        """
        # Verifica se email já existe
        existing = await self.get_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email já está cadastrado",
            )

        # Cria o usuário com senha hasheada
        user = User(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            user_type=payload.user_type,
        )

        db.add(user)
        await db.flush()  # Gera o ID sem commitar ainda
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> str:
        """
        Autentica o usuário e retorna um token JWT.
        Lança exceção 401 se as credenciais forem inválidas.
        """
        user = await self.get_by_email(db, email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta desativada. Entre em contato com o suporte.",
            )

        # Gera o token JWT com o ID do usuário
        token = create_access_token(data={"sub": str(user.id)})
        return token, user

    async def update(self, db: AsyncSession, user: User, payload: UserUpdate) -> User:
        """Atualiza dados do usuário."""
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        await db.refresh(user)
        return user


# Instância global do serviço
user_service = UserService()
