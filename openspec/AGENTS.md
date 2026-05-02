# OpenSpec — Convenções FixNow

## O que é OpenSpec

OpenSpec é a metodologia de Spec-Driven Development (SDD) usada neste projeto.
Antes de qualquer mudança significativa, criamos uma especificação formal que o agente deve seguir.

## Quando usar OpenSpec (obrigatório)

- ✅ Nova feature ou domínio (ex: módulo de pagamentos)
- ✅ Mudança de arquitetura
- ✅ Nova integração com serviço externo
- ✅ Mudança no schema do banco de dados
- ✅ Nova rota na API

## Quando NÃO precisa de OpenSpec

- ✅ Correção de bug simples
- ✅ Atualização de documentação
- ✅ Refatoração interna sem impacto na API
- ✅ Ajuste de configuração

## Estrutura de uma mudança

```
openspec/changes/<nome-da-mudanca>/
├── .openspec.yaml   ← metadados
├── proposal.md      ← O QUE será feito e POR QUÊ
├── design.md        ← COMO será feito (arquitetura)
└── tasks.md         ← lista de tarefas para o agente executar
```

## Fluxo

```
Lucas descreve o que quer
        ↓
Agente cria proposal.md
        ↓
Lucas aprova ✅
        ↓
Agente cria design.md
        ↓
Lucas aprova ✅
        ↓
Agente cria tasks.md
        ↓
Agente implementa task por task
        ↓
Agente marca [x] ao concluir
        ↓
Mudança arquivada em proposals/
```

## Template de proposta

Veja `templates/proposal-template.md`

## Mudanças em andamento

| ID | Nome | Status |
|---|---|---|
| 001 | setup-inicial | ✅ Concluído |
| 002 | modulo-usuarios | 🔄 Em andamento |
