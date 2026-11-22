# API REST — BCDADOS

Base URL padrão: `http://localhost:5000/api`

Todas as requisições e respostas usam JSON. Envie o header `Content-Type: application/json` em `POST`, `PUT` e `PATCH`.

## Padrão de resposta

Sucesso:

```json
{
  "success": true,
  "message": "Operação realizada com sucesso.",
  "data": {}
}
```

Erro:

```json
{
  "success": false,
  "message": "Dados inválidos.",
  "error": "O campo 'nome' não pode estar vazio."
}
```

`data` é omitido quando não há conteúdo (ex.: exclusões). Mensagens de erro nunca expõem SQL, senhas ou detalhes internos do banco.

## Códigos HTTP

| Código | Uso |
|---|---|
| 200 | Sucesso em leitura, atualização ou exclusão |
| 201 | Recurso criado |
| 400 | Dados inválidos ou faltantes |
| 404 | Recurso não encontrado / rota inexistente |
| 405 | Método não permitido |
| 409 | Conflito com regra de negócio ou integridade referencial |
| 415 | Corpo não está em `application/json` |
| 500 | Erro interno genérico |
| 503 | Banco indisponível ou mal configurado |

---

## Saúde da API

### `GET /api/health`

Verifica apenas se o servidor Flask está no ar (não consulta o banco).

```json
{
  "success": true,
  "message": "API BCDADOS online.",
  "data": { "status": "ok" }
}
```

---

## Clientes

Campos reais: `id_cliente`, `nome`, `telefone`, `email`.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/clientes` | Lista todos, ordenados por nome |
| GET | `/api/clientes/{id}` | Busca por ID |
| POST | `/api/clientes` | Cadastra |
| PUT | `/api/clientes/{id}` | Atualiza campos enviados |
| DELETE | `/api/clientes/{id}` | Exclui (409 se houver equipamentos vinculados) |

**POST /api/clientes**

```json
{ "nome": "Maria Silva", "telefone": "11999999999", "email": "maria@exemplo.com" }
```

`nome` e `telefone` são obrigatórios; `email` é opcional.

---

## Técnicos

Campos reais: `id_tecnico`, `nome`, `telefone`, `especialidade`.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/tecnicos` | Lista todos |
| GET | `/api/tecnicos/{id}` | Busca por ID |
| POST | `/api/tecnicos` | Cadastra |
| PUT | `/api/tecnicos/{id}` | Atualiza campos enviados |
| DELETE | `/api/tecnicos/{id}` | Exclui e desvincula ordens abertas/canceladas (409 se houver ordens concluídas) |

**POST /api/tecnicos**

```json
{ "nome": "João Oliveira", "telefone": "11888888888", "especialidade": "Eletrônica" }
```

Os três campos são obrigatórios.

---

## Equipamentos

Campos reais: `id_equipamento`, `id_cliente`, `tipo`, `marca`, `modelo`, `numero_serie`, `status`, `diagnostico`. A resposta inclui também `nome_cliente` (join com clientes).

