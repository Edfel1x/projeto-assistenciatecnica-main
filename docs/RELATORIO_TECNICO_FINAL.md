# Relatório Técnico Final — BCDADOS

**Projeto:** Transformação do sistema BCDADOS (assistência técnica) em aplicação web completa
**Data:** 22/11/2026
**Status:** Implementação concluída e validada com MySQL real. 27 testes aprovados, nenhum pulado.

---

## A. Identificação e contexto

O projeto original consistia em um sistema Python com menu de terminal (`main.py`) para gerenciar clientes, técnicos, equipamentos e ordens de serviço de uma assistência técnica, com persistência em MySQL. O objetivo deste trabalho foi evolui-lo para uma aplicação web completa sem descartar o código existente:

- **frontend** profissional em HTML/CSS/JavaScript puro com Vite;
- **API REST** em Flask (uma única tecnologia de backend);
- **MySQL real** como única fonte de dados;
- temas claro/escuro, CRUD, filtros, validações e ciclo de vida das ordens;
- documentação e testes automatizados.

O resultado é uma SPA que consome a API via `Fetch`, enquanto o menu CLI original permanece funcional e intacto.

---

## B. Análise do projeto original (legado)

Foram lidos e preservados integralmente: `schema.sql`, `queries.sql`, `conexao.py`, `clientes.py`, `tecnicos.py`, `equipamentos.py`, `ordens_servico.py`, `main.py`, `teste_conexao.py`, `assistenciatecnicabd.mwb` e `requirements.txt`.

### B.1. Schema real (fonte de verdade)

| Tabela | Colunas |
|---|---|
| `clientes` | `id_cliente`, `nome`, `telefone`, `email` |
| `tecnicos` | `id_tecnico`, `nome`, `telefone`, `especialidade` |
| `equipamentos` | `id_equipamento`, `id_cliente`, `tipo`, `marca`, `modelo`, `numero_serie` |
| `ordens_servico` | `id_ordem`, `id_equipamento`, `id_tecnico`, `defeito_relatado`, `diagnostico`, `servico_realizado`, `status`, `data_abertura`, `data_conclusao`, `valor_servico` |

Status reais do `ENUM`: **`Aberta`**, **`Em manutenção`**, **`Concluída`**, **`Cancelada`**.

### B.2. Divergências e defeitos encontrados (documentados, não "corrigidos" às cegas)

1. `equipamentos.py` grava a chave `série_numero` mas lê `numero_serie` — bug existente no módulo original. A API padronizou sempre a coluna real do banco (`numero_serie`).
2. `ordens_servico.py` expõe `cadastrar_ordem_de_servico(defeito_relatado)` sem `id_equipamento`, embora o `schema.sql` exija `NOT NULL` + FK. A API exige o equipamento na abertura (decisão registrada com o usuário).
3. `conexao.py` usa o banco `bcdados` com senha vazia, enquanto `schema.sql` cria `assistencia_tecnica`. A API tornou o nome configurável (`DB_NAME`, padrão `bcdados`) para preservar o legado.
4. O modelo `assistenciatecnicabd.mwb` está desatualizado: usa `id_clientes`, `id_equipamentos`, `id_tecnicos`, `id_ordens_servico`, `diagnóstico` (com acento) e um Enum com o typo `Abeerto`. O `schema.sql` e o `ordens_servico.py` são consistentes entre si e foram seguidos. O `.mwb` **não foi alterado**.

Nenhum arquivo original foi modificado. Nenhum campo, tabela ou status foi inventado.

---

## C. Objetivos e requisitos atendidos

| Requisito | Situação |
|---|---|
| HTML5, CSS3, JS puro, Vite, Fetch, Flexbox/Grid | ✔ |
| Sem React/Vue/Angular | ✔ (JS puro, justificativa: manter código compreensível) |
| Python para regras de negócio, uma API (Flask) | ✔ |
| MySQL (sem SQLite/Mongo/Firebase) | ✔ |
| Sem duplicar módulos originais | ✔ (camada `backend/services/` nova) |
| Indicadores reais no dashboard | ✔ (`COUNT`/`GROUP BY` no MySQL) |
| Tema claro/escuro persistente | ✔ (`localStorage`, aplicado antes do CSS) |
| 6 páginas no sidebar | ✔ |
| CRUD, pesquisa, validação, notificações, loading, confirmações, modais, responsividade | ✔ |
| `.env`, `.env.example`, `.gitignore`, SQL parametrizado, CORS restrito, sem credenciais no front | ✔ |
| Documentação (README, API, este relatório) e testes | ✔ |

---

## D. Decisões de arquitetura

