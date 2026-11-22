"""Operações de ordens de serviço sobre o MySQL.

Regras replicadas de ordens_servico.py (CLI):
  - defeito_relatado é obrigatório no cadastro;
  - ordens encerradas (Concluída/Cancelada) não aceitam diagnóstico,
    técnico nem mudança de status;
  - finalizar exige técnico, diagnóstico e valor não negativo;
  - cancelar não é permitido para uma ordem Concluída;
  - atualizar_status só aceita 'Aberta' e 'Em manutenção';
    Concluída e Cancelada usam rotas específicas.

Status reais do ENUM: Aberta, Em manutenção, Concluída, Cancelada.
"""

from ..database import obter_conexao, transacao
from . import equipamentos_service
from .common import (
    ConflictError,
    NotFoundError,
    ValidationError,
    inteiro_positivo,
    serializar_registro,
    texto_obrigatorio,
    valor_monetario,
)

STATUS_PERMITIDOS = ("Aberta", "Em manutenção", "Concluída", "Cancelada")
STATUS_ENCERRADOS = ("Concluída", "Cancelada")
STATUS_MANUAIS = ("Aberta", "Em manutenção")

CAMPOS = """os.id_ordem, os.id_equipamento, os.id_tecnico,
            os.defeito_relatado, os.diagnostico, os.servico_realizado,
            os.status, os.data_abertura, os.data_conclusao, os.valor_servico,
            e.tipo AS tipo_equipamento, e.marca AS marca_equipamento,
            e.modelo AS modelo_equipamento, e.numero_serie, e.id_cliente,
            c.nome AS nome_cliente, c.telefone AS telefone_cliente,
            t.nome AS nome_tecnico, t.especialidade AS especialidade_tecnico"""
JOINS = """FROM ordens_servico os
           INNER JOIN equipamentos e ON os.id_equipamento = e.id_equipamento
           INNER JOIN clientes c ON e.id_cliente = c.id_cliente
           LEFT JOIN tecnicos t ON os.id_tecnico = t.id_tecnico"""


def listar() -> list[dict]:
    """Lista ordens com dados de cliente, equipamento e técnico.

    Filtros disponíveis (id, status, técnico, cliente/equipamento) são
    aplicados no frontend sobre estes dados, evitando SQL dinâmico.
    """
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {CAMPOS} {JOINS} ORDER BY os.id_ordem DESC"
            )
            return [serializar_registro(reg) for reg in cursor.fetchall()]
        finally:
            cursor.close()


def buscar_por_id(id_ordem: int) -> dict | None:
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {CAMPOS} {JOINS} WHERE os.id_ordem = %s", (id_ordem,)
            )
            return serializar_registro(cursor.fetchone())
        finally:
            cursor.close()


def _buscar_para_atualizar(cursor, id_ordem: int) -> dict:
    """Busca a ordem com bloqueio pessimista dentro da transação."""
    cursor.execute(
        "SELECT id_ordem, id_tecnico, status, diagnostico "
        "FROM ordens_servico WHERE id_ordem = %s FOR UPDATE",
        (id_ordem,),
    )
    ordem = cursor.fetchone()
    if ordem is None:
        raise NotFoundError("Ordem de serviço não encontrada.")
    return ordem


def _exigir_aberta(ordem: dict, acao: str) -> None:
    """Impede alterações em ordens já encerradas (regra do CLI)."""
    if ordem["status"] in STATUS_ENCERRADOS:
        raise ConflictError(
            f"Não é possível {acao} em uma ordem {ordem['status']}."
        )


def criar(dados: dict) -> dict:
    """Abre uma nova ordem.

    O módulo CLI original cadastrava apenas o defeito, mas o schema.sql
    exige id_equipamento NOT NULL com FK. Por isso a API exige o
    equipamento e valida sua existência antes de inserir.

    O campo id_tecnico é opcional: permite designar o responsável já na
    abertura da ordem. Se ausente, a ordem fica sem técnico e a atribuição
    pode ser feita depois pelo endpoint /tecnico.
    """
    id_equipamento = inteiro_positivo(dados.get("id_equipamento"), "id_equipamento")
    if equipamentos_service.buscar_por_id(id_equipamento) is None:
        raise NotFoundError("Equipamento não encontrado para a ordem de serviço.")

    defeito = texto_obrigatorio(
        dados.get("defeito_relatado"), "defeito_relatado", 65535
    )

    id_tecnico = dados.get("id_tecnico")
    if id_tecnico is None or (isinstance(id_tecnico, str) and not id_tecnico.strip()):
        id_tecnico = None
    else:
        id_tecnico = inteiro_positivo(id_tecnico, "id_tecnico")

    with transacao() as (_, cursor):
        if id_tecnico is not None:
            cursor.execute(
                "SELECT 1 FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,)
            )
            if cursor.fetchone() is None:
                raise NotFoundError("Técnico não encontrado para a ordem de serviço.")

        cursor.execute(
            """INSERT INTO ordens_servico
               (id_equipamento, id_tecnico, defeito_relatado, status)
               VALUES (%s, %s, %s, 'Aberta')""",
            (id_equipamento, id_tecnico, defeito),
        )
        novo_id = cursor.lastrowid
    return buscar_por_id(novo_id)


