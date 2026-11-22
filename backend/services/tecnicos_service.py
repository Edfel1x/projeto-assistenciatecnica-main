"""Operações de técnicos sobre o MySQL.

Campos reais da tabela (schema.sql): id_tecnico, nome, telefone, especialidade.
As validações replicam tecnicos.py.
"""

from ..database import obter_conexao, transacao
from .common import (
    ConflictError,
    NotFoundError,
    ValidationError,
    serializar_registro,
    texto_obrigatorio,
)

CAMPOS = "id_tecnico, nome, telefone, especialidade"


def listar() -> list[dict]:
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT {CAMPOS} FROM tecnicos ORDER BY nome, id_tecnico")
            return [serializar_registro(reg) for reg in cursor.fetchall()]
        finally:
            cursor.close()


def buscar_por_id(id_tecnico: int) -> dict | None:
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {CAMPOS} FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,)
            )
            return serializar_registro(cursor.fetchone())
        finally:
            cursor.close()


def criar(dados: dict) -> dict:
    nome = texto_obrigatorio(dados.get("nome"), "nome", 100)
    telefone = texto_obrigatorio(dados.get("telefone"), "telefone", 20)
    especialidade = texto_obrigatorio(dados.get("especialidade"), "especialidade", 100)

    with transacao() as (_, cursor):
        cursor.execute(
            "INSERT INTO tecnicos (nome, telefone, especialidade) VALUES (%s, %s, %s)",
            (nome, telefone, especialidade),
        )
        novo_id = cursor.lastrowid
    return buscar_por_id(novo_id)


def atualizar(id_tecnico: int, dados: dict) -> dict:
    if buscar_por_id(id_tecnico) is None:
        raise NotFoundError("Técnico não encontrado.")

    atualizacoes = []
    valores = []
    if "nome" in dados:
        atualizacoes.append("nome = %s")
        valores.append(texto_obrigatorio(dados["nome"], "nome", 100))
    if "telefone" in dados:
        atualizacoes.append("telefone = %s")
        valores.append(texto_obrigatorio(dados["telefone"], "telefone", 20))
    if "especialidade" in dados:
        atualizacoes.append("especialidade = %s")
        valores.append(texto_obrigatorio(dados["especialidade"], "especialidade", 100))

    if not atualizacoes:
        raise ValidationError("Nenhum campo válido foi informado para atualização.")

    valores.append(id_tecnico)
    with transacao() as (_, cursor):
        cursor.execute(
            f"UPDATE tecnicos SET {', '.join(atualizacoes)} WHERE id_tecnico = %s",
            tuple(valores),
        )
        if cursor.rowcount == 0:
            raise NotFoundError("Técnico não encontrado.")
    return buscar_por_id(id_tecnico)


def excluir(id_tecnico: int) -> None:
    """Exclui o técnico, liberando os vínculos que o banco permitir.

    Cancelar uma ordem NÃO remove o vínculo: a linha continua apontando para
    o técnico. Por isso desvinculamos automaticamente as ordens que aceitam
    técnico nulo (Aberta, Em manutenção e Cancelada). Ordens Concluídas são
    protegidas por CHECK e exigem a exclusão da ordem antes.
    """
    with transacao() as (_, cursor):
        cursor.execute(
            "SELECT COUNT(*) AS total FROM ordens_servico "
            "WHERE id_tecnico = %s AND status = 'Concluída'",
            (id_tecnico,),
        )
        if cursor.fetchone()["total"]:
            raise ConflictError(
                "Este técnico está vinculado a ordens concluídas. Exclua essas "
                "ordens na tela Ordens de Serviço antes de excluir o técnico."
            )

        cursor.execute(
            "UPDATE ordens_servico SET id_tecnico = NULL WHERE id_tecnico = %s",
            (id_tecnico,),
        )
        cursor.execute("DELETE FROM tecnicos WHERE id_tecnico = %s", (id_tecnico,))
        if cursor.rowcount == 0:
            raise NotFoundError("Técnico não encontrado.")
