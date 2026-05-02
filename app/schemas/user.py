"""
Schemas Pydantic para validação de dados de usuário.
Usados nos endpoints da API para entrada e saída de dados.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserType


class UserCreate(BaseModel):
    """Schema para criação de novo usuário (registro)."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    user_type: UserType = UserType.CLIENT

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        """Valida que a senha tem pelo menos 8 caracteres."""
        if len(v) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres")
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("O nome não pode ser vazio")
        return v.strip()


class UserResponse(BaseModel):
    """Schema de resposta com dados do usuário (sem senha)."""
    id: uuid.UUID
    name: str
    email: str
    phone: Optional[str]
    user_type: UserType
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema para atualização de dados do usuário."""
    name: Optional[str] = None
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Schema de resposta após login bem-sucedido."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
