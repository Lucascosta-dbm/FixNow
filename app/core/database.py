"""
Configuração da conexão assíncrona com o banco de dados PostgreSQL.
Usa SQLAlchemy com driver asyncpg para alta performance.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Motor de banco de dados assíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,  # Loga as queries SQL em modo debug
    pool_size=10,
    max_overflow=20,
)

# Fábrica de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency injection para obter sessão do banco de dados.
    Garante que a sessão seja sempre fechada após o uso.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