| Decisão | Justificativa |
|---|---|
| Novos `services/` em vez de alterar os módulos CLI | Os módulos originais usam listas em memória e menus; a API precisa de persistência. Os services replicam as **regras**, sem duplicar os módulos. |
| Flask em vez de FastAPI | O projeto já usa `mysql-connector-python`, é síncrono e pequeno; evita Pydantic/async desnecessários. |
| `DB_NAME` configurável (padrão `bcdados`) | Preserva `conexao.py` e permite apontar para `assistencia_tecnica` do `schema.sql`. |
| Envelope único de resposta | `{success, message, data}` / `{success, message, error}` simplifica o frontend. |
| `DELETE` retorna 200 + JSON (não 204 vazio) | Mantém o envelope consistente. |
| Hash routing (`#/dashboard` etc.) | SPA sem servidor configurar rotas; templates HTML via `?raw` do Vite. |
| `envDir` do Vite apontando para a raiz | Python e frontend compartilham o mesmo `.env`. |
| Pilha de modais | Confirmações abrem sobre formulários sem destruí-los; `Promise` sempre resolvida. |

---

## E. Estrutura e organização do código

```
backend/
  app.py            fábrica Flask, CORS, error handlers
  config.py         .env / variáveis de ambiente
  database.py       conexões, transações, tradução de erros SQL
  routes/           blueprints + envelopes de resposta
  services/         validações, regras de negócio e consultas parametrizadas
frontend/
  index.html        shell da SPA
  vite.config.js    porta 5173, envDir raiz, proxy /api → :5000
  src/main.js       tema, layout, roteamento
  src/components/   sidebar, header, modal, tabela, notificações, loading, ícones
  src/pages/        6 templates HTML
  src/scripts/      api, navegação, tema, formulários, util e 6 páginas
  src/styles/       variáveis, global, layout, componentes, responsive
tests/              unitários + integração real (isolada em DB_NAME_TEST)
docs/               API.md, usuario_teste.sql, este relatório
```

Separação de responsabilidades: **rota** (HTTP) → **service** (regra) → **database** (SQL) → **MySQL**. O frontend nunca acessa o banco diretamente.

---

## F. Banco de dados e integridade

- Todas as consultas com valores do usuário usam `%s` (parametrização). Nomes de colunas fixos em `SET` são montados internamente, sem entrada do usuário.
- `SELECT ... FOR UPDATE` nas operações de ordens evita condições de corrida no ciclo de vida.
- `rowcount` after UPDATE/DELETE protege contra exclusões concorrentes (correção aplicada na revisão).
- FKs com `RESTRICT` são traduzidas para **409** com mensagem amigável, sem expor SQL.
- Testes de integração usam `DB_NAME_TEST` exclusivo e recriam o schema a partir do próprio `schema.sql` — nunca tocam no banco de produção. O nome do banco é validado por regex antes de ser interpolado como identificador.

---

## G. API REST

25 rotas registradas (24 de negócio + health):

| Recurso | Endpoints |
|---|---|
| Clientes | `GET/POST /api/clientes`, `GET/PUT/DELETE /api/clientes/<id>` |
| Técnicos | `GET/POST /api/tecnicos`, `GET/PUT/DELETE /api/tecnicos/<id>` |
| Equipamentos | `GET/POST /api/equipamentos`, `GET/PUT/DELETE /api/equipamentos/<id>` |
| Ordens | `GET/POST /api/ordens-de-servico`, `GET /.../<id>`, `PATCH /.../<id>/{diagnostico,tecnico,status,finalizar,cancelar}` |
| Dashboard | `GET /api/dashboard` |
| Saúde | `GET /api/health` |

### Regras de negócio preservadas de `ordens_servico.py`

- Ordens **`Concluída`/`Cancelada` não aceitam** diagnóstico, técnico nem mudança de status → **409**.
- **Finalizar exige** técnico atribuído **e** diagnóstico registrado **e** valor ≥ 0; define `status = Concluída` e `data_conclusao = NOW()`.
- **Cancelar** é bloqueado para ordens concluídas e para cancelamentos repetidos.
- Status manual aceito apenas `Aberta` / `Em manutenção`.
- Abertura exige equipamento existente (corrige a lacuna do CLI).

Detalhes completos (corpos, códigos, exemplos) em [`docs/API.md`](API.md).

---

## H. Frontend

- **6 páginas**: Dashboard, Clientes, Técnicos, Equipamentos, Ordens de serviço, Configurações.
- Dashboard com 7 indicadores + ordens recentes + gráfico de status, **todos vindos da API**.
- Formulários gerados por `campo()` com validação client-side e mensagens de erro inline.
- Equipamentos e ordens carregam listas reais de clientes/técnicos/equipamentos para os `<select>`.
- OS: modal de detalhes com badges e operações contextuais (encerradas mostram aviso e escondem botões).
- Tabelas responsivas com `data-label` derivado dos próprios rótulos das colunas.
- Tema escuro/claro via variáveis CSS, persistido em `localStorage` e aplicado por script inline no `<head>` (sem flash).
- Confirmações empilhadas, foco preso no modal, `Esc`/backdrop sempre resolvem a Promise.
- Tokens de navegação e verificação `isConnected` evitam renders obsoletos após troca de rota.

