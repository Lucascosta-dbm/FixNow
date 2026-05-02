"""
FixNow — Entry point da aplicação FastAPI.
Marketplace de serviços domésticos com segurança e rastreamento em tempo real.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, users

# Inicialização da aplicação
app = FastAPI(
    title=settings.APP_NAME,
    description="Marketplace de serviços domésticos com Trust Score, matching inteligente e rastreamento em tempo real.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração de CORS (permitir requisições do app mobile/web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Autenticação"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["Usuários"])


@app.get("/", tags=["Health"])
async def root():
    """Rota raiz — verifica se a API está no ar."""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check para monitoramento."""
    return {"status": "healthy"}
