# PROMPT PARA RODAR NO ANTIGRAVITY — FixNow Setup Inicial

Cole esse prompt no agente Claude dentro do Antigravity:

---

Você está trabalhando no projeto FixNow, meu TCC do MBA em Engenharia de Dados na FIAP.

Leia o arquivo AGENTS.md e o CLAUDE.md para entender o projeto antes de qualquer ação.

Agora execute as seguintes tarefas em ordem:

1. Instale as dependências do projeto:
   pip install -e ".[dev]"

2. Configure o banco de dados:
   - Copie .env.example para .env
   - Suba os serviços com: docker-compose up -d
   - Aguarde o PostgreSQL estar disponível

3. Configure o Alembic para migrações:
   alembic init alembic
   - Edite alembic/env.py para usar o DATABASE_URL do .env e importar os models

4. Crie e aplique a primeira migração:
   alembic revision --autogenerate -m "criacao tabela usuarios"
   alembic upgrade head

5. Suba a API e verifique se está funcionando:
   uvicorn app.main:app --reload
   - Abra http://localhost:8000/docs no browser
   - Confirme que o Swagger está disponível

6. Rode os testes:
   pytest tests/ -v

7. Configure o Git e suba para o GitHub:
   git init
   git add .
   git commit -m "feat: setup inicial da plataforma FixNow"
   git branch -M main
   git remote add origin https://github.com/Lucascosta-dbm/fixnow.git
   git push -u origin main

Após concluir, me diga quais tarefas foram concluídas e se houve algum erro.
