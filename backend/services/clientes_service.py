"""Operações de clientes sobre o MySQL.

Campos reais da tabela (schema.sql): id_cliente, nome, telefone, email.
As validações de nome/telefone obrigatórios replicam clientes.py.
"""

from ..database import obter_conexao, transacao
from .common import (
    NotFoundError,
    ValidationError,
    serializar_registro,
    texto_obrigatorio,
    texto_opcional,
)

CAMPOS = "id_cliente, nome, telefone, email"


def listar() -> list[dict]:
    """Lista todos os clientes ordenados por nome (pesquisa feita no front)."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT {CAMPOS} FROM clientes ORDER BY nome, id_cliente")
            return [serializar_registro(reg) for reg in cursor.fetchall()]
        finally:
            cursor.close()


def buscar_por_id(id_cliente: int) -> dict | None:
    """Retorna um cliente pelo ID ou None."""
    with obter_conexao() as conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {CAMPOS} FROM clientes WHERE id_cliente = %s", (id_cliente,)
            )
            return serializar_registro(cursor.fetchone())
        finally:
            cursor.close()


def criar(dados: dict) -> dict:
    """Cadastra um cliente e devolve o registro criado."""
    nome = texto_obrigatorio(dados.get("nome"), "nome", 100)
    telefone = texto_obrigatorio(dados.get("telefone"), "telefone", 20)
    email = texto_opcional(dados.get("email"), "email", 100)

    with transacao() as (_, cursor):
        cursor.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (%s, %s, %s)",
            (nome, telefone, email),
        )
        novo_id = cursor.lastrowid
    return buscar_por_id(novo_id)


def atualizar(id_cliente: int, dados: dict) -> dict:
    """Atualiza os campos enviados. Campos ausentes são mantidos."""
    if buscar_por_id(id_cliente) is None:
        raise NotFoundError("Cliente não encontrado.")

    atualizacoes = []
    valores = []
    if "nome" in dados:
        atualizacoes.append("nome = %s")
        valores.append(texto_obrigatorio(dados["nome"], "nome", 100))
    if "telefone" in dados:
        atualizacoes.append("telefone = %s")
        valores.append(texto_obrigatorio(dados["telefone"], "telefone", 20))
    if "email" in dados:
        atualizacoes.append("email = %s")
        valores.append(texto_opcional(dados["email"], "email", 100))

    if not atualizacoes:
        raise ValidationError("Nenhum campo válido foi informado para atualização.")

    valores.append(id_cliente)
    with transacao() as (_, cursor):
        cursor.execute(
            f"UPDATE clientes SET {', '.join(atualizacoes)} WHERE id_cliente = %s",
            tuple(valores),
        )
        # rowcount protege contra exclusão concorrente entre a checagem e o UPDATE.
        if cursor.rowcount == 0:
            raise NotFoundError("Cliente não encontrado.")
    return buscar_por_id(id_cliente)


def excluir(id_cliente: int) -> None:
    """Exclui um cliente. FKs com ON DELETE RESTRICT geram conflito 409."""
    with transacao() as (_, cursor):
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        if cursor.rowcount == 0:
            raise NotFoundError("Cliente não encontrado.")
