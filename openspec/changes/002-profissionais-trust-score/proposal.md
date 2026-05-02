# Proposta 002 — Módulo Profissionais + Trust Score

## Metadados

| Campo | Valor |
|---|---|
| ID | 002 |
| Nome | modulo-profissionais-trust-score |
| Autor | Lucas Costa |
| Status | ✅ Aprovado |
| Data | 2025-05 |

---

## Problema

A FixNow precisa diferenciar clientes de profissionais na plataforma.
Profissionais têm dados extras: especialidades, área de atuação, documentos verificados
e — o principal diferencial da plataforma — o **Trust Score**.

## O que é o Trust Score

É um score de 0 a 100 que mede a confiabilidade do profissional,
calculado automaticamente com base em dados reais da plataforma:

```
TrustScore = (avaliação_media × 0.35)
           + (taxa_conclusao   × 0.30)
           + (pontualidade     × 0.20)
           + (tempo_plataforma × 0.15)
```

Este score é recalculado a cada serviço concluído e alimenta diretamente
o algoritmo de matching — profissionais com Trust Score maior aparecem
primeiro para os clientes.

## Escopo

### Inclui:
- `app/models/professional.py` — modelo do profissional
- `app/models/service_request.py` — solicitação de serviço (base para calcular o score)
- `app/schemas/professional.py` — schemas Pydantic
- `app/services/professional_service.py` — CRUD e lógica de negócio
- `app/services/trust_score_service.py` — cálculo do Trust Score ← núcleo do TCC
- `app/api/routes/professionals.py` — endpoints da API
- `tests/test_professionals.py` — testes do módulo
- `tests/test_trust_score.py` — testes do cálculo do score

### Não inclui (próximas propostas):
- Algoritmo de matching completo (Proposta 003)
- Upload de documentos/fotos
- Notificações

## Rotas da API

- `POST /api/v1/professionals/profile` — cria perfil de profissional
- `GET  /api/v1/professionals/{id}` — busca profissional por ID
- `GET  /api/v1/professionals/` — lista profissionais (com filtros)
- `PATCH /api/v1/professionals/profile` — atualiza perfil
- `GET  /api/v1/professionals/{id}/trust-score` — retorna Trust Score detalhado

## Critérios de aceite

- [ ] Profissional criado com especialidades e área de atuação
- [ ] Trust Score calculado corretamente pela fórmula
- [ ] Endpoint retorna score + detalhamento de cada componente
- [ ] Score atualiza quando novos dados chegam
- [ ] Testes cobrem cálculo do score com diferentes cenários
