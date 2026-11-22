# BCDADOS — Sistema de Gerenciamento para Assistência Técnica

Sistema web para gerenciar clientes, técnicos, equipamentos e ordens de serviço de uma assistência técnica. A aplicação evoluuiu um projeto Python existente (menu de terminal) com uma interface web profissional, uma API REST em Flask e persistência real em MySQL.

> **Compatibilidade preservada:** os arquivos originais (`main.py`, `clientes.py`, `tecnicos.py`, `equipamentos.py`, `ordens_servico.py`, `conexao.py`) continuam intactos e o menu de terminal continua funcionando. A API usa uma camada de serviços separada, que replica as regras de negócio com acesso persistente ao MySQL.

---

## 1. Tecnologias utilizadas

| Camada | Tecnologia | Função |
|---|---|---|
| Frontend | HTML5, CSS3, JavaScript (ES modules) | Interface e interatividade |
| Build do frontend | Vite 7 + Node.js/npm | Servidor de desenvolvimento e build de produção |
| API | Flask 3 + Flask-Cors | Endpoints REST e tratamento de erros |
| Configuração | python-dotenv | Variáveis de ambiente via `.env` |
| Banco | MySQL 8 + mysql-connector-python | Persistência e integridade referencial |
| Testes | pytest | Testes unitários e de integração |

Não foi utilizado React, Vue, Angular ou outro framework: a interface foi construída com JavaScript puro para manter o código compreensível, conforme solicitado.

---

## 2. Arquitetura da aplicação

```
Navegador (HTML / CSS / JavaScript — Vite)
        │  Fetch API (JSON) — VITE_API_URL
        ▼
API REST (Flask — backend/app.py)
        │  blueprints → services → regras de negócio
        ▼
Camada de acesso (backend/database.py — SQL parametrizado)
        │
        ▼
MySQL (banco definido em DB_NAME)
```

O frontend **nunca** acessa o MySQL. Nenhuma credencial do banco existe no JavaScript.

### Fluxo de uma requisição

1. O usuário clica em "Novo cliente" no frontend.
2. `clientes.js` valida o formulário e chama `api.criarCliente(dados)`.
3. `api.js` envia `POST /api/clientes` com corpo JSON.
4. O blueprint `clientes_routes.py` repassa os dados a `clientes_service.criar()`.
5. O service valida os campos, abre uma transação e executa `INSERT` parametrizado.
6. O MySQL confirma a gravação; a API devolve `{ success: true, message, data }`.
7. O frontend exibe uma notificação e recarrega a lista.

---

## 3. Estrutura de pastas

```
projeto-assistenciatecnica-main/
│
├── backend/                         # API REST Flask
│   ├── __init__.py
│   ├── app.py                       # Fábrica da aplicação, CORS e error handlers
│   ├── config.py                    # Configuração via variáveis de ambiente
│   ├── database.py                  # Conexões, transações e tradução de erros SQL
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── responses.py             # Envelopes padronizados de resposta
│   │   ├── clientes_routes.py
│   │   ├── tecnicos_routes.py
│   │   ├── equipamentos_routes.py
│   │   ├── ordens_routes.py
│   │   └── dashboard_routes.py
│   └── services/
│       ├── __init__.py
│       ├── common.py                # Validações, exceções e serialização
│       ├── clientes_service.py
│       ├── tecnicos_service.py
│       ├── equipamentos_service.py
│       ├── ordens_service.py
│       └── dashboard_service.py
│
├── frontend/                        # SPA com Vite
│   ├── index.html                   # Shell da aplicação
│   ├── package.json                 # Dependências e scripts npm
│   ├── package-lock.json            # Lockfile gerado pelo npm
│   ├── vite.config.js               # Porta 5173, proxy opcional /api → :5000
│   ├── public/
│   │   └── favicon.svg
│   └── src/
│       ├── main.js                  # Entrada: temas, layout e roteamento
│       ├── styles/
│       │   ├── variables.css        # Paletas escuro/claro e variáveis
│       │   ├── global.css           # Reset e tipografia
│       │   ├── layout.css           # Sidebar, header e grids
│       │   ├── components.css       # Cards, tabelas, forms, modais, badges
│       │   └── responsive.css       # Media queries
│       ├── components/
│       │   ├── icons.js             # Ícones SVG reutilizáveis
│       │   ├── sidebar.js
│       │   ├── header.js
│       │   ├── modal.js             # Modais e confirmações
│       │   ├── notification.js      # Notificações + escapeHtml (XSS)
│       │   ├── table.js             # Tabelas com rótulos mobile
│       │   └── loading.js           # Spinners e estados vazios
│       ├── pages/                   # Templates HTML carregados com ?raw
│       │   ├── dashboard.html
│       │   ├── clientes.html
│       │   ├── tecnicos.html
│       │   ├── equipamentos.html
│       │   ├── ordens.html
│       │   └── configuracoes.html
│       └── scripts/
│           ├── api.js               # Única camada de requisições HTTP
│           ├── navigation.js        # Roteamento por hash
│           ├── theme.js             # Alternância e persistência do tema
│           ├── util.js              # Formatação de datas, moeda e badges
│           ├── form.js              # Geração e validação de formulários
│           ├── dashboard.js
│           ├── clientes.js
│           ├── tecnicos.js
│           ├── equipamentos.js
│           ├── ordens.js
│           └── configuracoes.js
│
├── tests/                           # Testes automatizados
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_regras.py
│   └── test_integracao_mysql.py
│
├── docs/
│   ├── API.md                       # Documentação detalhada dos endpoints
│   └── sql/
│       └── usuario_teste.sql        # Criação de usuário dedicado do MySQL
│
├── clientes.py                      # Módulos originais do projeto (preservados)
├── tecnicos.py
├── equipamentos.py
├── ordens_servico.py
├── main.py                          # Menu CLI original (preservado)
├── conexao.py                       # Conexão original do CLI (preservada)
├── teste_conexao.py
├── schema.sql                       # Estrutura original do banco (não alterada)
├── queries.sql
├── assistenciatecnicabd.mwb
├── requirements.txt                 # Convertido para UTF-8, dependências da API
├── .env.example                     # Modelo de configuração (sem credenciais)
└── .gitignore                       # Ignora .env, .venv, node_modules, dist
```