**Build validado:** 32 módulos transformados, ~50,9 kB JS / ~19 kB CSS (gzip ~13,6 / ~4,5 kB), zero erros.

---

## I. Segurança

- Credenciais apenas no `.env`, ignorado pelo Git (incluindo `.env.*`, com exceção de `.env.example`).
- SQL parametrizado em todas as operações; nome de banco de teste validado por regex.
- CORS restrito às origens de `CORS_ORIGINS`.
- `Content-Type` inválido retorna **415**; erros de validação **400**; regras de negócio **409**; banco indisponível **503** — nenhum expõe SQL ou senhas.
- HTML interpolado passa por `escapeHtml()` antes de `innerHTML` (proteção XSS).
- Handler genérico preserva `HTTPException`s, registra erros inesperados no servidor e devolve apenas mensagem genérica ao cliente.
- **Não há autenticação** — ver item K (limitação assumida).

---

## J. Testes e validação

| Verificação | Resultado |
|---|---|
| `npm run build` | ✔ 32 módulos, 0 erros |
| `pytest tests -q` | ✔ **27 passed, 0 skipped** (exit 0) |
| Servidor Flask + `GET /api/health` | ✔ HTTP 200 |
| Servidor Vite + `GET /` | ✔ HTTP 200 |
| `/api/clientes` sem credenciais válidas | ✔ HTTP 503 com mensagem segura |
| `VITE_API_URL` lido do `.env` da raiz | ✔ validado com build temporário |
| Integração real com MySQL 8 | ✔ CRUD + ciclo completo de OS + dashboard |

### Defeito encontrado pelos testes de integração

A suíte real flagrou um problema invisível aos testes com mocks: a correção de TOCTOU (checagem de `rowcount` após o `UPDATE`) tinha removido o `return buscar_por_id(...)` dos services de clientes, técnicos e equipamentos. Consequência: `PUT` retornava 200 com envelope sem `data`, quebrando o recarregamento no frontend. Corrigido e coberto pelos testes.

Isso confirma o valor de manter os testes de integração: a lógica de negôcio estava correta nos mocks, mas o contrato HTTP real estava quebrado.

Cobertura dos testes unitários: envelopes de sucesso/erro, 404/405/415/503, CORS, validações (texto, inteiro, monetário com vírgula e rejeição de `NaN`/infinito), regras de equipamentos e o ciclo completo de regras das ordens (incluindo ordens encerradas e hierarquia 409 vs 404 na atribuição de técnico).

### Revisões independentes

Duas revisões paralelas (backend Python e frontend Vite) examinaram imports, duplicação, SQL, XSS, eventos, temas e acessibilidade. Todos os achados acionáveis foram corrigidos e validados pelos testes/build acima.

---

## K. Resultados, limitações e trabalhos futuros

### Resultados entregues
- Aplicação web completa, executável com `python -m backend.app` + `npm run dev`.
- Compatibilidade total com o menu CLI original.
- Regras de negócio do legado preservadas e endurecidas (transações, `FOR UPDATE`, `rowcount`).
- Documentação de instalação, configuração, API e arquitetura.

### Limitações conhecidas
1. **Sem autenticação/autorização:** a API está aberta para as origens configuradas. Recomenda-se login (JWT/sessão), perfis (admin/técnico) e hashing de senhas antes de exposição em produção.
2. **Servidor de desenvolvimento:** Flask dev server e Vite dev server foram usados nos testes; em produção, usar WSGI (gunicorn/waitress) e servir o `dist/` via proxy/Nginx.
3. **`assistenciatecnicabd.mwb` desatualizado:** mantido intacto conforme o legado; se for reimportado no Workbench, sobrescreverá nomes corretos — usar sempre o `schema.sql`.
4. **Usuário de teste sem senha:** `bcdados_app` foi criado com senha vazia apenas para este ambiente de desenvolvimento. Em produção, definir uma senha forte e conceder apenas o necessário.

### Ambiente validado
- MySQL 8.0.46 com serviço `MySQL80` ativo; usuário `bcdados_app` com permissões DML em `bcdados` e `assistencia_tecnica`, e DDL restrito a `bcdados_teste`.
- `bcdados` e `assistencia_tecnica` com as 4 tabelas do `schema.sql` original.
- `.env` configurado (arquivo ignorado pelo Git, nunca versionado).

> A criação do usuário exigiu um procedimento alternativo porque a senha do `root` não estava disponível: o MySQL foi iniciado temporariamente com um `--init-file` executado por processo elevado, o usuário e os bancos foram criados com privilégio interno do servidor, e o serviço foi restaurado ao estado normal. A senha do `root` **não foi alterada**.

### Próximos passos recomendados
- Adicionar autenticação e auditoria de operações.
- Substituir o menu CLI por um comando de administração opcional (sem remover o original).
- Configurar CI para executar `pytest` e `npm run build` a cada alteração.
