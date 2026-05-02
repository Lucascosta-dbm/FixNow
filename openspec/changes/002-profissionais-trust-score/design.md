# Design 002 — Módulo Profissionais + Trust Score

## Modelo de dados

```
users (existente)
  └── professionals (1:1 com user)
        ├── specialties (categorias de serviço)
        ├── service_area_km (raio de atendimento)
        ├── trust_score (0-100, recalculado automaticamente)
        ├── total_services (contador)
        ├── completed_services (contador)
        ├── cancelled_services (contador)
        └── avg_rating (média das avaliações)
```

## Fórmula do Trust Score

```python
def calculate_trust_score(professional) -> float:
    rating_score      = (professional.avg_rating / 5.0) * 100  # normaliza 0-5 para 0-100
    completion_rate   = professional.completion_rate * 100      # % de serviços concluídos
    punctuality_score = professional.punctuality_score          # % de chegadas no prazo
    seniority_score   = min(professional.months_active / 24, 1) * 100  # cap em 24 meses

    trust_score = (
        rating_score      * 0.35 +
        completion_rate   * 0.30 +
        punctuality_score * 0.20 +
        seniority_score   * 0.15
    )
    return round(min(max(trust_score, 0), 100), 2)  # garante 0-100
```

## Fluxo de atualização do score

```
Serviço concluído
      ↓
Usuário avalia profissional (1-5 estrelas)
      ↓
trust_score_service.recalculate(professional_id)
      ↓
Atualiza avg_rating, completion_rate, punctuality_score
      ↓
Calcula novo trust_score
      ↓
Salva no banco → afeta próximos matchings
```

## Especialidades disponíveis

```python
class Specialty(str, Enum):
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
```