Status válidos do equipamento (ENUM do MySQL): `Disponível`, `Em análise`, `Em manutenção`, `Aguardando peça`, `Pronto para entrega`, `Entregue`. Padrão: `Disponível`.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/equipamentos` | Lista com dados do cliente |
| GET | `/api/equipamentos/{id}` | Busca por ID |
| POST | `/api/equipamentos` | Cadastra (valida cliente existente) |
| PUT | `/api/equipamentos/{id}` | Atualiza campos enviados (inclusive status/diagnóstico) |
| PATCH | `/api/equipamentos/{id}/situacao` | Atualiza somente `status` e/ou `diagnostico` |
| DELETE | `/api/equipamentos/{id}` | Exclui (409 se houver ordens vinculadas) |

**POST /api/equipamentos**

```json
{
  "id_cliente": 1,
  "tipo": "Notebook",
  "marca": "Dell",
  "modelo": "Latitude 5420",
  "numero_serie": "ABC123456",
  "status": "Disponível",
  "diagnostico": null
}
```

Os cinco primeiros campos são obrigatórios. `id_cliente` deve existir. `status` e `diagnostico` são opcionais.

**PATCH /api/equipamentos/{id}/situacao**

```json
{ "status": "Aguardando peça", "diagnostico": "Fonte substituída; aguardando chegada." }
```

Envie ao menos um dos dois campos. `diagnostico` vazio limpa o valor (volta a `null`). Esse diagnóstico é o do **equipamento**, independente do `diagnostico` da ordem de serviço; a interface mostra ambos para contexto.

> Persistência: se o usuário do MySQL puder `ALTER TABLE`, os valores ficam nas colunas `status`/`diagnostico` de `equipamentos`. Caso contrário (é o caso do usuário padrão `bcdados_app`), ficam em `dados/situacao_equipamentos.json`. A API e a interface funcionam igual nos dois casos.

---

## Ordens de serviço

Campos reais: `id_ordem`, `id_equipamento`, `id_tecnico`, `defeito_relatado`, `diagnostico`, `servico_realizado`, `status`, `data_abertura`, `data_conclusao`, `valor_servico`. As respostas incluem dados de cliente, equipamento e técnico.

Status válidos (ENUM do MySQL): `Aberta`, `Em manutenção`, `Concluída`, `Cancelada`.

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/ordens-de-servico` | Lista todas com joins |
| GET | `/api/ordens-de-servico/{id}` | Busca por ID |
| POST | `/api/ordens-de-servico` | Abre ordem com status `Aberta` |
| PATCH | `/api/ordens-de-servico/{id}/diagnostico` | Atualiza diagnóstico |
| PATCH | `/api/ordens-de-servico/{id}/tecnico` | Atribui técnico |
| PATCH | `/api/ordens-de-servico/{id}/status` | Altera para `Aberta` ou `Em manutenção` |
| PATCH | `/api/ordens-de-servico/{id}/finalizar` | Conclui com valor e data |
| PATCH | `/api/ordens-de-servico/{id}/cancelar` | Cancela (mantém o vínculo) |
| DELETE | `/api/ordens-de-servico/{id}` | Exclui a ordem e libera o vínculo com equipamento/técnico |

**POST /api/ordens-de-servico**

```json
{ "id_equipamento": 3, "defeito_relatado": "Não liga após queda", "id_tecnico": 2 }
```

O equipamento deve existir (FK `NOT NULL`). O campo `id_tecnico` é **opcional**: informe-o para designar o responsável já na abertura da ordem; se omitido, use o `PATCH .../tecnico` depois. Quando informado, o técnico precisa existir.

**PATCH .../diagnostico**

```json
{ "diagnostico": "Placa mãe danificada" }
```

**PATCH .../tecnico**

```json
{ "id_tecnico": 2 }
```

**PATCH .../status**

```json
{ "status": "Em manutenção" }
```

`Concluída` e `Cancelada` são rejeitadas aqui (409) — use as rotas específicas.

**PATCH .../finalizar**

```json
{ "valor_servico": "320,50" }
```

Aceita número ou string com vírgula decimal. Regras (replicadas de `ordens_servico.py`):

- a ordem não pode estar encerrada;
- precisa ter técnico atribuído;
- precisa ter diagnóstico registrado;
- valor não pode ser negativo.

Em caso de sucesso, define `status = Concluída` e `data_conclusao = NOW()`.

**PATCH .../cancelar** — sem corpo. Não permite cancelar uma ordem `Concluída` nem repetir o cancelamento.

---

## Dashboard

### `GET /api/dashboard`

Todos os números são calculados no MySQL (`COUNT`/`GROUP BY`), sem dados fictícios.

```json
{
  "success": true,
  "message": "Indicadores obtidos com sucesso.",
  "data": {
    "total_clientes": 12,
    "total_tecnicos": 3,
    "total_equipamentos": 20,
    "total_ordens": 45,
    "ordens_em_andamento": 7,
    "ordens_finalizadas": 30,
    "ordens_pendentes": 6,
    "ordens_canceladas": 2,
    "ordens_por_status": {
      "Aberta": 6,
      "Em manutenção": 7,
      "Concluída": 30,
      "Cancelada": 2
    },
    "ordens_recentes": []
  }
}
```

> Os valores acima são apenas ilustrativos da forma da resposta. A aplicação nunca inventa números: em execução real, os valores vêm das consultas ao banco.

---

## CORS

Somente as origens listadas em `CORS_ORIGINS` (no `.env`) podem chamar a API via navegador. Métodos permitidos: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`.

## Segurança

- Credenciais apenas no `.env` (ignorado pelo Git).
- Todas as consultas com valores do usuário são parametrizadas (`%s`).
- A API não possui autenticação — veja a recomendação no relatório final para versões futuras.
