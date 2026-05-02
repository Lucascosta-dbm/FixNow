# Proposta 001 — Setup Inicial da Plataforma FixNow

## Metadados

| Campo | Valor |
|---|---|
| ID | 001 |
| Nome | setup-inicial |
| Autor | Lucas Costa |
| Status | ✅ Aprovado |
| Data | 2025-05 |

---

## Problema

Precisamos criar a estrutura base da API da FixNow com FastAPI, incluindo:
- Configuração do projeto
- Conexão com banco de dados
- Sistema de autenticação JWT
- Estrutura de rotas
- Primeiro módulo funcional (usuários)

## Solução

Criar o esqueleto completo da aplicação FastAPI seguindo arquitetura em camadas:
`routes → services → models`

## Escopo

### Inclui:
- `app/main.py` — entry point
- `app/core/config.py` — configurações
- `app/core/database.py` — conexão async com PostgreSQL
- `app/core/security.py` — JWT e hash de senha
- `app/models/user.py` — modelo de usuário
- `app/schemas/user.py` — schemas Pydantic
- `app/services/user_service.py` — lógica de negócio
- `app/api/routes/users.py` — endpoints de usuário
- `app/api/routes/auth.py` — login e registro
- `alembic/` — configuração de migrações
- `tests/test_users.py` — testes básicos

### Não inclui (próximas propostas):
- Módulo de profissionais
- Algoritmo de matching
- Pagamentos
- Rastreamento

## Critérios de aceite

- [ ] API sobe sem erros com `uvicorn app.main:app --reload`
- [ ] Swagger disponível em `/docs`
- [ ] Rota `POST /api/v1/auth/register` funciona
- [ ] Rota `POST /api/v1/auth/login` retorna JWT
- [ ] Rota `GET /api/v1/users/me` retorna dados do usuário autenticado
- [ ] Testes passam com `pytest tests/ -v`
- [ ] Migrações funcionam com `alembic upgrade head`
