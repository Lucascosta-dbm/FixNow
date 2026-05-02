"""
Rotas de Autenticação — registro e login de usuários.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.user_service import user_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Registra um novo usuário na plataforma FixNow.
    
    - **name**: Nome completo
    - **email**: Email único (usado para login)
    - **password**: Senha com mínimo 8 caracteres
    - **user_type**: `client` (padrão) ou `professional`
    """
    user = await user_service.create(db, payload)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Autentica o usuário e retorna um token JWT.
    
    Use o token no header: `Authorization: Bearer <token>`
    """
    token, user = await user_service.authenticate(db, form_data.username, form_data.password)
    return TokenResponse(access_token=token, user=user)
