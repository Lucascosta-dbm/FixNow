# Instruções para Claude — Projeto FixNow

## Contexto

Este projeto é o TCC do Lucas Costa no MBA em Engenharia de Dados da FIAP (trilha Startup One).
A plataforma se chama **FixNow** — marketplace de serviços domésticos com foco em segurança, qualificação e rastreamento em tempo real.

## Comportamento esperado

- Sempre leia `AGENTS.md` antes de qualquer tarefa nova
- Antes de implementar qualquer feature, verifique se existe proposta OpenSpec em `openspec/changes/`
- Prefira soluções simples e bem documentadas — este é um projeto acadêmico que também precisa ser apresentado
- Quando criar código, adicione comentários em português explicando a lógica de negócio
- Sempre sugira o próximo passo ao final de cada tarefa

## Stack técnica

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Uvicorn |
| ORM | SQLAlchemy + Alembic |
| Banco principal | PostgreSQL |
| Cache | Redis |
| Streaming | Apache Kafka |
| Autenticação | JWT (python-jose) |
| Validação | Pydantic v2 |
| Testes | Pytest + httpx |
| Containerização | Docker + Docker Compose |

## Padrões de código

```python
# Exemplo de rota correta
@router.post("/services", response_model=ServiceResponse, status_code=201)
async def create_service(
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova solicitação de serviço."""
    return await service_service.create(db, payload, current_user)
```

## Comandos úteis

```bash
# Rodar o projeto
uvicorn app.main:app --reload

# Rodar testes
pytest tests/ -v

# Criar migração
alembic revision --autogenerate -m "descricao"

# Aplicar migração
alembic upgrade head
```

## Algoritmo de Matching (núcleo da plataforma)

O matching usa score ponderado:
```
Score = (0.30 × Proximidade) + (0.25 × Avaliação) + (0.20 × TrustScore) + (0.15 × Disponibilidade) + (0.10 × TempoResposta)
```

Este é o diferencial técnico do TCC — sempre que for relevante, explique como os dados alimentam esse algoritmo.