def atualizar_diagnostico(id_ordem: int, dados: dict) -> dict:
    diagnostico = texto_obrigatorio(dados.get("diagnostico"), "diagnostico", 65535)

    with transacao() as (_, cursor):
        ordem = _buscar_para_atualizar(cursor, id_ordem)
        _exigir_aberta(ordem, "atualizar o diagnóstico")
        cursor.execute(
            "UPDATE ordens_servico SET diagnostico = %s WHERE id_ordem = %s",
            (diagnostico, id_ordem),
        )
    return buscar_por_id(id_ordem)


def atribuir_tecnico(id_ordem: int, dados: dict) -> dict:
    id_tecnico = inteiro_positivo(dados.get("id_tecnico"), "id_tecnico")

    with transacao() as (_, cursor):
        ordem = _buscar_para_atualizar(cursor, id_ordem)
        _exigir_aberta(ordem, "atribuir técnico")
        # Valida a FK na mesma transação: evita que uma ordem encerrada
        # com técnico inexistente responda 404 em vez de 409.
        cursor.execute("SELECT 1 FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,))
        if cursor.fetchone() is None:
            raise NotFoundError("Técnico não encontrado.")
        cursor.execute(
            "UPDATE ordens_servico SET id_tecnico = %s WHERE id_ordem = %s",
            (id_tecnico, id_ordem),
        )
    return buscar_por_id(id_ordem)


def atualizar_status(id_ordem: int, dados: dict) -> dict:
    """Altera o status apenas entre 'Aberta' e 'Em manutenção'."""
    status = dados.get("status")
    if not isinstance(status, str):
        raise ValidationError("O campo 'status' é obrigatório.")
    # Aceita variações de caixa e espaços, como fazia o CLI original.
    status_normalizado = next(
        (item for item in STATUS_PERMITIDOS if item.casefold() == status.strip().casefold()),
        None,
    )
    if status_normalizado is None:
        raise ValidationError("Status inválido.")
    if status_normalizado not in STATUS_MANUAIS:
        raise ConflictError(
            "Para concluir ou cancelar, utilize a operação específica da ordem."
        )

    with transacao() as (_, cursor):
        ordem = _buscar_para_atualizar(cursor, id_ordem)
        _exigir_aberta(ordem, "alterar o status")
        cursor.execute(
            "UPDATE ordens_servico SET status = %s WHERE id_ordem = %s",
            (status_normalizado, id_ordem),
        )
    return buscar_por_id(id_ordem)


def finalizar(id_ordem: int, dados: dict) -> dict:
    """Conclui a ordem: exige técnico, diagnóstico e valor do serviço."""
    valor = valor_monetario(dados.get("valor_servico"))

    with transacao() as (_, cursor):
        ordem = _buscar_para_atualizar(cursor, id_ordem)
        _exigir_aberta(ordem, "finalizar")
        if ordem["id_tecnico"] is None:
            raise ConflictError("Atribua um técnico antes de finalizar a ordem.")
        sem_diagnostico = not (ordem["diagnostico"] or "").strip()
        if sem_diagnostico:
            raise ConflictError("Registre um diagnóstico antes de finalizar a ordem.")

        cursor.execute(
            """UPDATE ordens_servico
               SET status = 'Concluída',
                   valor_servico = %s,
                   data_conclusao = NOW()
               WHERE id_ordem = %s""",
            (valor, id_ordem),
        )
    return buscar_por_id(id_ordem)


def cancelar(id_ordem: int) -> dict:
    with transacao() as (_, cursor):
        ordem = _buscar_para_atualizar(cursor, id_ordem)
        if ordem["status"] == "Concluída":
            raise ConflictError("Não é possível cancelar uma ordem concluída.")
        if ordem["status"] == "Cancelada":
            raise ConflictError("Esta ordem já foi cancelada.")

        cursor.execute(
            "UPDATE ordens_servico SET status = 'Cancelada' WHERE id_ordem = %s",
            (id_ordem,),
        )
    return buscar_por_id(id_ordem)


def excluir(id_ordem: int) -> None:
    """Exclui a ordem para liberar vínculos de equipamento/técnico.

    Cancelar NÃO remove o vínculo: a linha continua referenciando o
    equipamento e o técnico. Sem esta operação, a orientação dada ao usuário
    ("exclua os registros vinculados") era impossível de cumprir pela API.
    """
    with transacao() as (_, cursor):
        cursor.execute("DELETE FROM ordens_servico WHERE id_ordem = %s", (id_ordem,))
        if cursor.rowcount == 0:
            raise NotFoundError("Ordem de serviço não encontrada.")