---

## 4. Pré-requisitos

- **Python 3.10+** (testado com 3.15)
- **Node.js 18+** e **npm** (testado com Node 26 / npm 11)
- **MySQL 8+** em execução
- Git (opcional)

---

## 5. Instalação

### 5.1. Dependências Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No Linux/macOS: `source .venv/bin/activate`.

### 5.2. Dependências Node.js

```powershell
cd frontend
npm install
```

O `package-lock.json` garante versões reproduzíveis.

---

## 6. Configuração do banco MySQL

O `schema.sql` original cria o banco `assistencia_tecnica`. O `conexao.py` original usa `bcdados`. Para manter compatibilidade com ambos, o nome do banco é configurável.

1. Crie o banco e as tabelas:

```powershell
mysql -u root -p < schema.sql
```

2. Se preferir manter o nome `bcdados` (padrão da API), execute apenas as instruções `CREATE TABLE` do `schema.sql` dentro desse banco, ou ajuste `DB_NAME` no `.env` para `assistencia_tecnica`.

3. (Recomendado) Crie um usuário dedicado:

```powershell
mysql -u root -p < docs/sql/usuario_teste.sql
```

### 6.1. Variáveis de ambiente

```powershell
Copy-Item .env.example .env
```

Edite o `.env`:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=bcdados_app
DB_PASSWORD=
DB_NAME=bcdados

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
VITE_API_URL=
```

> **Recomendado:** mantenha `VITE_API_URL` vazio. Assim o navegador chama `/api` no **mesmo endereço da página** e o Vite repassa ao Flask por `127.0.0.1:5000`. Isso evita falhas de conexão quando o navegador resolve `localhost` como IPv6 (`::1`, onde o Flask não escuta) e também funciona se você abrir o sistema pelo IP da rede. Se precisar chamar a API direto, use `VITE_API_URL=http://127.0.0.1:5000/api` (prefira `127.0.0.1` a `localhost`).

Para **testes de integração**, configure também `DB_NAME_TEST=bcdados_teste`. O banco é criado pelo próprio `docs/sql/usuario_teste.sql` (com a conta administrativa) e os testes recriam apenas as tabelas a partir do `schema.sql`. Isso evita conceder privilégio global de `CREATE DATABASE` ao usuário da aplicação.

---

## 7. Como executar

### 7.1. Backend (API)

Na raiz do projeto, com o `.venv` ativado:

```powershell
python -m backend.app
```

Ao iniciar, o servidor tenta aplicar as migrações idempotentes
(`backend/migracoes.py`): se a conta do banco tiver `ALTER`, bancos antigos
ganham as colunas `status` e `diagnostico` em `equipamentos` sem perder dados.
O usuário padrão `bcdados_app` **não** tem essa permissão; nesse caso o
sistema funciona normalmente e guarda esses dois campos em
`dados/situacao_equipamentos.json` (criado automaticamente, ignorado pelo
Git). Se depois você der `ALTER` à conta (ou rodar a migração como root),
basta reiniciar: o backend passa a gravar também nas colunas do MySQL.

A API ficará em `http://localhost:5000`. Verifique com:

```powershell
curl http://localhost:5000/api/health
```

### 7.2. Frontend

Em outro terminal:

```powershell
cd frontend
npm run dev
```

Acesse `http://localhost:5173`.

> O Vite está com `strictPort: true`: se a porta 5173 estiver ocupada, ele
> encerra com erro em vez de abrir 5174/5175 (onde a configuração do proxy
> pode ficar desatualizada). Se isso acontecer, aperte **Ctrl+C** no terminal
> da instância antiga antes de rodar `npm run dev` novamente.

### 7.3. Build de produção

```powershell
cd frontend
npm run build
npm run preview
```

Os arquivos otimizados são gerados em `frontend/dist/`.

> Para servir o `dist/` pelo próprio Flask, adicione um blueprint estático — não implementado para manter as responsabilidades separadas (Node somente no frontend).

### 7.4. Menu CLI original

```powershell
python main.py
```

Continua disponível e funciona com os módulos originais em memória.

---

## 8. Testes

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

- Testes unitários (API com mocks + regras de negócio): executam sem banco.
- Testes de integração: são pulados automaticamente se `DB_NAME_TEST` não estiver configurado. Quando configurado, criam o schema a partir do `schema.sql` e testam CRUD real, regras de encerramento e integridade referencial.

Testes realizados neste ambiente: **27 passaram, 0 pulados**, incluindo os 2 testes de integração com MySQL real (CRUD de clientes e ciclo completo de ordem de serviço).

> **Nota:** os testes de integração revelaram um defeito que os testes unitários não detectavam: após a correção de concorrência no `UPDATE`, o service deixava de retornar o registro atualizado e o `PUT` respondia sem `data`. Corrigido nos três services de cadastro.

---

## 9. Principais funcionalidades

- Dashboard com indicadores reais e ordens recentes.
- Cadastro, edição, consulta, exclusão e pesquisa de clientes, técnicos e equipamentos.
- Exclusão de ordens na tela "Ordens de Serviço" para liberar vínculos: cancelar uma ordem **não** remove o vínculo; excluir, sim.
- Ao excluir um técnico, ordens abertas/canceladas são desvinculadas automaticamente; ordens concluídas exigem a exclusão da ordem antes (o banco exige técnico nelas).
- Abertura de ordens com equipamento existente obrigatório.
- Detalhamento completo da ordem com diagnóstico, técnico, status e valores.
- Operações de diagnóstico, atribuição, status, finalização e cancelamento com confirmação.
- Filtros por ID, status, técnico, cliente e equipamento.
- Badges visuais para os quatro status reais do banco.
- Tema escuro e claro com persistência em `localStorage`.
- Layout responsivo com sidebar recolhível e tabelas adaptadas para mobile.
- Notificações visuais, loading, estados vazios e validação de formulários.

---

## 10. Decisões importantes de arquitetura

| Decisão | Motivo |
|---|---|
| Novos `services/` em vez de alterar os módulos originais | Preserva o menu CLI e evita duplicar regras de negócio — os services replicam as regras com persistência |
| Flask (não FastAPI) | Projeto pequeno, sem necessidade de async/Pydantic; reduz dependências |
| `id_equipamento` obrigatório na abertura da OS | O `schema.sql` exige `NOT NULL` + FK; a função CLI antiga não pedia esse campo |
| `id_cliente` obrigatório no equipamento | O `schema.sql` exige `NOT NULL`; o módulo CLI permitia `None` (incompatível com o banco) |
| Nome `numero_serie` padronizado | O módulo `equipamentos.py` original grava `série_numero` mas lê `numero_serie` (bug existente); a API usa sempre a coluna real do banco |
| DELETE retorna 200 com JSON | Mantém o envelope de resposta consistente para o frontend |
| CORS restrito | Apenas as origens do Vite configuradas em `CORS_ORIGINS` |
| `schema.sql` como fonte dos nomes de colunas | O arquivo `assistenciatecnicabd.mwb` está desatualizado: usa `id_clientes`, `id_equipamentos`, `id_tecnicos`, `id_ordens_servico`, `diagnóstico` (com acento) e um Enum com o typo `Abeerto`. O `schema.sql` e o `ordens_servico.py` originais são consistentes (`id_cliente`, `id_equipamento`, `id_tecnico`, `id_ordem`, `diagnostico`, status `Aberta`/`Em manutenção`/`Concluída`/`Cancelada`) e foram seguidos pela API. O `.mwb` não foi alterado. |

---

## 11. Documentação da API

Consulte [`docs/API.md`](docs/API.md) para endpoints, parâmetros, códigos HTTP e exemplos de requisições e respostas.

O relatório técnico completo (seções A–K: contexto, análise do legado, decisões, arquitetura, segurança, testes, limitações e trabalhos futuros) está em [`docs/RELATORIO_TECNICO_FINAL.md`](docs/RELATORIO_TECNICO_FINAL.md).
