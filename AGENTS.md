# FixNow — Agente de Desenvolvimento

## Sobre o Projeto

**FixNow** é uma plataforma brasileira de marketplace de serviços domésticos e técnicos (encanador, eletricista, pintor, diarista, etc.), desenvolvida como TCC do MBA em Engenharia de Dados na FIAP — trilha Startup One.

A plataforma resolve os principais problemas do GetNinjas: falta de segurança, profissionais não qualificados, pagamentos inseguros e ausência de rastreamento em tempo real.

**Stack:** Python · FastAPI · PostgreSQL · Redis · Apache Kafka · Docker

---

## Regras para o Agente

### Sempre siga estas diretrizes:

1. **Leia o OpenSpec antes de codar.** Qualquer nova feature começa com uma proposta em `openspec/changes/`. Não escreva código antes de ter `proposal.md` e `tasks.md` aprovados.
2. **Idioma:** Todo código em inglês. Comentários, commits e documentação em português.
3. **Arquitetura em camadas:** respeite sempre a separação `routes → services → models`.
4. **Testes obrigatórios:** toda nova rota ou serviço deve ter teste correspondente em `tests/`.
5. **Variáveis de ambiente:** nunca hardcode credenciais. Use sempre `.env` com `python-dotenv`.
6. **Commits semânticos:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`.

### Estrutura do projeto:

```
fixnow/
├── AGENTS.md              ← você está aqui
├── CLAUDE.md              ← instruções específicas para Claude
├── README.md              ← documentação principal
├── .env.example           ← variáveis de ambiente (nunca commitar .env)
├── pyproject.toml         ← dependências
├── openspec/              ← especificações e propostas
│   ├── AGENTS.md          ← convenções OpenSpec
│   ├── proposals/         ← propostas aprovadas
│   ├── changes/           ← mudanças em andamento
│   └── templates/         ← templates de proposta
├── .agent/
│   ├── workflows/         ← fluxos de trabalho do agente
│   └── skills/            ← habilidades especializadas
├── app/
│   ├── main.py            ← entry point FastAPI
│   ├── core/              ← config, segurança, database
│   ├── api/routes/        ← endpoints da API
│   ├── models/            ← modelos SQLAlchemy
│   ├── schemas/           ← schemas Pydantic
│   └── services/          ← lógica de negócio
├── tests/                 ← testes automatizados
└── docs/                  ← documentação técnica
```

### Domínios da plataforma:

- **users** — clientes e profissionais
- **professionals** — perfil, qualificações, Trust Score
- **services** — solicitações de serviço
- **matching** — algoritmo de seleção de profissional
- **payments** — transações seguras
- **tracking** — localização em tempo real
- **ratings** — avaliações pós-serviço
- **notifications** — alertas e comunicação

---

## Fluxo OpenSpec (obrigatório para mudanças grandes)

```
1. Criar proposta → openspec/changes/<nome>/proposal.md
2. Aguardar aprovação do Lucas
3. Criar design → openspec/changes/<nome>/design.md
4. Criar tasks → openspec/changes/<nome>/tasks.md
5. Implementar seguindo as tasks
6. Marcar tasks como [x] ao concluir
7. Arquivar em openspec/proposals/
```

Trigger obrigatório para OpenSpec:
- Nova feature ou domínio
- Mudança de arquitetura
- Integração com serviço externo
- Mudança no banco de dados

---

## Contexto de Negócio

**Problema:** Usuários do GetNinjas relatam falta de segurança nos pagamentos, profissionais sem qualificação verificada e ausência de rastreamento do profissional contratado.

**Solução FixNow:**
- Trust Score: score de confiabilidade do profissional baseado em histórico, avaliações e pontualidade
- Pagamento seguro via escrow (liberado só após conclusão)
- Rastreamento em tempo real do profissional (como Uber)
- Algoritmo de matching inteligente com IA

**Modelo de receita:** Comissão de 15-20% por serviço + planos premium para profissionais

**Mercado:** Brasil — 70M+ de usuários potenciais
